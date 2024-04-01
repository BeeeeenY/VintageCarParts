from flask import Flask, request, jsonify, render_template, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
import requests
from datetime import datetime
from os import environ
from flasgger import Swagger
import pytz

app = Flask(__name__)

app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

app.config["SQLALCHEMY_DATABASE_URI"] = (
    environ.get("dbURL") or "mysql+mysqlconnector://root@localhost:3306/orders"
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


# Initialize flasgger 
app.config['SWAGGER'] = {
    'title': 'order microservice API',
    'version': 1.0,
    "openapi": "3.0.2",
    'description': 'Allows retrieval of orders, update order status and creating orders'
}
swagger = Swagger(app)

class Orderdetails(db.Model):
    __tablename__ = 'orderdetails'

    OrderDetailID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    PartID = db.Column(db.Integer)
    Quantity = db.Column(db.Integer)
    Purchaseddate = db.Column(db.DateTime)
    Receivedate = db.Column(db.DateTime, nullable=True)
    Price = db.Column(db.Float)
    SellerID = db.Column(db.Integer)
    Status = db.Column(db.String(255))
    BuyerID = db.Column(db.Integer)
    ShippingAddress = db.Column(db.String(255))

    def __init__(self, PartID, Quantity, Purchaseddate, Price, SellerID, Status, BuyerID, Receivedate=None, ShippingAddress=None):
        self.PartID = PartID
        self.Quantity = Quantity
        self.Purchaseddate = Purchaseddate
        self.Receivedate = Receivedate
        self.Price = Price
        self.SellerID = SellerID
        self.Status = Status
        self.BuyerID = BuyerID
        self.ShippingAddress = ShippingAddress

    def json(self):
        return {"OrderDetailID": self.OrderDetailID, "PartID": self.PartID, "Quantity": self.Quantity, "Purchaseddate": self.Purchaseddate, 
                "Receivedate": self.Receivedate, "Price": self.Price, "SellerID": self.SellerID, "Status": self.Status, 
                "BuyerID": self.BuyerID, "ShippingAddress": self.ShippingAddress}
        
# Order Management for Seller
@app.route("/seller")
def find_by_SellerID():
    loggedin_user_id = session.get('loggedin_user_id')

    order_details = db.session.scalars(db.select(Orderdetails).filter_by(SellerID=loggedin_user_id)).all()

    if order_details:
        pending_orders = []
        packing_orders = []
        shipping_orders = []
        for order_detail in order_details:
            partid = order_detail.PartID

            get_part_url = 'http://host.docker.internal:5002/part'
            get_part_params = {'partid': partid}
            get_part_response = requests.get(get_part_url, params=get_part_params)

            if get_part_response.status_code == 200:
                part_details = get_part_response.json().get('part_details')

            if part_details:
                order_item = {
                    "OrderID": order_detail.OrderDetailID,
                    "BuyerID": order_detail.BuyerID,
                    "Purchaseddate": order_detail.Purchaseddate,
                    "ProductName": part_details['ProductName'],
                    "Quantity": order_detail.Quantity,
                    "UnitPrice": order_detail.Price,
                    "TotalPrice": order_detail.Price*order_detail.Quantity
                }

                if order_detail.Status == "Pending":
                    pending_orders.append(order_item)
                elif order_detail.Status == "Packing":
                    packing_orders.append(order_item)
                elif order_detail.Status == "Shipping":
                    shipping_orders.append(order_item)

        return render_template('seller.html', pending_orders=pending_orders, packing_orders=packing_orders, shipping_orders=shipping_orders)

    else:
        return render_template('seller.html', data = "There are no items ordered.") 

# Order Details
@app.route('/order/<int:OrderDetailID>')
def order_detail(OrderDetailID):
    order = db.session.scalars(db.select(Orderdetails).filter_by(OrderDetailID=OrderDetailID).limit(1)).first()
    
    get_username_url = 'http://host.docker.internal:5004/get_username'
    get_username_params = {'user_id': order.BuyerID}
    get_username_response = requests.get(get_username_url, params=get_username_params)

    if get_username_response.status_code == 200:
            username = get_username_response.json().get('username')
    else:
            username = "Unknown"

    partid = order.PartID

    get_part_url = 'http://host.docker.internal:5002/part'
    get_part_params = {'partid': partid}
    get_part_response = requests.get(get_part_url, params=get_part_params)

    if get_part_response.status_code == 200:
        part_details = get_part_response.json().get('part_details')

    if order:
        order_detail = {
            "OrderID": order.OrderDetailID,
            "BuyerID": order.BuyerID,
            "BuyerName": username,
            "Purchaseddate": order.Purchaseddate,
            "ProductName": part_details['ProductName'],
            "ProductPrice": order.Price,
            "Quantity": order.Quantity,
            "TotalPrice": order.Price*order.Quantity
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

# Update status
@app.route('/update_status', methods=['PUT'])
def update_status():
    """
    Update the status of an order.
    ---
    tags:
      - Order
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            properties:
              orderId:
                type: integer
                description: ID of the order to update.
              status:
                type: string
                description: New status of the order.
    responses:
      200:
        description: Order status updated successfully.
      404:
        description: Order not found.
    """
    data = request.json
    order_id = data.get('orderId')
    status = data.get('status')

    order = db.session.query(Orderdetails).filter_by(OrderDetailID=order_id).first()
    if order:
        order.Status = status
        db.session.commit()
        return jsonify({'success': True}), 200
    else:
        return jsonify({'success': False, 'error': 'Order not found'}), 404

@app.route("/create_order_new")
def cart():
    return render_template('success.html')
   
@app.route("/create_order", methods=['POST'])
def create_order():

    """
    Create a new order.
    ---
    tags:
        - Order
    requestBody:
        required: true
        content:
            application/json:
                schema:
                    type: object
                    properties:
                        orders:
                            type: array
                            description: Array of orders.
                            items:
                                type: object
                                properties:
                                    BuyerID:
                                        type: integer
                                        description: ID of the user placing the order.
                                    PartID:
                                        type: integer
                                        description: ID of the part being ordered.
                                    Quantity:
                                        type: integer
                                        description: Quantity of the part being ordered.
                                    Price:
                                        type: number
                                        description: Price of the part being ordered.
                                    SellerID:
                                        type: integer
                                        description: ID of the seller.
                                    name:
                                        type: string
                                        description: Optional name of the product.
    responses:
        201:
            description: Order created successfully.
        500:
            description: An error occurred while creating the order.
    """
    try:
        orders_data = request.json.get('orders')  # Expecting a JSON array of orders
        if not orders_data:
            return jsonify({"code": 400, "message": "No order data provided"}), 400

        for order_data in orders_data:
            PartID = order_data.get('PartID')
            Quantity = order_data.get('Quantity')
            Price = order_data.get('Price')  # Assuming this is in dollars
            BuyerID = order_data.get('BuyerID')
            SellerID = order_data.get('SellerID')
            ProductName = order_data.get('name')  # opetional
            
            my_timezone = pytz.timezone('Asia/Singapore')

            current_datetime = datetime.now(my_timezone)
            
            
            order = Orderdetails(
                PartID=PartID,
                Quantity=Quantity,
                Purchaseddate=current_datetime,
                Price=Price,
                SellerID=SellerID,
                Status="Pending",
                BuyerID=BuyerID
            )
            db.session.add(order)
        
            db.session.commit()  # Commit once after all orders are added            
            
            reduce_quantity_url = 'http://host.docker.internal:5002/reduce_quantity'
            reduce_quantity_params = {'PartID': PartID, 'Quantity':Quantity}
            reduce_quantity_response = requests.get(reduce_quantity_url, params=reduce_quantity_params)

            if reduce_quantity_response.status_code != 200:
                return jsonify({"code": 500, "message": f"Failed to reduce quantity for PartID {PartID}"}), 500
            
        return jsonify({"code": 201, "message": "Orders created successfully"}), 201
    
    except Exception as e:
        db.session.rollback()  # Rollback in case of error
        return jsonify({"code": 500, "message": "An error occurred while creating the orders: " + str(e)}), 500
    
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

            get_part_url = 'http://host.docker.internal:5002/part'
            get_part_params = {'partid': partid}
            get_part_response = requests.get(get_part_url, params=get_part_params)

            if get_part_response.status_code == 200:
                # Get the username from the response if needed
                part_details = get_part_response.json().get('part_details')

            print(part_details)
            
            if part_details:
                formatted_purchase_datetime = order_detail.Purchaseddate.strftime("%Y-%m-%d %H:%M:%S")
                receive_date = order_detail.Receivedate
                expired = False
                if receive_date:
                    current_date = datetime.now()
                    difference = current_date - receive_date
                    if difference.days > 30:
                        expired = True
                    print(difference.days)
                    print(expired)
                total_price = order_detail.Quantity * part_details['Price']
                order_item = {
                    "OrderID": order_detail.OrderDetailID,
                    "SellerID": order_detail.SellerID,
                    "Purchaseddate": formatted_purchase_datetime,
                    "ProductName": part_details['ProductName'],
                    "PartID": order_detail.PartID,
                    "Quantity": order_detail.Quantity,
                    "UnitPrice": part_details['Price'],
                    "TotalPrice": total_price,
                    "Status": order_detail.Status,
                    "Expired": expired
                }
                order_items.append(order_item)
                print(order_item)

    if order_items != []:
        return render_template('buyerorders.html', orders = order_items)
    else:
        return render_template('buyerorders.html', data = "There are no items ordered.")  # Render a template indicating no orders
    
@app.route('/receive/<int:OrderID>')
def receive(OrderID):
    order = db.session.scalars(db.select(Orderdetails).filter_by(OrderDetailID=OrderID).limit(1)).first()
    if order:
        order.Status = 'Received'
        order.Receivedate = datetime.now()
        db.session.commit()

    return redirect('http://127.0.0.1:5005/buyer_order')

@app.route('/review/<int:OrderID>')
def review(OrderID):
    order = db.session.scalars(db.select(Orderdetails).filter_by(OrderDetailID=OrderID).limit(1)).first()
    if order:
        order.Status = 'Reviewed'
        db.session.commit()

    return redirect('http://127.0.0.1:5005/buyer_order')
    
if __name__ == '__main__':
    app.run(host='0.0.0.0',port=5005, debug=True)



