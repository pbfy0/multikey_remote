
from flask import Flask, render_template, session, request
from flask_socketio import SocketIO, emit
import kb

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, async_mode=None)

kb.init()

@app.route('/')
def root():
	return app.send_static_file('index.html')

@socketio.on('hello', namespace='/key')
def hello(arg):
	#print('hello')
	session['kb'] = kb.Keyboard(arg['name'])
	emit('ack', None)

@socketio.on('get_maps', namespace='/key')
def maps():
	#print('get_maps')
	k = session['kb']
	emit('maps', {'ui': k.ui_map, 'g': k.g_map})
	print(k.ui_map, k.g_map)
@socketio.on('keydown', namespace='/key')
def keydown(arg):
	#print('keydown: ' + str(arg['mask']) + ' ' + str(arg['ui']))
	session['kb'].key_down(arg['ui'], True)
	session['kb'].key_down(arg['g'], False)
@socketio.on('keyup', namespace='/key')
def keyup(arg):
	#print('keyup')
	session['kb'].key_up(arg['ui'], True)
	session['kb'].key_up(arg['g'], False)
@socketio.on('disconnect', namespace='/key')
def dc():
	session['kb'].__del__()
	del session['kb']

if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0')