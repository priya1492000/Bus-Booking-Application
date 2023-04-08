from flask import request, Blueprint
from constants import *
from crud.stops import *
from helpers import *
from flask_jwt_extended import (jwt_required, get_jwt_identity)

stops_view = Blueprint('stops_routes', __name__)

@stops_view.route("/stops", methods=["POST","GET"])
@jwt_required
def add_and_get_stops():
    """Function to add and get stops

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
                    bus_id, stops, stop_names, timings = get_all_stop_data()

                    #check if payload is valid
                    result = is_valid_post_stops(bus_id, stops, stop_names, timings)
                    if result == True:
                        #add stops to Stops table
                        return add_stops(bus_id, stop_names, timings)
                    return result

            elif request.method == 'GET':
                #return all stops
                stops = get_all_stops()
                return fetch_msg("stops", stops)
        return inactive_user      
    except Exception as e:
        return raise_internal_server_error(e)

@stops_view.route("/buses/<bus_id>/stops/<stop_no>", methods=["GET", "PUT", "DELETE"])
@jwt_required
def stop_no_based_operations(bus_id, stop_no):
    """Function to get, update and delete bus based on stop_no

    Args:
        bus_id (int): Unique id of bus
        stop_no (int): Stop_no of a bus

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

            stop = get_stop_by_stop_no(bus_id, stop_no)

            if not stop:
                return custom_response({"message":"Stop with stop_no:{} and bus_id: {} not found".format(stop_no, bus_id)}, 404)
            else:
                if request.method == 'GET':
                    return fetch_msg_by_id("stop", stop)

                role = get_user_role(user_id)
                if role != ADMIN:
                    return restrict_actions("user",id)
                else:
                    if request.method =='PUT':
                        stop_name, timing = get_stop_data()
                        stop_name, timing = get_updated_stop_data(stop, stop_name, timing)

                        #check if payload is valid
                        result = is_valid_update_stops(stop_name, timing)
                        if result == True:
                            return update_stop(bus_id, stop_no, stop_name, timing)
                        return result
                        
                    elif request.method == 'DELETE':
                        delete_stop(bus_id, stop_no, stop)
                        return custom_response({"message":"Stop with stop_no:{} and bus_id: {} deleted successfully".format(stop_no, bus_id)}, 200)
        return inactive_user
    except Exception as e:
        return raise_internal_server_error(e)
