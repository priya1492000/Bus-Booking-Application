from flask import make_response
from database import db_session
from constants import *
from itsdangerous import json
from sqlalchemy import and_
from datetime import datetime, timedelta
from models.db_models import Users, Buses, Stops
import hashlib

def make_md5(data):
    """Function to hash password"""
    md5_value = hashlib.md5(data.encode('utf-8')).hexdigest()
    return md5_value

def get_user_role(user_id):
    """Function to role of user"""
    role = db_session.query(Users.role) \
            .filter(Users.id == user_id) \
            .first()
    if role:
        return role[0]

def get_last_stop_no(bus_id):
    """Function to get last stop no"""
    last_stop_no = db_session.query(Stops) \
                    .filter(Stops.bus_id == bus_id) \
                    .count()
    return last_stop_no

def is_user_inactive(user_id):
    """Function to check inactive user"""
    inactive_time_period = datetime.now() - timedelta(minutes=INACTIVE_TIME_MINUTES)
    inactive_user = db_session.query(Users) \
                    .filter(Users.id == user_id) \
                    .filter(Users.last_active_at <= inactive_time_period) \
                    .first()
    
    if inactive_user:
        return custom_response({"message":"Your session has expired"}, 440)

def update_last_active_at(user_id):
    """Function to update last active time of user"""
    last_active_at = datetime.now()
    db_session.query(Users) \
    .filter(Users.id == user_id) \
    .update({'last_active_at':last_active_at}, synchronize_session = 'fetch')
    
    db_session.commit()

def get_stop_no(stop_name, bus_id):
    """Function to get stop_no"""
    stop_no = db_session.query(Stops.stop_no) \
                .filter(and_(Stops.stop_name == stop_name, Stops.bus_id == bus_id)) \
                .first()
    if stop_no:
        return stop_no[0]

def get_bus_by_id(id):
    """Function to get bus by id"""
    bus = db_session.query(Buses.name, Buses.seat_count, Buses.source, Buses.destination, Buses.timing) \
            .filter(Buses.id == id) \
            .first()
    return bus

def delete_entity(entity, id):
    """Function to delete a entity based on id"""
    db_session.query(entity) \
    .filter(entity.id == id) \
    .delete(synchronize_session ='fetch')
    db_session.commit()

def custom_response(data, status_code):
    """Function to return custom response"""
    return make_response(json.dumps(data, default=str),status_code)

def raise_not_found_error(record, id):
    """Function to raise_not_found_error"""
    data = {"message": "{} with id: {} not found.".format(record,id)}
    return custom_response(data, 404)

def raise_internal_server_error(e):
    """Function to raise_internal_server_error"""
    data = {INTERNAL_SERVER_ERROR:e }
    return custom_response(data, 500)

def restrict_actions(record, id):
    """Function to restrict_actions"""
    data = {"message": "You cannot perform actions on {} with id : {}.".format(record,id)}
    return custom_response(data, 403)

def insert_msg(record, id):
    """Function to return insert_msg"""
    data = {"message": "{} for user_id:{} has been added successfully.".format(record,id)}
    return custom_response(data, 201)

def fetch_msg(record, data):
    """Function to return fetch_msg"""
    data = {"{}".format(record):[dict(r) for r in data]}
    return custom_response(data, 200)

def fetch_msg_by_id(record, data):
    """Function to return fetch_msg_by_id"""
    data = {"{}".format(record):[dict(data)]}
    return custom_response(data, 200)

def update_msg(record, id):
    """Function to return update_msg"""
    data = {"message": "{} with id: {} Updated successfully.".format(record,id)}
    return custom_response(data, 200)

def delete_msg(record, id):
    """Function to return delete_msg"""
    data = {"message": "{} with id: {} Deleted successfully.".format(record,id)}
    return custom_response(data, 200)
