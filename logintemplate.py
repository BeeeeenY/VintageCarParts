from flask import Flask, request, redirect, url_for, session, render_template, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from invokes import invoke_http
import bcrypt

app = Flask(__name__)

app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

# Configure SQLAlchemy
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root@localhost:3306/Authentication'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.config['SQLALCHEMY_BINDS'] = {
    'users': 'mysql+mysqlconnector://root@localhost:3306/Users'
}

db = SQLAlchemy(app)

# Define your UserAuth model
class UserAuth(db.Model):
    __tablename__ = 'UserAuth'  # Specify the correct table name here

    AuthID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    UserID = db.Column(db.Integer, nullable=False)
    Email = db.Column(db.String(255), unique=True, nullable=False)
    PasswordHash = db.Column(db.String(255), nullable=False)

class Users(db.Model):
    __bind_key__ = 'users'
    __tablename__ = 'users'  # Ensure this matches the actual table name in your database

    UserID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Name = db.Column(db.String(255), nullable=False)
    Phone = db.Column(db.String(20))
    Age = db.Column(db.Integer)
    Country = db.Column(db.String(255))

# Routes for authentication
@app.route('/', methods=['GET', 'POST'])
def login():
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
                return invoke_http(url='http://127.0.0.1:5002/', method='GET', redirect_url='http://127.0.0.1:5002/')
        return 'Invalid email/password'
    return render_template('login.html')

@app.route('/logout', methods=['POST'])
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
        
        new_user = Users(Name=name, Phone=phone, Age=age, Country=country)
        db.session.add(new_user)
        db.session.commit()
        
        new_user_id = new_user.UserID
        
        # Create a new user authentication record using the retrieved UserID
        new_user_auth = UserAuth(UserID=new_user_id, Email=email, PasswordHash=hashed_password)
        db.session.add(new_user_auth)
        db.session.commit()
        
        flash('Registration successful. Please log in.')
        return redirect(url_for('login'))
    return render_template('register.html')

if __name__ == '__main__':
    app.run(port=5001, debug=True)
