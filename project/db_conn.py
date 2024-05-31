from . import get_db_connection

def add_user(email, name, password):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('INSERT INTO public.users (email, password, name)'
                'VALUES (%s, %s, %s)',
                (f"{email}",
                 f"{password}",
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

def add_room(code):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(f"insert into public.rooms (name) values ('{code}');")
    conn.commit()
    cur.close()
    conn.close()
    print(f"added room with code {code} to db")

def get_rooms_codes():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(f"select (name) from public.rooms;")
    codes = cur.fetchall()
    cur.close()
    conn.close()

    return [code[0] for code in codes]

def add_message(text="", user_id="", room_code=""):
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute(f"select id from public.rooms where name='{room_code}';")
    room_id = cur.fetchall()[0][0]

    user_name = get_user_name(user_id)

    cur.execute(f"insert into public.messages (user_from_id, text, room_id) values ({user_id}, '{text}', {room_id});")
    conn.commit()
    cur.close()
    conn.close()
    print(f"added message {text} from {user_name}/{user_id} into {room_code}/{room_id} to db")

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

    conn.commit()
    cur.close()
    conn.close()

    return result

