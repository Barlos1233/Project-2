from functools import wraps

from flask import abort
from flask_login import current_user, login_required


def role_required(role):
    def decorator(view):
        @wraps(view)
        @login_required
        def wrapped(*args, **kwargs):
            if current_user.role != role:
                abort(403)
            return view(*args, **kwargs)

        return wrapped

    return decorator


def vendor_required(view):
    # Check sign-in first, then make sure the person has a vendor account.
    return role_required("Vendor")(view)


student_required = role_required("Student")
