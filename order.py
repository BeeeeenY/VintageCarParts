from flask import Flask, request, jsonify, render_template, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
import requests
from datetime import datetime

app = Flask(__name__)

app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

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
        self.Quantity = Quantity
        self.Purchaseddate = Purchaseddate
        self.Price = Price
        self.SellerID = SellerID
        self.Status = Status
        self.BuyerID = BuyerID

    def json(self):
        return {"OrderDetailID": self.OrderDetailID, "PartID": self.PartID, "Quantity": self.Quantity, "Purchaseddate": self.Purchaseddate, "Price": self.Price, "SellerID": self.SellerID, "Status": self.Status, "BuyerID": self.BuyerID}
    
# http://127.0.0.1:5000/seller/<SellerID> to render seller.html to manage orders.
@app.route("/seller")
def find_by_SellerID():
    loggedin_user_id = session.get('loggedin_user_id')

    order_details = db.session.query(Orderdetails).filter_by(SellerID=loggedin_user_id).all()

    if order_details:
        pending_orders = []
        packing_orders = []
        shipping_orders = []
        for order_detail in order_details:
            partid = order_detail.PartID

            get_part_url = 'http://127.0.0.1:5002/part'
            get_part_params = {'partid': partid}
            get_part_response = requests.get(get_part_url, params=get_part_params)

            if get_part_response.status_code == 200:
                # Get the username from the response if needed
                part_details = get_part_response.json().get('part_details')

            print(part_details)
                
            if part_details:
                order_item = {
                    "OrderID": order_detail.OrderDetailID,
                    "BuyerID": order_detail.BuyerID,
                    "Purchaseddate": order_detail.Purchaseddate,
                    "ProductName": part_details['ProductName'],
                    "Quantity": order_detail.Quantity,
                    "UnitPrice": part_details['Price'],
                    "TotalPrice": order_detail.Price
                }

                if order_detail.Status == "Pending":
                    pending_orders.append(order_item)
                elif order_detail.Status == "Packing":
                    packing_orders.append(order_item)
                elif order_detail.Status == "Shipped":
                    shipping_orders.append(order_item)

        return render_template('seller.html', pending_orders=pending_orders, packing_orders=packing_orders, shipping_orders=shipping_orders)

    return jsonify(
        {
            "code": 404,
            "message": "Order not found."
        }
    ), 404

# http://127.0.0.1:5000/order/<OrderDetailID> to render order.html to view order details.
# Or click [view] hyperlink in seller.html.
@app.route('/order/<int:OrderDetailID>')
def order_detail(OrderDetailID):
    order = db.session.scalars(db.select(Orderdetails).filter_by(OrderDetailID=OrderDetailID).limit(1)).first()
    if order:
        order_detail = {
            "OrderID": order.OrderDetailID,
            "BuyerID": order.BuyerID,
            "Purchaseddate": order.Purchaseddate,
            "Quantity": order.Quantity,
            "TotalPrice": order.Price
        }

        return render_template('order.html', order=order_detail)
    
    return jsonify(
        {
            "code": 404,
            "data": {
                "OrderDetailID": OrderDetailID
            },
            "message": "Order not found."
        }
    ), 404

@app.route('/update_status', methods=['PUT'])
def update_status():
    data = request.json
    order_id = data.get('orderId')
    status = data.get('status')

    # Update the status in the database
    order = db.session.query(Orderdetails).filter_by(OrderDetailID=order_id).first()
    if order:
        order.Status = status
        db.session.commit()
        return jsonify({'success': True}), 200
    else:
        return jsonify({'success': False, 'error': 'Order not found'}), 404

# To integrate with cart page.    
@app.route("/create_order", methods=['POST'])
def create_order():
    try:
        # Get form data
        UserID = request.form.get('UserID')
        PartID = request.form.get('PartID')
        Quantity = int(request.form.get('quantity'))  # Note: 'quantity' field, not 'Quantity'
        Price = float(request.form.get('Price'))
        print("Form Data:", request.form)
        
        # Get current date and time
        current_datetime = datetime.now()

        # Create a new Orderdetails instance
        orderdetails = Orderdetails(PartID=PartID, Quantity=Quantity, Purchaseddate=current_datetime.date(), Price=Price, SellerID=UserID, Status="Pending", BuyerID=1) # To change buyer id.
        db.session.add(orderdetails)
        db.session.commit()

        # Return success response
        return jsonify({
            "code": 201,
            "message": "Order created successfully."
        }), 201
    
    except Exception as e:
        # Return error response
        return jsonify({
            "code": 500,
            "message": "An error occurred while creating the order " + str(e)
        }), 500

@app.route('/buyer_order')
def buyer_orders():
    loggedin_user_id = session.get('loggedin_user_id')
    print(loggedin_user_id)

    order_items = []

    order_details = db.session.query(Orderdetails).filter_by(BuyerID = loggedin_user_id).all()
    print(order_details)
    if order_details:
        for order_detail in order_details:
            partid = order_detail.PartID

            get_part_url = 'http://127.0.0.1:5002/part'
            get_part_params = {'partid': partid}
            get_part_response = requests.get(get_part_url, params=get_part_params)

            if get_part_response.status_code == 200:
                # Get the username from the response if needed
                part_details = get_part_response.json().get('part_details')

            print(part_details)
            
            if part_details:
                formatted_datetime = order_detail.Purchaseddate.strftime("%Y-%m-%d %H:%M:%S")
                total_price = order_detail.Quantity * part_details['Price']
                order_item = {
                    "SellerID": order_detail.SellerID,
                    "Purchaseddate": formatted_datetime,
                    "ProductName": part_details['ProductName'],
                    "Quantity": order_detail.Quantity,
                    "UnitPrice": part_details['Price'],
                    "TotalPrice": total_price,
                    "Status": order_detail.Status
                }
                order_items.append(order_item)
                print(order_item)

    if order_items != []:
        return render_template('buyerorders.html', orders = order_items)
    else:
        return render_template('buyerorders.html', data = "There are no items ordered.")  # Render a template indicating no orders
    
if __name__ == '__main__':
    app.run(port=5005, debug=True)



