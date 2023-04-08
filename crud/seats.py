from database import db_session
from flask import request
from helpers import *
import datetime
from models.db_models import Seats, Prices
from sqlalchemy import and_

def get_seat_data():
    """Function to get seat data"""
    seats_data = request.json
    bus_id = seats_data.get("bus_id")
    booked_seat_no = seats_data.get("booked_seat_no")
    occupied_from = seats_data.get("occupied_from")
    occupied_to = seats_data.get("occupied_to")
    return bus_id, booked_seat_no, occupied_from, occupied_to

def get_total_seats_by_bus_id(id):
    """Function to get total seats"""
    total_seats = db_session.query(Buses.seat_count) \
                    .filter(Buses.id == id) \
                    .first()
    if total_seats:
        return total_seats[0]

def get_price(bus_id, occupied_from, occupied_to):
    """Function to get price"""
    price = db_session.query(Prices.price) \
            .filter(Prices.bus_id == bus_id) \
            .filter(and_(Prices.start_location == occupied_from, Prices.end_location == occupied_to)) \
            .first()
    if price:
        return price[0]

def is_valid_post_or_update_seats(bus_id, booked_seat_no, occupied_from, occupied_to):
    """Function to validate payload"""
    if not bus_id or not isinstance(bus_id, int):
        return custom_response({"message":"Missing bus_id or entered bus_id is not an integer"}, 400)
    if not get_bus_by_id(bus_id):
        return custom_response({"message":"Bus with id : {} is not present".format(bus_id)}, 400)
    if (not booked_seat_no and booked_seat_no != 0) or not isinstance(booked_seat_no, int):
        return custom_response({"message":"Missing booked_seat_no or entered booked_seat_no is not an integer"}, 400)

    total_seats = get_total_seats_by_bus_id(bus_id)
    if booked_seat_no <= 0 or booked_seat_no > total_seats:
        return custom_response({"message":"Your preferred seat no does not exist"}, 400)
    if not occupied_from or not isinstance(occupied_from, str):
        return custom_response({"message":"Missing occupied_from or entered occupied_from is not a string"}, 400)
    if not occupied_to or not isinstance(occupied_to, str):
        return custom_response({"message":"Missing occupied_to or entered occupied_to is not a string"}, 400)
    if occupied_from ==  occupied_to:
        return custom_response({"message":"Occupied_from and occupied_to cannot be same"}, 400)

    occupied_from_stop_no = get_stop_no(occupied_from, bus_id)
    occupied_to_stop_no = get_stop_no(occupied_to, bus_id)
    
    if not occupied_from_stop_no or not occupied_to_stop_no:
        return custom_response({"message":"Wrong pick up or drop location."}, 400)

    if occupied_from_stop_no > occupied_to_stop_no:
        return custom_response({"message":"Wrong sequence of pick up and drop location."}, 400)
    return True

def add_seat(user_id, bus_id, booked_seat_no, occupied_from, occupied_to, price):
    """Function to add seat"""
    seat = Seats(user_id, bus_id, booked_seat_no, occupied_from, occupied_to)
    db_session.add(seat)
    db_session.commit()
    data = {"message": "Seat no : {} booked for price : {}.".format(booked_seat_no, price)}
    return custom_response(data, 200)

def get_all_seats():
    """Function to get all seats"""
    seats = db_session.query(Seats.bus_id, Seats.user_id, Seats.booked_seat_no, Seats.occupied_from, Seats.occupied_to) \
            .limit(LIMIT) \
            .all()
    return seats

def check_seat_availability(bus_id, booked_seat_no, occupied_from, occupied_to):
    """Function to check seat availability"""
    occupied_from_stop_no = get_stop_no(occupied_from, bus_id)
    occupied_to_stop_no = get_stop_no(occupied_to, bus_id)

    seats = db_session.query(Seats) \
            .filter(and_(Seats.bus_id == bus_id, Seats.booked_seat_no == booked_seat_no)) \
            .all()

    for seat in seats:
        already_occupied_from_stop_no = get_stop_no(seat.occupied_from, bus_id)
        already_occupied_to_stop_no = get_stop_no(seat.occupied_to, bus_id)

        if already_occupied_from_stop_no <= occupied_from_stop_no and already_occupied_to_stop_no >= occupied_from_stop_no \
            and already_occupied_to_stop_no >= occupied_to_stop_no:
            return custom_response({"message":"Your preferred seat is not available for your pick up location."}, 200)
        if already_occupied_from_stop_no == occupied_from_stop_no or \
            (already_occupied_from_stop_no < occupied_to_stop_no and already_occupied_to_stop_no == occupied_to_stop_no):
            return custom_response({"message":"Your preferred seat is not available for your pick up location."}, 200)

        last_stop_no = get_last_stop_no(bus_id)
        if occupied_from_stop_no == FIRST_STOP and occupied_to_stop_no == last_stop_no:
            return custom_response({"message":"Your preferred seat is not available for your pick up location."}, 200)
        
        last_already_occupied_stop_no = FIRST_STOP
        last_already_occupied_stop_no = max(last_already_occupied_stop_no, already_occupied_to_stop_no)
    
    if occupied_to_stop_no > last_already_occupied_stop_no and occupied_from_stop_no < last_already_occupied_stop_no:
        return custom_response({"message":"Your preferred seat is not available for your pick up location."}, 200)


def update_seat(seat_id, bus_id, booked_seat_no, occupied_from, occupied_to, updated_at=datetime.datetime.now()):
    """Function to update seat"""
    db_session.query(Seats) \
    .filter(Seats.id == seat_id) \
    .update({"bus_id":bus_id, "booked_seat_no": booked_seat_no, "occupied_from": occupied_from, "occupied_to": occupied_to, "updated_at":updated_at}, synchronize_session = 'fetch')
    
    db_session.commit()
    return update_msg("Seat", seat_id)

def get_updated_seat_data(seat, bus_id, booked_seat_no, occupied_from, occupied_to):
    """Function to get updated seat data"""
    bus_id = bus_id if bus_id else seat.bus_id
    booked_seat_no = booked_seat_no if booked_seat_no else seat.booked_seat_no
    occupied_from = occupied_from if occupied_from else seat.occupied_from
    occupied_to = occupied_to if occupied_to else seat.occupied_to
    return bus_id, booked_seat_no, occupied_from, occupied_to

def get_seat_by_id(id):
    """Function to get seat by id"""
    seat = db_session.query(Seats.bus_id, Seats.user_id, Seats.booked_seat_no, Seats.occupied_from, Seats.occupied_to) \
            .filter(Seats.id == id) \
            .first()
    return seat
