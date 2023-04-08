from flask import Flask
from flask_jwt_extended import JWTManager
from routes.users import users_view
from routes.buses import buses_view
from routes.seats import seats_view
from routes.stops import stops_view
from routes.prices import prices_view
from configparser import ConfigParser

app = Flask(__name__)

app.register_blueprint(users_view)
app.register_blueprint(buses_view)
app.register_blueprint(seats_view)
app.register_blueprint(stops_view)
app.register_blueprint(prices_view)

config_object = ConfigParser()
config_object.read("config.ini")

userinfo = config_object["USERINFO"]

app.config['SECRET_KEY'] = userinfo["secret_key"]

jwt = JWTManager(app)

@app.route('/')
def bus_booking_app():
    return 'BUS BOOKING APP'

if __name__=="__main__":
    app.run(debug=True)
