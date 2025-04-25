from functools import wraps
from flask import abort, redirect, url_for, flash
from flask_login import current_user

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.username != 'admin':
            abort(403)  # 관리자 아니면 접근 금지
        return f(*args, **kwargs)
    return decorated_function

