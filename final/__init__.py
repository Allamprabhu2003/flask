# # # # from flask_admin import Admin
# # # # from flask_login import LoginManager
# # # # from flask_sqlalchemy import SQLAlchemy
# # # # from werkzeug.middleware.profiler import ProfilerMiddleware

# # # # from flask import Flask

# # # # from .admin import AdminModelView
# # # # # from .utils import init_face_data
# # # # from .extention import db

# # # # from flask_migrate import Migrate



# # # # print("\nFirst line\n")

# # # # # Configure database
# # # # # db = SQLAlchemy()

# # # # print("\n Secons line\n")


# # # # def create_app():
# # # #     """ "sumary_line:
# # # #     Create Flask app
# # # #     """
# # # #     print("\n Third line\n")
# # # #     # Initialize Flask app
# # # #     app = Flask(__name__)

# # # #     app.config["SECRET_KEY"] = "dshjkdshfkldjklfkj"
# # # #     app.config["SQLALCHEMY_DATABASE_URI"] = "mysql://root:1234@localhost/abd"
# # # #     # app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    

# # # #     db.init_app(app)
# # # #     migrate = Migrate(app, db)
    
# # # #     print("\n Fourth line\n")
# # # #     # app.wsgi_app = ProfilerMiddleware(app.wsgi_app, restrictions=[30])

# # # #     # Register blueprints
# # # #     from .auth import auth
# # # #     from .views import views

# # # #     app.register_blueprint(views, url_prefix="/")
# # # #     app.register_blueprint(auth, url_prefix="/")
    
    
# # # #     # from .auth_views import auth as auth_blueprint
# # # #     # app.register_blueprint(auth_blueprint)
    
# # # #     from .student_views import student as student_blueprint
# # # #     app.register_blueprint(student_blueprint)
    
# # # #     from .class_views import class_views as class_blueprint
# # # #     app.register_blueprint(class_blueprint)
    
# # # #     from .attendance_views import attendance as attendance_blueprint
# # # #     app.register_blueprint(attendance_blueprint)
    
# # # #     # from .admin_views import admin as admin_blueprint
# # # #     # app.register_blueprint(admin_blueprint)
    
# # # #     from .face_recognition_views import \
# # # #         face_recognition as face_recognition_blueprint
# # # #     app.register_blueprint(face_recognition_blueprint)
    
# # # #     print("\n Fifth line\n")


# # # #     with app.app_context():
# # # #         # db.create_all()
# # # #         pass
# # # #     print("\n Sixth line\n")

        

# # # #     from .models import Face, User



# # # #     login_manager = LoginManager()
# # # #     login_manager.login_view = "auth.login"
# # # #     login_manager.init_app(app)
# # # #     from .admin import admin_bp  # Import the admin blueprint

# # # #     app.register_blueprint(admin_bp)  # Register the admin blueprint
    
# # # #     admin = Admin(app, name='Admin Panel', template_mode='bootstrap4')
# # # #     admin.add_view(AdminModelView(User, db.session))
# # # #     admin.add_view(AdminModelView(Face, db.session))



# # # #     @login_manager.user_loader
# # # #     def load_user(id):
# # # #         return User.query.get(int(id))
    
# # # #     # migrate = Migrate(app, db)

# # # #     # init_face_data()
# # # #     return app



# # # from flask import Flask
# # # from flask_login import LoginManager
# # # from flask_sqlalchemy import SQLAlchemy
# # # from flask_migrate import Migrate
# # # from .extention import db
# # # from .admin import init_admin  # Import the new init_admin function

# # # def create_app():
# # #     app = Flask(__name__)
# # #     app.config["SECRET_KEY"] = "dshjkdshfkldjklfkj"
# # #     app.config["SQLALCHEMY_DATABASE_URI"] = "mysql://root:1234@localhost/abd"

# # #     db.init_app(app)
# # #     migrate = Migrate(app, db)

# # #     # Register blueprints
# # #     from .auth import auth
# # #     from .views import views
# # #     from .student_views import student
# # #     from .class_views import class_views
# # #     from .attendance_views import attendance
# # #     from .face_recognition_views import face_recognition

# # #     app.register_blueprint(views, url_prefix="/")
# # #     app.register_blueprint(auth, url_prefix="/")
# # #     app.register_blueprint(student, url_prefix="/")
# # #     app.register_blueprint(class_views, url_prefix="/")
# # #     app.register_blueprint(attendance, url_prefix="/")
# # #     app.register_blueprint(face_recognition, url_prefix="/")

# # #     from .models import User

# # #     login_manager = LoginManager()
# # #     login_manager.login_view = "auth.login"
# # #     login_manager.init_app(app)

# # #     @login_manager.user_loader
# # #     def load_user(id):
# # #         return User.query.get(int(id))

# # #     # Initialize the admin
# # #     init_admin(app)

# # #     return app



# # from flask import Flask
# # from flask_login import LoginManager
# # from flask_sqlalchemy import SQLAlchemy
# # from flask_migrate import Migrate
# # from .extention import db
# # from .admin import init_admin  # Import the new init_admin function

# # def create_app():
# #     app = Flask(__name__)
# #     app.config["SECRET_KEY"] = "dshjkdshfkldjklfkj"
# #     app.config["SQLALCHEMY_DATABASE_URI"] = "mysql://root:1234@localhost/abd"

# #     db.init_app(app)
# #     migrate = Migrate(app, db)

# #     # Register blueprints with unique names
# #     from .auth import auth as auth_blueprint
# #     from .views import views as views_blueprint
# #     from .student_views import student as student_blueprint
# #     from .class_views import class_views as class_blueprint
# #     from .attendance_views import attendance as attendance_blueprint
# #     from .face_recognition_views import face_recognition as face_recognition_blueprint

# #     app.register_blueprint(views_blueprint, url_prefix="/")
# #     app.register_blueprint(auth_blueprint, url_prefix="/")
# #     app.register_blueprint(student_blueprint, url_prefix="/student")
# #     app.register_blueprint(class_blueprint, url_prefix="/class")
# #     app.register_blueprint(attendance_blueprint, url_prefix="/attendance")
# #     app.register_blueprint(face_recognition_blueprint, url_prefix="/face_recognition")

# #     from .models import User

# #     login_manager = LoginManager()
# #     login_manager.login_view = "auth.login"
# #     login_manager.init_app(app)

# #     @login_manager.user_loader
# #     def load_user(id):
# #         return User.query.get(int(id))

# #     # Initialize the admin
# #     init_admin(app)

# #     return app


# from flask import Flask
# from flask_login import LoginManager
# from flask_sqlalchemy import SQLAlchemy
# from flask_migrate import Migrate
# from .extention import db
# from .admin import init_admin  # Import the new init_admin function

# def create_app():
#     app = Flask(__name__)
#     app.config["SECRET_KEY"] = "dshjkdshfkldjklfkj"
#     app.config["SQLALCHEMY_DATABASE_URI"] = "mysql://root:1234@localhost/abd"

#     db.init_app(app)
#     migrate = Migrate(app, db)

#     # Register blueprints with unique names
#     from .auth import auth as auth_blueprint
#     from .views import views as views_blueprint
#     from .student_views import student as student_blueprint
#     from .class_views import class_views as course_class_blueprint  # Changed variable name
#     from .attendance_views import attendance as attendance_blueprint
#     from .face_recognition_views import face_recognition as face_recognition_blueprint

#     app.register_blueprint(views_blueprint, url_prefix="/")
#     app.register_blueprint(auth_blueprint, url_prefix="/")
#     app.register_blueprint(student_blueprint, url_prefix="/student")
#     app.register_blueprint(course_class_blueprint, url_prefix="/course_class")  # Changed URL prefix
#     app.register_blueprint(attendance_blueprint, url_prefix="/attendance")
#     app.register_blueprint(face_recognition_blueprint, url_prefix="/face_recognition")

#     from .models import User

#     login_manager = LoginManager()
#     login_manager.login_view = "auth.login"
#     login_manager.init_app(app)

#     @login_manager.user_loader
#     def load_user(id):
#         return User.query.get(int(id))

#     # Initialize the admin
#     init_admin(app)

#     return app



from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from .extention import db
from .admin import init_admin  # Import the new init_admin function

def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "dshjkdshfkldjklfkj"
    app.config["SQLALCHEMY_DATABASE_URI"] = "mysql://root:1234@localhost/abd"

    db.init_app(app)
    migrate = Migrate(app, db)

    # Register blueprints with unique names
    from .auth import auth as auth_blueprint
    from .views import views as views_blueprint
    from .student_views import student as student_blueprint
    from .class_views import class_views as course_class_blueprint  # Changed variable name
    from .attendance_views import attendance as attendance_blueprint
    from .face_recognition_views import face_recognition as face_recognition_blueprint

    app.register_blueprint(views_blueprint, url_prefix="/")
    app.register_blueprint(auth_blueprint, url_prefix="/")
    app.register_blueprint(student_blueprint, url_prefix="/student")
    app.register_blueprint(course_class_blueprint, url_prefix="/course_class")  # Changed URL prefix
    app.register_blueprint(attendance_blueprint, url_prefix="/attendance")
    app.register_blueprint(face_recognition_blueprint, url_prefix="/face_recognition")

    from .models import User

    login_manager = LoginManager()
    login_manager.login_view = "auth.login"
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    # Initialize the admin
    init_admin(app)

    return app
