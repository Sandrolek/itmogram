import psycopg2
import hashlib
def get_db_connection():
    conn = psycopg2.connect(host='localhost',
                            database='flask_db',
                            user="flask_admin",
                            password="P@ssw0rd")
    return conn

def check_user(email):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(f"select * from public.users where email='{email}';")
    user = cur.fetchall()
    cur.close()
    conn.close()
    return user

# init_db()

password = "123"
m = hashlib.sha256()
num = str("P@ssw0rd")
m.update(num.encode('utf8'))
code = m.hexdigest()

print(code)

password2 = "P@ssw0rd"
m = hashlib.sha256()
num = str(password2)
m.update(num.encode('utf8'))
code = m.hexdigest()

print(code)

# print(get_rooms())