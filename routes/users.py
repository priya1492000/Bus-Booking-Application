from flask import request, Blueprint
from constants import *
from crud.users import *
from helpers import *
import datetime
from flask_jwt_extended import (jwt_required, create_access_token, get_jwt_identity)

users_view = Blueprint('users_routes', __name__)

@users_view.route('/login', methods=['POST'])
def login():
    """Function to login using email and password

    Args:
        None

    Returns:
        response: response of endpoint
    """ 
    try:
        user_data = request.json
        email = user_data.get('email', None)
        password = user_data.get('password', None)

        #check payload contains email and password
        result = is_valid_login(email, password)
        if result == True:
            #verify email and password
            user = authenticate_user(email, password)
            if not user:
                return custom_response({"message": "Incorrect credentials"}, 401)
            expires_delta = datetime.timedelta(minutes=TOKEN_EXPIRE_MINUTES)

            #generate access_token and add last_active_at for user
            access_token = create_access_token(identity={"id":user.id, "email": email}, expires_delta=expires_delta)
            update_last_active_at(user.id)
            return custom_response({"access_token": access_token}, 200)
        return result
    except Exception as e:
        return raise_internal_server_error(e)

@users_view.route("/register", methods=["POST"])
def register_user():
    """Function to register new user

    Args:
        None

    Returns:
        response: response of endpoint
    """
    try:
        name, email, password, role = get_user_data()

        #check if payload is valid and then add to Users table
        result = is_valid_post_users(name, email, password, role)
        if result == True:
            return add_user(name, email, password, role)
        return result    
    except Exception as e:
        return raise_internal_server_error(e)

@users_view.route("/users", methods=["GET"])
@jwt_required
def get_users():
    """Function to get all the users with limit specified

    Args:
        None

    Returns:
        response: All users
    """
    try:
        user = get_jwt_identity()
        user_id = user.get("id",None)

        #if user is active return all users
        inactive_user = is_user_inactive(user_id)
        if not inactive_user:
            update_last_active_at(user_id)
            return get_all_users()
        return inactive_user
    except Exception as e:
        return raise_internal_server_error(e)
