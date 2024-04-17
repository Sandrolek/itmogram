from flask import Flask
import psycopg2
from flask_login import LoginManager
from flask_socketio import SocketIO

def get_db_connection():
    conn = psycopg2.connect(host='localhost',
                            database='flask_db',
                            user="flask_admin",
                            password="P@ssw0rd")
    return conn

def create_app():
    app = Flask(__name__)

    app.config['SECRET_KEY'] = 'P@ssw0rd'

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    from .models import User

    @login_manager.user_loader
    def load_user(user_id):
        return User(int(user_id))

    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    socketio = SocketIO(app)

    return app