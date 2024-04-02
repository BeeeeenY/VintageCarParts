from flask import Flask, request, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from os import environ
from flasgger import Swagger


app = Flask(__name__)

app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

app.config["SQLALCHEMY_DATABASE_URI"] = (
    environ.get("dbURL") or "mysql+mysqlconnector://root@localhost:3306/users"

)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

app.config['SWAGGER'] = {
    'title': 'users microservice API',
    'version': 1.0,
    "openapi": "3.0.2",
    'description': 'Allows retrieval of username and creating users'
}
swagger = Swagger(app)

class Users(db.Model):
    __tablename__ = 'users'

    UserID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Name = db.Column(db.String(255), nullable=False)
    Phone = db.Column(db.String(20))
    Age = db.Column(db.Integer)
    Country = db.Column(db.String(255))

    def __init__(self, Name, Phone, Age, Country):
        self.Name = Name
        self.Phone = Phone
        self.Age = Age
        self.Country = Country

    def json(self):
        return {"UserID": self.UserID, "Name": self.Name, "Phone": self.Phone, "Age": self.Age, "Country": self.Country}

@app.route("/get_username")
def get_username():
    """
    Get the username associated with the provided user ID.

    ---
        parameters:
            -   name: user_id
                in: query
                description: The ID of the user whose username is to be retrieved.
                required: true
                schema:
                type: string
        responses:
            200:
                description: OK. The username was retrieved successfully.
                content:
                application/json:
                    schema:
                    type: object
                    properties:
                        username:
                        type: string
                        description: The username associated with the provided user ID.
            400:
                description: Bad Request. The request is missing the user ID parameter.
            404:
                description: Not Found. The provided user ID does not exist in the database.
"""

    user_id = request.args.get('user_id')
    print(user_id)
    user_name = db.session.query(Users.Name).filter(Users.UserID == user_id).first()

    user_name = user_name[0]
    print(user_name)

    return jsonify(username=user_name)

@app.route("/get_userphone")
def get_userphone(user_id=None):
    """
    Get the username associated with the provided user ID.

    ---
        parameters:
            -   name: user_id
                in: query
                description: The ID of the user whose phone number is to be retrieved.
                required: true
                schema:
                type: string
        responses:
            200:
                description: OK. The phone number was retrieved successfully.
                content:
                application/json:
                    schema:
                    type: object
                    properties:
                        username:
                        type: string
                        description: The username associated with the provided user ID.
            400:
                description: Bad Request. The request is missing the user ID parameter.
            404:
                description: Not Found. The provided user ID does not exist in the database.
"""

    user_id = request.args.get('user_id')
   
    user_phone = db.session.query(Users.Phone).filter(Users.UserID == user_id).first()

    if user_phone: 
        user_phone = user_phone[0]
        print(user_phone)
        return jsonify(userphone=user_phone)
    else:
        return jsonify(error="User not found"), 404

@app.route("/add_user")
def add_user():
    """
        Add a new user to the database.

        ---
        parameters:
            -   name: name
                in: query
                description: The name of the user to be added.
                required: true
                schema:
                type: string
            -   name: phone
                in: query
                description: The phone number of the user to be added.
                required: true
                schema:
                type: string
            -   name: age
                in: query
                description: The age of the user to be added.
                required: true
                schema:
                type: integer
            -   name: country
                in: query
                description: The country of the user to be added.
                required: true
                schema:
                type: string
        responses:
            200:
                description: OK. The user was added successfully.
                content:
                application/json:
                    schema:
                    type: object
                    properties:
                        user_id:
                        type: integer
                        description: The ID of the newly added user.
            400:
                description: Bad Request. The request is missing required parameters or contains invalid data.
"""

    name = request.args.get('name')
    phone = request.args.get('phone')
    age = request.args.get('age')
    country = request.args.get('country')

    new_user = Users(Name=name, Phone=phone, Age=age, Country=country)
    db.session.add(new_user)
    db.session.commit()

    user_id = new_user.UserID
    return jsonify(user_id=user_id)


if __name__ == '__main__':
    app.run(host='0.0.0.0',port=5004, debug=True)
