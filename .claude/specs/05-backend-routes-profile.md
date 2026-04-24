# Spec: Backend Routes for Profile Page

## Overview
This feature connects the profile page to real data from the database. Instead of hardcoded values, the `/profile` route will query the `users` and `expenses` tables to display the logged-in user's actual profile information, expense statistics, transaction history, and category breakdown. This completes the profile feature by making it dynamic and user-specific.

## Depends on
- Step 1: Database setup (schema with users and expenses tables)
- Step 2: Registration (users can be created)
- Step 3: Login + Logout (session management)
- Step 4: Profile Page (UI template already exists)

## Routes
- GET /profile — already exists, will be updated to fetch real data from database — logged-in only

## Database changes
No new tables or columns. Will add query functions to `database/db.py` to:
- Get user profile info (name, email, created_at)
- Get expense statistics for a user (total spent, transaction count, top category)
- Get recent transactions for a user
- Get category breakdown for a user

## Templates
No template changes. The existing `templates/profile.html` will receive real data instead of hardcoded values.

## Files to change
- `app.py` — update the `/profile` route to query real data from the database instead of using hardcoded values
- `database/db.py` — add new query functions:
  - `get_user_profile(user_id)` — returns user info including created_at
  - `get_expense_stats(user_id)` — returns total_spent, transaction_count, top_category
  - `get_recent_transactions(user_id, limit=10)` — returns recent expenses
  - `get_category_breakdown(user_id)` — returns list of categories with totals and percentages

## Files to create
No new files.

## New dependencies
No new dependencies.

## Rules for implementation
- No SQLAlchemy or ORMs — use raw sqlite3 via `get_db()`
- Parameterised queries only — never string-format SQL
- All database queries must be isolated in `database/db.py` — no raw SQL in `app.py` routes
- Use `session.get("user_id")` to identify the current user
- Handle edge cases: user with no expenses should show zeros/empty lists gracefully
- Format currency values to 2 decimal places
- Format dates in a human-readable format (e.g., "April 2026" for member_since, "Apr 9" for transactions)
- Category breakdown percentages should sum to approximately 100%
- All templates extend `base.html` (already satisfied by existing profile.html)

## Definition of done
- [ ] The `/profile` route fetches the logged-in user's actual name, email, and member_since from the database
- [ ] Summary stats show real values: total_spent, transaction_count, and top_category from the user's expenses
- [ ] Transaction history displays actual expenses from the database, ordered by date descending
- [ ] Category breakdown shows real categories with accurate totals and percentages
- [ ] A user with no expenses sees zeros/empty state gracefully (no errors)
- [ ] The demo user (seeded in database) shows the correct 8 transactions totaling $423.99
- [ ] All database queries use parameterised statements via functions in `database/db.py`
- [ ] No hardcoded expense data remains in `app.py`
