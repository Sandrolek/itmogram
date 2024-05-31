from flask import Blueprint, Flask, request, render_template, redirect, url_for, session
from flask_login import login_required, current_user
from . import socketio

from .db_conn import *

import random
from pprint import pprint

from flask_socketio import join_room, leave_room, send

main = Blueprint('main', __name__)

chat_rooms = {}

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/profile')
@login_required
def profile():
    username = get_user_name(current_user.id)
    return render_template('profile.html', name=username)


def generate_room_code(length: int, existing_codes: list[str]) -> str:
    while True:
        code_chars = [random.choice("QWERTYUIOPASDFGHJKLZXCVBNM") for _ in range(length)]
        code = ''.join(code_chars)
        if code not in existing_codes:
            return code

@main.route('/rooms', methods=["GET", "POST"])
@login_required
def rooms():
    session.clear()

    rooms_list = [{"room_code": room_code} for room_code in get_rooms_codes()]

    if request.method == "POST":
        user_id = current_user.id
        name = get_user_name(user_id)
        create = request.form.get('create', False)
        code = request.form.get('code')
        join = request.form.get('join', False)
        if create is not False:
            room_code = generate_room_code(6, list(chat_rooms.keys()))
            new_room = {
                'members': 0,
                'messages': []
            }
            chat_rooms[room_code] = new_room
            add_room(room_code)
        else:
            # no code
            if not code:
                return render_template('rooms.html', error="Please enter a room code to enter a chat room", name=name, rooms=rooms_list)

            codes_db = get_rooms_codes()
            # invalid code
            if code not in codes_db:
                return render_template('rooms.html', error="Room code invalid", name=name, rooms=rooms_list)

            room_code = code
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
    if user_id is None or room_code is None or room_code not in get_rooms_codes():
        return redirect(url_for('main.rooms'))

    if request.method == "POST":
        if request.form.get("delete", False) is not False:
            delete_messages(room_code=room_code)

    messages = get_messages(room_code=room_code)
    return render_template('room.html', room=room_code, user=name, messages=messages)


@socketio.on('connect')
def handle_connect():
    user_id = session.get('user_id')
    room = session.get('room_code')
    name = get_user_name(user_id)
    if user_id is None or room is None:
        return
    if room not in chat_rooms:
        leave_room(room)
    join_room(room)
    send({
        "sender": "",
        "message": f"{name} has entered the chat"
    }, to=room)
    print(f"{name} has entered the chat")


@socketio.on('message')
def handle_message(payload):
    room = session.get('room_code')
    user_id = session.get('user_id')
    name = get_user_name(user_id)
    if room not in get_rooms_codes():
        return
    message = {
        "sender": name,
        "message": payload["message"]
    }
    send(message, to=room)
    add_message(text=payload["message"], user_id=user_id, room_code=room)


@socketio.on('disconnect')
def handle_disconnect():
    room = session.get("room_code")
    user_id = session.get("user_id")
    name = get_user_name(user_id)
    leave_room(room)
    if room in chat_rooms:
        send({
        "message": f"{name} has left the chat",
        "sender": ""
    }, to=room)
    print(f"{name} has left the chat")
