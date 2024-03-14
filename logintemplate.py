from flask import Flask, request, redirect, url_for, session, render_template, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from invokes import invoke_http
import bcrypt
import requests

app = Flask(__name__)

app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

# Configure SQLAlchemy
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root@localhost:3306/Authentication'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class UserAuth(db.Model):
    __tablename__ = 'UserAuth'

    AuthID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    UserID = db.Column(db.Integer, nullable=False)
    Email = db.Column(db.String(255), unique=True, nullable=False)
    PasswordHash = db.Column(db.String(255), nullable=False)

# Routes for authentication
@app.route('/', methods=['GET', 'POST'])
def login():
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
    session.pop('email', None)
    return redirect(url_for('login'))
    
@app.route('/register', methods=['GET', 'POST'])
def register():
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
        
        add_user_url = 'http://127.0.0.1:5004/add_user'
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

if __name__ == '__main__':
    app.run(port=5001, debug=True)
