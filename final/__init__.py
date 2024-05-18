from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy

from flask import Flask

# Configure database
db = SQLAlchemy()


def create_app():
    """ "sumary_line:
    Create Flask app
    """

    # Initialize Flask app
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "dshjkdshfkldjklfkj"
    app.config["SQLALCHEMY_DATABASE_URI"] = "mysql://root:1234@localhost/face_rec"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.init_app(app)

    # Register blueprints
    from .auth import auth
    from .views import views

    app.register_blueprint(views, url_prefix="/")
    app.register_blueprint(auth, url_prefix="/")

    from .models import User

    with app.app_context():
        db.create_all()

    login_manager = LoginManager()
    login_manager.login_view = "auth.login"
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    return app
