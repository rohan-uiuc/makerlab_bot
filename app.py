from flask import Flask, render_template
from flask_socketio import SocketIO, emit
from main import run

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)


@app.route('/')
def index():
    return render_template('index.html')


@socketio.on('message')
def handle_message(data):
    question = data['question']
    print("question: " + question)
    response = run(question)
    emit('response', {'response': response})


if __name__ == '__main__':
    socketio.run(app)
