from flask import Flask, request, jsonify, render_template
from focus_bot import FocusBot
from focus_timer import FocusTimer
import traceback
from flask_socketio import SocketIO
import time
from threading import Thread
from focus_timer import TimerState

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")
bot = FocusBot()
timer = FocusTimer()

def background_timer():
    """Background task to emit timer updates every second"""
    last_time = time.time()
    while True:
        current_time = time.time()
        if current_time - last_time >= 1.0:
            timer_status = {
                'status': timer.get_status(),
                'is_paused': timer.is_paused,
                'state': timer.current_state.value,
                'timer_active': timer.running,
                'remaining_time': timer._calculate_remaining_time()
            }
            socketio.emit('timer_update', timer_status)
            last_time = current_time
        socketio.sleep(0.1)

@app.route('/')
def home():
    welcome_message = "Welcome to Beluga Focus Timer!\nType 'help' to see available commands\n=================================="
    return render_template('index.html', welcome_message=welcome_message)

@app.route('/chat', methods=['POST'])
def chat():
    try:
        user_message = request.json.get('message', '')
        print(f"\nUser: {user_message}")
        
        if not user_message:
            return jsonify({'response': 'Please enter a command'})
        
        response = bot.process_command(user_message.strip())
        print(f"Beluga: {response}")
        
        formatted_response = response.replace('\n', '<br>') if response else 'No response received'
        
        return jsonify({
            'response': formatted_response,
            'user_message': user_message,
            'status': 'success'
        })
        
    except Exception as e:
        error_msg = f"An error occurred: {str(e)}"
        print(error_msg)
        return jsonify({
            'response': error_msg,
            'status': 'error'
        })

@app.route('/api/start', methods=['POST'])
def start_timer():
    data = request.get_json()
    task = data.get('task', '')
    status = timer.start_focus(task)
    timer_status = {
        'status': timer.get_status(),
        'is_paused': False,
        'state': timer.current_state.value,
        'can_resume': False,
        'message': status
    }
    socketio.emit('timer_update', timer_status)
    return jsonify(timer_status)

@app.route('/api/pause', methods=['POST'])
def pause_timer():
    if timer.current_state == TimerState.IDLE:
        return jsonify({'error': 'No active timer to pause'})
    
    status = timer.pause()
    timer_status = {
        'status': timer.get_status(),
        'is_paused': True,
        'state': timer.current_state.value,
        'can_resume': True,
        'timer_active': True,
        'remaining_time': timer._calculate_remaining_time(),
        'message': status
    }
    socketio.emit('timer_update', timer_status)
    return jsonify(timer_status)

@app.route('/api/resume', methods=['POST'])
def resume_timer():
    if not timer.is_paused:
        return jsonify({'error': 'Timer is not paused'})
    
    status = timer.resume()
    timer_status = {
        'status': timer.get_status(),
        'is_paused': False,
        'state': timer.current_state.value,
        'can_resume': False,
        'timer_active': True,
        'remaining_time': timer._calculate_remaining_time(),
        'message': status
    }
    socketio.emit('timer_update', timer_status)
    return jsonify(timer_status)

@app.route('/api/stop', methods=['POST'])
def stop_timer():
    status = timer.stop()
    timer_status = {
        'status': timer.get_status(),
        'is_paused': False,
        'state': timer.current_state.value,
        'can_resume': False,
        'message': status
    }
    socketio.emit('timer_update', timer_status)
    return jsonify(timer_status)

@app.route('/api/complete', methods=['POST'])
def complete_timer():
    status = timer.complete_cycle()
    timer_status = {
        'status': timer.get_status(),
        'is_paused': False,
        'state': timer.current_state.value,
        'can_resume': False,
        'timer_active': True,
        'remaining_time': timer._calculate_remaining_time(),
        'message': status
    }
    socketio.emit('timer_update', timer_status)
    return jsonify(timer_status)

@app.route('/api/stats', methods=['GET'])
def get_stats():
    try:
        stats = timer.get_stats()
        return jsonify({
            "status": "success",
            "stats": stats
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"\nAn error occurred: {str(e)}"
        })

@app.route('/api/motivate', methods=['GET'])
def get_motivation():
    try:
        response = bot.process_command("motivate")
        return jsonify({
            "status": "success",
            "message": f"\n{response}"
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"\nAn error occurred: {str(e)}"
        })

@socketio.on('connect')
def handle_connect():
    """Start the background timer when a client connects"""
    socketio.start_background_task(background_timer)

if __name__ == '__main__':
    print("Welcome to Beluga Focus Timer!")
    print("Type 'help' to see available commands")
    print("==================================")
    print("\nStarting web interface at http://127.0.0.1:5000")
    socketio.run(app, debug=True, port=5000)