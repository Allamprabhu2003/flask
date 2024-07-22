# auth.py
from flask import request, render_template, redirect, url_for, flash, Blueprint
from werkzeug.security import check_password_hash, generate_password_hash
from flask_login import login_required, login_user, logout_user, current_user
from .models import User
from . import db, csrf

auth = Blueprint("auth", __name__)


@auth.route("/login", methods=["GET", "POST"])
@csrf.exempt 
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
                flash("Incorrect password. Please try again.",
                      category="error")
        else:
            flash("Email not found. Please check your email or sign up.",
                  category="error")

    return render_template("login.html")


@auth.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Logged out successfully.", category="success")
    return redirect(url_for("auth.login"))


# @auth.route("/sign-up", methods=["GET", "POST"])
# def sign_up():
#     print("Signing UP .................")
#     errors = {}

#     if request.method == "POST":
#         email = request.form.get("email")
#         first_name = request.form.get("first_name")
#         last_name = request.form.get("last_name")
#         password1 = request.form.get("password1")
#         password2 = request.form.get("password2")
#         is_teacher = request.form.get("is_teacher") == "on"

#         user = User.query.filter_by(email=email).first()
#         if user:
#             errors['email'] = "Email already exists. Please use a different email or login."

#             flash(
#                 "Email already exists. Please use a different email or login.",
#                 category="error")
#             print(
#                 "Email already exists. Please use a different email or login.")
#         elif not email or len(email) < 4:
#             flash(
#                 "Please provide a valid email address (at least 4 characters).",
#                 category="error")
#             errors['email'] = "Please provide a valid email address (at least 4 characters)."

#         elif not first_name or len(first_name) < 2:
#             errors['first_name'] = "First name must be at least 2 characters long."
#             flash("First name must be at least 2 characters long.",
#                   category="error")
#         elif not last_name or len(last_name) < 2:
#             errors['last_name'] = "Last name must be at least 2 characters long."

#             flash("Last name must be at least 2 characters long.",
#                   category="error")
#         elif not password1 or len(password1) < 7:

#             errors['password1'] = "Password must be at least 7 characters long."
#             flash("Password must be at least 7 characters long.",
#                   category="error")
#         elif password1 != password2:
#             errors['password2'] = "Passwords don't match. Please try again."

#             flash("Passwords don't match. Please try again.", category="error")
#         else:
#             new_user = User(
#                 email=email,
#                 first_name=first_name,
#                 last_name=last_name,
#                 password=generate_password_hash(password1,
#                                                 method="pbkdf2:sha256"),
#                 is_admin=
#                 is_teacher  # Assuming teachers are admins in your system
#             )
#             db.session.add(new_user)
#             db.session.commit()
#             login_user(new_user, remember=True)
#             flash("Account created successfully!", category="success")
#             print("Account created successfully!")
#             return redirect(url_for("views.dashboard"))

#     return render_template("sign_up.html", user=current_user, errors=errors)



@auth.route("/sign-up", methods=["GET", "POST"])
def sign_up():
    errors = {}
    form_data = {
        "email": "",
        "first_name": "",
        "last_name": "",
        "password1": "",
        "password2": "",
        "is_teacher": False
    }

    if request.method == "POST":
        form_data['email'] = request.form.get("email")
        form_data['first_name'] = request.form.get("first_name")
        form_data['last_name'] = request.form.get("last_name")
        form_data['password1'] = request.form.get("password1")
        form_data['password2'] = request.form.get("password2")
        form_data['is_teacher'] = request.form.get("is_teacher") == "on"

        user = User.query.filter_by(email=form_data['email']).first()
        if user:
            errors['email'] = "Email already exists. Please use a different email or login."
        if not form_data['email'] or len(form_data['email']) < 4:
            errors['email'] = "Please provide a valid email address (at least 4 characters)."
        if not form_data['first_name'] or len(form_data['first_name']) < 2:
            errors['first_name'] = "First name must be at least 2 characters long."
        if not form_data['last_name'] or len(form_data['last_name']) < 2:
            errors['last_name'] = "Last name must be at least 2 characters long."
        if not form_data['password1'] or len(form_data['password1']) < 7:
            errors['password1'] = "Password must be at least 7 characters long."
        if form_data['password1'] != form_data['password2']:
            errors['password2'] = "Passwords don't match. Please try again."

        if not errors:
            new_user = User(
                email=form_data['email'],
                first_name=form_data['first_name'],
                last_name=form_data['last_name'],
                password=generate_password_hash(form_data['password1'], method="pbkdf2:sha256"),
                is_admin=form_data['is_teacher']  # Assuming teachers are admins in your system
            )
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=True)
            flash("Account created successfully!", category="success")
            return redirect(url_for("views.dashboard"))

    return render_template("sign_up.html", user=current_user, errors=errors, form_data=form_data)


from flask import render_template, url_for, flash, redirect, request
from flask_mail import Message
from . import mail
from .models import User
from .forms import RequestResetForm, ResetPasswordForm


@auth.route("/reset_password", methods=['GET', 'POST'])
def reset_request():
    print("It worked")
    form = RequestResetForm()
    print(form)
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        print("User  ", user)
        if user:
            print("dashadskl", user.email)
            send_reset_email(user)
        flash(
            'An email has been sent with instructions to reset your password.',
            'info')
        print(
            'An email has been sent with instructions to reset your password.',
            'info')
        return redirect(url_for('auth.login'))
    return render_template('reset_request.html',
                           title='Reset Password',
                           form=form)


@auth.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_token(token):
    user = User.verify_reset_token(token)
    if user is None:
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for('auth.reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash('Your password has been updated! You are now able to log in',
              'success')
        return redirect(url_for('auth.login'))
    return render_template('reset_token.html',
                           title='Reset Password',
                           form=form)


def send_reset_email(user):
    token = user.get_reset_token()
    print("Token", token)
    msg = Message('Password Reset Request',
                  sender="allamprabhuhiremath9@gmail.com",
                  recipients=[user.email])
    msg.body = f'''To reset your password, visit the following link:
{url_for('auth.reset_token', token=token, _external=True)}

If you did not make this request then simply ignore this email and no changes will be made.
'''
    print("fdjh", msg)

    mail.send(msg)
