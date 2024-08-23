from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from .extention import db, csrf
from .admin import init_admin  # Import the new init_admin function
from flask_mail import Mail
from .config import Config
from flask_wtf.csrf import CSRFProtect
from flask_cors import CORS

mail = Mail()
# csrf = CSRFProtect()
# Enable CORS for all routes


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    # WTF_CSRF_ENABLED = True

    # Setup mail
    mail.init_app(app)

    # Setup CSRF protection
    csrf.init_app(app)
    CORS(app)
    # Initialize the database
    db.init_app(app)
    migrate = Migrate(app, db)

    # Register blueprints with unique names
    from .auth import auth as auth_blueprint
    from .views import views as views_blueprint
    from .student_views import student as student_blueprint
    from .class_views import class_views as course_class_blueprint
    from .attendance_views import attendance as attendance_blueprint
    from .face_recognition_views import face_recognition as face_recognition_blueprint

    from .email_service import email_blueprint  # Import the Blueprint
    from .manual_attendance import manual_attendance

    app.register_blueprint(views_blueprint, url_prefix="/")
    app.register_blueprint(auth_blueprint, url_prefix="/")
    app.register_blueprint(student_blueprint, url_prefix="/student")
    app.register_blueprint(course_class_blueprint, url_prefix="/course_class")
    app.register_blueprint(attendance_blueprint, url_prefix="/attendance")
    app.register_blueprint(face_recognition_blueprint, url_prefix="/face_recognition")
    app.register_blueprint(email_blueprint, url_prefix="/email")
    app.register_blueprint(manual_attendance, url_prefix="/manual_attendance")

    # Import and initialize models
    from .models import User

    # Setup Flask-Login
    login_manager = LoginManager()
    login_manager.login_view = "auth.login"
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    # Initialize the admin
    init_admin(app)

    return app
