from sqlalchemy.ext.declarative import declarative_base
import datetime
from sqlalchemy import Column, Float, ForeignKey, Integer, String, DateTime

Base = declarative_base()

class Users(Base):
    __tablename__ = 'users'
    __table_args__ = {"schema": "public"}
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password = Column(String(100), nullable=False)
    role = Column(String(100), nullable=False)
    last_active_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.datetime.now())
   
    def __init__(self, name, email, password, role) -> None:
        self.name = name
        self.email = email
        self.password = password
        self.role = role

class Buses(Base):
    __tablename__ = 'buses'
    __table_args__ = {"schema": "public"}
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer,ForeignKey(Users.id, ondelete= 'CASCADE'), nullable=False)
    name = Column(String(100), unique=True, nullable=False)
    seat_count = Column(Integer, nullable=False)
    source = Column(String(100), nullable=False)
    destination = Column(String(100), nullable=False)
    timing = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.now())
    updated_at = Column(DateTime)

    def __init__(self, user_id, name, seat_count, source, destination, timing) -> None:
        self.user_id = user_id
        self.name = name
        self.seat_count = seat_count
        self.source = source
        self.destination = destination
        self.timing = timing

class Seats(Base):
    __tablename__ = 'seats'
    __table_args__ = {"schema": "public"}
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey(Users.id, ondelete= 'CASCADE'), nullable=False)
    bus_id = Column(Integer, ForeignKey(Buses.id, ondelete= 'CASCADE'), nullable=False)
    booked_seat_no = Column(Integer, nullable=False)
    occupied_from = Column(String(1000), nullable=False)
    occupied_to = Column(String(1000), nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.now())
    updated_at = Column(DateTime)

    def __init__(self, user_id, bus_id, booked_seat_no, occupied_from, occupied_to) -> None:
        self.user_id = user_id
        self.bus_id = bus_id
        self.booked_seat_no = booked_seat_no
        self.occupied_from = occupied_from
        self.occupied_to = occupied_to

class Prices(Base):
    __tablename__ = 'prices'
    __table_args__ = {"schema": "public"}
    id = Column(Integer, primary_key=True, autoincrement=True)
    bus_id = Column(Integer, ForeignKey(Buses.id, ondelete= 'CASCADE'), nullable=False)
    start_location = Column(String(1000), nullable=False)
    end_location = Column(String(1000), nullable=False)
    price = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.now())
    updated_at = Column(DateTime)

    def __init__(self, bus_id, start_location, end_location, price) -> None:
        self.bus_id = bus_id
        self.start_location = start_location
        self.end_location = end_location
        self.price = price

class Stops(Base):
    __tablename__ = 'stops'
    __table_args__ = {"schema": "public"}
    bus_id = Column(Integer, ForeignKey(Buses.id, ondelete= 'CASCADE'), primary_key=True,  nullable=False)
    stop_no = Column(Integer, nullable=False, primary_key=True)
    stop_name = Column(String(1000), nullable=False)
    timing = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.now())
    updated_at = Column(DateTime)

    def __init__(self, bus_id, stop_no, stop_name, timing) -> None:
        self.bus_id = bus_id
        self.stop_no = stop_no
        self.stop_name = stop_name
        self.timing = timing
