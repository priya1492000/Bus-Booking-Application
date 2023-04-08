from flask import request, Blueprint
from constants import *
from crud.buses import *
from helpers import *
from models.db_models import Buses
from flask_jwt_extended import (jwt_required, get_jwt_identity)

buses_view = Blueprint('buses_routes', __name__)

@buses_view.route("/buses", methods=["POST","GET"])
@jwt_required
def add_and_get_buses():
    """Function to add and get buses

    Args:
        None

    Returns:
        response: Response of the endpoint
    """
    try:
        user = get_jwt_identity()
        user_id = user.get("id", None)

        #check if user is active and is a admin
        inactive_user = is_user_inactive(user_id)
        if not inactive_user:
            update_last_active_at(user_id)

            if request.method == 'POST':
                role = get_user_role(user_id)
                if role != ADMIN:
                    return restrict_actions("Bus", user_id)
                else:
                    name, seat_count, source, destination, timing = get_buses_data()

                    #check if payload is valid
                    result = is_valid_post_or_update_buses(name, seat_count, source, destination, timing)
                    if result == True:
                        #add bus to Buses table
                        return add_bus(user_id, name, seat_count, source, destination, timing)
                    return result

            elif request.method == 'GET':
                #return all buses
                buses = get_all_buses()
                return fetch_msg("Buses", buses)
        return inactive_user
    except Exception as e:
        return raise_internal_server_error(e)

@buses_view.route("/buses/<id>", methods=["GET", "PUT", "DELETE"])
@jwt_required
def bus_id_based_operations(id):
    """Function to get, update and delete bus based on id 

    Args:
        id (int): Unique id of bus

    Returns:
        response: Response of the endpoint
    """
    try:
        user = get_jwt_identity()
        user_id = user.get("id", None)
        
        #check if user is active
        inactive_user = is_user_inactive(user_id)
        if not inactive_user:
            update_last_active_at(user_id)
        
            bus = get_bus_by_id(id)
            if not bus:
                return raise_not_found_error("Bus", id)
            else:
                if request.method == 'GET':
                    return fetch_msg_by_id("bus", bus)

                role = get_user_role(user_id)
                if role != ADMIN:
                    return restrict_actions("bus", id)
                else:
                    if request.method == 'PUT':
                        name, seat_count, source, destination, timing = get_buses_data()
                        name, seat_count, source, destination, timing = get_updated_bus_data(bus, name, seat_count, source, destination, timing)
                        
                        #check if payload is valid
                        result = is_valid_post_or_update_buses(name, seat_count, source, destination, timing, id, PUT)
                        if result == True:
                            #update the bus
                            return update_bus(id, name, seat_count, source, destination, timing)
                        return result
                        
                    elif request.method == 'DELETE':
                        delete_entity(Buses, id)
                        return delete_msg("Bus", id)
        return inactive_user
    except Exception as e:
        return raise_internal_server_error(e)

@buses_view.route("/buses/<bus_id>/prices", methods=["GET"])
@jwt_required
def get_prices(bus_id):
    """Function to get prices of bus based on bus_id 

    Args:
        bus_id (int): Unique id of bus

    Returns:
        response: Response of the endpoint
    """
    try:
        user = get_jwt_identity()
        user_id = user.get("id",None)

        #check if user is active
        inactive_user = is_user_inactive(user_id)
        if not inactive_user:
            update_last_active_at(user_id)
            return get_prices_by_bus_id(bus_id)
        return inactive_user
    except Exception as e:
        return raise_internal_server_error(e)

@buses_view.route("/buses/<bus_id>/stops", methods=["GET"])
@jwt_required
def get_stops(bus_id):
    """Function to get stops of bus based on bus_id 

    Args:
        bus_id (int): Unique id of bus

    Returns:
        response: Response of the endpoint
    """
    try:
        user = get_jwt_identity()
        user_id = user.get("id",None)

        #check if user is active
        inactive_user = is_user_inactive(user_id)
        if not inactive_user:
            update_last_active_at(user_id)
            return get_stops_by_bus_id(bus_id)
        return inactive_user
    except Exception as e:
        return raise_internal_server_error(e)

@buses_view.route("/buses/<source>/<destination>", methods=["GET"])
@jwt_required
def get_buses(source, destination):
    """Function to get bus based on source and destination

    Args:
        source (str): source
        destination(str): destination

    Returns:
        response: Response of the endpoint
    """
    try:
        user = get_jwt_identity()
        user_id = user.get("id",None)

        #check if user is active
        inactive_user = is_user_inactive(user_id)
        if not inactive_user:
            update_last_active_at(user_id)
            return  get_bus_by_source_and_destination(source, destination)
        return inactive_user
    except Exception as e:
        return raise_internal_server_error(e)
