"""Authentication routes for Legacy DataForce.

Enforces single-account administrative authentication defined in .env.
Provides login and logout endpoints.
Strictly disallows sign-up, registration, or password reset flows.
"""

from urllib.parse import urlparse
from flask import (
    request,
    render_template,
    redirect,
    url_for,
    flash,
    jsonify,
)
from . import auth_bp
from services import (
    is_admin_authenticated,
    authenticate_admin,
    logout_admin,
)


def is_safe_redirect(target: str) -> bool:
    """Ensures redirect target is a safe relative URL within the application."""
    if not target or not isinstance(target, str):
        return False
    target = target.strip()
    if not target.startswith("/") or target.startswith("//"):
        return False
    parsed = urlparse(target)
    return not parsed.netloc and not parsed.scheme


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    """Administrative authentication entry point.

    GET: Renders login page (or redirects to dashboard if already authenticated).
    POST: Authenticates credentials against environment-defined admin account.
    """
    if request.method == "GET":
        if is_admin_authenticated():
            next_url = request.args.get("next")
            if next_url and is_safe_redirect(next_url):
                return redirect(next_url)
            return redirect(url_for("main_bp.index"))
        return render_template("auth/login.html", active_page="login")

    # POST processing (Form or JSON)
    if request.is_json:
        payload = request.get_json(silent=True) or {}
        username = payload.get("username", "").strip()
        password = payload.get("password", "")
    else:
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

    next_url = request.args.get("next") or request.form.get("next")

    if authenticate_admin(username, password):
        if request.is_json:
            return (
                jsonify(
                    {
                        "status": "success",
                        "message": f"Administrative session established for {username}.",
                        "user": username,
                    }
                ),
                200,
            )

        flash(f"Welcome, {username}. Administrative session established.", "success")
        if next_url and is_safe_redirect(next_url):
            return redirect(next_url)
        return redirect(url_for("main_bp.index"))

    # Authentication failure
    if request.is_json:
        return (
            jsonify(
                {
                    "status": "fail",
                    "message": "Invalid administrator username or password. Access denied.",
                    "code": 401,
                }
            ),
            401,
        )

    flash("Invalid administrator credentials. Access denied.", "danger")
    return render_template("auth/login.html", error="Invalid credentials", active_page="login"), 401


@auth_bp.route("/logout", methods=["GET", "POST"])
def logout():
    """Terminates administrative session and redirects to login."""
    was_logged_in = is_admin_authenticated()
    logout_admin()

    if request.is_json:
        return jsonify({"status": "success", "message": "Administrative session ended."}), 200

    if was_logged_in:
        flash("You have been logged out successfully.", "info")
    return redirect(url_for("auth_bp.login"))
