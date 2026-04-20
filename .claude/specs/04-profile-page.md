# Spec: Profile Page

## Overview

This feature creates the user profile page where logged-in users can view and edit their account information. After login (Step 3), users need a place to manage their profile details like name and email. The profile page displays current user information and provides a form to update it. This is essential for user account management and serves as the foundation for user-specific features like expense tracking in later steps.

## Depends on

- Step 01 — Database setup (users table exists)
- Step 02 — Registration (users can create accounts)
- Step 03 — Login and Logout (users can authenticate)

## Routes

- `GET /profile` — Render profile page with user info — logged-in users only
- `POST /profile` — Update user profile (name, email) — logged-in users only

## Database changes

Add a new helper function to `database/db.py`:
- `update_user(user_id, name, email)` — Updates user name and email, returns True on success
- Should raise `sqlite3.IntegrityError` if email already exists

No schema changes needed — existing `users` table has all required columns.

## Templates

- **Create**: `templates/profile.html`
  - Display current user name and email
  - Form with fields: name, email
  - Submit button to save changes
  - Flash message display for success/error feedback
  - Consistent design with existing templates (centered card layout)
  - Extends `base.html`

## Files to change

- `app.py` — Replace placeholder `/profile` route with actual implementation for GET and POST
- `database/db.py` — Add `update_user()` helper function
- `templates/profile.html` — Create new template (replaces the placeholder if one exists)

## Files to create

- `templates/profile.html`

## New dependencies

No new dependencies.

## Rules for implementation

- No SQLAlchemy or ORMs
- Parameterised queries only — never use f-strings in SQL
- Use `flash()` for success/error messages
- Protect `/profile` routes — redirect to `/login` if user not logged in
- On profile update success, redirect to `GET /profile` (PRG pattern)
- Validate email format using existing `is_valid_email()` helper
- Check for duplicate email before update — flash error if taken
- All templates extend `base.html`
- Use CSS variables — never hardcode hex values
- Use `url_for()` for every internal link — never hardcode URLs
- Display current user info using `current_user` from context processor

## Definition of done

- [ ] `GET /profile` redirects to `/login` when not authenticated
- [ ] `GET /profile` renders profile page with user's current name and email when logged in
- [ ] `POST /profile` updates name and email successfully and shows success flash message
- [ ] `POST /profile` shows error flash message when email already exists
- [ ] `POST /profile` shows error flash message when email format is invalid
- [ ] Profile form pre-fills with current user data
- [ ] After update, page redirects to `GET /profile` showing updated info
- [ ] Navbar shows user's updated name after profile change
- [ ] All SQL queries use parameterised statements
