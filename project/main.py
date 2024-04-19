from flask import Blueprint, Flask, request, render_template, redirect, url_for, session
from flask_login import login_required, current_user
from . import get_db_connection, socketio

import random
from pprint import pprint

from flask_socketio import join_room, leave_room, send

main = Blueprint('main', __name__)

chat_rooms = {}

@main.route('/')
def index():
    return render_template('index.html')

def get_user_name(id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(f"select name from public.users where id='{id}';")
    user_id = cur.fetchall()
    cur.close()
    conn.close()

    return user_id[0][0]

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

def add_room(code):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(f"insert into public.rooms (name) values ('{code}');")
    # user_id = cur.fetchall()
    # print(cur.fetchall())
    conn.commit()
    cur.close()
    conn.close()
    print(f"added room with code {code} to db")
    # print(f"insert into public.rooms (name) values ('{code}');")

def add_message(text="", user_name="", room_code=""):
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute(f"select id from public.users where name='{user_name}';")
    user_id = cur.fetchall()[0][0]
    cur.execute(f"select id from public.rooms where name='{room_code}';")
    room_id = cur.fetchall()[0][0]

    cur.execute(f"insert into public.messages (user_from_id, text, room_id) values ({user_id}, '{text}', {room_id});")
    # user_id = cur.fetchall()
    # print(cur.fetchall())
    conn.commit()
    cur.close()
    conn.close()
    print(f"added message {text} from {user_name}/{user_id} into {room_code}/{room_id} to db")
    # print(f"insert into public.rooms (name) values ('{code}');")

def get_codes():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(f"select (name) from public.rooms;")
    codes = cur.fetchall()
    # print("codes from db")
    # print(codes)
    # print(type(codes))
    cur.close()
    conn.close()

    return [code[0] for code in codes]

@main.route('/rooms', methods=["GET", "POST"])
@login_required
def rooms():
    session.clear()
    # print(request.method)
    if request.method == "POST":
        # name = request.form.get('name')
        name = get_user_name(current_user.id)
        create = request.form.get('create', False)
        code = request.form.get('code')
        join = request.form.get('join', False)
        # print(type(name), type(create), type(code), type(join))
        # if create is not False:
        #     print("create")
        # print(f"name: {name}, create: {create}, code: {code}, join: {join}")
        # pprint(chat_rooms)
        # if not name:
        #     return render_template('home.html', error="Name is required", code=code)
        if create is not False:
            room_code = generate_room_code(6, list(chat_rooms.keys()))
            new_room = {
                'members': 0,
                'messages': []
            }
            chat_rooms[room_code] = new_room
            add_room(room_code)
            # print("create")
        # elif join:
        else:
            # no code
            if not code:
                return render_template('rooms.html', error="Please enter a room code to enter a chat room", name=name)

            codes_db = get_codes()
            # invalid code
            if code not in codes_db:

            # if code not in chat_rooms:
                return render_template('rooms.html', error="Room code invalid", name=name)
            room_code = code
        session['room_code'] = room_code
        session['name'] = name
        return redirect(url_for('main.room'))
    else:
        return render_template('rooms.html')


def delete_messages(room_code):
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute(f"select id from public.rooms where name='{room_code}';")
    room_id = cur.fetchall()[0][0]

    cur.execute(f"delete from public.messages where room_id={room_id};")

    conn.commit()
    cur.close()
    conn.close()

def get_messages(room_code):
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute(f"select id from public.rooms where name='{room_code}';")
    room_id = cur.fetchall()[0][0]

    cur.execute(f"select user_from_id, text from public.messages m where m.room_id={room_id};")

    messages = cur.fetchall()
    result = []
    for msg in messages:
        cur.execute(f"select name from public.users where id='{msg[0]}';")
        user_name = cur.fetchall()[0][0]
        result.append({
            "sender": user_name,
            "message": msg[1]
        })

    # user_id = cur.fetchall()
    # print(cur.fetchall())
    conn.commit()
    cur.close()
    conn.close()

    return result
    # print(f"added message {text} from {user_name}/{user_id} into {room_code}/{room_id} to db")

@main.route('/room', methods=['GET', 'POST'])
@login_required
def room():

    name = session.get('name')
    room = session.get('room_code')
    if name is None or room is None or room not in get_codes():
        return redirect(url_for('main.rooms'))

    if request.method == "POST":
        # print("posted delete from room")
        # print(type(request.form.get("delete")))
        # print(request.form.get("delete"))
        if request.form.get("delete", False) is not False:
            delete_messages(room_code=room)

    messages = get_messages(room_code=room)
    # messages = chat_rooms[room]['messages']
    return render_template('room.html', room=room, user=name, messages=messages)


@socketio.on('connect')
def handle_connect():
    name = session.get('name')
    room = session.get('room_code')
    if name is None or room is None:
        return
    if room not in chat_rooms:
        leave_room(room)
    join_room(room)
    send({
        "sender": "",
        "message": f"{name} has entered the chat"
    }, to=room)
    # chat_rooms[room]["members"] += 1


@socketio.on('message')
def handle_message(payload):
    room = session.get('room_code')
    name = session.get('name')
    if room not in get_codes():
        return
    message = {
        "sender": name,
        "message": payload["message"]
    }
    send(message, to=room)
    add_message(text=payload["message"], user_name=name, room_code=room)
    # chat_rooms[room]["messages"].append(message)


@socketio.on('disconnect')
def handle_disconnect():
    room = session.get("room_code")
    name = session.get("name")
    leave_room(room)
    if room in chat_rooms:
        # chat_rooms[room]["members"] -= 1
        # if chat_rooms[room]["members"] <= 0:
        #     del chat_rooms[room]
        send({
        "message": f"{name} has left the chat",
        "sender": ""
    }, to=room)

