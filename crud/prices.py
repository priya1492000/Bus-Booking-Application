from database import db_session
from flask import request
from helpers import *
import datetime
from models.db_models import Prices

def get_all_price_data():
    """Function to get prices data"""
    start_locations = []
    end_locations = []
    prices = []
    price_data = request.json
    bus_id = price_data.get("bus_id")
    routes = price_data.get("routes")
    if routes:
        start_locations = routes.get("start_locations")
        end_locations = routes.get("end_locations")
        prices = routes.get("prices")
    return bus_id, routes, start_locations, end_locations, prices

def get_price_by_bus_id(bus_id):
    """Function to get price by bus_id"""
    prices = db_session.query(Prices) \
            .filter(Prices.bus_id == bus_id) \
            .all()
    return prices

def is_valid_post_price(bus_id, routes, start_locations, end_locations, prices):
    """Function to validate payload"""

    #check for valid bus_id
    if not bus_id or not isinstance(bus_id, int):
        return custom_response({"message":"Missing bus_id or entered bus_id is not an integer"}, 400)
    if not get_bus_by_id(bus_id):
        return custom_response({"message":"Bus with id : {} is not present".format(bus_id)}, 400)

    #check if prices are already added for bus
    if get_price_by_bus_id(bus_id):
        return custom_response({"message":"Prices are already added for bus_id : {}".format(bus_id)}, 400)

    #check for valid routes
    if not routes or not isinstance(routes, dict):
        return custom_response({"message":"Missing routes details or entered routes is not dictionary"}, 400)
    if not start_locations or not isinstance(start_locations, list):
        return custom_response({"message":"Missing start_locations or entered start_locations is not a list"}, 400)

    for start_location in start_locations:
        if not isinstance(start_location, str):
            return custom_response({"message":"start_locations should be list of string"}, 400)

    if not end_locations or not isinstance(end_locations, list):
        return custom_response({"message":"Missing end_locations or entered end_locations is not a list"}, 400)

    for end_location in end_locations:
        if not isinstance(end_location, str):
            return custom_response({"message":"end_locations should be list of string"}, 400)

    if not prices or not isinstance(prices, list):
        return custom_response({"message":"Missing prices  or entered prices is not a list"}, 400)

    for price in prices:
        if not isinstance(price, float):
            return custom_response({"message":"prices should be list of float"}, 400)

    if not (len(start_locations) == len(end_locations) and len(end_locations) == len(prices)):
        return custom_response({"message":"Please provide route details for all routes"}, 400)
    
    #check for valid start and end location
    for i in range(len(prices)):
        if start_locations[i] == end_locations[i]:
            return custom_response({"message":"Start and end location cannot be same"}, 400)
        if not get_stop_no(start_locations[i], bus_id) or not get_stop_no(end_locations[i], bus_id):
            return custom_response({"message":"Start or end location does not exist in stops for bus_id:{}".format(bus_id)}, 400)
        if get_stop_no(start_locations[i], bus_id) >= get_stop_no(end_locations[i], bus_id):
            return custom_response({"message":"Wrong sequence of start and end locations"}, 400)
    return True

def add_prices(bus_id, start_locations, end_locations, prices):
    """Function to add prices"""
    for i in range(len(prices)):
        price = Prices(bus_id, start_locations[i], end_locations[i], prices[i])
        db_session.add(price)
        db_session.commit()
    return insert_msg("Prices", bus_id)

def get_all_prices():
    """Function to get all prices"""
    prices = db_session.query(Prices.bus_id, Prices.start_location, Prices.end_location, Prices.price) \
            .limit(LIMIT) \
            .all()
    return prices

def get_price_by_id(price_id):
    """Function to get price by id"""
    price = db_session.query(Prices.bus_id, Prices.start_location, Prices.end_location, Prices.price) \
            .filter(Prices.id == price_id) \
            .first()
    return price

def update_price(price_id, bus_id, start_location, end_location, price, updated_at=datetime.datetime.now()):
    """Function to update price"""
    db_session.query(Prices) \
    .filter(Prices.id == price_id) \
    .update({"bus_id":bus_id, "start_location": start_location, "end_location":end_location, "price":price, "updated_at":updated_at}, synchronize_session = 'fetch')
    
    db_session.commit()
    return update_msg("Price", price_id)

def get_updated_price_data(existing_price, bus_id, start_location, end_location, price):
    """Function to get updated price data"""
    bus_id = bus_id if bus_id else existing_price.bus_id
    start_location = start_location if start_location else existing_price.start_location
    end_location = end_location if end_location else existing_price.end_location
    price = price if price else existing_price.price
    return bus_id, start_location, end_location, price 

def is_valid_update_prices(bus_id, start_location, end_location, price):
    """Function to validate payload"""
    if not bus_id or not isinstance(bus_id, int):
        return custom_response({"message":"Missing bus_id or entered bus_id is not an integer"}, 400)
    if not get_bus_by_id(bus_id):
        return custom_response({"message":"Bus with id : {} is not present".format(bus_id)}, 400)
    if not start_location or not isinstance(start_location, str):
        return custom_response({"message":"Missing start_location or entered start_location is not a string"}, 400)
    if not end_location or not isinstance(end_location, str):
        return custom_response({"message":"Missing end_location or entered end_location is not a string"}, 400)
    if not price or not isinstance(price, float):
        return custom_response({"message":"Missing price or entered price is not a float"}, 400)
    return True

def get_price_data():
    """Function to get price data"""
    price_data = request.json
    bus_id = price_data.get("bus_id")
    start_location = price_data.get("start_location")
    end_location = price_data.get("end_location")
    price = price_data.get("price")
    return bus_id, start_location, end_location, price
