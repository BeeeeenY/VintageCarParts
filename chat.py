# from Flask import Flask, render_template
# from flask_socketio import SocketIO, send

# app = Flask(__name__)
# app.config['SECRET'] = "secret!123"
# socketio = SocketIO(app, cors_allowed_origins="*")

# socketio.on('message')
# def handle_message(message):
#     print("Received message: " + message)
#     if message != "User connected!":
#         send(message, broadcast=True)
        
        
# @app.route('/chat')
# def index():
#     return render_template("chat.html")

# if __name__== "__main__":
#     socketio.run(app, host="192.168.50.68")
        
        

from flask import Flask, render_template
from flask_socketio import SocketIO, send
from flasgger import Swagger

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")


# Initialize flasgger 
app.config['SWAGGER'] = {
    'title': 'chat microservice API',
    'version': 1.0,
    "openapi": "3.0.2",
    'description': 'Allows renders of chat interface'
}
swagger = Swagger(app)

@socketio.on("message")
def sendMessage(message):
    send(message, broadcast=True)
    # send() function will emit a message vent by default


@app.route("/")
def message():
    """
    This route renders a chat interface.

    ---
    responses:
        200:
            description: A chat interface is rendered successfully.
    """
    return render_template("chat.html")


if __name__ == "__main__":
    app.run(debug=True)
