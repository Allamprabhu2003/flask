# # # # # admin.py
# # # # from flask_admin.contrib.sqla import ModelView
# # # # from flask_login import current_user

# # # # from flask import Blueprint, redirect, request, url_for

# # # # from flask import Blueprint, flash, redirect, render_template, request, url_for
# # # # from flask_login import login_required, current_user
# # # # from .extention import db
# # # # from .models import User

# # # # admin_bp = Blueprint('admin_bp', __name__, url_prefix='/admin')

# # # # @admin_bp.route("/user_permissions", methods=["GET", "POST"])
# # # # @login_required
# # # # def user_permissions():
# # # #     if not current_user.is_admin:
# # # #         flash("You do not have permission to access this page", "danger")
# # # #         return redirect(url_for("views.dashboard"))

# # # #     users = User.query.all()

# # # #     if request.method == "POST":
# # # #         changes_made = False
# # # #         print("Form Data:", request.form)  # Debug: Print all form data

# # # #         user_id = request.form.get('user_id')
# # # #         user = User.query.get(user_id)

# # # #         if user:
# # # #             can_add = 'can_add_classes' in request.form
# # # #             can_edit = 'can_edit_classes' in request.form
# # # #             can_delete = 'can_delete_classes' in request.form

# # # #             print(f"User {user_id} - Current: Add:{user.can_add_classes}, Edit:{user.can_edit_classes}, Delete:{user.can_delete_classes}")
# # # #             print(f"User {user_id} - New: Add:{can_add}, Edit:{can_edit}, Delete:{can_delete}")

# # # #             if user.can_add_classes != can_add:
# # # #                 user.can_add_classes = can_add
# # # #                 changes_made = True
# # # #             if user.can_edit_classes != can_edit:
# # # #                 user.can_edit_classes = can_edit
# # # #                 changes_made = True
# # # #             if user.can_delete_classes != can_delete:
# # # #                 user.can_delete_classes = can_delete
# # # #                 changes_made = True

# # # #             if changes_made:
# # # #                 try:
# # # #                     db.session.commit()
# # # #                     flash("Permissions updated successfully", "success")
# # # #                 except Exception as e:
# # # #                     db.session.rollback()
# # # #                     flash(f"An error occurred while updating permissions: {str(e)}", "danger")
# # # #             else:
# # # #                 flash("No changes were made to permissions", "info")
# # # #         else:
# # # #             flash("User not found", "danger")

# # # #         return redirect(url_for('admin_bp.user_permissions'))

# # # #     return render_template("user_permissions.html", users=users)

# # # # class AdminModelView(ModelView):
# # # #     def is_accessible(self):
# # # #         return current_user.is_authenticated and current_user.is_admin

# # # #     def inaccessible_callback(self, name, **kwargs):
# # # #         return redirect(url_for('auth.login', next=request.url))

# # # # from flask_admin import AdminIndexView, expose
# # # # from flask_login import current_user
# # # # from .models import User, Class

# # # # class CustomAdminIndexView(AdminIndexView):
# # # #     @expose('/')
# # # #     def index(self):
# # # #         user_count = User.query.count()
# # # #         class_count = Class.query.count()

# # # #         return self.render('admin.html', user_count=user_count, class_count=class_count)

# # # from flask_admin import Admin, AdminIndexView, expose
# # # from flask_admin.contrib.sqla import ModelView
# # # from flask_login import current_user
# # # from flask import Blueprint, flash, redirect, render_template, request, url_for
# # # from flask_login import login_required
# # # from .extention import db
# # # from .models import User, Class, Student, Attendance

# # # admin_bp = Blueprint('admin_bp', __name__, url_prefix='/admin')

# # # class AdminModelView(ModelView):
# # #     def is_accessible(self):
# # #         return current_user.is_authenticated and current_user.is_admin

# # #     def inaccessible_callback(self, name, **kwargs):
# # #         return redirect(url_for('auth.login', next=request.url))

# # # class CustomAdminIndexView(AdminIndexView):
# # #     @expose('/')
# # #     def index(self):
# # #         user_count = User.query.count()
# # #         class_count = Class.query.count()
# # #         student_count = Student.query.count()
# # #         attendance_count = Attendance.query.count()
# # #         return self.render('admin/index.html', user_count=user_count, class_count=class_count,
# # #                            student_count=student_count, attendance_count=attendance_count)

# # # class UserPermissionsView(AdminModelView):
# # #     @expose('/')
# # #     def index(self):
# # #         users = User.query.all()
# # #         return self.render('admin/user_permissions.html', users=users)

# # #     @expose('/update', methods=['POST'])
# # #     def update_permissions(self):
# # #         user_id = request.form.get('user_id')
# # #         user = User.query.get(user_id)

# # #         if user:
# # #             user.can_add_classes = 'can_add_classes' in request.form
# # #             user.can_edit_classes = 'can_edit_classes' in request.form
# # #             user.can_delete_classes = 'can_delete_classes' in request.form

# # #             db.session.commit()
# # #             flash('User permissions updated successfully', 'success')
# # #         else:
# # #             flash('User not found', 'error')

# # #         return redirect(url_for('.index'))

# # # def init_admin(app):
# # #     admin = Admin(app, name='Admin Panel', template_mode='bootstrap3', index_view=CustomAdminIndexView())
# # #     admin.add_view(AdminModelView(User, db.session, name='Users'))
# # #     admin.add_view(AdminModelView(Class, db.session, name='Classes'))
# # #     admin.add_view(AdminModelView(Student, db.session, name='Students'))
# # #     admin.add_view(AdminModelView(Attendance, db.session, name='Attendance'))
# # #     admin.add_view(UserPermissionsView(User, db.session, name='User Permissions'))

# # from flask_admin import Admin, AdminIndexView, expose
# # from flask_admin.contrib.sqla import ModelView
# # from flask_login import current_user
# # from flask import Blueprint, flash, redirect, render_template, request, url_for
# # from flask_login import login_required
# # from .extention import db
# # from .models import User, Class, Student, Attendance

# # admin_bp = Blueprint('admin_bp', __name__, url_prefix='/admin')

# # class AdminModelView(ModelView):
# #     def is_accessible(self):
# #         return current_user.is_authenticated and current_user.is_admin

# #     def inaccessible_callback(self, name, **kwargs):
# #         return redirect(url_for('auth.login', next=request.url))

# # class CustomAdminIndexView(AdminIndexView):
# #     @expose('/')
# #     def index(self):
# #         user_count = User.query.count()
# #         class_count = Class.query.count()
# #         student_count = Student.query.count()
# #         attendance_count = Attendance.query.count()
# #         return self.render('admin/index.html', user_count=user_count, class_count=class_count,
# #                            student_count=student_count, attendance_count=attendance_count)

# # class UserPermissionsView(AdminModelView):
# #     @expose('/')
# #     def index(self):
# #         users = User.query.all()
# #         return self.render('admin/user_permissions.html', users=users)

# #     @expose('/update', methods=['POST'])
# #     def update_permissions(self):
# #         user_id = request.form.get('user_id')
# #         user = User.query.get(user_id)

# #         if user:
# #             user.can_add_classes = 'can_add_classes' in request.form
# #             user.can_edit_classes = 'can_edit_classes' in request.form
# #             user.can_delete_classes = 'can_delete_classes' in request.form

# #             db.session.commit()
# #             flash('User permissions updated successfully', 'success')
# #         else:
# #             flash('User not found', 'error')

# #         return redirect(url_for('.index'))

# # def init_admin(app):
# #     admin = Admin(app, name='Admin Panel', template_mode='bootstrap3', index_view=CustomAdminIndexView())
# #     admin.add_view(AdminModelView(User, db.session, name='Users'))
# #     admin.add_view(AdminModelView(Class, db.session, name='CourseClasses'))  # Changed name from 'Classes' to 'CourseClasses'
# #     admin.add_view(AdminModelView(Student, db.session, name='Students'))
# #     admin.add_view(AdminModelView(Attendance, db.session, name='Attendance'))
# #     admin.add_view(UserPermissionsView(User, db.session, name='User Permissions'))

# from flask_admin import Admin, AdminIndexView, expose
# from flask_admin.contrib.sqla import ModelView
# from flask_login import current_user
# from flask import Blueprint, flash, redirect, render_template, request, url_for
# from flask_login import login_required
# from .extention import db
# from .models import User, Class, Student, Attendance

# admin_bp = Blueprint('admin_bp', __name__, url_prefix='/admin')

# class AdminModelView(ModelView):
#     def is_accessible(self):
#         return current_user.is_authenticated and current_user.is_admin

#     def inaccessible_callback(self, name, **kwargs):
#         return redirect(url_for('auth.login', next=request.url))

# class CustomAdminIndexView(AdminIndexView):
#     @expose('/')
#     def index(self):
#         user_count = User.query.count()
#         class_count = Class.query.count()
#         student_count = Student.query.count()
#         attendance_count = Attendance.query.count()
#         return self.render('admin/index.html', user_count=user_count, class_count=class_count,
#                            student_count=student_count, attendance_count=attendance_count)

# class UserPermissionsView(AdminModelView):
#     @expose('/')
#     def index(self):
#         users = User.query.all()
#         return self.render('admin/user_permissions.html', users=users)

#     @expose('/update', methods=['POST'])
#     def update_permissions(self):
#         user_id = request.form.get('user_id')
#         user = User.query.get(user_id)

#         if user:
#             user.can_add_classes = 'can_add_classes' in request.form
#             user.can_edit_classes = 'can_edit_classes' in request.form
#             user.can_delete_classes = 'can_delete_classes' in request.form

#             db.session.commit()
#             flash('User permissions updated successfully', 'success')
#         else:
#             flash('User not found', 'error')

#         return redirect(url_for('.index'))

# class CourseClassModelView(AdminModelView):
#     # You can customize this view if needed
#     pass

# def init_admin(app):
#     admin = Admin(app, name='Admin Panel', template_mode='bootstrap3', index_view=CustomAdminIndexView())
#     admin.add_view(AdminModelView(User, db.session, name='Users'))
#     admin.add_view(CourseClassModelView(Class, db.session, name='CourseClasses', endpoint='admin_courseclasses'))
#     admin.add_view(AdminModelView(Student, db.session, name='Students'))
#     admin.add_view(AdminModelView(Attendance, db.session, name='Attendance'))
#     admin.add_view(UserPermissionsView(User, db.session, name='User Permissions', endpoint='admin_user_permissions'))

from flask_admin import Admin, AdminIndexView, expose
from flask_admin.contrib.sqla import ModelView
from flask_login import current_user
from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import login_required
from .extention import db
from .models import User, Class, Student, Attendance

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
