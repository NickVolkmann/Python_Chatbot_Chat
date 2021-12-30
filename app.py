from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_socketio import SocketIO, join_room, leave_room, emit
from flask_session import Session

from datetime import datetime
import time

from Analytical_Chatbot.chat import ana_chat
from Emotional_Chatbot.chat import emo_chat


app = Flask(__name__)
app.debug = True
app.config['SECRET_KEY'] = 'secret'
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)
socketio = SocketIO(app, manage_session=False)

loggerInformation = []

def logger_function():
    with open('activity_information.txt', 'w') as f:
        for information in loggerInformation:
            f.write(f"{information}\n")

def ana_chatbot(message):
    bot_response = ana_chat(message)
    return bot_response

def emo_chatbot(message):
    bot_response = emo_chat(message)
    return bot_response

@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')

@app.route('/chat', methods=['GET', 'POST'])
def chat():
    if(request.method=='POST'):
        username = request.form['username']
        room = "username"
        #Store the data in session
        session['username'] = username
        session['room'] = room
        if session.get('username') == "Nick":
            return render_template('chatcsa.html', session = session)
        else:
            return render_template('chat.html', session = session)
    else:
        if session.get('username') is not None:
            return render_template('chat.html', session = session)
        else:
            return redirect(url_for('index'))

@socketio.on('join', namespace='/chat')
def join(message):
    room = "username"
    join_room(room)
    emit('status', {'msg':  session.get('username') + ' has entered the room.'}, room=room)
    if session.get('username') == "Nick":
        emit('status_csa_connected', {'msg': "You" + ' has entered the room.'}, room=room)
        loggerInformation.append(datetime.now().strftime("%d/%m/%Y %H:%M:%S") + "=" + session.get('username') + ":" + ' has entered the room.')
        logger_function()
    if session.get('username') != "Nick":
        emit('status_user_connected', {'msg': session.get('username') + ' has entered the room.'}, room=room)
        loggerInformation.append(datetime.now().strftime("%d/%m/%Y %H:%M:%S") + "=" + session.get('username') + ":" + ' has entered the room.')
        logger_function()

@socketio.on('text', namespace='/chat')
def text(message):
    room = "username"
    if session.get('username') != "Nick":
        emit('message', {'msg': session.get('username') + ' : ' + message['msg']}, room=room)
        loggerInformation.append(datetime.now().strftime("%d/%m/%Y %H:%M:%S") + "=" + session.get('username') + ' : ' + message['msg'])
        logger_function()
        if ana_chatbot(message['msg']) != "I do not understand...":
            emit('analytical_chatbot', {'msg': ana_chatbot(message['msg'])}, room=room)
            emit('emotional_chatbot', {'msg': emo_chatbot(message['msg'])}, room=room)
    else:
        emit('message_to_csa', {'msg': session.get('username') + ' : ' + message['msg']}, room=room)
        emit('messager', {'msg': session.get('username') + ' : ' + message['msg']}, room=room)
        loggerInformation.append(datetime.now().strftime("%d/%m/%Y %H:%M:%S") + "=" + session.get('username') + ' : ' + message['msg'])
        logger_function()

@socketio.on('send_data_to_client', namespace='/chat')
def text(message):
    room = "username"
    emit('message_to_csa', {'msg': "Nick" + ' : ' + message['msg']}, room=room)
    loggerInformation.append(datetime.now().strftime("%d/%m/%Y %H:%M:%S") + "=" + "Nick" + ' : ' + message['msg'])
    logger_function()
    emit('messager', {'msg': "Nick" + ' : ' + message['msg']}, room=room)

@socketio.on('left', namespace='/chat')
def left(message):
    room = session.get('room')
    username = session.get('username')
    leave_room(room)
    session.clear()
    emit('status', {'msg': username + ' has left the room.'}, room=room)
    loggerInformation.append(datetime.now().strftime("%d/%m/%Y %H:%M:%S") + "=" + username + ' has left the room.')
    logger_function()

if __name__ == '__main__':
    socketio.run(app)