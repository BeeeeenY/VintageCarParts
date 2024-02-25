from flask import Flask, request, jsonify, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import update
from datetime import datetime
from sqlalchemy import ForeignKey
import firebase_admin
from firebase_admin import credentials, storage
from sqlalchemy import and_

cred = credentials.Certificate("./serviceAccountKey.json")
firebase_admin.initialize_app(cred, {'storageBucket': 'esdfirebase-2fe43.appspot.com'})
bucket = storage.bucket()


app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root@localhost:3306/orders'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.config['SQLALCHEMY_BINDS'] = {
    'products': 'mysql+mysqlconnector://root@localhost:3306/products'
}

db = SQLAlchemy(app)


class Cart(db.Model):
    __tablename__ = 'cart'

    CartID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    UserID = db.Column(db.Integer)
    OrderDate = db.Column(db.DateTime)
    Status = db.Column(db.String(255))

    def __init__(self, UserID, OrderDate, Status):
        self.UserID = UserID
        self.OrderDate = OrderDate
        self.Status = Status

    def json(self):
        return {"CartID": self.CartID, "UserID": self.UserID, "OrderDate": self.OrderDate, "Status": self.Status}

class Orderdetails(db.Model):
    __tablename__ = 'orderdetails'

    OrderDetailID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    CartID = db.Column(db.Integer)
    PartID = db.Column(db.Integer)
    Quantity = db.Column(db.Integer)
    Purchaseddate = db.Column(db.DateTime)
    Price = db.Column(db.Float)

    def __init__(self, CartID, PartID, Quantity, Purchaseddate, Price):
        self.CartID = CartID
        self.PartID = PartID
        self.CartID = Quantity
        self.Purchaseddate = Purchaseddate
        self.Price = Price

    def json(self):
        return {"OrderDetailID": self.OrderDetailID, "CartID": self.CartID, "PartID": self.PartID, "Quantity": self.Quantity, "Purchaseddate": self.Purchaseddate, "Price": self.Price}
    
class Parts(db.Model):
    __bind_key__ = 'products'
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

@app.route("/cart/<int:UserID>")
def find_by_cartID(UserID):
    cart_details = db.session.query(Cart).filter(and_(Cart.UserID == UserID, Cart.Status == "pending")).limit(1).scalar()

    if cart_details:
        CartID = cart_details.CartID
        order_details = db.session.query(Orderdetails).filter_by(CartID=CartID).all()

        cart = {}
        for order_detail in order_details:
            part_details = db.session.query(Parts).filter_by(PartID=order_detail.PartID).first()
            if part_details:
                cart_item = {
                    "ProductName": part_details.Name,
                    "Description": part_details.Description,
                    "Quantity": order_detail.Quantity,
                    "Unit Price": part_details.Price,
                    "Total Price": order_detail.Quantity * part_details.Price
                }
                cart[order_detail.OrderDetailID] = cart_item

        return display_cart(cart)

    return jsonify(
        {
            "code": 404,
            "message": "Cart not found."
        }
    ), 404

# Display cart
def display_cart(cart):
    return render_template('cart.html', cart=cart)

if __name__ == '__main__':
    app.run(port=5000, debug=True)