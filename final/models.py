from flask import current_app
from networkx import cubical_graph
from .extention import db
import final
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
import datetime
from flask_login import UserMixin

from werkzeug.security import generate_password_hash, check_password_hash
# from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from itsdangerous import URLSafeTimedSerializer as Serializer  # Updated import


class Face(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer,
                           db.ForeignKey('student.id'),
                           nullable=False)
    face_encodings = db.Column(db.PickleType, nullable=False)


# class User(db.Model, UserMixin):
#     id = db.Column(db.Integer, primary_key=True)
#     email = db.Column(db.String(120), unique=True, nullable=False)
#     password = db.Column(db.String(255), nullable=False)
#     first_name = db.Column(db.String(120), nullable=False)
#     last_name = db.Column(db.String(120), nullable=False)
#     is_admin = db.Column(db.Boolean, default=False)
#     can_add_classes = db.Column(db.Boolean, default=False)
#     can_edit_classes = db.Column(db.Boolean, default=False)
#     can_delete_classes = db.Column(db.Boolean, default=False)
#     classes = db.relationship('Class', secondary='class_teacher', back_populates='teachers')

#     def set_password(self, password):
#         self.password = generate_password_hash(password, method='pbkdf2:sha256')
#         print(f"Password hash: {self.password}")  # Debugging line

#     def check_password(self, password):
#         return check_password_hash(self.password, password)

#     def get_reset_token(self, expires_sec=1800):
#         s = Serializer(final.config['SECRET_KEY'], expires_sec)
#         return s.dumps({'user_id': self.id}).decode('utf-8')

#     @staticmethod
#     def verify_reset_token(token):
#         s = Serializer(final.config['SECRET_KEY'])
#         try:
#             user_id = s.loads(token)['user_id']
#         except:
#             return None
#         return User.query.get(user_id)

# models.py
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import URLSafeTimedSerializer as Serializer
from .extention import db
import final


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(120), nullable=False)
    last_name = db.Column(db.String(120), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    can_add_classes = db.Column(db.Boolean, default=False)
    can_edit_classes = db.Column(db.Boolean, default=False)
    can_delete_classes = db.Column(db.Boolean, default=False)
    classes = db.relationship('Class',
                              secondary='class_teacher',
                              back_populates='teachers')

    def set_password(self, password):
        self.password = generate_password_hash(password,
                                               method='pbkdf2:sha256')

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def get_reset_token(self, expires_sec=1800):
        s = Serializer(current_app.config['SECRET_KEY'])
        return s.dumps({'user_id': self.id})

    @staticmethod
    def verify_reset_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return User.query.get(user_id)


class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(120), nullable=False)
    last_name = db.Column(db.String(120), nullable=False)

    email = db.Column(db.String(120), unique=True, nullable=False)
    roll_number = db.Column(db.String(20), unique=True,
                            nullable=False)  # New field for roll number

    course_type = db.Column(db.String(10),
                            nullable=False)  # New field for course type
    face = db.relationship('Face', backref='student', uselist=False, lazy=True)
    classes = db.relationship('Class',
                              secondary='class_student',
                              back_populates='students')


class Class(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    course_type = db.Column(db.String(10),
                            nullable=False)  # New field for course type
    students = db.relationship('Student',
                               secondary='class_student',
                               back_populates='classes')
    teachers = db.relationship('User',
                               secondary='class_teacher',
                               back_populates='classes')
    attendances = db.relationship('Attendance',
                                  backref='class',
                                  cascade='all, delete-orphan')


class ClassTeacher(db.Model):
    __tablename__ = 'class_teacher'
    class_id = db.Column(db.Integer,
                         db.ForeignKey('class.id'),
                         primary_key=True)
    teacher_id = db.Column(db.Integer,
                           db.ForeignKey('user.id'),
                           primary_key=True)


class ClassStudent(db.Model):
    __tablename__ = 'class_student'
    class_id = db.Column(db.Integer,
                         db.ForeignKey('class.id'),
                         primary_key=True)
    student_id = db.Column(db.Integer,
                           db.ForeignKey('student.id'),
                           primary_key=True)


# class Attendance(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     student_id = db.Column(db.Integer,
#                            db.ForeignKey('student.id'),
#                            nullable=False)
#     timestamp = db.Column(db.DateTime, default=datetime.datetime.utcnow)
#     class_id = db.Column(db.Integer, db.ForeignKey("class.id"), nullable=False)
#     status = db.Column(db.String(20),
#                        nullable=False)  # 'present', 'absent', 'late


class Attendance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    class_id = db.Column(db.Integer, db.ForeignKey('class.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    status = db.Column(db.String(20), nullable=False)  # 'present', 'absent'
