# auth.py
from flask import request, render_template, redirect, url_for, flash, Blueprint
from werkzeug.security import check_password_hash, generate_password_hash
from flask_login import login_required, login_user, logout_user, current_user
from .models import User
from . import db

auth = Blueprint("auth", __name__)


@auth.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("views.dashboard"))

    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        user = User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password, password):
                login_user(user)
                flash("Logged in successfully.", category="success")
                next_page = request.args.get('next')
                if next_page:
                    return redirect(next_page)
                elif user.is_admin:
                    return redirect(url_for("admin.index"))
                else:
                    return redirect(url_for("views.dashboard"))
            else:
                flash("Incorrect password. Please try again.", category="error")
        else:
            flash("Email not found. Please check your email or sign up.", category="error")

    return render_template("login.html")

@auth.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Logged out successfully.", category="success")
    return redirect(url_for("auth.login"))

@auth.route("/sign-up", methods=["GET", "POST"])
def sign_up():
    print("Signing UP .................")
    if request.method == "POST":
        email = request.form.get("email")
        first_name = request.form.get("first_name")
        last_name = request.form.get("last_name")
        password1 = request.form.get("password1")
        password2 = request.form.get("password2")
        is_teacher = request.form.get("is_teacher") == "on"

        user = User.query.filter_by(email=email).first()
        if user:
            flash("Email already exists. Please use a different email or login.", category="error")
            print("Email already exists. Please use a different email or login.")
        elif not email or len(email) < 4:
            flash("Please provide a valid email address (at least 4 characters).", category="error")
        elif not first_name or len(first_name) < 2:
            flash("First name must be at least 2 characters long.", category="error")
        elif not last_name or len(last_name) < 2:
            flash("Last name must be at least 2 characters long.", category="error")
        elif not password1 or len(password1) < 7:
            flash("Password must be at least 7 characters long.", category="error")
        elif password1 != password2:
            flash("Passwords don't match. Please try again.", category="error")
        else:
            new_user = User(
                email=email,
                first_name=first_name,
                last_name=last_name,
                password=generate_password_hash(password1, method="pbkdf2:sha256"),
                is_admin=is_teacher  # Assuming teachers are admins in your system
            )
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=True)
            flash("Account created successfully!", category="success")
            print("Account created successfully!")
            return redirect(url_for("views.dashboard"))

    return render_template("sign_up.html", user=current_user)