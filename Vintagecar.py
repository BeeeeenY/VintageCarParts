from flask import Flask, request, jsonify, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import update
from datetime import datetime
import firebase_admin
from firebase_admin import credentials, storage
import datetime

cred = credentials.Certificate("./serviceAccountKey.json")
firebase_admin.initialize_app(cred, {'storageBucket': 'esdfirebase-2fe43.appspot.com'})
bucket = storage.bucket()


app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root@localhost:3306/products'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.config['SQLALCHEMY_BINDS'] = {
    'users': 'mysql+mysqlconnector://root@localhost:3306/users',
    'listing': 'mysql+mysqlconnector://root@localhost:3306/listing'
}

db = SQLAlchemy(app)


class Parts(db.Model):
    __tablename__ = 'parts'

    PartID = db.Column(db.Integer, primary_key=True, autoincrement=True)
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

    def __init__(self, Name, AuthenticationNum, Category, Description, Price, QuantityAvailable, Location, Brand, Model, Status):
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

    def json(self):
        return {"PartID": self.PartID, "Name": self.Name, "AuthenticationNum": self. AuthenticationNum, "Category": self.Category, 
                "Description": self.Description, "Price": self.Price, "QuantityAvailable": self.QuantityAvailable, "Location": self.Location, 
                "Brand": self.Brand, "Model": self.Model, "Brand": self.Model, "Status": self.Status}

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
    

class Listing(db.Model):
    __bind_key__ = 'listing'
    __tablename__ = 'Listing'  # Ensure table name matches the one in your database

    PostID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    PartID = db.Column(db.Integer)
    UserID = db.Column(db.Integer)
    Content = db.Column(db.String(255))
    PostDate = db.Column(db.DateTime)

    def __init__(self, PartID, UserID, Content, PostDate):
        self.PartID = PartID
        self.UserID = UserID
        self.Content = Content
        self.PostDate = PostDate

    def json(self):
        return {"PostID": self.PostID, "PartID": self.PartID, "UserID": self.UserID, "Content": self.Content, "PostDate": self.PostDate}

class Comments(db.Model):
    __bind_key__ = 'listing'
    __tablename__ = 'Comments'

    CommentID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    PostID = db.Column(db.Integer)
    UserID = db.Column(db.Integer)
    Content = db.Column(db.Text)
    CommentDate = db.Column(db.DateTime)


    def __init__(self, PostID, UserID, Content, CommentDate):
        self.PostID = PostID
        self.UserID = UserID
        self.Content = Content
        self.CommentDate = CommentDate

    def json(self):
        return {"CommentID": self.CommentID, "PostID": self.PostID, "UserID": self.UserID, "Content": self.Content, "CommentDate": self.CommentDate}
    
@app.route("/")
def get_all_posts():
    posts_data = []  # List to hold data for each post

    # Fetch all posts
    posts = db.session.query(Listing).all()

    for post in posts:
        part_id = post.PartID
        user_id = post.UserID

        # Fetch user name for the current post
        user_name = db.session.query(Users.Name).filter(Users.UserID == user_id).scalar()

        # Fetch part details for the current post
        part_details = db.session.query(Parts).filter(Parts.PartID == part_id).first()

        part_id_str = str(part_id)

        print(part_id_str)

        # Get a reference to the folder
        folder_prefix = part_id_str + '/'

        # Retrieves all the files within the folder specified by folder_prefix.
        blobs = bucket.list_blobs(prefix=folder_prefix)

        # Initialize first_picture_url
        first_picture_url = None

        # Define a distant future timestamp
        future_timestamp = datetime.datetime.utcnow() + datetime.timedelta(days=3650)

        for blob in blobs:
            first_picture_url = blob.generate_signed_url(expiration=future_timestamp)  # URL expiration time in seconds (adjust as needed)
            print("URL of the first picture:", first_picture_url)
            break  # Stop after retrieving the first file's URL

        if first_picture_url is None:
            print("No files found.")

    
        if part_details:
            # Create a dictionary to hold post data
            post_data = {
                "PartID": part_details.PartID,
                "ProductName": part_details.Name,
                "Description": part_details.Description,
                "Price": part_details.Price,
                "Brand": part_details.Brand,
                "Model": part_details.Model,
                "UserName": user_name,
                "Pic": first_picture_url  # Pass the download URL to the HTML template
            }

            posts_data.append(post_data)  # Add post data to the list

    if posts_data:
        # Return the list of post data as JSON response
        return display_all_posts(posts_data)
    
    else:
        return jsonify(
            {
                "code": 404,
                "message": "There are no posts."
            }
        ), 404

@app.route("/<int:PostID>")
def find_by_postID(PostID):
    post = db.session.scalars(db.select(Listing).filter_by(PostID=PostID).limit(1)).first()

    part_id = post.PartID
    user_id = post.UserID

    # Fetch user name for the current post
    user_name = db.session.query(Users.Name).filter(Users.UserID == user_id).scalar()

    # Fetch part details for the current post
    part_details = db.session.query(Parts).filter(Parts.PartID == part_id).first()

    comments = db.session.scalars(db.select(Comments).filter_by(PostID=PostID)).all()


    if part_details:
        # Create a dictionary to hold post data
        post = {
            "ProductName": part_details.Name,
            "Description": part_details.Description,
            "Price": part_details.Price,
            "UserName": user_name,
            "Brand": part_details.Brand,
            "Model": part_details.Model,
            "Status": part_details.Status,
            "Comments": comments
            }


    if post:
        return display_post(post)

    return jsonify(
        {
            "code": 404,
            "message": "Post not found."
        }
    ), 404



@app.route("/create_part", methods=['POST'])
def create_part():
    name = request.form.get('Name')
    if request.form.get('AuthenticationNum'):
        auth_num = request.form.get('AuthenticationNum')
    else:
        auth_num = ""  
    category = request.form.get('Category')
    if request.form.get('Description'):
        description = request.form.get('Description') 
    else:
        description = ""  
    price = float(request.form.get('Price'))
    quantity_available = int(request.form.get('QuantityAvailable'))
    if request.form.get('Location'):
        location = request.form.get('Location') 
    else:
        location = ""
    if request.form.get('Brand'):
        brand = request.form.get('Brand')
    else:
        brand = "" 
    if request.form.get('Model'):
        model = request.form.get('Model')
    else:
        model = "" 
    if request.form.get('AddInfo'):
        add_info = request.form.get('AddInfo')
    else:
        add_info = "" 
    status = "Available"

    if not name or not category or not price or not quantity_available:
        return 'Missing form data.', 400

    part = Parts(Name=name, AuthenticationNum = auth_num, Category=category, Description=description, Price=price, 
                 QuantityAvailable=quantity_available, Location=location, Brand = brand, Model = model, Status = status)
    
    try:
        db.session.add(part)
        db.session.commit()
        
    except Exception as e:
        return jsonify({
            "code": 500,
            "message": f"An error occurred creating the part: {str(e)}"
        }), 500
    

    part_id = part.PartID
    print(part_id)
    listing = Listing(part_id, 3, add_info, datetime.datetime.now())
    
    try:
        db.session.add(listing)
        db.session.commit()

    except Exception as e:
        return jsonify({
            "code": 500,
            "message": f"An error occurred creating the post: {str(e)}"
        }), 500

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
                photo_blob = bucket.blob(f"{part_id}/{photo.filename}")
                
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

@app.route("/listing")
def seller_product_listing():
    parts_data = []  # List to hold data for each post

    # Fetch all posts
    part_ids = db.session.query(Listing.PartID).filter(Listing.UserID == 3).all()

    for part_id in part_ids:
        part_id = part_id[0]  # Extract PartID from tuple

        # Fetch all part details for the part_id
        part_details = db.session.query(Parts).filter(Parts.PartID == part_id).first()

        part_id_str = str(part_id)

        print(part_id_str)

        # Get a reference to the folder
        folder_prefix = part_id_str + '/'

        # Retrieves all the files within the folder specified by folder_prefix.
        blobs = bucket.list_blobs(prefix=folder_prefix)

        # Initialize first_picture_url
        first_picture_url = None

        # Define a distant future timestamp
        future_timestamp = datetime.datetime.utcnow() + datetime.timedelta(days=3650)

        for blob in blobs:
            first_picture_url = blob.generate_signed_url(expiration=future_timestamp)  # URL expiration time in seconds (adjust as needed)
            print("URL of the first picture:", first_picture_url)
            break  # Stop after retrieving the first file's URL

        if first_picture_url is None:
            print("No files found.")

    
        if part_details:
            # Create a dictionary to hold post data
            part_data = {
                "PartID": part_details.PartID,
                "Name": part_details.Name,
                "Qty": part_details.QuantityAvailable,
                "Pic": first_picture_url  # Pass the download URL to the HTML template
            }

            parts_data.append(part_data)  # Add post data to the list

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
    AddInfo = db.session.query(Listing.Content).filter(Listing.PartID == part_id).first()[0]

    if part_details:
        # Create a dictionary to hold post data
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
            "AddInfo": AddInfo
            }

    if part:
        return render_template('update.html', part = part)

    return jsonify(
        {
            "code": 404,
            "message": "Part not found."
        }
    ), 404
    

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

        # Remove keys that are not valid column names in the Parts table
        valid_column_names = ['Name', 'AuthenticationNum', 'Category', 'Description', 'Price', 'QuantityAvailable', 'Location', 'Brand', 'Model']
        update_parts_data = {key: value for key, value in data.items() if key in valid_column_names}

        try:
            db.session.query(Parts).filter_by(PartID=PartID).update(update_parts_data)
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

        try:
            db.session.query(Listing).filter_by(PartID=PartID).update({'Content': data['AddInfo']})
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
    
    
@app.route("/carparts/<int:PartID>", methods=['DELETE'])
def delete_part(PartID):
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

    part = db.session.scalars(db.select(Parts).filter_by(PartID=PartID).limit(1)).first()

    try:
        db.session.delete(part)
        db.session.commit()

    except Exception as e:
        return jsonify(
            {
                "code": 500,
                "data": {
                    "partID": PartID
                },
                "message": f"An error occurred while deleting the part: {str(e)}"
            }
        ), 500

    return jsonify(
        {
            "code": 201,
            "message": f"Part with ID {PartID} has been successfully deleted."
        }
    ), 201

# Display all carparts
def display_all_posts(posts_data):
    # Render the template and pass data to it
    return render_template('template.html', posts=posts_data)

# Display selected carpart
def display_post(post):
    return render_template('product.html', post=post)

@app.route('/store')
def store_page():
    return render_template('store.html')

if __name__ == '__main__':
    app.run(port=5000, debug=True)
