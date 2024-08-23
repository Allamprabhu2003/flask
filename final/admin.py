
from flask_admin import Admin, AdminIndexView, expose
from flask_admin.contrib.sqla import ModelView
from flask_login import current_user
from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import login_required
from .extention import db, csrf
from .models import User, Class, Student, Attendance
# from . import csrf
admin_bp = Blueprint('admin_bp', __name__, url_prefix='/admin')


class AdminModelView(ModelView):

    def is_accessible(self):
        return current_user.is_authenticated and current_user.is_admin

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('auth.login', next=request.url))


class CustomAdminIndexView(AdminIndexView):

    @expose('/')
    def index(self):
        user_count = User.query.count()
        class_count = Class.query.count()
        student_count = Student.query.count()
        attendance_count = Attendance.query.count()
        return self.render('admin/index.html',
                           user_count=user_count,
                           class_count=class_count,
                           student_count=student_count,
                           attendance_count=attendance_count)


class UserPermissionsView(AdminModelView):

    @expose('/')
    def index(self):
        users = User.query.all()
        return self.render('admin/user_permissions.html', users=users)

    @expose('/update', methods=['POST'])
    @csrf.exempt
    def update_permissions(self):
        user_id = request.form.get('user_id')
        user = User.query.get(user_id)

        if user:
            user.can_add_classes = 'can_add_classes' in request.form
            user.can_edit_classes = 'can_edit_classes' in request.form
            user.can_delete_classes = 'can_delete_classes' in request.form

            db.session.commit()
            flash('User permissions updated successfully', 'success')
        else:
            flash('User not found', 'error')

        return redirect(url_for('.index'))


class CourseClassModelView(AdminModelView):
    # You can customize this view if needed
    pass


class StudentModelView(AdminModelView):
    # You can customize this view if needed
    pass


class AttendanceModelView(AdminModelView):
    # You can customize this view if needed
    pass


def init_admin(app):
    admin = Admin(app,
                  name='Admin Panel',
                  template_mode='bootstrap3',
                  index_view=CustomAdminIndexView())
    admin.add_view(
        AdminModelView(User, db.session, name='Users', endpoint='admin_users'))
    admin.add_view(
        CourseClassModelView(Class,
                             db.session,
                             name='CourseClasses',
                             endpoint='admin_courseclasses'))
    admin.add_view(
        StudentModelView(Student,
                         db.session,
                         name='Students',
                         endpoint='admin_students'))
    admin.add_view(
        AttendanceModelView(Attendance,
                            db.session,
                            name='Attendance',
                            endpoint='admin_attendance'))
    admin.add_view(
        UserPermissionsView(User,
                            db.session,
                            name='User Permissions',
                            endpoint='admin_user_permissions'))
