from flask import Flask, request, jsonify, session, redirect
from flask_cors import CORS, cross_origin  # Import Flask-CORS
from flask_sqlalchemy import SQLAlchemy
import firebase_admin
from firebase_admin import credentials, storage
import datetime as dt
from os import environ
from flasgger import Swagger

cred = credentials.Certificate("./serviceAccountKey.json")
firebase_admin.initialize_app(cred, {'storageBucket': 'esdfirebase-2fe43.appspot.com'})
bucket = storage.bucket()

app = Flask(__name__)
CORS(app)  # Initialize Flask-CORS

app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

# app.config['SQLALCHEMY_DATABASE_URI'] = environ.get('dbURL')
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root@localhost:3306/products'
app.config["SQLALCHEMY_DATABASE_URI"] = (
    environ.get("dbURL") or "mysql+mysqlconnector://root@localhost:3306/products"
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize flasgger 
app.config['SWAGGER'] = {
    'title': 'createpart microservice API',
    'version': 1.0,
    "openapi": "3.0.2",
    'description': 'Allows create of carparts'
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

@app.route("/create_part", methods=['POST'])
@cross_origin(origin='*', headers=['Content-Type', 'Authorization'])

def create_part():

    """
    Create Part
    ---
    tags:
        - carpart
    parameters: []
    requestBody:
        required: true
        content:
            application/x-www-form-urlencoded:
                schema:
                    type: object
                    properties:
                        Name:
                            type: string
                            description: The Name of the part
                        AuthenticationNum:
                            type: string                
                            description: The Authentication number of the part
                        Category:
                            type: string
                            description: The Category of the part   
                        Description:
                            type: string    
                            description: The Description of the part
                        Price:      
                            type: number
                            description: The Price of the part
                        QuantityAvailable:
                            type: integer
                            description: The Quantity available of the part
                        Location:
                            type: string
                            description: The Location of the part
                        Brand:
                            type: string
                            description: The Brand of the part
                        Model:
                            type: string
                            description: The Model of the part
                        AddInfo:
                            type: string
                            description: Additional information about the part
                        Status:
                            type: string            
                            description: The Status of the part 
    responses:
        302:
            description: Part created successfully.
            headers:
                Location:
                    description: URL of the created part.
                    schema:
                        type: string
                        example: "http://127.0.0.1:5002/listing"
        400:
            description: Missing form data or invalid request.
        500:
            description: An error occurred while creating the part.
    """

    if request.form.get('Name'):
        name = request.form.get('Name')
    else:
        name= ""
    if request.form.get('AuthenticationNum'):
        auth_num = request.form.get('AuthenticationNum')
    else:
        auth_num = ""  
    if request.form.get('Category'):
        category = request.form.get('Category')
    else:
        category = ""
    if request.form.get('Description'):
        description = request.form.get('Description') 
    else:
        description = ""  
    if request.form.get('Price'):
        price = float(request.form.get('Price'))
    else:
        price = ''
    if request.form.get('QuantityAvailable'):
        quantity_available = int(request.form.get('QuantityAvailable'))
    else:
        quantity_available = ''
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

    loggedin_user_id = session.get('loggedin_user_id')

    part = Parts(UserID= loggedin_user_id, Name=name, AuthenticationNum = auth_num, Category=category, Description=description, Price=price, 
                 QuantityAvailable=quantity_available, Location=location, Brand = brand, Model = model, Status = status, 
                 Content = add_info, PostDate = dt.datetime.now())
    
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
                photo_blob = bucket.blob(f"parts/{part_id}/{photo.filename}")
                
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
        
        redirect_url = 'http://127.0.0.1:5002/listing'
    
        # Redirect to the constructed URL
        return redirect(redirect_url, code=302)
    


if __name__ == '__main__':
    app.run(host='0.0.0.0',port=5003, debug=True)
