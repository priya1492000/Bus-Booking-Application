from database import db_session
from flask import request
from sqlalchemy import and_
from constants import *
from helpers import *
from models.db_models import Buses, Stops, Prices
import datetime

def get_bus_by_name(name):
    """Function to get bus by name"""
    bus = db_session.query(Buses) \
            .filter(Buses.name == name) \
            .first()
    return bus

def get_bus_by_bus_id_and_name(name, bus_id):
    """Function to get bus by name and bus_id"""
    bus = db_session.query(Buses) \
            .filter(and_(Buses.name == name, Buses.id != bus_id))\
            .first()
    return bus

def is_valid_post_or_update_buses(name, seat_count, source, destination, timing, bus_id=None, method=POST):
    """Function to validate payload"""
    if not name or not isinstance(name, str):
        return custom_response({"message":"Missing name or entered name is not a string"}, 400)

    #check for already existing bus_name
    if method == POST and get_bus_by_name(name):
            return custom_response({"message":"Bus name :{} already exists".format(name)}, 400)
    elif get_bus_by_bus_id_and_name(name, bus_id):
            return custom_response({"message":"Bus name :{} already exists".format(name)}, 400)

    if not seat_count or not isinstance(seat_count, int):
        return custom_response({"message":"Missing seat_count or entered seat_count is not a integer"}, 400)
    if not source or not isinstance(source, str):
        return custom_response({"message":"Missing source or entered source is not a string"}, 400)
    if not destination or not isinstance(destination, str):
        return custom_response({"message":"Missing destination or entered destination is not a string"}, 400)
    if source == destination:
        return custom_response({"message":"Source and destination cannot be same"}, 400)
    if not timing or not(isinstance(timing, datetime.time) or isinstance(timing, str)):
        return custom_response({"message":"Missing timing or entered timing is not a time"}, 400)
    return True

def add_bus(user_id, name, seat_count, source, destination, timing):
    """Function to add bus"""
    bus = Buses(user_id, name, seat_count, source, destination, timing)
    db_session.add(bus)
    db_session.commit()
    return insert_msg("Bus", user_id)

def get_buses_data():
    """Function to get buses data"""
    buses_data = request.json
    name = buses_data.get("name")
    seat_count = buses_data.get("seat_count")
    source = buses_data.get("source")
    destination = buses_data.get("destination")
    timing = buses_data.get("timing")
    return name, seat_count, source, destination, timing

def get_updated_bus_data(bus,name, seat_count, source, destination, timing):
    """Function to get updated bus data"""
    name = name if name else bus.name
    seat_count = seat_count if seat_count else bus.seat_count
    source = source if source else bus.source
    destination = destination if destination else bus.destination
    timing = timing if timing else bus.timing
    return name, seat_count, source, destination, timing

def get_all_buses():
    """Function to get all buses"""
    buses = db_session.query(Buses.name, Buses.seat_count, Buses.source, Buses.destination, Buses.timing) \
            .limit(LIMIT) \
            .all()
    return buses

def update_bus(bus_id, name, seat_count, source, destination, timing, updated_at=datetime.datetime.now()):
    """Function to get update bus"""
    db_session.query(Buses) \
    .filter(Buses.id == bus_id) \
    .update({"name":name, "seat_count": seat_count, "source": source, "destination":destination, "timing":timing, "updated_at":updated_at},
    synchronize_session = 'fetch')
    
    db_session.commit()
    return update_msg("Bus", bus_id)

def get_prices_by_bus_id(bus_id):
    """Function to get prices by bus_id"""
    prices = db_session.query(Prices.bus_id, Prices.start_location, Prices.end_location, Prices.price) \
            .filter(Prices.bus_id == bus_id) \
            .limit(LIMIT) \
            .all()
    if not prices:
        return custom_response({"message":"Prices with bus_id:{} not found.".format(bus_id)}, 404)
    return fetch_msg("prices", prices)

def get_stops_by_bus_id(bus_id):
    """Function to get stops by bus_id"""
    stops = db_session.query(Stops.bus_id, Stops.stop_no, Stops.stop_name, Stops.timing) \
            .filter(Stops.bus_id == bus_id) \
            .limit(LIMIT) \
            .all()
    if not stops:
        return custom_response({"message":"Stops with bus_id:{} not found.".format(bus_id)}, 404)
    return fetch_msg("Stops", stops)

def get_bus_by_source_and_destination(source, destination):
    """Function to get bus by source and destination"""
    buses = db_session.query(Buses.name, Buses.seat_count, Prices.start_location, Prices.end_location, Buses.timing, Prices.price) \
            .filter(Buses.id == Prices.bus_id) \
            .filter(and_(Prices.start_location == source, Prices.end_location == destination)) \
            .limit(LIMIT) \
            .all()
    if not buses:
        return custom_response({"message":"Bus with entered source:{} and destination:{} not found.".format(source, destination)}, 404)
    return fetch_msg("Buses", buses)
