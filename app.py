import os
import sqlite3
from datetime import datetime

from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import check_password_hash
from database.db import (
    get_db,
    init_db,
    seed_db,
    get_user_by_email,
    create_user,
    get_user_by_id,
    get_user_expenses,
    get_user_expense_summary,
    get_user_category_breakdown,
)

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-change-me")


@app.template_filter("money")
def money(value):
    return f"৳{(value or 0):,.2f}"

with app.app_context():
    init_db()
    seed_db()


# ------------------------------------------------------------------ #
# Routes                                                              #
# ------------------------------------------------------------------ #

@app.route("/")
def landing():
    return render_template("landing.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if session.get("user_id"):
        return redirect(url_for("landing"))

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        if not name or not email or not password or not confirm_password:
            return render_template(
                "register.html",
                error="All fields are required.",
                name=name,
                email=email,
            )

        if len(password) < 8:
            return render_template(
                "register.html",
                error="Password must be at least 8 characters.",
                name=name,
                email=email,
            )

        if password != confirm_password:
            return render_template(
                "register.html",
                error="Passwords do not match.",
                name=name,
                email=email,
            )

        if get_user_by_email(email):
            return render_template(
                "register.html",
                error="An account with this email already exists.",
                name=name,
                email=email,
            )

        try:
            create_user(name, email, password)
        except sqlite3.IntegrityError:
            return render_template(
                "register.html",
                error="An account with this email already exists.",
                name=name,
                email=email,
            )

        return redirect(url_for("login", registered=1))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if session.get("user_id"):
        return redirect(url_for("landing"))

    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")

        if not email or not password:
            return render_template(
                "login.html",
                error="Email and password are required.",
                email=email,
            )

        user = get_user_by_email(email)
        if user is None or not check_password_hash(user["password_hash"], password):
            return render_template(
                "login.html",
                error="Invalid email or password.",
                email=email,
            )

        session.clear()
        session["user_id"] = user["id"]
        session["user_name"] = user["name"]
        flash("Signed in — welcome back!")
        return redirect(url_for("landing"))

    return render_template("login.html")


@app.route("/terms")
def terms():
    return render_template("terms.html")


@app.route("/privacy")
def privacy():
    return render_template("privacy.html")


# ------------------------------------------------------------------ #
# Placeholder routes — students will implement these                  #
# ------------------------------------------------------------------ #

@app.route("/logout")
def logout():
    session.clear()
    flash("You have been signed out.")
    return redirect(url_for("login"))


@app.route("/profile")
def profile():
    user_id = session.get("user_id")
    if not user_id:
        return redirect(url_for("login"))

    user = get_user_by_id(user_id)
    if user is None:                 # stale session (user no longer exists)
        session.clear()
        return redirect(url_for("login"))

    expenses = get_user_expenses(user_id)
    summary = get_user_expense_summary(user_id)
    breakdown = get_user_category_breakdown(user_id)

    total = summary["total"] or 0
    max_total = max((r["total"] for r in breakdown), default=0)
    # Augment each category row with its share of overall spend (guard /0) and a
    # sequential shade intensity — one hue, light (low spend) -> dark (high spend).
    categories = [
        {
            "category": r["category"],
            "count": r["count"],
            "total": r["total"],
            "pct": (r["total"] / total * 100) if total else 0,
            "intensity": (0.4 + 0.6 * (r["total"] / max_total)) if max_total else 0,
        }
        for r in breakdown
    ]
    top_category = categories[0]["category"] if categories else None

    # Human-readable "member since" (e.g. "July 12, 2026"); fall back to raw value.
    try:
        member_since = datetime.strptime(
            user["created_at"][:10], "%Y-%m-%d"
        ).strftime("%B %d, %Y")
    except (ValueError, TypeError):
        member_since = user["created_at"]

    return render_template(
        "profile.html",
        user=user,
        member_since=member_since,
        expenses=expenses,
        summary=summary,
        categories=categories,
        top_category=top_category,
    )


@app.route("/expenses/add")
def add_expense():
    return "Add expense — coming in Step 7"


@app.route("/expenses/<int:id>/edit")
def edit_expense(id):
    return "Edit expense — coming in Step 8"


@app.route("/expenses/<int:id>/delete")
def delete_expense(id):
    return "Delete expense — coming in Step 9"


if __name__ == "__main__":
    app.run(debug=True, port=5001)
