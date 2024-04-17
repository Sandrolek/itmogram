from flask import Blueprint, render_template
from flask_login import login_required, current_user
from . import get_db_connection

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/profile')
@login_required
def profile():

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(f"select name from public.users where id='{current_user.id}';")
    user_id = cur.fetchall()
    cur.close()
    conn.close()

    return render_template('profile.html', name=user_id[0][0])
