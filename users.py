from flask import Flask, request, jsonify, render_template, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from invokes import invoke_http
from os import environ

app = Flask(__name__)

app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

# app.config['SQLALCHEMY_DATABASE_URI'] = environ.get('dbURL')
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root@localhost:3306/users'
app.config["SQLALCHEMY_DATABASE_URI"] = (
    environ.get("dbURL") or "mysql+mysqlconnector://root@host.docker.internal:3306/users"
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

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
    user_id = request.args.get('user_id')
    print(user_id)
    user_name = db.session.query(Users.Name).filter(Users.UserID == user_id).first()

    user_name = user_name[0]  # Assuming the name is in the first column
    print(user_name)

    return jsonify(username=user_name)

@app.route("/add_user")
def add_user():
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
