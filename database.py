# imports for SQLAlchemy database integration and operation
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import func, or_, desc
from flask_sqlalchemy import SQLAlchemy

# importing bcrypt for password hashing
import bcrypt

# initialise SQLAlchemy database instance
db = SQLAlchemy()

# base class for declarative models
Base = declarative_base()

# creating the users table, with an integer ID as the primary key and non-null username and password columns
class User(db.Model):
    __tablename__ = "users"
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, nullable=False)
    password = db.Column(db.String, nullable=False)

# creating the search_history table, with an search ID as the primary key and all other columns not null 
# user_id is a foreign key from the users table, and the timestamp column contains the date and time at the time of SQL query execution
class SearchHistory(db.Model):
    __tablename__ = "search_history"
    search_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id', ondelete="CASCADE"), nullable=False)
    place_name = db.Column(db.String, nullable=False)
    address = db.Column(db.String, nullable=False)
    timestamp = db.Column(db.DateTime, default=db.func.now())

# function to hash a password with bycrypt import, utilising a salt and returning the password as a UTF-8 encoded string
def hash_password(password):
    salt = bcrypt.gensalt()  # Generate a salt for password hashing
    hashed_password = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed_password.decode("utf-8")

# function to save generated locations to the database for a user
def save_history(db_session, user_id, results):
    # obtain the user_id from the users table
    user = db_session.get(User, user_id)
    if user:
        for result in results:
            # obtain the place name and address for each result
            place_name = result["name"]
            address = result["location"]["formatted_address"]

            # add a SearchHistory object with the user ID and place details, commiting to the database
            search_history = SearchHistory(user_id=user_id, place_name=place_name, address=address)
            db_session.add(search_history)
        db_session.commit()

# function to retrieve all locations for a specific user
def get_history(db_session, user_id):
    # execute query to the search_history table for place name, address, and timestamp of all entries for a specific  user_id
    return db_session.query(SearchHistory.place_name, SearchHistory.address, SearchHistory.timestamp).\
        filter(SearchHistory.user_id == user_id).all()

# function to get the top 10 top search queries for a specific user, obtaining the place name and address
def get_top_searches(db_session, user_id):
    # obtain the top 10 results through ordering the search count in descending order for all unique entries for a specific user
    return db_session.query(SearchHistory.place_name, SearchHistory.address, func.count(SearchHistory.place_name).label("search_count")).\
        filter(SearchHistory.user_id == user_id).\
        group_by(SearchHistory.place_name, SearchHistory.address).\
        order_by(desc("search_count")).\
        limit(10).all()

# function to search for results across the user history based on a keyword
def search_history(db_session, user_id, keyword):
    # obtain place name, addresse and timestamp of entries for the specified user_id where the place name or the address contains the specified keyword, case-insensitive
    return db_session.query(SearchHistory.place_name, SearchHistory.address, SearchHistory.timestamp).\
        filter(SearchHistory.user_id == user_id).\
        filter(or_(SearchHistory.place_name.ilike(f"%{keyword}%"), SearchHistory.address.ilike(f"%{keyword}%"))).\
        all()

# function to delete a user account and its associated search history
def delete_account(db_session, user_id):
    # obtain the user through user_id
    user = db_session.get(User, user_id)

    if user:
        # delete the user's search history in search_history table
        SearchHistory.query.filter_by(user_id=user_id).delete()

        # delete the user from users table and commit to the database
        db_session.delete(user)
        db_session.commit()
        
        return True 
    else:
        # return False for any unexpected issues
        return False

# function to verify password input on a login page against the password stored in the database
def verify_password(input_password, hashed_password):
    return bcrypt.checkpw(input_password.encode("utf-8"), hashed_password.encode("utf-8"))