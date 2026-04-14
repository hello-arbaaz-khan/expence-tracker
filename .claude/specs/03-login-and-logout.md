# Spec: Login and Logout

## Overview

This feature implements user authentication for Spendly. Users can log in with their email and password, and log out to end their session. The login system verifies credentials against the database, establishes a session using Flask's session mechanism, and protects authenticated routes. Logout clears the session and redirects to the login page. This is a critical step that enables all user-specific features that follow.

## Depends on

- Step 01 — Database setup (users table exists)
- Step 02 — Registration (users can create accounts)

## Routes

- `GET /login` — Render login form — public (already exists as stub, upgrade it)
- `POST /login` — Verify credentials, create session, redirect to profile — public
- `GET /logout` — Clear session, redirect to login — logged-in users

## Database changes

No database changes. The existing `users` table with `id`, `email`, and `password_hash` is sufficient for authentication.

A new helper function should be added to `database/db.py`:
- `get_user_by_email(email)` — Returns user dict with id, name, email if found, None otherwise

## Templates

- **Modify**: `templates/login.html`
  - Change form `action` to `url_for('login')` with `method="post"`
  - Add flash message display block for errors (e.g., "Invalid email or password")
  - Keep existing visual design

## Files to change

- `app.py` — Upgrade `login()` to handle POST, verify credentials, manage session; add `logout()` route
- `database/db.py` — Add `get_user_by_email()` helper function
- `templates/login.html` — Wire up form action and flash message display

## Files to create

None.

## New dependencies

No new dependencies. Uses Flask's built-in `session` object.

## Rules for implementation

- No SQLAlchemy or ORMs
- Parameterised queries only — never use f-strings in SQL
- Verify password with `werkzeug.security.check_password_hash`
- Use Flask `session` to store logged-in user id: `session['user_id'] = user_id`
- Set `session.permanent = True` if persistent sessions needed
- Use `flash()` for error/success messages
- On login success, redirect to `url_for('profile')` (Step 4) or `/` for now
- On logout, clear session with `session.clear()` and redirect to login
- All templates extend `base.html`
- Use CSS variables — never hardcode hex values
- Use `url_for()` for every internal link — never hardcode URLs

## Definition of done

- [ ] `GET /login` renders the login form without errors
- [ ] Submitting valid email/password creates a session and redirects to profile/home
- [ ] Submitting invalid credentials shows "Invalid email or password" error
- [ ] `GET /logout` clears the session and redirects to `/login`
- [ ] Session stores `user_id` — verifiable by inspecting Flask session
- [ ] Password verification uses `check_password_hash` — never plaintext comparison
- [ ] Flash message displayed on login failure
