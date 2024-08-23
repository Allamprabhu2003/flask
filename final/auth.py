from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user
from flask_wtf import FlaskForm
from werkzeug.security import check_password_hash, generate_password_hash
from wtforms import BooleanField, PasswordField, StringField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError
from flask_mail import Message
from . import mail
from .forms import RequestResetForm, ResetPasswordForm
from .models import User
from . import db
from . import csrf

auth = Blueprint("auth", __name__)


class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Login")


class SignUpForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email(), Length(min=4)])
    first_name = StringField("First Name", validators=[DataRequired(), Length(min=2)])
    last_name = StringField("Last Name", validators=[DataRequired(), Length(min=2)])
    password1 = PasswordField("Password", validators=[DataRequired(), Length(min=7)])
    password2 = PasswordField(
        "Confirm Password",
        validators=[
            DataRequired(),
            EqualTo("password1", message="Passwords must match"),
        ],
    )
    is_teacher = BooleanField("I am a teacher")
    submit = SubmitField("Sign Up")

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError(
                "Email already exists. Please use a different email or login."
            )


@auth.route("/login", methods=["GET", "POST"])
@csrf.exempt
def login():
    if current_user.is_authenticated:
        return redirect(url_for("views.dashboard"))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user)
            flash("Logged in successfully.", category="success")
            next_page = request.args.get("next")
            if next_page:
                return redirect(next_page)
            elif user.is_admin:
                return redirect(url_for("admin.index"))
            else:
                return redirect(url_for("views.dashboard"))
        else:
            flash("Invalid email or password. Please try again.", category="error")

    return render_template("login.html", form=form)


@auth.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Logged out successfully.", category="success")
    return redirect(url_for("auth.login"))


@auth.route("/sign-up", methods=["GET", "POST"])
@csrf.exempt
def sign_up():
    form = SignUpForm()

    errors = {}
    form_data = {
        "email": "",
        "first_name": "",
        "last_name": "",
        "password1": "",
        "password2": "",
        "is_teacher": False,
    }

    if request.method == "POST":
        form_data["email"] = request.form.get("email")
        form_data["first_name"] = request.form.get("first_name")
        form_data["last_name"] = request.form.get("last_name")
        form_data["password1"] = request.form.get("password1")
        form_data["password2"] = request.form.get("password2")
        form_data["is_teacher"] = request.form.get("is_teacher") == "on"

        user = User.query.filter_by(email=form_data["email"]).first()
        if user:
            errors["email"] = (
                "Email already exists. Please use a different email or login."
            )
        if not form_data["email"] or len(form_data["email"]) < 4:
            errors["email"] = (
                "Please provide a valid email address (at least 4 characters)."
            )
        if not form_data["first_name"] or len(form_data["first_name"]) < 2:
            errors["first_name"] = "First name must be at least 2 characters long."
        if not form_data["last_name"] or len(form_data["last_name"]) < 2:
            errors["last_name"] = "Last name must be at least 2 characters long."
        if not form_data["password1"] or len(form_data["password1"]) < 7:
            errors["password1"] = "Password must be at least 7 characters long."
        if form_data["password1"] != form_data["password2"]:
            errors["password2"] = "Passwords don't match. Please try again."

        if not errors:
            new_user = User(
                email=form_data["email"],
                first_name=form_data["first_name"],
                last_name=form_data["last_name"],
                password=generate_password_hash(
                    form_data["password1"], method="pbkdf2:sha256"
                ),
                is_admin=form_data[
                    "is_teacher"
                ], 
            )
            print(new_user)
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=True)
            flash("Account created successfully!", category="success")
            return redirect(url_for("views.dashboard"))

    return render_template(
        "login.html", user=current_user, errors=errors, form_data=form_data, form=form
    )

@auth.route("/reset_password", methods=["GET", "POST"])
def reset_request():
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        print(user)
        if user:
            send_reset_email(user)
        flash(
            "An email has been sent with instructions to reset your password.", "info"
        )
        return redirect(url_for("auth.login"))
    return render_template("reset_request.html", title="Reset Password", form=form)


@auth.route("/reset_password/<token>", methods=["GET", "POST"])

def reset_token(token):
    user = User.verify_reset_token(token)
    print(user)
    if user is None:
        flash("That is an invalid or expired token", "warning")
        return redirect(url_for("auth.reset_request"))
    form = ResetPasswordForm()
    print(form)
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash("Your password has been updated! You are now able to log in", "success")
        return redirect(url_for("auth.login"))
    return render_template("reset_token.html", title="Reset Password", form=form)


def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message(
        "Password Reset Request",
        sender="allamprabhuhiremath2003@gmail.com",
        recipients=[user.email],
    )
    msg.body = f"""To reset your password, visit the following link:
{url_for('auth.reset_token', token=token, _external=True)}

If you did not make this request then simply ignore this email and no changes will be made.
"""
    mail.send(msg)




