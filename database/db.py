import sqlite3
from flask import g
from werkzeug.security import generate_password_hash

DATABASE = "spendly.db"


def get_db():
    """
    Returns a SQLite connection with row_factory and foreign keys enabled.
    Uses Flask's g object to reuse connections within a request.
    """
    if "db" not in g:
        conn = sqlite3.connect(DATABASE)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        g.db = conn
    return g.db


def close_db(e=None):
    """
    Closes the database connection at the end of a request.
    """
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    """
    Creates all tables using CREATE TABLE IF NOT EXISTS.
    """
    conn = sqlite3.connect(DATABASE)
    conn.execute("PRAGMA foreign_keys = ON")
    cursor = conn.cursor()

    # Users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Expenses table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            amount REAL NOT NULL,
            category TEXT NOT NULL,
            date TEXT NOT NULL,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
        )
    """)

    conn.commit()
    conn.close()


def get_user_profile(user_id):
    """
    Fetches a user's profile from the database by id.
    Returns a dict with id, name, email, member_since (formatted as "Month YYYY").
    Returns None if user not found.
    """
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, name, email, created_at FROM users WHERE id = ?
    """, (user_id,))

    row = cursor.fetchone()
    conn.close()

    if row:
        user_dict = dict(row)
        # Format created_at as "Month YYYY"
        from datetime import datetime
        created_at = user_dict.get("created_at")
        if created_at:
            try:
                dt = datetime.strptime(created_at, "%Y-%m-%d %H:%M:%S")
                user_dict["member_since"] = dt.strftime("%B %Y")
            except ValueError:
                user_dict["member_since"] = "Unknown"
        else:
            user_dict["member_since"] = "Unknown"
        return user_dict
    return None


def get_user_by_id(user_id):
    """
    Fetches a user from the database by id.
    Returns a dict with id, name, email if found, None otherwise.
    """
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, name, email FROM users WHERE id = ?
    """, (user_id,))

    row = cursor.fetchone()
    conn.close()

    if row:
        return dict(row)
    return None


def get_summary_stats(user_id):
    """
    Fetches expense summary statistics for a user.
    Returns a dict with total_spent, transaction_count, top_category.
    Returns default values if user has no expenses.
    """
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Get total spent and transaction count
    cursor.execute("""
        SELECT
            COALESCE(SUM(amount), 0) as total_spent,
            COUNT(*) as transaction_count
        FROM expenses WHERE user_id = ?
    """, (user_id,))

    row = cursor.fetchone()
    total_spent = row["total_spent"]
    transaction_count = row["transaction_count"]

    # Get top category
    cursor.execute("""
        SELECT category, SUM(amount) as category_total
        FROM expenses WHERE user_id = ?
        GROUP BY category
        ORDER BY category_total DESC
        LIMIT 1
    """, (user_id,))

    top_row = cursor.fetchone()
    conn.close()

    if top_row:
        top_category = top_row["category"]
    else:
        top_category = "—"

    return {
        "total_spent": total_spent,
        "transaction_count": transaction_count,
        "top_category": top_category
    }


def get_recent_transactions(user_id, limit=10):
    """
    Fetches recent transactions for a user, ordered by date descending.
    Returns a list of dicts with date, description, category, amount.
    Returns empty list if user has no expenses.
    """
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("""
        SELECT date, description, category, amount
        FROM expenses
        WHERE user_id = ?
        ORDER BY date DESC
        LIMIT ?
    """, (user_id, limit))

    rows = cursor.fetchall()
    conn.close()

    return [dict(row) for row in rows]


def get_category_breakdown(user_id):
    """
    Fetches category breakdown for a user.
    Returns a list of dicts with name, total, percentage (summing to 100).
    Returns empty list if user has no expenses.
    """
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("""
        SELECT category as name, SUM(amount) as total
        FROM expenses
        WHERE user_id = ?
        GROUP BY category
        ORDER BY total DESC
    """, (user_id,))

    rows = cursor.fetchall()
    conn.close()

    if not rows:
        return []

    # Calculate grand total
    grand_total = sum(dict(row)["total"] for row in rows)

    if grand_total == 0:
        return []

    # Calculate percentages
    categories = []
    for row in rows:
        cat_dict = dict(row)
        raw_pct = (cat_dict["total"] / grand_total) * 100
        cat_dict["percentage"] = round(raw_pct)
        categories.append(cat_dict)

    # Adjust largest category to ensure percentages sum to 100
    total_pct = sum(cat["percentage"] for cat in categories)
    if total_pct != 100 and categories:
        diff = 100 - total_pct
        categories[0]["percentage"] += diff

    return categories


def get_user_by_email(email):
    """
    Fetches a user from the database by email.
    Returns a dict with id, name, email, password_hash if found, None otherwise.
    """
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, name, email, password_hash FROM users WHERE email = ?
    """, (email,))

    row = cursor.fetchone()
    conn.close()

    if row:
        return dict(row)
    return None


def create_user(name, email, password):
    """
    Creates a new user with the given name, email, and password.
    Hashes the password before storing.
    Returns the new user's id.
    Raises sqlite3.IntegrityError if email already exists.
    """
    conn = sqlite3.connect(DATABASE)
    conn.execute("PRAGMA foreign_keys = ON")
    cursor = conn.cursor()

    password_hash = generate_password_hash(password)
    cursor.execute("""
        INSERT INTO users (name, email, password_hash)
        VALUES (?, ?, ?)
    """, (name, email, password_hash))

    user_id = cursor.lastrowid
    conn.commit()
    conn.close()

    return user_id


def seed_db():
    """
    Inserts sample data for development.
    Idempotent - will not duplicate data on repeated runs.
    """
    conn = sqlite3.connect(DATABASE)
    conn.execute("PRAGMA foreign_keys = ON")
    cursor = conn.cursor()

    # Check if data already exists
    cursor.execute("SELECT COUNT(*) FROM users")
    if cursor.fetchone()[0] > 0:
        conn.close()
        return  # Already seeded

    # Demo user with hashed password
    password_hash = generate_password_hash("demo123")
    cursor.execute("""
        INSERT INTO users (name, email, password_hash) VALUES
        ('Demo User', 'demo@spendly.com', ?)
    """, (password_hash,))

    # 8 sample expenses across categories for demo user (user_id=1)
    expenses = [
        (1, 85.50, 'Food', '2026-04-01', 'Grocery shopping'),
        (1, 45.00, 'Transport', '2026-04-02', 'Gas station'),
        (1, 15.99, 'Entertainment', '2026-04-03', 'Netflix subscription'),
        (1, 120.00, 'Bills', '2026-04-05', 'Electric bill'),
        (1, 65.00, 'Food', '2026-04-07', 'Restaurant dinner'),
        (1, 50.00, 'Health', '2026-04-08', 'Gym membership'),
        (1, 12.50, 'Food', '2026-04-09', 'Coffee shop'),
        (1, 30.00, 'Transport', '2026-04-10', 'Bus pass'),
    ]

    cursor.executemany("""
        INSERT INTO expenses (user_id, amount, category, date, description)
        VALUES (?, ?, ?, ?, ?)
    """, expenses)

    conn.commit()
    conn.close()


def init_app(app):
    """
    Initialize the database with the Flask app.
    Registers teardown and provides init command.
    """
    app.teardown_appcontext(close_db)

    @app.cli.command("init-db")
    def init_db_command():
        """Initialize the database."""
        init_db()
        seed_db()
        print("Database initialized and seeded.")


# Export functions for use in app.py
__all__ = ["get_db", "close_db", "init_db", "seed_db", "create_user", "get_user_by_email", "get_user_by_id", "init_app", "get_user_profile", "get_summary_stats", "get_recent_transactions", "get_category_breakdown"]
