from flask import request, Blueprint
from constants import *
from crud.seats import *
from helpers import *
from models.db_models import Seats
from flask_jwt_extended import (jwt_required, get_jwt_identity)

seats_view = Blueprint('seats_routes', __name__)

@seats_view.route("/seats", methods=["POST","GET"])
@jwt_required
def book_and_get_seats():
    """Function to book and get seats

    Args:
        None

    Returns:
        response: Response of the endpoint
    """
    try:
        user = get_jwt_identity()
        user_id = user.get("id",None)

        #check if user is active and is a regular user
        inactive_user = is_user_inactive(user_id)
        if not inactive_user:
            update_last_active_at(user_id)

            if request.method == 'POST':
                role = get_user_role(user_id)
                if role == ADMIN:
                    data = {"message": "Only regular users can book a seat."}
                    return custom_response(data, 200)
                else:
                    bus_id, booked_seat_no, occupied_from, occupied_to = get_seat_data()

                    #check if payload is valid
                    result = is_valid_post_or_update_seats(bus_id, booked_seat_no, occupied_from, occupied_to)
                    if result == True:
                        seat_not_available = check_seat_availability(bus_id, booked_seat_no, occupied_from, occupied_to)
                        if not seat_not_available:
                            price = get_price(bus_id, occupied_from, occupied_to)
                            if not price:
                                return custom_response({"message":"Price for journey not added by the admin."}, 200)

                            #add seat to Seats table
                            return add_seat(user_id, bus_id, booked_seat_no, occupied_from, occupied_to, price)
                        else:
                            return seat_not_available
                    return result

            elif request.method == 'GET':
                seats = get_all_seats()
                return fetch_msg("seats", seats)
        return inactive_user
    except Exception as e:
        return raise_internal_server_error(e)

@seats_view.route("/seats/<id>", methods=["GET", "PUT", "DELETE"])
@jwt_required
def seat_id_based_operations(id):
    """Function to get, update and delete seats based on id 

    Args:
        id (int): Unique id of bus

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

            seat = get_seat_by_id(id)
            if not seat:
                return raise_not_found_error("Seat",id)
            else:
                if request.method == 'GET':
                    return fetch_msg_by_id("seat", seat)

                role = get_user_role(user_id)
                if role != ADMIN:
                    return restrict_actions("seat", id)
                else:
                    if request.method == 'PUT':
                        bus_id, booked_seat_no, occupied_from, occupied_to = get_seat_data()
                        bus_id, booked_seat_no, occupied_from, occupied_to = get_updated_seat_data(seat, bus_id, booked_seat_no, occupied_from, occupied_to)
                        result = is_valid_post_or_update_seats(bus_id, booked_seat_no, occupied_from, occupied_to)
                        if result == True:
                            return update_seat(id, bus_id, booked_seat_no, occupied_from, occupied_to)
                        return result
                        
                    elif request.method == 'DELETE':
                        delete_entity(Seats, id)
                        return delete_msg("Seat", id)
        return inactive_user
    except Exception as e:
        return raise_internal_server_error(e)
