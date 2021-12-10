from flask import session
from flask_socketio import emit, join_room, leave_room
from flask_login import current_user
from . import socketio


@socketio.event
def connect():
    if current_user.is_authenticated:
        print("response")
        join_room(current_user.username) #User
        emit('my_response', {'data': 'Connected', 'count': current_user.username})
    else:
        return False # not logged in

#@socketio.event
#def my_room_event(message):
#    session['receive_count'] = session.get('receive_count', 0) + 1
#    emit('my_response',
#         {'data': message['data'], 'count': session['receive_count']},
#         to=message['room'])