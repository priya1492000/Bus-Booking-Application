from flask import request, Blueprint
from constants import *
from crud.prices import *
from helpers import *
from models.db_models import Prices
from flask_jwt_extended import (jwt_required, get_jwt_identity)

prices_view = Blueprint('prices_routes', __name__)

@prices_view.route("/prices", methods=["POST","GET"])
@jwt_required
def add_and_get_prices():
    """Function to add and get prices

    Args:
        None

    Returns:
        response: Response of the endpoint
    """
    try:
        user = get_jwt_identity()
        user_id = user.get("id",None)
        
        #check if user is active and is a admin
        inactive_user = is_user_inactive(user_id)
        if not inactive_user:
            update_last_active_at(user_id)

            if request.method == 'POST':
                role = get_user_role(user_id)
                if role != ADMIN:
                    return restrict_actions("stop", user_id)
                else:
                    bus_id, routes, start_locations, end_locations, prices = get_all_price_data()

                    #check if payload is valid
                    result = is_valid_post_price(bus_id, routes, start_locations, end_locations, prices)
                    if result == True:
                        #add prices to Prices table
                        return add_prices(bus_id, start_locations, end_locations, prices)
                    return result
                    
            elif request.method == 'GET':
                prices = get_all_prices()
                return fetch_msg("prices", prices)
        return inactive_user
    except Exception as e:
        return raise_internal_server_error(e)

@prices_view.route("/prices/<id>", methods=["GET", "PUT", "DELETE"])
@jwt_required
def price_id_based_operations(id):
    """Function to get, update and delete prices based on id 

    Args:
        id (int): Unique id of price

    Returns:
        response: Response of the endpoint
    """
    try:
        user = get_jwt_identity()
        user_id = user.get("id", None)

        #check if the user is active
        inactive_user = is_user_inactive(user_id)
        if not inactive_user:
            update_last_active_at(user_id)

            existing_price = get_price_by_id(id)
            if not existing_price:
                return raise_not_found_error("Price",id)
            else:
                if request.method == 'GET':
                    return fetch_msg_by_id("price", existing_price)

                role = get_user_role(user_id)
                if role != ADMIN:
                    return restrict_actions("user",id)
                else:
                    if request.method =='PUT':
                        bus_id, start_location, end_location, price = get_price_data()
                        bus_id, start_location, end_location, price = get_updated_price_data(existing_price, bus_id, start_location, end_location, price)
                        
                        #check if payload is valid
                        result = is_valid_update_prices(bus_id, start_location, end_location, price)
                        if result == True:
                            #update the price
                            return update_price(id, bus_id, start_location, end_location, price)
                        else:
                            return result
                        
                    elif request.method == 'DELETE':
                        delete_entity(Prices, id)
                        return delete_msg("Price", id)
        return inactive_user
    except Exception as e:
        return raise_internal_server_error(e)
