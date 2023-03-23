from flask import Flask, render_template
from flask_socketio import SocketIO, emit
from flask_cors import cross_origin, CORS
from main import run
import concurrent.futures

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, cors_allowed_origins="*")
cors = CORS(app)

max_workers=4
executor = concurrent.futures.ThreadPoolExecutor(max_workers)

@app.route('/')
def index():
    return render_template('index.html')


@socketio.on('message')
def handle_message(data):
    question = data['question']
    print("question: " + question)

    if executor._work_queue.qsize() >= max_workers:
        emit('response', {'response': 'Server is busy, please try again later'})
        return

    try:
        future = executor.submit(run, question)
        response = future.result()
        emit('response', {'response': response})
    except Exception as e:
        print(f"Error processing request: {str(e)}")
        emit('response', {'response': 'Server is busy. Please try again later.'})

# if __name__ == '__main__':
#     socketio.run(app, host="0.0.0.0", port=7860)

def create_app(**config_overrides):
    return app