from flask import Flask, render_template, request, redirect, url_for, session, jsonify, g

import utils
import config

import sqlite3
import bcrypt

app = Flask(__name__)
app.secret_key = config.key3

def get_db():
    if "db" not in g:
        g.db = sqlite3.connect("hotelhelper.db")
        g.db.row_factory = sqlite3.Row 
    return g.db

@app.teardown_appcontext
def close_db(exception):
    db = g.pop("db", None)
    if db is not None:
        db.close()

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/search.html", methods=["GET"])
def search_page():
    checkboxes = utils.generate_checkboxes()
    return render_template("search.html", checkboxes_html=checkboxes)


@app.route("/search", methods=["POST"])
def search_location():
    with app.app_context():
        db = get_db()
        c = db.cursor()  
        query = request.form["search"]
        query, error_message = utils.enter_query(query)
        if not query:
            return jsonify({"error": error_message})
        
        latitude, longitude, error_message = utils.get_coordinates(query)
        if not latitude or not longitude:
            return jsonify({"error": error_message})

        categories_str = ",".join(request.form.getlist("categories"))  

        user_id = session.get("user_id")

        results = utils.get_destinations(latitude, longitude, categories_str, c, db, user_id)

        return jsonify({"results": results})

@app.route("/register.html", methods=["GET", "POST"])
def register():
    username_error = ""
    password_error = ""

    if request.method == "POST":
        with app.app_context():
            db = get_db()
            c = db.cursor()
            username = request.form.get("username")
            password = request.form.get("password")

            c.execute("SELECT username FROM users WHERE username=?", (username,))
            if c.fetchone():
                username_error = "Username already exists - try another"
            else:
                if len(password) < 8:
                    password_error = "Password must be at least eight characters"
                else:
                    hashed_password = utils.hash_password(password)
                    c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_password))
                    db.commit()
                    c.execute("SELECT user_id FROM users WHERE username=?", (username,))
                    user_id = c.fetchone()[0]
                    session["user_id"] = user_id
                    session["username"] = username
                    return redirect(url_for("account"))

    return render_template("register.html", username_error=username_error, password_error=password_error)



@app.route("/login.html", methods=["GET", "POST"])
def login_handler():

    if request.method == "POST":
        with app.app_context():
            db = get_db()
            c = db.cursor()
            username = request.form.get("username")
            password = request.form.get("password")

            c.execute("SELECT user_id, username, password FROM users WHERE username=?", (username,))
            user_data = c.fetchone()
            if user_data and bcrypt.checkpw(password.encode("utf-8"), user_data[2].encode("utf-8")):
                session["user_id"] = user_data[0]
                session["username"] = user_data[1]
                return redirect(url_for("account"))
            else:
                error_message = "Invalid username or password"
                return render_template("login.html", error_message=error_message)

    return render_template("login.html")

@app.route("/account.html")
def account():
    if "user_id" in session and "username" in session:
        user_id = session["user_id"]
        username = session["username"]
        return render_template("account.html", user_id=user_id, username=username)
    else:
        return redirect(url_for("login_handler"))
    
@app.route("/delete_account", methods=["POST"])
def delete_account():
    if "user_id" in session:
        with app.app_context(): 
            db = get_db()
            c = db.cursor()
            user_id = session["user_id"]

            c.execute("SELECT username FROM users WHERE user_id=?", (user_id,))
            username = c.fetchone()

            if username:
                c.execute("DELETE FROM search_history WHERE user_id=?", (user_id,))
                c.execute("DELETE FROM users WHERE user_id=?", (user_id,))
                db.commit()
                session.clear()
                return redirect(url_for("home"))
    return redirect(url_for("home"))

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))

@app.route("/search_history")
def show_search_history():
    if "user_id" in session:
        user_id = session["user_id"]
        with app.app_context():
            db = get_db()
            c = db.cursor()
            search_history = utils.get_search_history(c, user_id) 
            return render_template("results_summary.html", search_history=search_history, all_searches=True)
    else:
        return redirect(url_for("login_handler"))

@app.route("/popular_searches")
def show_popular_searches():
    if "user_id" in session:
        user_id = session["user_id"]
        with app.app_context():
            db = get_db()
            c = db.cursor()
            popular_searches = utils.get_most_popular_searches(c, user_id) 
            return render_template("results_summary.html", popular_searches=popular_searches)
    else:
        return redirect(url_for("login_handler"))

@app.route("/results_filter.html", methods=["GET"])
def results_filter_page():
    return render_template("results_filter.html")

@app.route("/search_keyword", methods=["POST"])
def search_keyword():
    with app.app_context():
        db = get_db()
        c = db.cursor()
        keyword = request.form["keyword"]
        
        if len(keyword) < 3:
            error_message = "Keyword must be at least 3 characters."
            return render_template("results_filter.html", error_message=error_message)

        user_id = session.get("user_id")
        search_results = utils.search_history(c, user_id, keyword)

        return render_template("results_filter.html", search_results=search_results, keyword=keyword)


if __name__ == "__main__":
    with app.app_context():
        db = get_db()
        c = db.cursor()
        utils.create_tables(c)
        db.commit()

    app.run(debug=True)