# Spec: Profile Page

## Overview
This feature turns the placeholder `/profile` route into a real, authenticated
account dashboard. A logged-in user can visit `/profile` to see, in one place:
their **account info** (display name, email, and when they joined), a **summary
stats row** of key numbers (total spent, number of expenses, average expense,
top category), a **transaction history table** listing their expenses, and a
**category breakdown** showing how their spending splits across categories. All
data is read from the existing `users` and `expenses` tables for the logged-in
user only. This is the first page in Spendly that is *only* for authenticated
users, so it also introduces the "login required" guard pattern that every later
feature (expense create/edit/delete in Steps 7–9) will reuse. The page is
read-only — creating, editing, and deleting expenses arrive in later steps; this
page will simply display richer data once those exist.

## Depends on
- Step 1 (Database Setup) — requires `get_db()`, the `users` table (`name`,
  `email`, `created_at`) and the `expenses` table (`amount`, `category`, `date`,
  `description`, `user_id`).
- Step 3 (Login and Logout) — requires a working session so `session['user_id']`
  identifies the current user; the profile page reads that id to load the record.

## Routes
- `GET /profile` — render the current user's account dashboard; if there is no
  `session['user_id']`, redirect to `/login` — logged-in only

No other new routes.

## Database changes
No schema changes. The page only reads existing tables via new parameterized
query helpers added to `database/db.py`:
- `get_user_by_id(user_id)` — `SELECT * FROM users WHERE id = ?`
- `get_user_expenses(user_id)` — all of the user's expenses for the transaction
  table: `SELECT id, amount, category, date, description FROM expenses
  WHERE user_id = ? ORDER BY date DESC, id DESC`
- `get_user_expense_summary(user_id)` — single aggregate for the stats row:
  `SELECT COUNT(*) AS count, COALESCE(SUM(amount), 0) AS total,
  COALESCE(AVG(amount), 0) AS average FROM expenses WHERE user_id = ?`
- `get_user_category_breakdown(user_id)` — per-category totals for the breakdown:
  `SELECT category, COUNT(*) AS count, SUM(amount) AS total FROM expenses
  WHERE user_id = ? GROUP BY category ORDER BY total DESC`

No new tables, columns, or constraints.

## Templates
- **Create:**
  - `templates/profile.html` — extends `base.html`; composed of four sections:
    1. **Account info card** — the user's name, email, and "member since" date
       shown in a **human-readable format** (e.g. "July 12, 2026"), formatted in
       the route from `created_at`.
    2. **Summary stats row** — a row of stat tiles: total spent, number of
       expenses, average expense, and top category (the first row of the
       category breakdown, or a neutral placeholder when there are no expenses).
    3 + 4. **Transaction history and category breakdown, side by side** — laid
       out in a **two-column split** (transaction history in the wider left
       column, category breakdown in the right column); the columns stack
       vertically on narrower screens.
       - **Transaction history table** — columns Date, Category, Description,
         Amount; rows from `get_user_expenses()`. Shows an empty-state message
         when the user has no expenses.
       - **Category breakdown** — one row per category (name, total, and its
         share of overall spend), with a proportional bar **shaded by amount
         spent**: a single-hue (green `--accent`) sequential scale, light for
         low spend → full-strength for the highest spender (intensity computed
         in the route, applied as per-bar opacity). Also handles the empty
         state.
- **Modify:**
  - `templates/base.html` — make the logged-in user's name in the navbar
    (`span.nav-user`) a link to `url_for('profile')` so the page is reachable.
    Keep the "Sign out" link unchanged.

## Files to change
- `app.py`:
  - Replace the placeholder `profile()` view with a real handler: if
    `session.get('user_id')` is missing, `redirect(url_for('login'))`; otherwise
    load the user with `get_user_by_id()`, and load `get_user_expenses()`,
    `get_user_expense_summary()`, and `get_user_category_breakdown()`, then
    `render_template("profile.html", ...)` passing all four.
  - If the session id no longer matches a user (stale session), clear the session
    and redirect to `/login`.
- `database/db.py`:
  - Add `get_user_by_id`, `get_user_expenses`, `get_user_expense_summary`, and
    `get_user_category_breakdown`, all using parameterized queries and the
    existing `get_db()` connection pattern.
- `templates/base.html` — link the navbar user name to `/profile` (see Templates).
- `static/css/style.css` — add styles for the profile dashboard (info card, stat
  tiles row, the **two-column split** holding the transaction table and category
  breakdown, and the spend-shaded breakdown bars) using existing CSS variables
  only. The split collapses to one column on narrow screens.

## Files to create
- `templates/profile.html`

## New dependencies
No new dependencies. `session` ships with Flask; all queries use the stdlib
`sqlite3` already used by `database/db.py`. Percentages and formatting are done in
Python/Jinja — no charting library.

## Rules for implementation
- No SQLAlchemy or ORMs
- Parameterised queries only
- Passwords hashed with werkzeug (never display or expose `password_hash` in the
  template or route)
- Use CSS variables — never hardcode hex values (the spend-shaded breakdown bars
  vary a single existing hue via computed opacity, not new hex colors)
- The category breakdown encodes spend magnitude, so its color scale is
  **sequential — one hue, light→dark** (not a rainbow, not judgemental
  status/red-amber-green colors)
- The "member since" date is formatted human-readably in the route (via
  `datetime`), never shown as a raw timestamp
- All templates extend `base.html`
- The profile route must read the user id from the server-side session only —
  never from a query string or form — so a user can only ever see their own data.
  Every expense/summary/breakdown query is filtered by that `user_id`.
- Never render `password_hash` or any secret to the page
- Format money for display with a consistent currency/decimal format; guard
  divide-by-zero when computing averages and category percentages (a user with no
  expenses must render cleanly, not 500)
- Every section (stats, table, breakdown) must have a defined empty state

## Definition of done
- [ ] Visiting `/profile` while logged out redirects to `/login`
- [ ] Visiting `/profile` while logged in renders the page with no errors
- [ ] **Account info:** the page shows the logged-in user's name, email, and a
      "member since" date shown human-readably (e.g. "July 12, 2026"), not a raw
      timestamp
- [ ] **Summary stats row:** shows total spent, number of expenses, average
      expense, and top category, computed only from the logged-in user's expenses
- [ ] **Two-column layout:** the transaction history and category breakdown sit
      side by side on desktop and stack to one column on narrow screens
- [ ] **Transaction history table:** lists the user's expenses with Date,
      Category, Description, and Amount, newest first
- [ ] **Category breakdown:** shows one row per category with its total and its
      share of overall spend; the shares are consistent with the totals, and each
      bar is shaded on a single-hue light→dark scale by amount spent (the highest
      spender is the darkest)
- [ ] All four sections show only the logged-in user's data, never other users'
- [ ] A user (or state) with zero expenses renders every section's empty state
      cleanly with no 500 and no divide-by-zero
- [ ] The rendered HTML never contains the user's `password_hash`
- [ ] The navbar user name links to `/profile` and clicking it opens the page
- [ ] Logging in as the demo account (`demo@spendly.com` / `demo123`) shows that
      account's details, its 8 seeded expenses in the table, and a category
      breakdown across the seeded categories (Food, Transport, Bills, Health,
      Entertainment, Shopping, Other)
- [ ] Restarting the app and revisiting `/profile` still works (no reliance on
      in-memory state beyond the session cookie)
