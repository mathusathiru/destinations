from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import func, or_, desc
from flask_sqlalchemy import SQLAlchemy
import bcrypt

db = SQLAlchemy()

Base = declarative_base()


class User(db.Model):
    __tablename__ = 'users'
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, nullable=False)
    password = db.Column(db.String, nullable=False)

class SearchHistory(db.Model):
    __tablename__ = 'search_history'
    search_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id', ondelete="CASCADE"), nullable=False)
    place_name = db.Column(db.String, nullable=False)
    address = db.Column(db.String, nullable=False)
    timestamp = db.Column(db.DateTime, default=db.func.now())

def hash_password(password):
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed_password.decode("utf-8")

def save_search_history(db_session, user_id, results):
    user = db_session.query(User).get(user_id)
    if user:
        for result in results:
            place_name = result["name"]
            address = result["location"]["formatted_address"]
            search_history = SearchHistory(user_id=user_id, place_name=place_name, address=address)
            db_session.add(search_history)
        db_session.commit()

def get_search_history(db_session, user_id):
    return db_session.query(SearchHistory.place_name, SearchHistory.address, SearchHistory.timestamp).\
        filter(SearchHistory.user_id == user_id).all()

def get_most_popular_searches(db_session, user_id):
    return db_session.query(SearchHistory.place_name, SearchHistory.address, func.count(SearchHistory.place_name).label("search_count")).\
        filter(SearchHistory.user_id == user_id).\
        group_by(SearchHistory.place_name, SearchHistory.address).\
        order_by(desc("search_count")).\
        limit(10).all()

def search_history(db_session, user_id, keyword):
    return db_session.query(SearchHistory.place_name, SearchHistory.address, SearchHistory.timestamp).\
        filter(SearchHistory.user_id == user_id).\
        filter(or_(SearchHistory.place_name.ilike(f"%{keyword}%"), SearchHistory.address.ilike(f"%{keyword}%"))).\
        all()
