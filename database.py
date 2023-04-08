from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from configparser import ConfigParser

config_object = ConfigParser()
config_object.read("config.ini")

userinfo = config_object["USERINFO"]

Base = declarative_base()
engine = create_engine(
        "postgresql://{}:{}@localhost/tutorialdb".format(userinfo["username"],userinfo["password"]),
        echo=True
        )

SessionLocal = sessionmaker(bind=engine)
db_session = SessionLocal()
Base.metadata.create_all(engine)
