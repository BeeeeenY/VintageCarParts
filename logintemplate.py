from flask import Flask, request, redirect, url_for, session, render_template, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

# Configure SQLAlchemy
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root@localhost:3306/Authentication'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


db = SQLAlchemy(app)

# Define your UserAuth model
class UserAuth(db.Model):
    __tablename__ = 'UserAuth'  # Specify the correct table name here

    AuthID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    UserID = db.Column(db.Integer, nullable=False)
    Email = db.Column(db.String(255), unique=True, nullable=False)
    PasswordHash = db.Column(db.String(255), nullable=False)
    LastLogin = db.Column(db.DateTime)
    FailedLoginAttempts = db.Column(db.Integer, default=0)
    PasswordResetToken = db.Column(db.String(255))
    TokenExpiryDate = db.Column(db.DateTime)

class Users(db.Model):
    __tablename__ = 'Users'  # Ensure this matches the actual table name in your database

    UserID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Name = db.Column(db.String(255), nullable=False)
    Phone = db.Column(db.String(20))
    Age = db.Column(db.Integer)
    Country = db.Column(db.String(255))

# Routes for authentication
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user_auth = UserAuth.query.filter_by(Email=email, PasswordHash=password).first()
        if user_auth:
            session['email'] = email
            # Update last login time
            user_auth.LastLogin = datetime.now()
            db.session.commit()
            return redirect(url_for('store'))  # Redirect to the template route on successful login
        else:
            return 'Invalid email/password'
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('email', None)
    return redirect(url_for('index'))

@app.route('/')
def index():
    if 'email' in session:
        return f'Logged in as {session["email"]}<br><a href="/logout">Logout</a>'
    return 'You are not logged in<br><a href="/login">Login</a>'

@app.route('/template', methods=['GET', 'POST'])  # Allow both GET and POST methods for /template
def template():
    if 'email' in session:
        return render_template('template.html')
    else:
        return redirect(url_for('login'))
    
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        # Check if user already exists
        existing_user = UserAuth.query.filter_by(Email=email).first()
        if existing_user:
            flash('Email already registered.')
            return redirect(url_for('register'))
        
        new_user = UserAuth(Email=email, PasswordHash=password, LastLogin=datetime.now())
        db.session.add(new_user)
        db.session.commit()
        
        flash('Registration successful. Please log in.')
        return redirect(url_for('login'))
    return render_template('register.html')
if __name__ == '__main__':
    app.run(port=5000, debug=True)
