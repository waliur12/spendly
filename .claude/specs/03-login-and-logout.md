# Spec: Login and Logout

## Overview
This feature completes the core authentication loop for Spendly by turning the existing `login.html` form into a working session-based login, and replacing the placeholder `/logout` route with a real one that ends the session. A registered user can enter their email and password, be verified against the hashed password in the `users` table, and have their identity stored in a Flask `session`. Logging out clears that session and returns them to a public page. This step depends on registration (Step 2) creating accounts and directly enables every authenticated feature that follows (profile, expense CRUD), since those will read the logged-in user's id from the session. after successful login user must see a success message. or if he unable to login due to validation he can see exact validation error message

## Depends on
- Step 1 (Database Setup) — requires `get_db()` and the `users` table with `password_hash`.
- Step 2 (Registration) — requires accounts to exist so there is something to log into; reuses `get_user_by_email()` from `database/db.py`.

## Routes
- `GET /login` — render the sign-in form (redirect to `/` if already logged in) — public
- `POST /login` — verify email + password against the stored hash, set the session on success (re-render form with error on failure) — public
- `GET /logout` — clear the session and redirect to `/login` — logged-in (harmless if called while logged out)

**Guest-only guard:** `/login` and `/register` (both `GET` and `POST`) must be
inaccessible to an already-authenticated user. When `session.get('user_id')` is
set, these views immediately `redirect(url_for('landing'))` before rendering or
processing anything — a logged-in user has no reason to see the auth forms.

## Database changes
No database changes. Login reads the existing `users` table via a parameterized `SELECT` (already provided by `get_user_by_email()` in `database/db.py`). Password verification uses `werkzeug.security.check_password_hash` against the existing `password_hash` column. No new tables, columns, or constraints.

## Templates
- **Create:** none
- **Modify:**
  - `templates/login.html` — no structural change required; it already renders a POST form to `/login` with an `{% if error %}` `auth-error` block and a `registered` success block. Confirm the email value persists on a failed submit (re-render with `email=email`); the password field is never re-populated.
  - `templates/base.html` — make the navbar reflect auth state: when a user is logged in, show their name and a "Sign out" link (to `url_for('logout')`) instead of the "Sign in" / "Get started" links. Use a session-derived flag exposed to templates (e.g. `session.get('user_id')`).

## Files to change
- `app.py`:
  - Set `app.secret_key` (read from an env var with a dev fallback) so `session` works.
  - Replace the GET-only `login()` view with a `GET`/`POST` handler: validate that email and password are present, look up the user with `get_user_by_email()`, verify with `check_password_hash`, and on success store `session['user_id']` (and `session['user_name']`) then redirect to a post-login destination; on failure re-render `login.html` with a single generic "Invalid email or password." error (do not reveal whether the email exists).
  - Replace the placeholder `logout()` view with one that calls `session.clear()` and redirects to `/login`.
  - Add a guest-only guard to the top of both `login()` and `register()`: if `session.get('user_id')` is set, `redirect(url_for('landing'))` before any rendering or form processing.
- `templates/base.html` — navbar auth-state links (see Templates).

## Files to create
- None.

## New dependencies
No new dependencies. `check_password_hash` ships with the already-installed `werkzeug`; `session` ships with Flask.

## Rules for implementation
- No SQLAlchemy or ORMs
- Parameterised queries only
- Passwords hashed with werkzeug (verify with `check_password_hash`, never compare plaintext)
- Use CSS variables — never hardcode hex values
- All templates extend `base.html`
- Store only the user id (and display name) in the session — never the password or hash
- Use a single generic error for bad credentials — do not disclose whether the email is registered
- `app.secret_key` must come from an environment variable with a development-only fallback; never commit a real secret
- Validate that email and password are present server-side before querying

## Definition of done
- [ ] Visiting `/login` renders the form with no errors
- [ ] Submitting valid credentials for an existing user redirects away from `/login` and sets a session cookie
- [ ] After logging in, the navbar shows the user's name and a "Sign out" link instead of "Sign in" / "Get started"
- [ ] Submitting a wrong password shows "Invalid email or password." on the same page instead of logging in
- [ ] Submitting an email that is not registered shows the same generic error (no account-enumeration difference)
- [ ] Submitting with a missing email or password shows a validation error instead of a 500
- [ ] Visiting `/logout` clears the session and redirects to `/login`; the navbar reverts to the logged-out links
- [ ] While logged in, visiting `/login` or `/register` redirects to `/` instead of showing the form (both GET and POST)
- [ ] The demo seed account (`demo@spendly.com` / `demo123`) can log in successfully
- [ ] Restarting the app with a stable `secret_key` does not invalidate the login flow
