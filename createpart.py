from flask import Flask, request, jsonify, session, redirect
from flask_sqlalchemy import SQLAlchemy
import firebase_admin
from firebase_admin import credentials, storage
import datetime as dt

cred = credentials.Certificate("./serviceAccountKey.json")
firebase_admin.initialize_app(cred, {'storageBucket': 'esdfirebase-2fe43.appspot.com'})
bucket = storage.bucket()

app = Flask(__name__)

app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root@localhost:3306/products'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

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
        return redirect(redirect_url)

if __name__ == '__main__':
    app.run(port=5003, debug=True)
