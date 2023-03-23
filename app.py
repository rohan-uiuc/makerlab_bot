from flask import Flask, render_template
from flask_socketio import SocketIO, emit
from flask_cors import cross_origin, CORS
from main import run
import threading

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='gevent')
cors = CORS(app)

thread_lock = threading.Lock()
thread_count = 0

@app.route('/')
def index():
    return render_template('index.html')


@socketio.on('message')
def handle_message(data):
    global thread_count

    with thread_lock:
        if thread_count >= 4:
            emit('response', {'response': 'Server is busy. Please try again later.'})
            return
        else:
            thread_count += 1

    question = data['question']
    print("question: " + question)
    response = run(question)

    with thread_lock:
        thread_count -= 1

    emit('response', {'response': response})


if __name__ == '__main__':
    socketio.run(app, host="0.0.0.0", port=7860)
