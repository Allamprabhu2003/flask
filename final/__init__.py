from flask_admin import Admin
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy

from flask import Flask

from .admin import AdminModelView

print("\nFirst line\n")

# Configure database
db = SQLAlchemy()

print("\n Secons line\n")


def create_app():
    """ "sumary_line:
    Create Flask app
    """
    print("\n Third line\n")
    # Initialize Flask app
    app = Flask(__name__)

    app.config["SECRET_KEY"] = "dshjkdshfkldjklfkj"
    app.config["SQLALCHEMY_DATABASE_URI"] = "mysql://root:1234@localhost/face_rec"
    # app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.init_app(app)
    print("\n Fourth line\n")

    # Register blueprints
    from .auth import auth
    from .views import views

    app.register_blueprint(views, url_prefix="/")
    app.register_blueprint(auth, url_prefix="/")
    print("\n Fifth line\n")


    with app.app_context():
        db.create_all()
    print("\n Sixth line\n")

        

    from .models import Face, User



    login_manager = LoginManager()
    login_manager.login_view = "auth.login"
    login_manager.init_app(app)
    
    admin = Admin(app, name='Admin Panel', template_mode='bootstrap3')
    admin.add_view(AdminModelView(User, db.session))
    admin.add_view(AdminModelView(Face, db.session))


    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    return app
