from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from database import User, db
import database
import config
import utils

# create Flask app instance, obtaining the secret key from config file
app = Flask(__name__)
app.secret_key = config.key3

# set SQLAlchemy database URI configuration for the Flask app
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///hotelhelper.db"

# initialise database object with the Flask app
db.init_app(app)

# function to remove database session when the app context is torn down
@app.teardown_appcontext
def close_db(exception):
    # removes current session from database object
    db.session.remove()

# function to process image into a template context
@app.context_processor
def inject_image_url():
    # static image to be used in website header which contains a link to the index page (handled in layout.html)
    return {"image_url": url_for("static", filename="images/logo.png")}

# route for the root Flask app url, the homepage
@app.route("/")
def home():
    # renders index.html template
    return render_template("index.html")

# route for the search.html URL Flask app path, utilising the GET method
@app.route("/search.html", methods=["GET"])
def search_page():
    # generates checkboxes with generate_checkboxes function from utils.py
    checkboxes = utils.generate_checkboxes()
    # generates radio buttons with generate_radio_buttons function from utils.py
    radius_buttons = utils.generate_radio_buttons()
    # renders search.html template with checkboxes and radius_buttons to display
    return render_template("search.html", checkboxes=checkboxes, radius_buttons=radius_buttons)

# route for search.html URL Flask app path, utilising the POST method
@app.route("/search", methods=["POST"])
def search_location():
    try:
        # obtain query value from an input box in a form 
        query = request.form["search"]
        # check validity of query with enter_query function, returning the query or an erorr message
        query, error_message = utils.enter_query(query)
        # if the query is None, return a JSON response with the error_message 
        if not query:
            return jsonify({"error": error_message})
        # obtain latitude and longitude from get_coordinates function, or error_message in cases of error
        latitude, longitude, error_message = utils.get_coordinates(query)
        # if latitude and longitude values are None, return JSON response with error message
        if not latitude or not longitude:
            return jsonify({"error": error_message})
        # concatenate categories from a form containing all categories, provided by generate_checkboxes
        categories_str = ",".join(request.form.getlist("categories"))
        # convert radius value from a form and JavaScript into an integer value
        radius = int(request.form.get("radius"))
        # obtain user ID through current session, will be None if the user is not logged in (handled in get_destinations)
        user_id = session.get("user_id")
        # obtain locations with get_destinations taking parameters from get_coordinates, form values and database-related values to save the locations to the user account if logged in
        results = utils.get_destinations(latitude, longitude, categories_str, radius, user_id, db.session)
        # return JSON response with location results 
        return jsonify({"results": results})
    except Exception as e:
        # return JSON response with error message in cases of unknown error
        return jsonify({"error": str(e)})

# route for register.html URL Flask app path, with GET and POST methods 
@app.route("/register.html", methods=["GET", "POST"])
def register():
    # create username_error variable, utilised if there is an issue in registration (username already existing)
    username_error = ""
    # if the request.method is POST, handle the form on register.html
    if request.method == "POST":
        # obtain username and password from the form and Javsscript on register.html
        username = request.form.get("username")
        password = request.form.get("password")
        # query users table to see if the username already exists
        user = db.session.query(User).filter_by(username=username).first()
        # if the username already exists, set the username_error erorr message, to be returned
        if user:
            username_error = "Username already exists - try another"
        else:
            # if the username does not exist, hash the input password to be inserted into the database
            hashed_password = database.hash_password(password)
            # create new User instance with the username and hashed password a new User instance
            new_user = User(username=username, password=hashed_password)
            # add the new_user instance to the database session and commit changes 
            db.session.add(new_user)
            db.session.commit()
            # set user_id and username values in the session from the new_user instance
            user_id = new_user.user_id
            session["user_id"] = user_id
            session["username"] = username
            # redirect the now logged in user the account page 
            return redirect(url_for("account"))
    # if the username already exists, return register.html with the username_error for the user, prompting them to try a different username
    return render_template("register.html", username_error=username_error)

# route for login.html URL Flask app path, with GET and POST methods 
@app.route("/login.html", methods=["GET", "POST"])
def login_handler():
    # if the request.method is POST, handle the form on login.html
    if request.method == "POST":
        try:
            # obtain username and password from the form on login.html
            username = request.form.get("username")
            password = request.form.get("password")
            # query users table to see if any usernames match the input user value
            user = User.query.filter_by(username=username).first()
            # check if username is valid (not None) if the input password matches the password stored in the database
            if user and database.verify_password(password, user.password):
                # set session user_id and username to values stored for that specific user in the database
                session["user_id"] = user.user_id
                session["username"] = user.username
                # redirects verified user to account page
                return redirect(url_for("account"))
            else:
                # render and return login.html with an error message if the username or password does not match any records in the database
                error_message = "Invalid username or password"
                return render_template("login.html", error_message=error_message)
        except Exception as e:
            # render login.html in cases of unknown errors
            return render_template("login.html", error_message=str(e))
    else:
        # render login.html if the request.method is GET
        return render_template("login.html")

# route for account.html URL Flask app path
@app.route("/account.html")
def account():
    # check if a user is logged in by seeing if user_id and username are in session
    if "user_id" in session and "username" in session:
        # obtain user_id and username values from session with get method
        user_id = session["user_id"]
        username = session["username"]
        # render account.html template with the user_id and username
        return render_template("account.html", user_id=user_id, username=username)
    else:
        # redirect users not loggeed in to login.html
        return redirect(url_for("login_handler"))


# route for /logout URL Flask app path
@app.route("/logout")
def logout():
    # clear session dictionary, removing user_id and username variables
    session.clear()
    # redirect user to homepage once they are logged out
    return redirect(url_for("home"))


# route for /delete_account URL Flask app path, with POST method
@app.route("/delete_account", methods=["POST"])
def delete_account():
    # obtain user_id from session with get method
    user_id = session.get("user_id")
    # if the user_id exists in the database, call the delete_account function to delete the account, and then clear the session dictionary
    if database.delete_account(db.session, user_id):
        session.clear()
        # redirect user to homepage once their account is deleted
        return redirect(url_for("home"))
    else:
        # if there is an error in deleting the account, render account.html with an error message
        return render_template("account.html", error_message="Failed to delete account")


# route for search_keyword URL Flask app path, with GET and POST methods
@app.route("/search_keyword", methods=["GET", "POST"])
def search_keyword():
    # if the request.method is POST, handle the form on results.html
    if request.method == "POST":
        try:
            # obtain keyword value from input box in a form on results.html
            keyword = request.form["keyword"]
            # check if the keyword is two characters or more, creating an error message if it is less than two characters
            if len(keyword) < 2:
                error_message = "Keyword must be at least 2 characters."
                # render results.html with the error message, prompting the user to enter a valid search
                return render_template("results.html", show_search_form=True, error_message=error_message)
            # obtain user_id value from session with get method
            user_id = session.get("user_id")
            # obtain search results for the keyword with search_history function from database.py
            search_results = database.search_history(db.session, user_id, keyword)
            # render results.html with the search form visible, search results and the keyword
            return render_template("results.html", show_search_form=True, search_results=search_results, keyword=keyword)
        except Exception as e:
            # render results.html with the search form visible and an error message in cases of unknown error
            return render_template("results.html", show_search_form=True, error_message=str(e))
    else:
        # if the request.method is GET, render results.html with the search form visible, to search for places
        return render_template("results.html", show_search_form=True)

# route for /search_history Flask app path
@app.route("/search_history")
def show_search_history():
    # check if the user is logged in by seeing if a user_id is in session
    if "user_id" in session:
        # obtain user_id value from the session with get method
        user_id = session["user_id"]
        # obtain all location history for the user from get_history function in database.py
        search_history = database.get_history(db.session, user_id)
        # render results.html with search_history to show all search history, and all_searches containing all searches
        return render_template("results.html", search_history=search_history, all_searches=True)
    else:
        # redirect user to login page in the case they are not logged in
        return redirect(url_for("login_handler"))

# route for /popular_searches Flask app path
@app.route("/popular_searches")
def show_popular_searches():
    # check if the user is logged in by seeing if a user_id is in session
    if "user_id" in session:
        # obtain user_id value from the session with get method
        user_id = session["user_id"]
        # obtain the top ten locations for the user from get_top_searches function in database.py
        popular_searches = database.get_top_searches(db.session, user_id)
        # render results.html with the top ten locations 
        return render_template("results.html", popular_searches=popular_searches)
    else:
        # redirect user to login page in the case they are not logged in
        return redirect(url_for("login_handler"))


if __name__ == "__main__":
    with app.app_context():
        # create all database tables
        db.create_all()
    app.run(debug=True)
