from project.db.db_conn import get_db_connection


def init_db():

    conn = get_db_connection()

    cur = conn.cursor()

    cur.execute('DROP TABLE IF EXISTS users CASCADE;')
    cur.execute('CREATE TABLE users (id serial PRIMARY KEY,'
                                     'email varchar NOT NULL,'
                                     'password varchar NOT NULL,'
                                     'name varchar NOT NULL);'
                                     )

    cur.execute('DROP TABLE IF EXISTS rooms CASCADE;')
    cur.execute('CREATE TABLE rooms (id serial PRIMARY KEY,'
                                    'name varchar NOT NULL,'
                                    'code varchar NOT NULL);'
                                    )

    cur.execute('DROP TABLE IF EXISTS messages CASCADE;')
    cur.execute('CREATE TABLE messages (id serial PRIMARY KEY,'
                                    'user_from_id INT REFERENCES users(id),'
                                    'text TEXT NOT NULL,'
                                    'room_id INT REFERENCES rooms(id));'
                                    )

    conn.commit()

    cur.close()
    conn.close()