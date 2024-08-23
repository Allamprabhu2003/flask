# Import necessary modules
from flask import (Blueprint, flash, jsonify, redirect, render_template,
                   request, url_for)
from flask_login import current_user, login_required
from sqlalchemy.exc import IntegrityError

from . import csrf, db
from .models import Class, User, Student
from .student_views import get_course_types_from_db

# Define the class views blueprint
class_views = Blueprint('class', __name__)

# Define routes for class views
@class_views.route("/class/add", methods=["GET", "POST"])
@login_required
@csrf.exempt
def add_class():
    """Add a new class"""
    if not (current_user.is_admin or current_user.can_add_classes):
        flash("You do not have permission to add classes", "danger")
        return redirect(url_for("views.dashboard"))

    course_types = get_course_types_from_db()
    print("Inside Edit class")


    if request.method == "POST":
        class_name = request.form.get("class_name")
        course_type = request.form.get("course_type")
        

        if not class_name or not course_type:
            flash("Class name and course type are required.", "error")
            return render_template("dashboard.html", course_types=course_types)

        try:
            new_class = Class(name=class_name, course_type=course_type)
            new_class.teachers.append(current_user)
            db.session.add(new_class)
            db.session.commit()

            # Automatically add students with the same course_type to the new class
            students = Student.query.filter_by(course_type=course_type).all()
            new_class.students.extend(students)

            flash("Class created successfully", "success")
            return redirect(url_for("views.dashboard"))

        except IntegrityError:
            db.session.rollback()
            flash("A class with this name already exists.", "error")

        except Exception as e:
            db.session.rollback()
            flash(f"An error occurred: {str(e)}", "error")

    return render_template("dashboard.html", course_types=course_types)


@class_views.route("/class/<int:class_id>/edit", methods=["GET", "POST"])
@login_required
@csrf.exempt
def edit_class(class_id):
    """Edit an existing class"""
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


@class_views.route("/delete_class/<int:class_id>", methods=["POST"])
@login_required
@csrf.exempt
def delete_class(class_id):
    """Delete a class"""
    if not (current_user.is_admin or current_user.can_delete_classes):
        return jsonify(success=False, message="You do not have permission to delete classes"), 403

    class_ = Class.query.get_or_404(class_id)
    if current_user not in class_.teachers:
        return jsonify(success=False, message="You do not have permission to delete this class"), 403

    try:
        if request.json and request.json.get('confirm_delete') == 'yes':
            db.session.delete(class_)
            db.session.commit()
            return jsonify(success=True, message=f"Class '{class_.name}' and all associated attendance records have been deleted.")
        else:
            return jsonify(success=False, message="Delete confirmation required."), 400
    except Exception as e:
        db.session.rollback()
        return jsonify(success=False, message=str(e)), 500