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

app.config["SQLALCHEMY_DATABASE_URI"] = (
    environ.get("dbURL") or "mysql+mysqlconnector://root@localhost:3306/products"
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

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

    parts_data = []
    search_data = []

    # Fetch user ID of user logged in
    loggedin_user_id = session.get('loggedin_user_id')
    print(loggedin_user_id)

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
                username = get_username_response.json().get('username')
                print("Username:", username)

            part_id_str = str(part_id)

            folder_prefix = 'parts/' + part_id_str + '/'

            blobs = bucket.list_blobs(prefix=folder_prefix)

            first_picture_url = None

            future_timestamp = dt.datetime.utcnow() + dt.timedelta(days=3650)

            for blob in blobs:
                first_picture_url = blob.generate_signed_url(expiration=future_timestamp) 
                print("URL of the first picture:", first_picture_url)
                break

            if first_picture_url is None:
                print("No files found.")

            if part:
                part_data = {
                    "PartID": part.PartID,
                    "ProductName": part.Name,
                    "Description": part.Description,
                    "Price": part.Price,
                    "Brand": part.Brand,
                    "Model": part.Model,
                    "UserName": username,
                    "Pic": first_picture_url,
                    "Status": part.Status,
                }
                
                if search_query in part.Name or search_query in part.Model or search_query in part.Brand:
                    print(search_query)
                    search_data.append(part_data)
                else:
                    parts_data.append(part_data)

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

# Car Parts Details
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

    part_details = db.session.query(Parts).filter(Parts.PartID == PartID).first()

    if part_details:
        user_id = part_details.UserID
        
        get_username_url = 'http://host.docker.internal:5004/get_username'
        get_username_params = {'user_id': user_id}
        get_username_response = requests.get(get_username_url, params=get_username_params)

        if get_username_response.status_code == 200:
            username = get_username_response.json().get('username')
        else:
            username = "Unknown"
        
        comments = db.session.scalars(db.select(Comments).filter_by(PartID=PartID)).all()

        part_id_str = str(PartID)
        folder_prefix = "parts/" + part_id_str + '/'
        blobs = bucket.list_blobs(prefix=folder_prefix)
        future_timestamp = dt.datetime.utcnow() + dt.timedelta(days=3650)
        pic_arr = [blob.generate_signed_url(expiration=future_timestamp) for blob in blobs]

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
            "Comments": [],
            "BuyerID": buyer_id,
            "SellerID": user_id
        }
        
        for comment in comments:
            get_comment_username_params = {'user_id': comment.UserID}
            get_comment_username_response = requests.get(get_username_url, params=get_comment_username_params)

            if get_comment_username_response.status_code == 200:
                comment_username = get_comment_username_response.json().get('username')
            else:
                comment_username = "Unknown"
            
            part["Comments"].append({
                "UserID": comment.UserID,
                "UserName": comment_username,
                "CommentDate": comment.CommentDate,
                "Content": comment.Content
            })

        return display_part(part)

    return jsonify(
        {
            "code": 404,
            "message": "Part not found."
        }
    ), 404

@app.route('/cart')
def cart():
    return render_template('cart.html')

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

    parts_data = []
    search_data = []

    loggedin_user_id = session.get('loggedin_user_id')
    
    part_details = db.session.query(Parts).filter(Parts.UserID == loggedin_user_id).all()

    for part in part_details:
        part_id = part.PartID

        part_id_str = str(part_id)

        print(part_id_str)

        folder_prefix = 'parts/' + part_id_str + '/'

        blobs = bucket.list_blobs(prefix=folder_prefix)

        first_picture_url = None

        future_timestamp = dt.datetime.utcnow() + dt.timedelta(days=3650)

        for blob in blobs:
            first_picture_url = blob.generate_signed_url(expiration=future_timestamp)
            print("URL of the first picture:", first_picture_url)
            break

        if first_picture_url is None:
            print("No files found.")

    
        if part:
            part_data = {
                "PartID": part.PartID,
                "Name": part.Name,
                "Price": part.Price,
                "Quantity": part.QuantityAvailable,
                "Status": part.Status,
                "Pic": first_picture_url
            }

            if search_query in part.Name:
                search_data.append(part_data)
            else:
                parts_data.append(part_data)

    if search_data:
        return render_template('productlisting.html', parts = search_data)

    elif search_data == [] and parts_data != []:
        return render_template("productlisting.html", data="There are no search results.")
    
    elif parts_data:
        return render_template('productlisting.html', parts = parts_data)
    
    else:
        return render_template('productlisting.html', data="Looks like you haven't posted any car parts yet. Click on the yellow button below to add car parts for sale to potential buyers!")

@app.route("/update")
def update_part_page():
    """
    Update Part
    ---
    parameters:
        -   name: part_id
            in: query
            type: integer
            required: true
            description: ID of the part to update.
    responses:
        200:
            description: Part updated successfully.
        404:
            description: Part not found.
    """
    part_id = request.args.get('part_id')
    part_details = db.session.query(Parts).filter(Parts.PartID == part_id).first()

    if part_details:
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
        QuantityAvailable = int(data.get('QuantityAvailable'))

        print(PartID)
        print(data)

        try:
            db.session.query(Parts).filter_by(PartID=PartID).update(data)
            db.session.commit()

            if QuantityAvailable != 0:
                db.session.query(Parts).filter_by(PartID=PartID).update({'Status': 'Available'})
                db.session.commit()
            
            if QuantityAvailable == 0:
                db.session.query(Parts).filter_by(PartID=PartID).update({'Status': 'Sold'})
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
            photos = request.files.getlist("file")

            photos = [photo for photo in photos if photo.filename]
            
            if photos:
                print("User uploaded photos, proceeding with upload")
                upload_results = []

                for photo in photos:
                    photo_blob = bucket.blob(f"parts/{PartID}/{photo.filename}")
                    
                    try:
                        photo_blob.upload_from_file(photo)
                        upload_results.append(True)
                    except Exception as e:
                        upload_results.append(False)
                        print(f"Error uploading photo: {e}")

                try:
                    all(upload_results)
                    print("Photos uploaded successfully!")
                except Exception as e:
                    print("Failed to upload all photos. Please try again.")

        return redirect(url_for('seller_product_listing'))
    
@app.route('/review/<int:PartID>/<int:OrderID>')
def review_page(PartID, OrderID):
    return render_template('review.html', PartID = PartID, OrderID = OrderID)

@app.route('/create_review/<int:PartID>/<int:OrderID>', methods=['POST'])
def create_review(PartID, OrderID):
    Content = request.form.get('content')
    print(Content)
    loggedin_user_id = session.get('loggedin_user_id')
    comment = Comments(PartID = PartID, UserID = loggedin_user_id, Content = Content, CommentDate = dt.datetime.now())

    try:
        db.session.add(comment)
        db.session.commit()
        
    except Exception as e:
        return jsonify({
            "code": 500,
            "message": f"An error occurred creating the comment: {str(e)}"
        }), 500

    redirect_url = f'http://127.0.0.1:5005/review/{OrderID}'
    return redirect(redirect_url)

@app.route("/reduce_quantity")
def reduce_quantity():
    PartID = request.args.get('PartID')
    Quantity = request.args.get('Quantity')
    part = db.session.query(Parts).filter(Parts.PartID == PartID).first()
    part.QuantityAvailable -= int(Quantity)
    if part.QuantityAvailable == 0:
        part.Status = 'Sold'
    db.session.commit()
    return 'success', 200

def display_all_parts(parts_data):
    return render_template('template.html', parts=parts_data)

def display_part(part):
    return render_template('product.html', part=part)

@app.route('/add')
def store_page():
    return render_template('add.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0',port=5002, debug=True)
