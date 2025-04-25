from dotenv import load_dotenv
load_dotenv()
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_socketio import SocketIO
from .config import Config
from flask_migrate import Migrate
import os

# 확장 객체 초기화
db = SQLAlchemy()
bcrypt = Bcrypt()
migrate = Migrate()
login_manager = LoginManager()
socketio = SocketIO(cors_allowed_origins="*")  # CORS 허용 (보통 개발환경에서는 * 허용)

login_manager.login_view = 'user_bp.login'
login_manager.login_message_category = 'info'

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    socketio.init_app(app)  # SocketIO 초기화
    
    from app.models import User  # user_loader 아래로 이동 방지

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # 블루프린트 등록
    from .routes import user_bp, product_bp, admin_bp
    from .chat import chat_bp  # 👈 새로운 chat 블루프린트 등록

    app.register_blueprint(user_bp)
    app.register_blueprint(product_bp)
    app.register_blueprint(chat_bp)  # 👈 chat 등록
    app.register_blueprint(admin_bp)
    return app

