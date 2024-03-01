from flask import Flask, request, jsonify, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import update
from datetime import datetime
from sqlalchemy import ForeignKey
from sqlalchemy import and_


app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root@localhost:3306/orders'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.config['SQLALCHEMY_BINDS'] = {
    'products': 'mysql+mysqlconnector://root@localhost:3306/products'
}

db = SQLAlchemy(app)

class Orderdetails(db.Model):
    __tablename__ = 'orderdetails'

    OrderDetailID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    PartID = db.Column(db.Integer)
    Quantity = db.Column(db.Integer)
    Purchaseddate = db.Column(db.DateTime)
    Price = db.Column(db.Float)
    SellerID = db.Column(db.Integer)
    Status = db.Column(db.String(255))
    BuyerID = db.Column(db.Integer)

    def __init__(self, PartID, Quantity, Purchaseddate, Price, SellerID, Status, BuyerID):
        self.PartID = PartID
        self.CartID = Quantity
        self.Purchaseddate = Purchaseddate
        self.Price = Price
        self.SellerID = SellerID
        self.Status = Status
        self.BuyerID = BuyerID

    def json(self):
        return {"OrderDetailID": self.OrderDetailID, "PartID": self.PartID, "Quantity": self.Quantity, "Purchaseddate": self.Purchaseddate, "Price": self.Price, "SellerID": self.SellerID, "Status": self.Status, "BuyerID": self.BuyerID}
    
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

@app.route("/seller/<int:SellerID>")
def find_by_SellerID(SellerID):
    order_details = db.session.query(Orderdetails).filter_by(SellerID=SellerID).all()

    if order_details:
        pending_orders = []
        packed_orders = []
        shipped_orders = []
        for order_detail in order_details:
            part_details = db.session.query(Parts).filter_by(PartID=order_detail.PartID).first()
            if part_details:
                order_item = {
                    "BuyerID": order_detail.BuyerID,
                    "Purchaseddate": order_detail.Purchaseddate,
                    "ProductName": part_details.Name,
                    "Quantity": order_detail.Quantity,
                    "UnitPrice": part_details.Price,
                    "TotalPrice": order_detail.Price
                }

                if order_detail.Status == "Pending":
                    pending_orders.append(order_item)
                elif order_detail.Status == "Packed":
                    packed_orders.append(order_item)
                elif order_detail.Status == "Shipped":
                    shipped_orders.append(order_item)

        return render_template('seller.html', pending_orders=pending_orders, packed_orders=packed_orders, shipped_orders=shipped_orders)

    return jsonify(
        {
            "code": 404,
            "message": "Order not found."
        }
    ), 404

if __name__ == '__main__':
    app.run(port=5000, debug=True)