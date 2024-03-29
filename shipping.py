from flask import Flask, request, jsonify, render_template, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import update
from datetime import datetime
import datetime as dt
from sqlalchemy import and_

import requests
import re
from bs4 import BeautifulSoup
from urllib.parse import urlencode

app = Flask(__name__)

app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root@localhost:3306/products'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.config['SQLALCHEMY_BINDS'] = {
    'users': 'mysql+mysqlconnector://root@localhost:3306/users',
    'userauth': 'mysql+mysqlconnector://root@localhost:3306/Authentication'
}

db = SQLAlchemy(app)

class Users(db.Model):
    __bind_key__ = 'users'
    __tablename__ = 'users'  # Ensure this matches the actual table name in your database

    UserID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Name = db.Column(db.String(255), nullable=False)
    Phone = db.Column(db.String(20))
    Age = db.Column(db.Integer)
    Country = db.Column(db.String(255))

class UserAuth(db.Model):
    __bind_key__ = 'userauth'
    __tablename__ = 'addresses'  # Specify the correct table name here

    AddressID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    UserID = db.Column(db.Integer, nullable=False)
    FirstName = db.Column(db.String(255), unique=True, nullable=False)
    Lastname = db.Column(db.String(255), nullable=False)
    Country = db.Column(db.String(255), nullable=False)

@app.route('/shipping', methods=['GET', 'POST'])
def get_shipping_rate():

    origin_country = db.session.query(Users.Country).filter(Users.UserID == 3).scalar()
    destination_country = db.session.query(UserAuth.Country).filter(UserAuth.UserID == 1).scalar()

    print(origin_country)
    print(destination_country)

    # Constructing the URL with dynamic origin and destination countries
    url = f"https://ship.freightos.com/api/shippingCalculator?loadtype=boxes&weight=1&width=50&length=50&height=50&origin={origin_country}&quantity=1&destination={destination_country}"

    response = requests.get(url)
    data = response.json()

    estimated_rates = data['response']['estimatedFreightRates']

    if 'mode' in estimated_rates:
        modes = estimated_rates['mode']
        if isinstance(modes, list) and len(modes) >= 1:
            # If 'mode' is a list, take the first mode
            first_mode = modes[0]
        elif isinstance(modes, dict):
            # If 'mode' is a dictionary, use it directly
            first_mode = modes

        min_price = first_mode['price']['min']['moneyAmount']['amount']
        max_price = first_mode['price']['max']['moneyAmount']['amount']
        min_transit_time = first_mode['transitTimes']['min']
        max_transit_time = first_mode['transitTimes']['max']
        
        print(f"Min Price: {min_price} USD")
        print(f"Max Price: {max_price} USD")
        print(f"Min Transit Time: {min_transit_time} days")
        print(f"Max Transit Time: {max_transit_time} days")
    else:
        print("No shipping rates found.")

    return "Shipping rates retrieved."

        # print("Max Price:", max_price, "USD")
        # print("Min Transit Time:", min_transit_time, "days")
        # print("Max Transit Time:", max_transit_time, "days")

if __name__ == '__main__':
    app.run(port=5001, debug=True)