from flask import Blueprint, flash, jsonify, redirect, render_template, request, url_for
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

from . import csrf

@class_views.route("/class/add", methods=["GET", "POST"])
@login_required
@csrf.exempt
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

from . import csrf
# @class_views.route("/delete_class/<int:class_id>", methods=["GET", "POST"])
# @login_required
# @csrf.exempt
# def delete_class(class_id):
#     if not (current_user.is_admin or current_user.can_delete_classes):
#         print("You do not have permission to delete classes")
#         return jsonify(success=False, message="You do not have permission to delete classes"), 403

#     class_ = Class.query.get_or_404(class_id)
#     if current_user not in class_.teachers:
#         print("You do not have permission to delete this class")
#         return jsonify(success=False, message="You do not have permission to delete this class"), 403

#     try:
#         if class_.attendances:
#             if request.json.get('confirm_delete') == 'yes':
#                 db.session.delete(class_)
#                 db.session.commit()
#                 print("Class '{class_.name}' and all associated attendance records have been deleted.")
#                 return jsonify(success=True, message=f"Class '{class_.name}' and all associated attendance records have been deleted.")
#             else:
#                 print("Please confirm deletion of class and associated records.")
#                 return jsonify(success=False, message="Please confirm deletion of class and associated records."), 400
            
#         else:
#             db.session.delete(class_)
#             db.session.commit()
#             print(f"Class '{class_.name}' has been deleted.")
#             return jsonify(success=True, message=f"Class '{class_.name}' has been deleted.")
#     except Exception as e:
#         print("Here =========================== ", e)
#         db.session.rollback()
#         return jsonify(success=False, message=str(e)), 500

@class_views.route("/delete_class/<int:class_id>", methods=["POST"])
@login_required
@csrf.exempt
def delete_class(class_id):
    if not (current_user.is_admin or current_user.can_delete_classes):
        print("You do not have permission to delete classes")
        return jsonify(success=False, message="You do not have permission to delete classes"), 403
    
    class_ = Class.query.get_or_404(class_id)
    if current_user not in class_.teachers:
        print("You do not have permission to delete this class")
        return jsonify(success=False, message="You do not have permission to delete this class"), 403
    
    try:
        if request.json and request.json.get('confirm_delete') == 'yes':
            db.session.delete(class_)
            db.session.commit()
            print(f"Class '{class_.name}' and all associated attendance records have been deleted.")
            return jsonify(success=True, message=f"Class '{class_.name}' and all associated attendance records have been deleted.")
        else:
            print("Delete confirmation required.")
            return jsonify(success=False, message="Delete confirmation required."), 400
    except Exception as e:
        print("Here =========================== ", e)
        db.session.rollback()
        return jsonify(success=False, message=str(e)), 500