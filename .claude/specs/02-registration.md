# Spec: Registration

## Overview
This feature implements user registration for Spendly, allowing a new visitor to create an account with a name, email, password, and password confirmation. It builds on the database layer from Step 1 (`database/db.py`) and wires up the existing `register.html` template — which already renders a POST form to `/register` — to a real Flask route that validates input, hashes the password, and inserts a new row into the `users` table. This is the first step in the app's auth flow, required before login, logout, and profile features can exist. on success user can see a success message and then redirected to the login page. This is the entry point of all of the authenticated features that follow.

## Depends on
- Step 1 (Database Setup) — requires `get_db()`, `init_db()`, and the `users` table to exist and work correctly.

## Routes
- `GET /register` — render the registration form — public
- `POST /register` — validate input, create the user, and redirect to login on success (re-render form with error on failure) — public

## Database changes
No database changes. The existing `users` table (`id, name, email, password_hash, created_at`) in `database/db.py` already supports registration. Registration will use parameterized `INSERT` and `SELECT` statements against this existing schema.

## Templates
- **Create:** none
- **Modify:** `templates/register.html` — add a "Confirm password" field below the password field, and add rendering for validation errors returned from the server (already has an `{% if error %}` block wired to the `auth-error` class; confirm field values persist on re-render, e.g. keep entered name/email on failed submit — password fields are never re-populated)

## Files to change
- `app.py` — replace the placeholder `register()` view with a `GET`/`POST` handler that validates form input, checks for duplicate email, hashes the password with `werkzeug.security.generate_password_hash`, inserts the user via `database/db.py`'s `get_db()`, and redirects to `/login` on success

## Files to create
- None

## New dependencies
No new dependencies.

## Rules for implementation
- No SQLAlchemy or ORMs
- Parameterised queries only
- Passwords hashed with werkzeug
- Use CSS variables — never hardcode hex values
- All templates extend `base.html`
- Validate required fields (name, email, password, confirm password) server-side before insert
- Enforce a minimum password length (8 characters, matching the placeholder text already in `register.html`)
- Reject submissions where password and confirm password do not match, with a friendly error
- Catch duplicate-email `UNIQUE` constraint failures and show a friendly error instead of a 500

## Definition of done
- [ ] Visiting `/register` renders the form with no errors
- [ ] Submitting the form with valid name/email/password creates a new row in the `users` table with a hashed password (not plaintext)
- [ ] Submitting the form with valid data redirects to `/login`
- [ ] Submitting with an email that already exists shows an error message on the same page instead of crashing
- [ ] Submitting with a password under 8 characters shows a validation error instead of inserting
- [ ] Submitting with a confirm password that does not match the password shows a validation error instead of inserting
- [ ] Submitting with a missing name, email, password, or confirm password shows a validation error instead of inserting
- [ ] Restarting the app does not affect previously registered users (no data loss, no duplicate seeding)
