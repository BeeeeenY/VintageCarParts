from flask import Flask, request, render_template, jsonify, session
from flask_sqlalchemy import SQLAlchemy
import firebase_admin
from firebase_admin import credentials, storage
import datetime as dt
# from invokes import invoke_http
from os import environ

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {'storageBucket': 'esdfirebase-2fe43.appspot.com'})
bucket = storage.bucket()

app = Flask(__name__)

app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root@localhost:3306/forum'
app.config['SQLALCHEMY_DATABASE_URI'] = environ.get('dbURL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.config['SQLALCHEMY_BINDS'] = {
    'Userauth': 'mysql+mysqlconnector://root@localhost:3306/Authentication'
}

db = SQLAlchemy(app)

class Forum(db.Model):
    __tablename__ = 'Posts'
    PostID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    UserID = db.Column(db.Integer)
    Title = db.Column(db.String(255), nullable=False)
    Content = db.Column(db.Text)
    Postdate = db.Column(db.DateTime)
    # Lastupdate = db.Column(db.DateTime)

    def __init__(self, UserID, Title, Content, Postdate):
            self.UserID = UserID
            self.Title = Title
            self.Content = Content
            self.Postdate = Postdate
            # self.Lastupdate = Lastupdate

    def json(self):
            return {"PostID": self.PostID, "UserID": self.UserID, "Title": self.Title, "Content": self.Content, "PostDate": self.Postdate, 
                    "LastUpdated": self.Lastupdate}


class UserAuth(db.Model):
    __tablename__ = 'UserAuth'  # Specify the correct table name here
    __bind_key__ = 'Userauth'

    AuthID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    UserID = db.Column(db.Integer, nullable=False)
    Email = db.Column(db.String(255), unique=True, nullable=False)
    PasswordHash = db.Column(db.String(255), nullable=False)

class Users(db.Model):
    __tablename__ = 'Users'
    UserID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Name = db.Column(db.String(255), nullable=False)
    Phone = db.Column(db.String(20))
    Age = db.Column(db.Integer)
    Country = db.Column(db.String(255))

        
class Comments(db.Model):
    __tablename__ = 'Comments'  # Specify the correct table name here
    CommentID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    UserID = db.Column(db.Integer, db.ForeignKey('Users.UserID'),nullable=False)
    Content = db.Column(db.String(255), nullable=False)
    CommentDate = db.Column(db.DateTime)
    # user = db.relationship('Users', foreign_keys=[UserID])

@app.route('/', methods=['GET'])
def index():
    return render_template('createforum.html')

@app.route("/create_post", methods=['POST'])
def create_post():
    title = request.form.get('Title')
    content = request.form.get('Content')

    if not title or not content:
        return 'Missing form data.', 400
    

    print(session)  # Add this line to check the session content
    email = session.get('email')


    # Check if the user is logged in
    if email is None:
        return 'User not logged in.', 401

    # Fetch user ID of the user logged in
    loggedin_user_id = db.session.query(UserAuth.UserID).filter(UserAuth.Email == email).scalar()

    # Check if loggedin_user_id is not None before creating the post
    if loggedin_user_id is None:
        return 'Invalid user.', 401

    post = Forum(UserID=loggedin_user_id, Title=title, Content=content, Postdate=dt.datetime.now())

    try:
        db.session.add(post)
        db.session.commit()
    except Exception as e:
        return jsonify({
            "code": 500,
            "message": f"An error occurred creating the post: {str(e)}"
        }), 500
    
    return render_template("createforum.html", posts=[post])



@app.route('/get_posts', methods=['GET'])
def get_posts():
    # Fetch the latest posts from the database
    latest_posts = Forum.query.order_by(Forum.Postdate.desc()).limit(5).all()

    # Convert posts to a list of dictionaries
    posts = [{
        'Title': post.Title,
        'Content': post.Content,
        'UserID': post.UserID,
        'PostDate': post.Postdate.strftime('%Y-%m-%d %H:%M:%S')
    } for post in latest_posts]

    # Return the posts as JSON
    return jsonify({'posts': posts})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5004, debug=True)
