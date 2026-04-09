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
