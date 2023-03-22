from flask import Flask, render_template
from flask_socketio import SocketIO, emit
from flask.ext.cors import cross_origin, CORS
from main import run

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, cors_allowed_origins="*")
cors = CORS(app)

@app.route('/')
def index():
    return render_template('index.html')


@socketio.on('message')
@cross_origin
def handle_message(data):
    question = data['question']
    print("question: " + question)
    response = run(question)
    emit('response', {'response': response})


if __name__ == '__main__':
    socketio.run(app, allow_unsafe_werkzeug=True)
