from flask import Flask, render_template
from flask_socketio import SocketIO, emit
from flask_cors import cross_origin, CORS
from main import run
import concurrent.futures

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, cors_allowed_origins="*")
cors = CORS(app)

executor = concurrent.futures.ThreadPoolExecutor(max_workers=4)

@app.route('/')
def index():
    return render_template('index.html')


@socketio.on('message')
def handle_message(data):
    question = data['question']
    print("question: " + question)

    future = executor.submit(run, question)
    response = future.result()

    emit('response', {'response': response})


if __name__ == '__main__':
    socketio.run(app, host="0.0.0.0", port=7860)
