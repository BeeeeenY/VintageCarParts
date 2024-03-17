from flask import Flask, request, render_template, jsonify, session, redirect
from flask_sqlalchemy import SQLAlchemy
import firebase_admin
from firebase_admin import credentials, storage
import datetime as dt
import requests
from os import environ

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {'storageBucket': 'esdfirebase-2fe43.appspot.com'})
bucket = storage.bucket()

app = Flask(__name__)

app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root@localhost:3306/forum'
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
    LastUpdated = db.Column(db.DateTime)

    def __init__(self, UserID, Title, Content, Postdate, LastUpdated):
            self.UserID = UserID
            self.Title = Title
            self.Content = Content
            self.Postdate = Postdate
            self.LastUpdated = LastUpdated

    def json(self):
            return {"PostID": self.PostID, "UserID": self.UserID, "Title": self.Title, "Content": self.Content, "PostDate": self.Postdate, 
                    "LastUpdated": self.LastUpdated}


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
    PostID = db.Column(db.Integer, nullable = False)
    UserID = db.Column(db.Integer)
    Content = db.Column(db.String(255), nullable=False)
    CommentDate = db.Column(db.DateTime)
    

@app.route('/forum', methods=['GET'])
def get_forum_posts():
    posts = db.session.query(Forum).all()
    posts_arr = []

    for post in posts:
        post_id = post.PostID
        comments = db.session.scalars(db.select(Comments).filter_by(PostID=post_id)).all()
        
        comments_arr = []
        for comment in comments:
            user_id = comment.UserID

            get_username_url = 'http://127.0.0.1:5004/get_username'
            get_username_params = {'user_id': user_id}
            get_username_response = requests.get(get_username_url, params=get_username_params)

            if get_username_response.status_code == 200:
                # Get the username from the response if needed
                username = get_username_response.json().get('username')
                print("Username:", username)

            if comment:
                comment_details = {
                    'username': username,
                    'content': comment.Content,
                    'CommentDate': comment.CommentDate.strftime('%Y-%m-%d %H:%M:%S')
                }
            comments_arr.append(comment_details)

        
        get_username_url = 'http://127.0.0.1:5004/get_username'
        get_username_params = {'user_id': post.UserID}
        get_username_response = requests.get(get_username_url, params=get_username_params)

        if get_username_response.status_code == 200:
            # Get the username from the response if needed
            username = get_username_response.json().get('username')
            print("Username:", username)

        if post:
            # Convert posts to a list of dictionaries
            post_details = {
                'PostID': post.PostID,
                'Title': post.Title,
                'Content': post.Content,
                'PostDate': post.Postdate.strftime('%Y-%m-%d %H:%M:%S'),
                'Username': username,
                'Comments': comments_arr
            }
        posts_arr.append(post_details)

    print(posts_arr)

    if posts_arr:
        return render_template('forum.html', posts = posts_arr)
    else:
        return render_template('forum.html', data = "There are no posts.")

@app.route('/create_post_page')
def create_post_page():
    return render_template('createforum.html')

@app.route("/create_post", methods=['POST'])
def create_post():
    title = request.form.get('Title')
    content = request.form.get('Content')

    if not title or not content:
        return 'Missing form data.', 400
    
    # Fetch user ID of user logged in
    loggedin_user_id = session.get('loggedin_user_id')
    print(loggedin_user_id)

    post = Forum(UserID=loggedin_user_id, Title=title, Content=content, Postdate=dt.datetime.now(), LastUpdated=dt.datetime.now())

    try:
        db.session.add(post)
        db.session.commit()
    except Exception as e:
        return jsonify({
            "code": 500,
            "message": f"An error occurred creating the post: {str(e)}"
        }), 500
    
    redirect_url = '/forum'
    
     # Redirect to the constructed URL
    return redirect(redirect_url)

@app.route('/create_comment', methods=['POST'])
def create_comment():
    comment_content = request.form.get('comment')
    post_id = request.form.get('post_id')

    print(post_id)
    print(comment_content)
    loggedin_user_id = session.get('loggedin_user_id')

    comment = Comments(PostID = post_id, UserID = loggedin_user_id, Content = comment_content, CommentDate = dt.datetime.now())

    try:
        db.session.add(comment)
        db.session.commit()
    except Exception as e:
        return jsonify({
            "code": 500,
            "message": f"An error occurred creating the comment: {str(e)}"
        }), 500

    redirect_url = '/forum'
    
     # Redirect to the constructed URL
    return redirect(redirect_url)

if __name__ == '__main__':
    app.run(port=5006, debug=True)
