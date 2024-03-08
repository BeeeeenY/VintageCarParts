from flask import Flask, request, jsonify, render_template, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import update
from datetime import datetime
import firebase_admin
from firebase_admin import credentials, storage
import datetime as dt
from sqlalchemy import and_

cred = credentials.Certificate("./serviceAccountKey.json")
firebase_admin.initialize_app(cred, {'storageBucket': 'esdfirebase-2fe43.appspot.com'})
bucket = storage.bucket()

app = Flask(__name__)

app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root@localhost:3306/products'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.config['SQLALCHEMY_BINDS'] = {
    'users': 'mysql+mysqlconnector://root@localhost:3306/users',
    'orders': 'mysql+mysqlconnector://root@localhost:3306/orders',
    'userauth': 'mysql+mysqlconnector://root@localhost:3306/Authentication',
    'forum': 'mysql+mysqlconnector://root@localhost:3306/forum'

}

db = SQLAlchemy(app)


class Parts(db.Model):
    __tablename__ = 'parts'

    PartID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    UserID = db.Column(db.Integer)
    Name = db.Column(db.String(255), nullable=False)
    AuthenticationNum = db.Column(db.String(255))
    Category = db.Column(db.String(255), nullable=False)
    Description = db.Column(db.Text)
    Price = db.Column(db.Float(precision=2), nullable = False)
    QuantityAvailable = db.Column(db.Integer, nullable = False)
    Location = db.Column(db.String(255))
    Brand = db.Column(db.String(255))
    Model = db.Column(db.String(255))
    Status = db.Column(db.String(255))
    Content = db.Column(db.String(255))
    PostDate = db.Column(db.DateTime)

    def __init__(self, UserID, Name, AuthenticationNum, Category, Description, Price, QuantityAvailable, Location, Brand, Model, Status, Content, PostDate):
        self.UserID = UserID
        self.Name = Name
        self.AuthenticationNum = AuthenticationNum
        self.Category = Category
        self.Description = Description
        self.Price = Price
        self.QuantityAvailable = QuantityAvailable
        self.Location = Location
        self.Brand = Brand
        self.Model = Model
        self.Status = Status
        self.Content = Content
        self.PostDate = PostDate

    def json(self):
        return {"PartID": self.PartID, "UserID": self.UserID, "Name": self.Name, "AuthenticationNum": self. AuthenticationNum, "Category": self.Category, 
                "Description": self.Description, "Price": self.Price, "QuantityAvailable": self.QuantityAvailable, "Location": self.Location, 
                "Brand": self.Brand, "Model": self.Model, "Brand": self.Model, "Status": self.Status, "Content": self.Content, "PostDate": self.PostDate}

class Users(db.Model):
    __bind_key__ = 'users'
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
    
class Comments(db.Model):
    __tablename__ = 'Comments'

    CommentID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    PartID = db.Column(db.Integer, nullable = False)
    UserID = db.Column(db.Integer)
    Content = db.Column(db.Text)
    CommentDate = db.Column(db.DateTime)

    def __init__(self, PartID, UserID, Content, CommentDate):
        self.PartID = PartID
        self.UserID = UserID
        self.Content = Content
        self.CommentDate = CommentDate

    def json(self):
        return {"CommentID": self.CommentID, "PartID": self.PartID, "UserID": self.UserID, "Content": self.Content, "CommentDate": self.CommentDate}
    
class UserAuth(db.Model):
    __bind_key__ = 'userauth'
    __tablename__ = 'UserAuth'  # Specify the correct table name here

    AuthID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    UserID = db.Column(db.Integer, nullable=False)
    Email = db.Column(db.String(255), unique=True, nullable=False)
    PasswordHash = db.Column(db.String(255), nullable=False)

class Forum(db.Model):
    __bind_key__ = 'forum'
    __tablename__ = 'Posts'
    PostID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    UserID = db.Column(db.Integer)
    Title = db.Column(db.String(255), nullable=False)
    Content = db.Column(db.Text)
    Postdate = db.Column(db.DateTime)
    LastUpdated = db.Column(db.DateTime)

    def __init__(self, PostID, UserID, Title, Content, Postdate, LastUpdated):
            self.PostID = PostID
            self.UserID = UserID
            self.Title = Title
            self.Content = Content
            self.Postdate = Postdate
            self.LastUpdated = LastUpdated

    def json(self):
            return {"PostID": self.PostID, "UserID": self.UserID, "Title": self.Title, "Content": self.Content, "PostDate": self.Postdate, 
                    "LastUpdated": self.Lastupdate}


@app.route("/")
def get_all_parts():
    parts_data = []  # List to hold data for each part

    email = session.get('email')
    print(email)
    
    # Fetch user ID of user logged in
    loggedin_user_id = db.session.query(UserAuth.UserID).filter(UserAuth.Email == email).scalar()
    print(loggedin_user_id)

    # Fetch all parts
    parts = db.session.query(Parts).all()

    for part in parts:
        part_id = part.PartID
        user_id = part.UserID

        if loggedin_user_id != user_id:
            print(user_id)
            print(loggedin_user_id)
            # Fetch user name for the current part
            user_name = db.session.query(Users.Name).filter(Users.UserID == user_id).scalar()

            part_id_str = str(part_id)

            # Get a reference to the folder
            folder_prefix = part_id_str + '/'

            # Retrieves all the files within the folder specified by folder_prefix.
            blobs = bucket.list_blobs(prefix=folder_prefix)

            # Initialize first_picture_url
            first_picture_url = None

            # Define a distant future timestamp
            future_timestamp = dt.datetime.utcnow() + dt.timedelta(days=3650)

            for blob in blobs:
                first_picture_url = blob.generate_signed_url(expiration=future_timestamp)  # URL expiration time in seconds (adjust as needed)
                print("URL of the first picture:", first_picture_url)
                break  # Stop after retrieving the first file's URL

            if first_picture_url is None:
                print("No files found.")

        
            if part:
                # Create a dictionary to hold part data
                part_data = {
                    "PartID": part.PartID,
                    "ProductName": part.Name,
                    "Description": part.Description,
                    "Price": part.Price,
                    "Brand": part.Brand,
                    "Model": part.Model,
                    "UserName": user_name,
                    "Pic": first_picture_url,  # Pass the download URL to the HTML template
                    "Status": part.Status,
                }

                parts_data.append(part_data)  # Add part data to the list
        
    print(parts_data)

    if parts_data:
        # Return the list of part data as JSON response
        return display_all_parts(parts_data)
    
    else:
        return jsonify(
            {
                "code": 404,
                "message": "There are no parts."
            }
        ), 404
    
@app.route("/<int:PartID>")
def find_by_partID(PartID):
    part = db.session.scalars(db.select(Parts).filter_by(PartID=PartID).limit(1)).first()

    user_id = part.UserID

    # Fetch user name for the current part
    user_name = db.session.query(Users.Name).filter(Users.UserID == user_id).scalar()

    # Fetch part details for the current part
    part_details = db.session.query(Parts).filter(Parts.PartID == PartID).first()

    part_id_str = str(PartID)

    # Get a reference to the folder
    folder_prefix = part_id_str + '/'
    
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

    print(pic_arr)

    comments = db.session.scalars(db.select(Comments).filter_by(PartID=PartID)).all()
    
    if part_details:
        # Create a dictionary to hold part data
        part = {
            "PartID": PartID,
            "ProductName": part_details.Name,
            "Description": part_details.Description,
            "Price": part_details.Price,
            "QuantityAvailable": part_details.QuantityAvailable,
            "UserName": user_name,
            "Brand": part_details.Brand,
            "Model": part_details.Model,
            "Status": part_details.Status,
            "Pics": pic_arr,
            "Comments": comments
            }


    if part:
        return display_part(part)

    return jsonify(
        {
            "code": 404,
            "message": "Part not found."
        }
    ), 404


@app.route("/listing")
def seller_product_listing():
    parts_data = []  # List to hold data for each parts

    email = session.get('email')
    print(email)
    
    # Fetch user ID of user logged in
    loggedin_user_id = db.session.query(UserAuth.UserID).filter(UserAuth.Email == email).scalar()
    print(loggedin_user_id)

    # Fetch all parts
    part_details = db.session.query(Parts).filter(Parts.UserID == loggedin_user_id).all()

    for part in part_details:
        part_id = part.PartID

        part_id_str = str(part_id)

        print(part_id_str)

        # Get a reference to the folder
        folder_prefix = part_id_str + '/'

        # Retrieves all the files within the folder specified by folder_prefix.
        blobs = bucket.list_blobs(prefix=folder_prefix)

        # Initialize first_picture_url
        first_picture_url = None

        # Define a distant future timestamp
        future_timestamp = dt.datetime.utcnow() + dt.timedelta(days=3650)

        for blob in blobs:
            first_picture_url = blob.generate_signed_url(expiration=future_timestamp)  # URL expiration time in seconds (adjust as needed)
            print("URL of the first picture:", first_picture_url)
            break  # Stop after retrieving the first file's URL

        if first_picture_url is None:
            print("No files found.")

    
        if part:
            # Create a dictionary to hold part data
            part_data = {
                "PartID": part.PartID,
                "Name": part.Name,
                "Price": part.Price,
                "Quantity": part.QuantityAvailable,
                "Status": part.Status,
                "Pic": first_picture_url  # Pass the download URL to the HTML template
            }

            parts_data.append(part_data)  # Add part data to the list
            
    if parts_data:
        # Return the list of part data as JSON response
        return render_template('productlisting.html', parts = parts_data)
    
    else:
        return jsonify(
            {
                "code": 404,
                "message": "There are no parts posted."
            }
        ), 404

@app.route("/update")
def update_part_page():
    part_id = request.args.get('part_id')
    part_details = db.session.query(Parts).filter(Parts.PartID == part_id).first()

    if part_details:
        # Create a dictionary to hold part data
        part = {
            "PartID": part_details.PartID,
            "ProductName": part_details.Name,
            "AuthenticationNum": part_details.AuthenticationNum,
            "Category": part_details.Category,
            "Description": part_details.Description,
            "Price": part_details.Price,
            "Qty": part_details.QuantityAvailable,
            "Location": part_details.Location,
            "Brand": part_details.Brand,
            "Model": part_details.Model,
            "AddInfo": part_details.Content
            }

    if part:
        return render_template('update.html', part = part)

    return jsonify(
        {
            "code": 404,
            "message": "Part not found."
        }
    ), 404

@app.route("/forum")
def forum():
        # Fetch all posts from the database
        posts = Forum.query.all()

        # Render the forum.html template with the posts data
        # return render_template("createforum.html", posts=posts)

    # @app.route('/forum')
    # def redirect_to_forum():
        # Redirect to the forum application (change the URL as needed)
        return redirect('http://localhost:5004/')

@app.route("/update_part/<int:PartID>", methods=['POST'])
def update_part(PartID):
    if request.method == 'POST':
        if (not db.session.scalars(db.select(Parts).filter_by(PartID=PartID).limit(1)).first()):
            return jsonify(
                {
                    "code": 400,
                    "data": {
                        "partID": PartID
                    },
                    "message": "Part does not exist."
                }
            ), 400

        data = request.form.to_dict()

        print(PartID)
        print(data)

        try:
            db.session.query(Parts).filter_by(PartID=PartID).update(data)
            db.session.commit()
        except Exception as e:
            return jsonify(
                {
                    "code": 500,
                    "data": {
                        "partID": PartID
                    },
                    "message": f"An error occurred while updating the part: {str(e)}"
                }
            ), 500
        
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
                    photo_blob = bucket.blob(f"{PartID}/{photo.filename}")
                    
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

        return redirect(url_for('seller_product_listing'))
    

# Display all carparts
def display_all_parts(parts_data):
    # Render the template and pass data to it
    return render_template('template.html', parts=parts_data)

# Display selected carpart
def display_part(part):
    return render_template('product.html', part=part)

@app.route('/add')
def store_page():
    return render_template('add.html')

if __name__ == '__main__':
    app.run(port=5002, debug=True)
