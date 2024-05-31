from flask import Blueprint, request, render_template, redirect, url_for, session
from flask_login import login_required, current_user
from . import socketio

from project.db.db_conn import *

import random

from flask_socketio import join_room, leave_room, send
import hashlib

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/profile')
@login_required
def profile():
    username = get_user_name(current_user.id)
    return render_template('profile.html', name=username)


def generate_room_code() -> str:
    m = hashlib.sha256()
    num = str(random.randint(1, 1000000))
    m.update(num.encode('utf8'))
    code = m.hexdigest()
    return code

@main.route('/rooms', methods=["GET", "POST"])
@login_required
def rooms():
    session.clear()

    rooms_list = [{"room_code": room_data["code"], "room_name": room_data["name"]} for room_data in get_rooms()]

    if request.method == "POST":
        user_id = current_user.id
        name = get_user_name(user_id)
        create = request.form.get('create', False)
        room_name = request.form.get('room_name')

        room_code = generate_room_code()
        add_room(name=room_name, code=room_code)

        # no code
        if not room_name:
            return render_template('rooms.html', error="Please enter a room code to enter a chat room", name=name, rooms=rooms_list)

        # codes_db = get_rooms_codes()
        # # invalid code
        # if code not in codes_db:
        #     return render_template('rooms.html', error="Room code invalid", name=name, rooms=rooms_list)

        session['room_code'] = room_code
        session['user_id'] = user_id
        return redirect(url_for('main.room', room_code=room_code))
    else:

        return render_template('rooms.html', rooms=rooms_list)


@main.route('/room/<room_code>', methods=['GET', 'POST'])
@login_required
def room(room_code):

    user_id = current_user.id
    session['room_code'] = room_code
    session['user_id'] = user_id

    name = get_user_name(user_id)
    room_name = get_room_name(room_code=room_code)

    room_codes = [i["code"] for i in get_rooms()]

    if user_id is None or room_code is None or room_code not in room_codes:
        return redirect(url_for('main.rooms'))

    if request.method == "POST":
        if request.form.get("delete", False) is not False:
            delete_messages(room_code=room_code)

    messages = get_messages(room_code=room_code)
    return render_template('room.html', room=room_name, user=name, messages=messages)


@socketio.on('connect')
def handle_connect():
    user_id = session.get('user_id')
    room_code = session.get('room_code')
    name = get_user_name(user_id)
    if user_id is None or room_code is None:
        return
    room_codes = [i["code"] for i in get_rooms()]
    if room_code not in room_codes:
        leave_room(room_code)
    join_room(room_code)
    send({
        "sender": "",
        "message": f"{name} has entered the chat"
    }, to=room_code)
    print(f"{name} has entered the chat")


@socketio.on('message')
def handle_message(payload):
    room_code = session.get('room_code')
    user_id = session.get('user_id')
    name = get_user_name(user_id)
    room_codes = [i["code"] for i in get_rooms()]
    if room_code not in room_codes:
        return
    message = {
        "sender": name,
        "message": payload["message"]
    }
    send(message, to=room_code)
    add_message(text=payload["message"], user_id=user_id, room_code=room_code)


@socketio.on('disconnect')
def handle_disconnect():
    room_code = session.get("room_code")
    user_id = session.get("user_id")
    name = get_user_name(user_id)
    leave_room(room)
    room_codes = [i["code"] for i in get_rooms()]
    if room_code in room_codes:
        send({
        "message": f"{name} has left the chat",
        "sender": ""
    }, to=room_code)
    print(f"{name} has left the chat")
