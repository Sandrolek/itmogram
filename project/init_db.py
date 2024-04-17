import psycopg2

conn = psycopg2.connect(
        host="localhost",
        database="flask_db",
        user="flask_admin",
        password="P@ssw0rd"
)

cur = conn.cursor()

cur.execute('DROP TABLE IF EXISTS users;')
cur.execute('CREATE TABLE users (id serial PRIMARY KEY,'
                                 'email varchar NOT NULL,'
                                 'password varchar NOT NULL,'
                                 'name varchar NOT NULL);'
                                 )

cur.execute('INSERT INTO users (email, password, name)'
            'VALUES (%s, %s, %s)',
            ('aaa@aaa.com',
             '123',
             'Jack')
            )

cur.execute('INSERT INTO users (email, password, name)'
            'VALUES (%s, %s, %s)',
            ('bbb@vvv.com',
             '123',
             'Simon')
            )

conn.commit()

cur.close()
conn.close()