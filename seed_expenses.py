#!/usr/bin/env python3
"""
Seed realistic dummy expenses for a specific user.
Usage: python seed_expenses.py <user_id> <count> <months>
Example: python seed_expenses.py 1 50 6
"""

import sqlite3
import random
import sys
from datetime import datetime, timedelta

# Database path matching db.py
DATABASE = "spendly.db"

# Category definitions with amount ranges and distribution weights
# Higher weight = more common
CATEGORIES = {
    "Food": {"min": 50, "max": 800, "weight": 30, "descriptions": [
        "Grocery shopping", "Restaurant dinner", "Lunch at office", "Street food",
        "Coffee shop", "Fast food", "Home delivery", "Breakfast", "Snacks",
        "Weekly groceries", "Family dinner", "Cafe visit", "Tiffin service",
        "Biryani order", "Pizza night", "South Indian tiffin", "Chai and samosa"
    ]},
    "Transport": {"min": 20, "max": 500, "weight": 20, "descriptions": [
        "Bus fare", "Auto rickshaw", "Taxi ride", "Metro card recharge",
        "Gas station", "Cab to airport", "Monthly bus pass", "Ola/Uber ride",
        "Fuel refill", "Parking fee", "Bike service", "Train ticket"
    ]},
    "Bills": {"min": 200, "max": 3000, "weight": 15, "descriptions": [
        "Electricity bill", "Water bill", "Internet bill", "Mobile recharge",
        "DTH recharge", "Gas cylinder", "Maintenance charges", "Society bill",
        "Postpaid bill", "Broadband bill", "Power backup"
    ]},
    "Health": {"min": 100, "max": 2000, "weight": 8, "descriptions": [
        "Pharmacy purchase", "Doctor consultation", "Gym membership",
        "Medical test", "Health supplements", "Physiotherapy", "Dental checkup",
        "Eye checkup", "Yoga class", "Ayurvedic medicine"
    ]},
    "Entertainment": {"min": 100, "max": 1500, "weight": 10, "descriptions": [
        "Movie tickets", "Netflix subscription", "Amazon Prime", "Cricket match",
        "Concert tickets", "Gaming subscription", "Theme park", "Bowling",
        "Spotify premium", "YouTube premium", "Standup comedy show"
    ]},
    "Shopping": {"min": 200, "max": 5000, "weight": 12, "descriptions": [
        "New clothes", "Shoes", "Electronics", "Home decor", "Kitchen items",
        "Birthday gift", "Festive shopping", "Mobile accessories", "Watch",
        "Sunglasses", "Bag purchase", "Furniture item"
    ]},
    "Other": {"min": 50, "max": 1000, "weight": 5, "descriptions": [
        "Stationery", "Pet supplies", "Car wash", "Laundry", "Haircut",
        "Beauty salon", "Donation", "Tip", "Miscellaneous", "Small repair"
    ]}
}


def get_db_connection():
    """Get a database connection similar to get_db() in db.py."""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def parse_arguments(args):
    """Parse command line arguments."""
    if len(args) != 3:
        return None

    try:
        user_id = int(args[0])
        count = int(args[1])
        months = int(args[2])
        return {"user_id": user_id, "count": count, "months": months}
    except ValueError:
        return None


def verify_user_exists(user_id):
    """Check if the user exists in the database."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()
    conn.close()
    return user is not None


def generate_expense(user_id, today, months):
    """Generate a single random expense."""
    # Select category based on weights
    categories = list(CATEGORIES.keys())
    weights = [CATEGORIES[cat]["weight"] for cat in categories]
    category = random.choices(categories, weights=weights, k=1)[0]

    cat_data = CATEGORIES[category]
    amount = round(random.uniform(cat_data["min"], cat_data["max"]), 2)
    description = random.choice(cat_data["descriptions"])

    # Random date within the past 'months' range
    days_back = random.randint(0, months * 30)
    expense_date = today - timedelta(days=days_back)

    return {
        "user_id": user_id,
        "amount": amount,
        "category": category,
        "date": expense_date.strftime("%Y-%m-%d"),
        "description": description
    }


def seed_expenses(user_id, count, months):
    """Generate and insert expenses for a user."""
    today = datetime.now().date()

    # Generate all expenses
    expenses = []
    for _ in range(count):
        expense = generate_expense(user_id, today, months)
        expenses.append(expense)

    # Find date range
    dates = [datetime.strptime(e["date"], "%Y-%m-%d").date() for e in expenses]
    min_date = min(dates)
    max_date = max(dates)

    # Insert all expenses in a single transaction
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.executemany("""
            INSERT INTO expenses (user_id, amount, category, date, description)
            VALUES (?, ?, ?, ?, ?)
        """, [
            (e["user_id"], e["amount"], e["category"], e["date"], e["description"])
            for e in expenses
        ])
        conn.commit()

        # Print confirmation
        print(f"Successfully inserted {count} expenses for user {user_id}")
        print(f"Date range: {min_date.strftime('%Y-%m-%d')} to {max_date.strftime('%Y-%m-%d')}")
        print()

        # Show sample of 5 records
        print("Sample expenses (first 5):")
        print("-" * 80)
        for i, e in enumerate(expenses[:5]):
            print(f"  {i+1}. {e['date']} | {e['category']:12} | ₹{e['amount']:>8.2f} | {e['description']}")

    except Exception as ex:
        conn.rollback()
        print(f"Error inserting expenses: {ex}")
        raise
    finally:
        conn.close()


def main():
    # Parse arguments
    args = sys.argv[1:]
    parsed = parse_arguments(args)

    if parsed is None:
        print("Usage: python seed_expenses.py <user_id> <count> <months>")
        print("Example: python seed_expenses.py 1 50 6")
        sys.exit(1)

    user_id = parsed["user_id"]
    count = parsed["count"]
    months = parsed["months"]

    # Verify user exists
    if not verify_user_exists(user_id):
        print(f"No user found with id {user_id}.")
        sys.exit(1)

    # Seed expenses
    seed_expenses(user_id, count, months)


if __name__ == "__main__":
    main()
