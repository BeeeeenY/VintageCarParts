from flask import Flask, render_template
from flask_socketio import SocketIO, send
from flasgger import Swagger

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

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
    app.run(host='0.0.0.0', port= 5007, debug=True)