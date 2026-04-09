# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Spendly - A Flask-based expense tracker web application (educational project).

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run the application
python app.py
```

The app runs on `http://localhost:5001` with debug mode enabled.

## Architecture

- **Framework**: Flask (Python web framework)
- **Database**: SQLite (via `database/db.py` - placeholder for Step 1 implementation)
- **Templates**: Jinja2 HTML templates in `templates/`
- **Static Assets**: CSS and JS in `static/`

## File Structure

```
expense-tracker/
├── app.py              # Main Flask application with routes
├── database/
│   ├── __init__.py     # Empty init file
│   └── db.py           # Database utilities (get_db, init_db, seed_db - placeholders)
├── static/
│   ├── css/style.css   # All styling
│   └── js/main.js      # YouTube video player + modal logic
├── templates/
│   ├── base.html       # Base template with navbar/footer
│   ├── landing.html    # Homepage
│   ├── login.html      # Login page
│   ├── register.html   # Registration page
│   ├── privacy_policy.html
│   └── terms_and_conditions.html
└── requirements.txt
```

## Current Implementation Status

Routes implemented in `app.py`:
- `/` - Landing page
- `/register` - Registration page
- `/login` - Login page
- `/terms-and-conditions` - Terms page
- `/privacy-policy` - Privacy page

Placeholder routes (to be implemented in later steps):
- `/logout` - Step 3
- `/profile` - Step 4
- `/expenses/add` - Step 7
- `/expenses/<id>/edit` - Step 8
- `/expenses/<id>/delete` - Step 9

## Testing

```bash
# Run all tests
pytest

# Run specific test
pytest tests/test_filename.py
```
