# admin.py
from flask_admin.contrib.sqla import ModelView
from flask_login import current_user

from flask import Blueprint, redirect, request, url_for



admin_bp = Blueprint('admin_bp', __name__)

class AdminModelView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.is_admin

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('auth.login', next=request.url))

