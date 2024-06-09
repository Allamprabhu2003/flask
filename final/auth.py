
# auth.py
from flask import request, render_template, redirect, url_for, flash, Blueprint
from werkzeug.security import check_password_hash, generate_password_hash
from flask_login import login_required, login_user, logout_user, current_user
from .models import User
from . import db
import time

auth = Blueprint("auth", __name__)


@auth.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        user = User.query.filter_by(email=email).first()
        if user:
            print("Correct")
            if check_password_hash(user.password, password):
                login_user(user)
                if user.is_admin:
                    return redirect(
                        url_for("admin.index")
                    )  # Redirect admin users to the admin panel
                else:
                    print("Not Correct")
                    return redirect(
                        url_for("views.dashboard")
                    )  # Redirect normal users to the homepage
            else:
                flash("Incorrect password, try again.", category="error")
        else:
            print("Email does not exist.")
            flash("Email does not exist.", category="error")
    return render_template("login.html", user=current_user)


@auth.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("auth.login"))


@auth.route("/sign-up", methods=["GET", "POST"])
def sign_up():
    if request.method == "POST":
        email = request.form.get("email")
        first_name = request.form.get("first_name")
        password1 = request.form.get("password1")
        password2 = request.form.get("password2")
        admin = request.form.get("admin")  # Checkbox to determine if user is admin

        if not first_name:  # Check if first_name is None or empty
            print("\n\nWrong")
            flash("First name is required.", category="error")
            return redirect(url_for("auth.sign_up"))
        user = User.query.filter_by(email=email).first()
        if user:
            print("Error 1\n\n")
            flash("Email already exists.", category="error")
        elif len(email) < 4:
            print("Error 2\n\n")
            flash("Email must be greater than 3 characters.", category="error")
        elif len(first_name) < 2:
            print("Error 3\n\n")
            flash("First name must be greater than 1 character.", category="error")
        elif password1 != password2:
            print("Error 4\n\n")
            flash("Passwords don't match.", category="error")
        elif len(password1) < 7:
            print("Error 5\n\n")
            flash("Password must be at least 7 characters.", category="error")
        else:
            print("Error 6\n\n")
            new_user = User(
                email=email,
                first_name=first_name,
                password=generate_password_hash(password1, method="sha256"),
                is_admin=(admin == "on"),
            )
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=True)
            flash("Account created!", category="success")
            return redirect(url_for("views.index"))
    return render_template("sign_up.html", user=current_user)
