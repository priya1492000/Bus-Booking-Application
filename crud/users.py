from database import db_session
from flask import request
from sqlalchemy import and_
from helpers import *
from models.db_models import Users

def get_user_data():
    """Function to get user data"""
    user_data = request.json
    name = user_data.get("name")
    email = user_data.get("email")
    password = user_data.get("password")
    role = user_data.get("role")
    return name, email, password, role

def is_valid_email(email):
    """Function to check valid email"""
    existing_email = db_session.query(Users.email) \
                    .filter(Users.email == email) \
                    .first()
    if existing_email:
        return existing_email[0]

def is_valid_post_users(name, email, password, role):
    """Function to validate payload"""
    if not email or not isinstance(email, str):
        return custom_response({"message":"Missing email or entered email is not a string"}, 400)
    if not password or not isinstance(password, str):
        return custom_response({"message":"Missing password or entered password is not a string"}, 400)
    if not name or not isinstance(name, str):
        return custom_response({"message":"Missing name or entered name is not a string"}, 400)
    if not role or not isinstance(role, str):
        return custom_response({"message":"Missing role or entered role is not a string"}, 400)
    if is_valid_email(email):
        return custom_response({"message":"Email already registered!!"}, 400)
    return True

def add_user(name, email, password, role):
    """Function to add user"""
    user = Users(name, email, make_md5(password), role)
    db_session.add(user)
    db_session.commit()

    data = {"message": "User {} has been registered successfully.".format(name)}
    return custom_response(data, 200)
    
def is_valid_login(email, password):
    """Function to validate payload"""
    if not email or not isinstance(email, str):
        return custom_response({"message":"Missing email or entered email is not a string"}, 400)
    if not password or not isinstance(password, str):
        return custom_response({"message":"Missing password or entered password is not a string"}, 400)
    return True

def authenticate_user(email, password):
    """Function to authenticate user"""
    user = db_session.query(Users.id, Users.email) \
            .filter(and_(Users.email == email, Users.password == make_md5(password))) \
            .first()
    return user

def get_all_users():
    """Function to get all users"""
    users = db_session.query(Users.id, Users.name, Users.email, Users.role) \
            .order_by(Users.id) \
            .limit(LIMIT) \
            .all()
    return fetch_msg("users", users)
