from database import db_session
from flask import request
from sqlalchemy import and_, or_
from helpers import *
from models.db_models import Prices, Stops
import datetime

def get_all_stop_data():
    """Function to get stops data"""
    stop_names = [], 
    timings = []
    stop_data = request.json
    bus_id = stop_data.get("bus_id")
    stops = stop_data.get("stops")
    if stops:
        stop_names = stops.get("stop_names")
        timings = stops.get("timings")
    return bus_id, stops, stop_names, timings

def get_stop_by_stop_no(bus_id, stop_no):
    """Function to get stop by stop_no"""
    stop = db_session.query(Stops.bus_id, Stops.stop_no, Stops.stop_name, Stops.timing) \
            .filter(and_(Stops.bus_id == bus_id, Stops.stop_no == stop_no)) \
            .first()
    return stop

def get_stops_by_bus_id(bus_id):
    """Function to get stop by bus_id"""
    stops = db_session.query(Stops) \
            .filter(Stops.bus_id == bus_id) \
            .all()
    return stops

def is_valid_post_stops(bus_id, stops, stop_names, timings):
    """Function to validate payload"""
    if not bus_id or not isinstance(bus_id, int):
        return custom_response({"message":"Missing bus_id or entered bus_id is not an integer"}, 400)

    if not get_bus_by_id(bus_id):
        return custom_response({"message":"Bus with id : {} is not present".format(bus_id)}, 400)

    if get_stops_by_bus_id(bus_id):
        return custom_response({"message":"Stops are already added for bus_id : {}".format(bus_id)}, 400)

    if not stops or not isinstance(stops, dict):
        return custom_response({"message":"Missing stops details or entered stops is not a dictionary"}, 400)

    if not stop_names or not isinstance(stop_names, list):
        return custom_response({"message":"Missing stop_names or entered stop_names is not a list"}, 400)

    for stop_name in stop_names:
        if not isinstance(stop_name, str):
            return custom_response({"message":"Stop_names should be list of string"}, 400)

    if not timings or not isinstance(timings, list):
        return custom_response({"message":"Missing timings  or entered timings is not a list"}, 400)

    for timing in timings:
        if not isinstance(timing, str):
            return custom_response({"message":"Timings should be list of time"}, 400)

    if not (len(stop_names) == len(timings)):
        return custom_response({"message":"Please provide stop details for all stops"}, 400)

    if len(stop_names) != len(set(stop_names)) or len(timings) != len(set(timings)):
        return custom_response({"message":"Duplicate stop_names or timings not allowed for a bus"}, 400)
    return True

def add_stops(bus_id, stop_names, timings):
    """Function to add stops"""
    for i in range(len(stop_names)):
        stop = Stops(bus_id, i+1, stop_names[i], timings[i])
        db_session.add(stop)
        db_session.commit()
    return insert_msg("Stops", bus_id)

def get_all_stops():
    """Function to get all stops"""
    stops = db_session.query(Stops.bus_id, Stops.stop_no, Stops.stop_name, Stops.timing) \
            .limit(LIMIT) \
            .all()
    return stops

def update_stop(bus_id, stop_no, stop_name, timing, updated_at=datetime.datetime.now()):
    """Function to update stops"""
    db_session.query(Stops) \
    .filter(and_(Stops.bus_id == bus_id, Stops.stop_no == stop_no)) \
    .update({"stop_name":stop_name, "timing":timing, "updated_at":updated_at}, synchronize_session = 'fetch')
    
    db_session.commit()
    return custom_response({"message":"Stop_no :{} with bus_id: {} updated successfully".format(stop_no, bus_id)}, 200)

def get_updated_stop_data(stop, stop_name, timing):
    """Function to get updated stop data"""
    stop_name = stop_name if stop_name else stop.stop_name
    timing = timing if timing else stop.timing
    return stop_name, timing

def get_stop_data():
    """Function to get stop data"""
    stop_data = request.json
    stop_name = stop_data.get("stop_name")
    timing = stop_data.get("timing")
    return stop_name, timing

def is_valid_update_stops(stop_name, timing):
    """Function to validate payload"""
    if not stop_name or not isinstance(stop_name, str):
        return custom_response({"message":"Missing stop_name or entered stop_name is not a string"}, 400)
    if not timing or not(isinstance(timing, datetime.time) or isinstance(timing, str)):
        return custom_response({"message":"Missing timing or entered timing is not a time"}, 400)
    return True

def delete_stop(bus_id, stop_no, stop):
    """Function to delete stop"""
    db_session.query(Stops) \
    .filter(and_(Stops.bus_id == bus_id, Stops.stop_no == stop_no)) \
    .delete(synchronize_session ='fetch')

    db_session.query(Prices) \
    .filter(Prices.bus_id == bus_id) \
    .filter(or_(Prices.start_location == stop.stop_name, Prices.end_location == stop.stop_name)) \
    .delete(synchronize_session ='fetch')

    stops = db_session.query(Stops) \
                .filter(and_(Stops.bus_id == bus_id, Stops.stop_no > stop_no)) \
                .all()
    for stop in stops:
        stop.stop_no = stop.stop_no - 1
        db_session.add(stop)

    db_session.commit()
