from flask import Flask, request, redirect, url_for, session, render_template, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
# from invokes import invoke_http
import bcrypt
import requests
from os import environ

from flasgger import Swagger
from flask import jsonify

app = Flask(__name__)

app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

# Configure SQLAlchemy
# app.config['SQLALCHEMY_DATABASE_URI'] = environ.get('dbURL', 'mysql+mysqlconnector://root@localhost:3306/Authentication')
app.config["SQLALCHEMY_DATABASE_URI"] = (
    environ.get("dbURL") or "mysql+mysqlconnector://root@localhost:3306/Authentication"
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Initialize flasgger 
app.config['SWAGGER'] = {
    'title': 'logintemplate microservice API',
    'version': 1.0,
    "openapi": "3.0.2",
    'description': 'Allows authentication of users'
}
swagger = Swagger(app)

class UserAuth(db.Model):
    __tablename__ = 'UserAuth'

    AuthID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    UserID = db.Column(db.Integer, nullable=False)
    Email = db.Column(db.String(255), unique=True, nullable=False)
    PasswordHash = db.Column(db.String(255), nullable=False)

# Routes for authentication
@app.route('/', methods=['GET', 'POST'])
def login():
    """
    User Login
    ---
        tags:
            - Authentication
        parameters:
            -   name: email
                in: formData
                type: string
                required: true
                description: The email of the user.
            -   name: password
                in: formData
                type: string
                required: true
                description: The password of the user.
        responses:
            302:
                description: Redirects to the home page on successful login.
                headers:
                    Location:
                        description: URL of the home page.
                        schema:
                            type: string
                            example: "http://127.0.0.1:5002/"
            200:
                description: Render the login page with an error message.
        """
    error = None
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        valid_email = UserAuth.query.filter_by(Email=email).first()
        if valid_email:
            hashed_password = db.session.query(UserAuth.PasswordHash).filter(UserAuth.Email == email).scalar()
            password_bytes = password.encode('utf-8')
            hashed_password_bytes = hashed_password.encode('utf-8')
            if bcrypt.checkpw(password_bytes, hashed_password_bytes):
                print("Password match!")

                session['email'] = email
                db.session.commit()

                email = session.get('email')
                print(email)
                    
                # Fetch user ID of user logged in
                loggedin_user_id = db.session.query(UserAuth.UserID).filter(UserAuth.Email == email).scalar()
                print(loggedin_user_id)

                session['loggedin_user_id'] = loggedin_user_id
                db.session.commit()

                redirect_url = 'http://127.0.0.1:5002/'
    
                # Redirect to the constructed URL
                return redirect(redirect_url)

            else:
                error = 'Invalid email/password'
        else:
            error = 'Invalid email/password'

    return render_template('login.html', error=error)

@app.route('/logout', methods=['POST','GET'])
def logout():
    """
        User Logout
        ---
        tags:
            - Authentication
        parameters: []
        responses:
            200:
                description: Redirects to the login page on successful logout.
                headers:
                Location:
                    description: URL of the login page.
                    schema:
                        type: string
                        example: "http://127.0.0.1:5002/login"

    """
    session.pop('email', None)
    return redirect(url_for('login'))


@app.route('/register', methods=['GET', 'POST'])
def register():

    """
User Registration
---
tags:
    - Authentication
parameters: []
requestBody:
    required: true
    content:
        application/x-www-form-urlencoded:
            schema:
                type: object
                properties:
                    email:
                        type: string
                        description: The email of the user.
                    password:
                        type: string
                        description: The password of the user.
                    name:
                        type: string
                        description: The name of the user.
                    phone:
                        type: string
                        description: The phone number of the user.
                    age:
                        type: integer
                        description: The age of the user.
                    country:
                        type: string
                        description: The country of the user.
responses:
    302:
        description: Redirects to the login page on successful registration.
        headers:
            Location:
                description: URL of the login page.
                schema:
                    type: string
                    example: "http://127.0.0.1:5001"
    400:
        description: Bad request. Registration failed.
    409:
        description: Conflict. Email already registered.
    200:
        description: Successful registration.
"""
    
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        name = request.form['name']
        phone = request.form['phone']
        age = request.form['age']
        country = request.form['country']
        
        # Generate a salt
        salt = bcrypt.gensalt()

        # Encode the password to bytes
        password_bytes = password.encode('utf-8')

        # Hash a password with the salt
        hashed_password = bcrypt.hashpw(password_bytes, salt)

        print('Hashed password:', hashed_password)

        existing_user = UserAuth.query.filter_by(Email=email).first()
        if existing_user:
            flash('Email already registered.')
            return redirect(url_for('register'))
        
        add_user_url = 'http://host.docker.internal:5004/add_user'
        # for swagger:-
        #add_user_url = 'http://127.0.0.1:5004/add_user'

        add_user_params = {'name': name, 'phone' : phone, 'age' : age, 'country' : country}
        add_user_response = requests.get(add_user_url, params=add_user_params)

        if add_user_response.status_code == 200:
            # Get the username from the response if needed
            user_id = add_user_response.json().get('user_id')
            print("user_id:", user_id)
        
        # Create a new user authentication record using the retrieved UserID
        new_user_auth = UserAuth(UserID=user_id, Email=email, PasswordHash=hashed_password)
        db.session.add(new_user_auth)
        db.session.commit()
        
        flash('Registration successful. Please log in.')
        return redirect(url_for('login'))
    return render_template('register.html')

# To pass loggedin user id to car rental
@app.route('/rentcar', methods=['GET'])
def get_loggedin_user_id():
    loggedin_user_id = session.get('loggedin_user_id')
    return render_template("rentcar.html", loggedin_user_id=loggedin_user_id)

# if __name__ == '__main__':
#     app.run(port=5001, debug=True)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
