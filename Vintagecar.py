from flask import Flask, request, jsonify, render_template, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
import firebase_admin
from firebase_admin import credentials, storage
import datetime as dt
import requests
from os import environ
from flasgger import Swagger

cred = credentials.Certificate("./serviceAccountKey.json")
firebase_admin.initialize_app(cred, {'storageBucket': 'esdfirebase-2fe43.appspot.com'})
bucket = storage.bucket()

app = Flask(__name__)

app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

# app.config['SQLALCHEMY_DATABASE_URI'] = environ.get('dbURL')
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root@localhost:3306/products'
app.config["SQLALCHEMY_DATABASE_URI"] = (
    environ.get("dbURL") or "mysql+mysqlconnector://root:root@localhost:3306/products"
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize flasgger 
app.config['SWAGGER'] = {
    'title': 'vintagecar microservice API',
    'version': 1.0,
    "openapi": "3.0.2",
    'description': 'Allows creating, retrieving, updating, and deleting car parts'
}
swagger = Swagger(app)

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

@app.route("/", methods=["GET","POST"])
def get_all_parts():
    """
    Get all car parts
    ---
    responses:
        200:
            description: Return all car parts
        404:
            description: No car parts 

    """
    search_query = request.args.get('search')
    if search_query == None:
        search_query = ""
    print(search_query)

    parts_data = []  # List to hold data for each part
    search_data = []

    # Fetch user ID of user logged in
    loggedin_user_id = session.get('loggedin_user_id')
    print(loggedin_user_id)

    # Fetch all parts
    parts = db.session.query(Parts).all()

    for part in parts:
        part_id = part.PartID
        user_id = part.UserID
        
        if int(loggedin_user_id) != user_id:
            print(user_id)

            get_username_url = 'http://host.docker.internal:5004/get_username'
            get_username_params = {'user_id': user_id}
            get_username_response = requests.get(get_username_url, params=get_username_params)

            if get_username_response.status_code == 200:
                # Get the username from the response if needed
                username = get_username_response.json().get('username')
                print("Username:", username)

            part_id_str = str(part_id)

            # Get a reference to the folder
            folder_prefix = 'parts/' + part_id_str + '/'

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
                    "UserName": username,
                    "Pic": first_picture_url,  # Pass the download URL to the HTML template
                    "Status": part.Status,
                }
                
                if search_query in part.Name or search_query in part.Model or search_query in part.Brand:
                    print(search_query)
                    search_data.append(part_data)  # Add part data to the list
                else:
                    parts_data.append(part_data)

    print(parts_data)
    print(search_data)

    if search_data:
        return display_all_parts(search_data)
    
    elif search_data == [] and parts_data != []:
        return render_template("template.html", data="There are no search results.")
    
    elif parts_data:
        # Return the list of part data as JSON response
        return display_all_parts(parts_data)
    
    else:
        return jsonify(
            {
                "code": 404,
                "message": "There are no parts."
            }
        ), 404

# http://127.0.0.1:5002/<PartID> to render product.html to view product details.    
@app.route("/<int:PartID>")
def find_by_partID(PartID):
    """
    Get a car part by its PartID
    ---
    parameters:
        -   in: path
            name: PartID
            required: true
    responses:
        200:
            description: Return the car part with the specified PartID
        404:
            description: No car part with the specified PartID found
    """
    buyer_id = session.get('loggedin_user_id')
    print(buyer_id)

    part = db.session.scalars(db.select(Parts).filter_by(PartID=PartID).limit(1)).first()

    user_id = part.UserID

    # Fetch user name for the current part
    get_username_url = 'http://host.docker.internal:5004/get_username'
    get_username_params = {'user_id': user_id}
    get_username_response = requests.get(get_username_url, params=get_username_params)

    if get_username_response.status_code == 200:
        # Get the username from the response if needed
        username = get_username_response.json().get('username')
        print("Username:", username)

    # Fetch part details for the current part
    part_details = db.session.query(Parts).filter(Parts.PartID == PartID).first()

    part_id_str = str(PartID)

    # Get a reference to the folder
    folder_prefix = "parts/" + part_id_str + '/'
    
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
            "UserName": username,
            "Brand": part_details.Brand,
            "Model": part_details.Model,
            "Status": part_details.Status,
            "Pics": pic_arr,
            "Comments": comments,
            "BuyerID": buyer_id,
            "SellerID":user_id
            }


    if part:
        return display_part(part)

    return jsonify(
        {
            "code": 404,
            "message": "Part not found."
        }
    ), 404

@app.route("/part")
def find_part_details():
    """
    Get car part details
    ---
    responses:
        200:
            description: Return car part details
        404:
            description: No car part details found
    """
    partid = request.args.get('partid')
    part = db.session.scalars(db.select(Parts).filter_by(PartID=partid).limit(1)).first()
    
    if part:
        # Create a dictionary to hold part data
        part = {
            "PartID": partid,
            "ProductName": part.Name,
            "Description": part.Description,
            "Price": part.Price,
            "QuantityAvailable": part.QuantityAvailable,
            "Brand": part.Brand,
            "Model": part.Model,
            "Status": part.Status
            }
        
    return jsonify(part_details=part)

@app.route("/listing")
def seller_product_listing():
    """
    Get listings
    ---
    responses:
        200:
            description: Return listings
        404:
            description: No listings found
    """
    search_query = request.args.get('search')
    if search_query == None:
        search_query = ""
    print(search_query)

    parts_data = []  # List to hold data for each parts
    search_data = []

    # Fetch user ID of user logged in
    loggedin_user_id = session.get('loggedin_user_id')
    
    # Fetch all parts
    part_details = db.session.query(Parts).filter(Parts.UserID == loggedin_user_id).all()

    for part in part_details:
        part_id = part.PartID

        part_id_str = str(part_id)

        print(part_id_str)

        # Get a reference to the folder
        folder_prefix = 'parts/' + part_id_str + '/'

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

            if search_query in part.Name:
                search_data.append(part_data)  # Add part data to the list
            else:
                parts_data.append(part_data)

    if search_data:
        return render_template('productlisting.html', parts = search_data)

    elif search_data == [] and parts_data != []:
        return render_template("productlisting.html", data="There are no search results.")
    
    elif parts_data:
        # Return the list of part data as JSON response
        return render_template('productlisting.html', parts = parts_data)
    
    else:
        return render_template('productlisting.html', data="Looks like you haven't posted any car parts yet. Click on the yellow button below to add car parts for sale to potential buyers!")

@app.route("/update")
def update_part_page():
    """
    Update part 
    ---
    responses:
        200:
            description: Part updated
        404:
            description: Part not found
    """
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
    

@app.route("/update_part/<int:PartID>", methods=['POST'])
def update_part(PartID):
    """
    Update a car part by its PartID
    ---
    parameters:
        -   in: path
            name: PartID
            required: true
    responses:
        200:
            description: Car part with the specified PartID updated
        404:
            description: No car part with the specified PartID found
    """
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
                    photo_blob = bucket.blob(f"parts/{PartID}/{photo.filename}")
                    
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

@app.route('/chat')
def chat_page():
    return render_template('chat.html')


# if __name__ == '__main__':
#     app.run(port=5002, debug=True)
if __name__ == '__main__':
    app.run(host='0.0.0.0',port=5002, debug=True)
