import json
import psycopg2
import hashlib

def get_db_connection():
    with open("db_conf.json") as conf_file:
        config = json.load(conf_file)

    host =      config["host"]
    database =  config["database"]
    user =      config["user"]
    password =  config["password"]

    connection = psycopg2.connect(
        host=host,
        database=database,
        user=user,
        password=password
    )

    return connection


def add_user(email, name, password):
    conn = get_db_connection()
    cur = conn.cursor()
    m = hashlib.sha256()
    num = str(password)
    m.update(num.encode('utf8'))
    code = m.hexdigest()
    cur.execute('INSERT INTO public.users (email, password, name)'
                'VALUES (%s, %s, %s)',
                (f"{email}",
                 f"{code}",
                 f"{name}")
                )

    conn.commit()
    cur.close()
    conn.close()

def get_user(email):
    # get user record by email
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(f"select id, email, name, password from public.users where email='{email}';")
    user = cur.fetchall()
    cur.close()
    conn.close()
    return user

def get_user_name(id):
    # get user name by id record
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(f"select name from public.users where id='{id}';")
    user_id = cur.fetchall()
    cur.close()
    conn.close()

    return user_id[0][0]

def add_room(name, code):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(f"insert into public.rooms (name, code) values ('{name}', '{code}');")
    conn.commit()
    cur.close()
    conn.close()
    print(f"added room with code {code} to db")

def get_rooms():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(f"select name, code from public.rooms;")
    rooms = cur.fetchall()
    cur.close()
    conn.close()

    return [{"name": room[0], "code": room[1]} for room in rooms]

def get_room_name(room_code):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(f"select name from public.rooms where code='{room_code}';")
    room_name = cur.fetchall()
    cur.close()
    conn.close()

    return room_name[0][0]


def add_message(text="", user_id="", room_code=""):
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute(f"select id from public.rooms where code='{room_code}';")
    room_id = cur.fetchall()[0][0]

    user_name = get_user_name(user_id)

    cur.execute(f"insert into public.messages (user_from_id, text, room_id) values ({user_id}, '{text}', {room_id});")
    conn.commit()
    cur.close()
    conn.close()
    print(f"added message {text} from {user_name}/{user_id} into {room_code} to db")

def delete_messages(room_code):
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute(f"select id from public.rooms where code='{room_code}';")
    room_id = cur.fetchall()[0][0]

    cur.execute(f"delete from public.messages where room_id={room_id};")

    conn.commit()
    cur.close()
    conn.close()

def get_messages(room_code):
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute(f"select id from public.rooms where code='{room_code}';")
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

    conn.commit()
    cur.close()
    conn.close()

    return result

