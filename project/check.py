import psycopg2
from flask import Blueprint, render_template, redirect, url_for, request
from werkzeug.security import generate_password_hash, check_password_hash


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

print(check_user("aa@aaa.com"))
print(type(check_user("aa@aaa.com")))
