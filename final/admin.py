# admin.py
from flask_admin.contrib.sqla import ModelView
from flask_login import current_user

from flask import Blueprint, redirect, request, url_for


# from flask import Blueprint, flash, redirect, render_template, request, url_for
# from flask_login import login_required, current_user
# from .extention import db
# from .models import User

# admin_bp = Blueprint('admin_bp', __name__, url_prefix='/admin')

# @admin_bp.route("/user_permissions", methods=["GET", "POST"])
# @login_required
# def user_permissions():
#     if not current_user.is_admin:
#         flash("You do not have permission to access this page", "danger")
#         return redirect(url_for("views.dashboard"))

#     users = User.query.all()

#     if request.method == "POST":
#         changes_made = False
#         print("Form Data:", request.form)  # Debug: Print all form data

#         for user in users:
#             user_id = str(user.id)
#             can_add = request.form.get(f"can_add_classes_{user_id}") == "on"
#             can_edit = request.form.get(f"can_edit_classes_{user_id}") == "on"
#             can_delete = request.form.get(f"can_delete_classes_{user_id}") == "on"
            
#             print(f"User {user_id} - Current: Add:{user.can_add_classes}, Edit:{user.can_edit_classes}, Delete:{user.can_delete_classes}")
#             print(f"User {user_id} - New: Add:{can_add}, Edit:{can_edit}, Delete:{can_delete}")

#             if user.can_add_classes != can_add:
#                 user.can_add_classes = can_add
#                 changes_made = True
#             if user.can_edit_classes != can_edit:
#                 user.can_edit_classes = can_edit
#                 changes_made = True
#             if user.can_delete_classes != can_delete:
#                 user.can_delete_classes = can_delete
#                 changes_made = True
        
#         if changes_made:
#             try:
#                 db.session.commit()
#                 flash("Permissions updated successfully", "success")
#                 # print(f"User {user_id} - Current: Add:{user.can_add_classes}, Edit:{user.can_edit_classes}, Delete:{user.can_delete_classes}")
#                 # print(f"User {user_id} - New: Add:{can_add}, Edit:{can_edit}, Delete:{can_delete}")
#             except Exception as e:
#                 db.session.rollback()
#                 flash(f"An error occurred while updating permissions: {str(e)}", "danger")
#         else:
#             flash("No changes were made to permissions", "info")
        
#         return redirect(url_for('admin_bp.user_permissions'))

#     return render_template("user_permissions.html", users=users)


from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import login_required, current_user
from .extention import db
from .models import User

admin_bp = Blueprint('admin_bp', __name__, url_prefix='/admin')

@admin_bp.route("/user_permissions", methods=["GET", "POST"])
@login_required
def user_permissions():
    if not current_user.is_admin:
        flash("You do not have permission to access this page", "danger")
        return redirect(url_for("views.dashboard"))

    users = User.query.all()

    if request.method == "POST":
        changes_made = False
        print("Form Data:", request.form)  # Debug: Print all form data

        user_id = request.form.get('user_id')
        user = User.query.get(user_id)

        if user:
            can_add = 'can_add_classes' in request.form
            can_edit = 'can_edit_classes' in request.form
            can_delete = 'can_delete_classes' in request.form
            
            print(f"User {user_id} - Current: Add:{user.can_add_classes}, Edit:{user.can_edit_classes}, Delete:{user.can_delete_classes}")
            print(f"User {user_id} - New: Add:{can_add}, Edit:{can_edit}, Delete:{can_delete}")

            if user.can_add_classes != can_add:
                user.can_add_classes = can_add
                changes_made = True
            if user.can_edit_classes != can_edit:
                user.can_edit_classes = can_edit
                changes_made = True
            if user.can_delete_classes != can_delete:
                user.can_delete_classes = can_delete
                changes_made = True
        
            if changes_made:
                try:
                    db.session.commit()
                    flash("Permissions updated successfully", "success")
                except Exception as e:
                    db.session.rollback()
                    flash(f"An error occurred while updating permissions: {str(e)}", "danger")
            else:
                flash("No changes were made to permissions", "info")
        else:
            flash("User not found", "danger")
        
        return redirect(url_for('admin_bp.user_permissions'))

    return render_template("user_permissions.html", users=users)


class AdminModelView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.is_admin

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('auth.login', next=request.url))

# from flask import Blueprint, flash, redirect, render_template, request, url_for
# from flask_login import login_required
# from .extention import db
# from .models import User

# admin_views = Blueprint('admin', __name__)

# @admin_bp.route("/admin/user_permissions", methods=["GET", "POST"])
# @login_required
# def user_permissions():
#     if not current_user.is_admin:
#         flash("You do not have permission to access this page", "danger")
#         return redirect(url_for("views.dashboard"))

#     users = User.query.all()

#     if request.method == "POST":
#         user_id = request.form.get("user_id")
#         can_manage_classes = request.form.get("can_manage_classes") == "on"

#         user = User.query.get(user_id)
#         if user:
#             user.can_manage_classes = can_manage_classes
#             db.session.commit()
#             flash(f"Permissions updated for {user.first_name} {user.last_name}", "success")
#         else:
#             flash("User not found", "danger")

#     return render_template("user_permissions.html", users=users)

