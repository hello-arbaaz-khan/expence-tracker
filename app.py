import re
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.security import check_password_hash
from database.db import init_app, init_db, seed_db, create_user, get_user_by_email, get_user_by_id

app = Flask(__name__)
app.secret_key = "dev-secret-key"
init_app(app)


# ------------------------------------------------------------------ #
# Helper functions                                                    #
# ------------------------------------------------------------------ #

def is_valid_email(email):
    """
    Validates email format using a simple regex pattern.
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


# ------------------------------------------------------------------ #
# Context processor — makes user info available in all templates      #
# ------------------------------------------------------------------ #

@app.context_processor
def inject_user():
    """
    Makes the current user available in all templates.
    If user_id is in session, fetch user from DB.
    """
    user_id = session.get("user_id")
    if user_id:
        user = get_user_by_id(user_id)
        if user:
            return {"current_user": user}
    return {"current_user": None}


# Initialize database on startup
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
    if request.method == "POST":
        # Get form data
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        # Validate input
        if not name:
            flash("Name is required", "error")
            return redirect(url_for("register"))
        if not email:
            flash("Email is required", "error")
            return redirect(url_for("register"))
        if not is_valid_email(email):
            flash("Invalid email format", "error")
            return redirect(url_for("register"))
        if len(password) < 8:
            flash("Password must be at least 8 characters", "error")
            return redirect(url_for("register"))
        if password != confirm_password:
            flash("Passwords do not match", "error")
            return redirect(url_for("register"))

        # Create user
        try:
            create_user(name, email, password)
            flash("Account created successfully! Please log in.", "success")
            return redirect(url_for("login"))
        except sqlite3.IntegrityError:
            flash("Email already registered", "error")
            return redirect(url_for("register"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    # If already logged in, redirect to landing page
    if session.get("user_id"):
        return redirect(url_for("landing"))

    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")

        if not email or not password:
            flash("Please enter both email and password", "error")
            return redirect(url_for("login"))

        user = get_user_by_email(email)

        if not user or not check_password_hash(user["password_hash"], password):
            flash("Invalid email or password", "error")
            return redirect(url_for("login"))

        session["user_id"] = user["id"]
        flash("Welcome back!", "success")
        return redirect(url_for("profile"))

    return render_template("login.html")


@app.route("/terms-and-conditions")
def terms_and_conditions():
    return render_template("terms_and_conditions.html")


@app.route("/privacy-policy")
def privacy_policy():
    return render_template("privacy_policy.html")


# ------------------------------------------------------------------ #
# Placeholder routes — students will implement these                  #
# ------------------------------------------------------------------ #

@app.route("/logout")
def logout():
    # Only allow logout if user is logged in
    if not session.get("user_id"):
        return redirect(url_for("login"))

    session.clear()
    flash("You have been logged out", "success")
    return redirect(url_for("login"))


@app.route("/profile")
def profile():
    # Auth guard: redirect if not logged in
    if not session.get("user_id"):
        return redirect(url_for("login"))

    # Hardcoded data for Step 4 (Step 5 will query DB)
    user = {
        "name": "Demo User",
        "email": "demo@spendly.com",
        "member_since": "April 2026"
    }

    # Summary stats (hardcoded)
    stats = {
        "total_spent": 423.99,
        "transaction_count": 8,
        "top_category": "Food"
    }

    # Recent transactions (hardcoded)
    transactions = [
        {"date": "2026-04-09", "description": "Coffee shop", "category": "Food", "amount": 12.50},
        {"date": "2026-04-08", "description": "Gym membership", "category": "Health", "amount": 50.00},
        {"date": "2026-04-07", "description": "Restaurant dinner", "category": "Food", "amount": 65.00},
        {"date": "2026-04-05", "description": "Electric bill", "category": "Bills", "amount": 120.00},
    ]

    # Category breakdown (hardcoded)
    categories = [
        {"name": "Food", "total": 163.49, "percentage": 39},
        {"name": "Transport", "total": 75.00, "percentage": 18},
        {"name": "Bills", "total": 120.00, "percentage": 28},
        {"name": "Health", "total": 50.00, "percentage": 12},
        {"name": "Entertainment", "total": 15.99, "percentage": 3},
    ]

    return render_template("profile.html",
                          user=user,
                          stats=stats,
                          transactions=transactions,
                          categories=categories)


@app.route("/expenses/add")
def add_expense():
    return "Add expense — coming in Step 7"


@app.route("/expenses/<int:id>/edit")
def edit_expense(_id):
    return "Edit expense — coming in Step 8"


@app.route("/expenses/<int:id>/delete")
def delete_expense(_id):
    return "Delete expense — coming in Step 9"


if __name__ == "__main__":
    app.run(debug=True, port=5000)
