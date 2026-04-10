#!/usr/bin/env python3
"""
Seed a random Indian user into the database.
"""

import sqlite3
import random
from datetime import datetime
from werkzeug.security import generate_password_hash

DATABASE = "spendly.db"

# Common Pakistani first names (mixed regions/religions)
FIRST_NAMES = [
    "Ahmed", "Ali", "Hassan", "Hussain", "Muhammad", "Bilal", "Omar", "Usman",
    "Hamza", "Saad", "Kashif", "Adnan", "Fahad", "Imran", "Faisal", "Waqas",
    "Ayesha", "Fatima", "Zainab", "Mariam", "Sana", "Hina", "Nadia", "Sadia",
    "Rabia", "Mahnoor", "Kinza", "Hira", "Bushra", "Sidra", "Aliza", "Mahira"
]

# Common Pakistani surnames (mixed regions/religions)
LAST_NAMES = [
    "Khan", "Malik", "Shaikh", "Ansari", "Qureshi", "Syed", "Bukhari", "Gilani",
    "Farooqi", "Usmani", "Deobandi", "Barelvi", "Chishti", "Soharwardi",
    "Butt", "Mir", "Dar", "Lone", "Wani", "Magre",
    "Chaudhry", "Raja", "Bhatti", "Gujjar", "Awan", "Jutt", "Tarar",
    "Rizvi", "Naqvi", "Zaidi", "Abbas", "Jafri", "Hussaini"
]


def get_db_connection():
    """Get a database connection similar to get_db() in db.py."""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def generate_user():
    """Generate a random Indian user with unique email."""
    while True:
        first_name = random.choice(FIRST_NAMES)
        last_name = random.choice(LAST_NAMES)
        name = f"{first_name} {last_name}"

        # Email: firstname.lastname with random 2-3 digit suffix
        email_prefix = f"{first_name.lower()}.{last_name.lower()}"
        number_suffix = random.randint(10, 999)
        email = f"{email_prefix}{number_suffix}@gmail.com"

        # Check if email already exists
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
        existing = cursor.fetchone()
        conn.close()

        if existing is None:
            break

    password_hash = generate_password_hash("password123")
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    return {
        "name": name,
        "email": email,
        "password_hash": password_hash,
        "created_at": created_at
    }


def seed_user():
    """Insert a random Indian user into the database."""
    user = generate_user()

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO users (name, email, password_hash, created_at)
        VALUES (?, ?, ?, ?)
    """, (user["name"], user["email"], user["password_hash"], user["created_at"]))

    conn.commit()
    user_id = cursor.lastrowid
    conn.close()

    print(f"User seeded successfully!")
    print(f"  id: {user_id}")
    print(f"  name: {user['name']}")
    print(f"  email: {user['email']}")


if __name__ == "__main__":
    seed_user()
