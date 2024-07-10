# from flask import Blueprint, flash, redirect, render_template, request, url_for
# from flask_login import login_required, current_user
# from . import db
# from .models import Class

# class_views = Blueprint('class', __name__)

# @class_views.route("/class/<int:class_id>/edit", methods=["GET", "POST"])
# @login_required
# def edit_class(class_id):
#     class_ = Class.query.get_or_404(class_id)
#     if current_user not in class_.teachers:
#         flash("You do not have permission to edit this class", "danger")
#         return redirect(url_for("views.dashboard"))

#     if request.method == "POST":
#         class_.name = request.form.get("class_name")
#         db.session.commit()
#         flash("Class updated successfully", "success")
#         return redirect(url_for("views.dashboard"))

#     return render_template("edit_class.html", class_=class_)


# @class_views.route("/class/add", methods=["GET", "POST"])
# @login_required
# def add_class():
#     course_types = ["BCA", "BCS", "BA"]
#     if request.method == "POST":
#         class_name = request.form.get("class_name")
#         course_type = request.form.get("course_type")
#         new_class = Class(name=class_name, course_type=course_type)
#         new_class.teachers.append(current_user)
#         db.session.add(new_class)
#         db.session.commit()
#         flash("Class created successfully", "success")
#         return redirect(url_for("views.dashboard"))
    
#     return render_template("dashboard.html", course_types=course_types)

# # Add other class-related routes here


# @class_views.route("/delete_class/<int:class_id>", methods=["GET", "POST"])
# @login_required
# def delete_class(class_id):
#     class_ = Class.query.get_or_404(class_id)

#     if current_user not in class_.teachers:
#         flash("You do not have permission to delete this tclass", "danger")
#         return redirect(url_for("views.dashboard"))

#     if request.method == "POST":
#         # Check if there are any attendance records
#         if class_.attendances:
#             # If confirmation is received (you might want to add a confirmation checkbox in your form)
#             if request.form.get('confirm_delete') == 'yes':
#                 db.session.delete(class_)
#                 db.session.commit()
#                 flash(f"Class '{class_.name}' and all associated attendance records have been deleted.", "success")
#                 return redirect(url_for("views.dashboard"))
#             else:
#                 flash("Please confirm deletion of class and associated records.", "warning")
#         else:
#             # If no attendance records, delete directly
#             db.session.delete(class_)
#             db.session.commit()
#             flash(f"Class '{class_.name}' has been deleted.", "success")
#             return redirect(url_for("views.dashboard"))


from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import login_required, current_user
from . import db
from .models import Class, User

class_views = Blueprint('class', __name__)

@class_views.route("/class/<int:class_id>/edit", methods=["GET", "POST"])
@login_required
def edit_class(class_id):
    if not (current_user.is_admin or current_user.can_edit_classes):
        flash("You do not have permission to edit classes", "danger")
        return redirect(url_for("views.dashboard"))

    class_ = Class.query.get_or_404(class_id)
    if current_user not in class_.teachers:
        flash("You do not have permission to edit this class", "danger")
        return redirect(url_for("views.dashboard"))

    if request.method == "POST":
        class_.name = request.form.get("class_name")
        db.session.commit()
        flash("Class updated successfully", "success")
        return redirect(url_for("views.dashboard"))

    return render_template("edit_class.html", class_=class_)

@class_views.route("/class/add", methods=["GET", "POST"])
@login_required
def add_class():
    if not (current_user.is_admin or current_user.can_add_classes):
        flash("You do not have permission to add classes", "danger")
        print("You do not have permission to add classes", "danger")
        return redirect(url_for("views.dashboard"))

    course_types = ["BCA", "BCS", "BA"]
    if request.method == "POST":
        class_name = request.form.get("class_name")
        course_type = request.form.get("course_type")
        new_class = Class(name=class_name, course_type=course_type)
        new_class.teachers.append(current_user)
        db.session.add(new_class)
        db.session.commit()
        flash("Class created successfully", "success")
        print("Class created successfully", "success")
        return redirect(url_for("views.dashboard"))
    
    return render_template("dashboard.html", course_types=course_types)

@class_views.route("/delete_class/<int:class_id>", methods=["GET", "POST"])
@login_required
def delete_class(class_id):
    if not (current_user.is_admin or current_user.can_delete_classes):
        flash("You do not have permission to delete classes", "danger")
        return redirect(url_for("views.dashboard"))

    class_ = Class.query.get_or_404(class_id)
    if current_user not in class_.teachers:
        flash("You do not have permission to delete this class", "danger")
        return redirect(url_for("views.dashboard"))

    if request.method == "POST":
        if class_.attendances:
            if request.form.get('confirm_delete') == 'yes':
                db.session.delete(class_)
                db.session.commit()
                flash(f"Class '{class_.name}' and all associated attendance records have been deleted.", "success")
                return redirect(url_for("views.dashboard"))
            else:
                flash("Please confirm deletion of class and associated records.", "warning")
        else:
            db.session.delete(class_)
            db.session.commit()
            flash(f"Class '{class_.name}' has been deleted.", "success")
            return redirect(url_for("views.dashboard"))

    return render_template("confirm_delete_class.html", class_=class_)