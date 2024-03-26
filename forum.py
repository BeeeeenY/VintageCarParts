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

# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root@localhost:3306/forum'
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.config["SQLALCHEMY_DATABASE_URI"] = (
    environ.get("dbURL") or "mysql+mysqlconnector://root:root@localhost:3306/forum"
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

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

        
class Comments(db.Model):
    __tablename__ = 'Comments'  # Specify the correct table name here
    CommentID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    PostID = db.Column(db.Integer, nullable = False)
    UserID = db.Column(db.Integer)
    Content = db.Column(db.String(255), nullable=False)
    CommentDate = db.Column(db.DateTime)
    

@app.route('/forum', methods=['GET'])
def get_forum_posts():
    search_query = request.args.get('search')
    if search_query == None:
        search_query = ""
    print(search_query)
    search_data = []

    posts = db.session.query(Forum).all()
    posts_arr = []

    for post in posts:
        post_id = post.PostID
        comments = db.session.scalars(db.select(Comments).filter_by(PostID=post_id)).all()
        
        comments_arr = []
        for comment in comments:
            loggedin_user_id = session.get('loggedin_user_id')
            user_id = comment.UserID

            own_comment = False
            if user_id == loggedin_user_id:
                own_comment = True

            get_username_url = 'http://host.docker.internal:5004/get_username'
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
                    'CommentDate': comment.CommentDate.strftime('%Y-%m-%d %H:%M:%S'),
                    'OwnComment': own_comment,
                    'CommentID': comment.CommentID
                }
            comments_arr.append(comment_details)

        
        get_username_url = 'http://host.docker.internal:5004/get_username'
        get_username_params = {'user_id': post.UserID}
        get_username_response = requests.get(get_username_url, params=get_username_params)

        if get_username_response.status_code == 200:
            # Get the username from the response if needed
            username = get_username_response.json().get('username')
            print("Username:", username)

        own_post = False
        if post.UserID == loggedin_user_id:
            own_post = True
        
        post_id_str = str(post_id)

        # Get a reference to the folder
        folder_prefix = "forum/" + post_id_str + '/'
        
        # Retrieves all the files within the folder specified by folder_prefix.
        blobs = bucket.list_blobs(prefix=folder_prefix)

        # Define a distant future timestamp
        future_timestamp = dt.datetime.utcnow() + dt.timedelta(days=3650)

        pic_arr = []

        for blob in blobs:
            picture_url = blob.generate_signed_url(expiration=future_timestamp)  # URL expiration time in seconds (adjust as needed)
            pic_arr.append(picture_url)

        if len(pic_arr) == 0:
            print("No files found.")

        if post:
            # Convert posts to a list of dictionaries
            post_details = {
                'PostID': post.PostID,
                'Title': post.Title,
                'Content': post.Content,
                'PostDate': post.Postdate.strftime('%Y-%m-%d %H:%M:%S'),
                'Username': username,
                'Comments': comments_arr,
                'OwnPost': own_post,
                "Pics": pic_arr
            }
        posts_arr.append(post_details)

        if search_query in post.Title:
            search_data.append(post_details)

    print(posts_arr)

    if search_data:
        return render_template('forum.html', posts = search_data)
    elif search_data == []:
        return render_template('forum.html', data = "There are no search results.")
    elif posts_arr:
        return render_template('forum.html', posts = posts_arr)
    else:
        return render_template('forum.html', data = "There are no posts.")

@app.route('/create_post_page')
def create_post_page():
    return render_template('createforum.html', data = 'Add Forum Content', button = 'Submit')

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
    
    post_id = post.PostID

    if request.method == "POST":
        # Get the uploaded photos from the HTML form
        photos = request.files.getlist("file")

        # Filter out empty FileStorage objects
        photos = [photo for photo in photos if photo.filename]
        
        if photos:
            print("User uploaded photos, proceeding with upload")
            # User uploaded photos, proceed with upload
            # List to store upload results
            upload_results = []

            # Upload each photo to Firebase Storage
            for photo in photos:
                # Specify a unique path for each photo in Firebase Storage
                photo_blob = bucket.blob(f"forum/{post_id}/{photo.filename}")
                
                # Upload the photo
                try:
                    photo_blob.upload_from_file(photo)
                    upload_results.append(True)  # Successful upload
                except Exception as e:
                    upload_results.append(False)  # Failed upload
                    print(f"Error uploading photo: {e}")

            # Check if all uploads were successful
            try:
                all(upload_results)
                print("Photos uploaded successfully!")
            except Exception as e:
                print("Failed to upload all photos. Please try again.")  # Return 400 status code for client-side error

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

@app.route("/delete_post/<int:PostID>")
def delete_post(PostID):
    db.session.query(Forum).filter_by(PostID=PostID).delete()
    db.session.commit()

    return redirect('/forum')

@app.route("/delete_comment/<int:CommentID>")
def delete_comment(CommentID):
    db.session.query(Comments).filter_by(CommentID=CommentID).delete()
    db.session.commit()

    return redirect('/forum')

@app.route("/update_post_page/<int:PostID>")
def update_post_page(PostID):
    post_details = db.session.query(Forum).filter(Forum.PostID == PostID).first()
    if post_details:
        post = {
            "PostID": PostID,
            "Title": post_details.Title,
            "Content": post_details.Content
        }
    return render_template('createforum.html', data = 'Update Forum Content', post = post, button = 'Update')

@app.route("/update_post/<int:PostID>", methods=['POST'])
def update_post(PostID):
    Title = request.form.get('Title')
    Content = request.form.get('Content')

    post = db.session.query(Forum).filter_by(PostID = PostID).first()
    post.Title = Title
    post.Content = Content
    post.LastUpdated = dt.datetime.now()

    try:
        db.session.commit()
    except Exception as e:
        return jsonify(
            {
                "code": 500,
                "data": {
                    "partID": PostID
                },
                "message": f"An error occurred while updating the post: {str(e)}"
            }
        ), 500
    
    post_id = post.PostID
    print(post_id)

    if request.method == "POST":
        # Get the uploaded photos from the HTML form
        photos = request.files.getlist("file")

        print(photos)

        # Filter out empty FileStorage objects
        photos = [photo for photo in photos if photo.filename]
        
        if photos:
            print("User uploaded photos, proceeding with upload")
            # User uploaded photos, proceed with upload
            # List to store upload results
            upload_results = []

            # Upload each photo to Firebase Storage
            for photo in photos:
                # Specify a unique path for each photo in Firebase Storage
                photo_blob = bucket.blob(f"forum/{post_id}/{photo.filename}")
                
                # Upload the photo
                try:
                    photo_blob.upload_from_file(photo)
                    upload_results.append(True)  # Successful upload
                except Exception as e:
                    upload_results.append(False)  # Failed upload
                    print(f"Error uploading photo: {e}")

            # Check if all uploads were successful
            try:
                all(upload_results)
                print("Photos uploaded successfully!")
            except Exception as e:
                print("Failed to upload all photos. Please try again.")  # Return 400 status code for client-side error

    return redirect("/forum")

@app.route("/update_comment/<int:CommentID>", methods=['POST'])
def update_comment(CommentID):
    edited_comment = request.form.get('edited_comment')

    comment = db.session.query(Comments).filter_by(CommentID = CommentID).first()
    comment.Content = edited_comment
    comment.CommentDate = dt.datetime.now()

    try:
        db.session.commit()
    except Exception as e:
        return jsonify(
            {
                "code": 500,
                "data": {
                    "partID": CommentID
                },
                "message": f"An error occurred while updating the comment: {str(e)}"
            }
        ), 500
        
    return redirect("/forum")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5006, debug=True)
