from flask import Flask
from flask_login import LoginManager
from flask_socketio import SocketIO
from .models import User

socketio = SocketIO()

def create_app():

    app = Flask(__name__)

    app.config['SECRET_KEY'] = 'P@ssw0rd'

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User(int(user_id))

    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    socketio.init_app(app)

    return app