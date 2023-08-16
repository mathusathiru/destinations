from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from database import User, SearchHistory, db
from sqlalchemy import func, desc
import database
import bcrypt
import config
import utils

app = Flask(__name__)
app.secret_key = config.key3
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///hotelhelper.db"
db.init_app(app)


@app.teardown_appcontext
def close_db(exception):
    db.session.remove()


@app.context_processor
def inject_image_url():
    return {"image_url": url_for("static", filename="images/logo.png")}


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/search.html", methods=["GET"])
def search_page():
    checkboxes = utils.generate_checkboxes()
    radius_buttons = utils.generate_radio_buttons()
    return render_template("search.html", checkboxes=checkboxes, radius_buttons=radius_buttons)


@app.route("/search", methods=["POST"])
def search_location():
    try:
        query = request.form["search"]
        query, error_message = utils.enter_query(query)
        if not query:
            return jsonify({"error": error_message})

        latitude, longitude, error_message = utils.get_coordinates(query)
        if not latitude or not longitude:
            return jsonify({"error": error_message})

        categories_str = ",".join(request.form.getlist("categories"))
        radius = int(request.form.get("radius"))

        user_id = session.get("user_id")

        results = utils.get_destinations(latitude, longitude, categories_str, radius, user_id, db.session)

        return jsonify({"results": results})

    except Exception as e:
        print("Error:", e)
        return jsonify({"error": str(e)})


@app.route("/register.html", methods=["GET", "POST"])
def register():
    username_error = ""

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        existing_user = db.session.query(User).filter_by(username=username).first()
        if existing_user:
            username_error = "Username already exists - try another"
        else:
            hashed_password = database.hash_password(password)
            new_user = User(username=username, password=hashed_password)
            db.session.add(new_user)
            db.session.commit()

            user_id = new_user.user_id
            session["user_id"] = user_id
            session["username"] = username
            return redirect(url_for("account"))

    return render_template("register.html", username_error=username_error)


@app.route("/login.html", methods=["GET", "POST"])
def login_handler():
    if request.method == "POST":
        try:
            username = request.form.get("username")
            password = request.form.get("password")

            user = User.query.filter_by(username=username).first()
            if user and bcrypt.checkpw(password.encode("utf-8"), user.password.encode("utf-8")):
                session["user_id"] = user.user_id
                session["username"] = user.username
                return redirect(url_for("account"))
            else:
                error_message = "Invalid username or password"
                return render_template("login.html", error_message=error_message)
        except Exception as e:
            return render_template("login.html", error_message=str(e))

    return render_template("login.html")


@app.route("/account.html")
def account():
    if "user_id" in session and "username" in session:
        user_id = session["user_id"]
        username = session["username"]
        return render_template("account.html", user_id=user_id, username=username)
    else:
        return redirect(url_for("login_handler"))


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))


@app.route("/search_keyword", methods=["GET", "POST"])
def search_keyword():
    if request.method == "POST":
        try:
            keyword = request.form["keyword"]
            if len(keyword) < 2:
                error_message = "Keyword must be at least 2 characters."
                return render_template("results.html", show_search_form=True, error_message=error_message)

            user_id = session.get("user_id")

            if user_id is None:
                return redirect(url_for("login_handler"))

            search_results = database.search_history(db.session, user_id, keyword)
    
            return render_template("results.html", show_search_form=True, search_results=search_results, keyword=keyword)
        except Exception as e:
            return render_template("results.html", show_search_form=True, error_message=str(e))

    return render_template("results.html", show_search_form=True)


@app.route("/delete_account", methods=["POST"])
def delete_account():
    if "user_id" in session:
        try:
            user_id = session["user_id"]
            user = User.query.get(user_id)

            if user:
                SearchHistory.query.filter_by(user_id=user_id).delete()

                db.session.delete(user)
                db.session.commit()

                session.clear()
                return redirect(url_for("home"))
        except Exception as e:
            return render_template("index.html", error_message=str(e))

    return redirect(url_for("home"))


@app.route("/search_history")
def show_search_history():
    if "user_id" in session:
        try:
            user_id = session["user_id"]
            search_history = SearchHistory.query.filter_by(user_id=user_id).all()
            return render_template("results.html", search_history=search_history, all_searches=True)
        except Exception as e:
            return render_template("results.html", error_message=str(e))
    else:
        return redirect(url_for("login_handler"))


@app.route("/popular_searches")
def show_popular_searches():
    if "user_id" in session:
        try:
            user_id = session["user_id"]
            popular_searches = db.session.query(SearchHistory.place_name, SearchHistory.address, func.count(SearchHistory.place_name).label("search_count")).\
                filter(SearchHistory.user_id == user_id).\
                group_by(SearchHistory.place_name, SearchHistory.address).\
                order_by(desc("search_count")).\
                limit(10).all()

            print(popular_searches)

            return render_template("results.html", popular_searches=popular_searches)
        except Exception as e:
            return render_template("results.html", error_message=str(e))
    else:
        return redirect(url_for("login_handler"))


if __name__ == "__main__":
    with app.app_context():
        db.create_all()

    app.run(debug=True)
