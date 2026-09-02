# usual-chores

Usual Chores is a simple tool for organizing recurring household tasks.

## Status

The application supports public households, seeded personas, member-managed
chores, open/claimed/done statuses, recurring occurrences, completion history,
contribution statistics, and fairness recommendations. See
[_docs/backlog.md](_docs/backlog.md) for the implementation backlog.

## How to run

Prerequisites:

- Python 3.14 or newer
- [UV](https://docs.astral.sh/uv/)

Install the dependencies and initialize the database:

```bash
uv sync
uv run python manage.py migrate
```

The database migrations automatically create the development admin account and
the four deterministic themed demo households, so the complete development
dataset is ready immediately after setup.

Development admin credentials:

- Username: `admin`
- Password: `usual-chores-admin`
- Admin URL: <http://127.0.0.1:8000/admin/>

These credentials are for local development only. Change the password or use
`createsuperuser` before deploying anywhere.

Demo application credentials (also shown on the login page):

- Username: `bong-joon-ho`
- Password: `usual-chores-director`

The demo account is the seeded Movie Directors household's first persona and
can be used to try authenticated chore actions.

Start the development server:

```bash
uv run python manage.py runserver
```

Open <http://127.0.0.1:8000/> to view chores. The available pages are:

- `/` — upcoming incomplete chores
- `/households/` — discover public households
- `/households/new/` — create a household (requires authentication)
- `/households/<slug>/` — members, chores, alerts, statistics, and recommendations
- `/new/` — create a chore (requires authentication)
- `/accounts/login/` — sign in to the application
- `/accounts/signup/` — create an account and sign in
- `/accounts/logout/` — sign out of the application (submitted by the **Sign out** button)
- `/admin/` — manage users, chores, and completion history

Sign in at `/accounts/login/` or `/admin/` before using the authenticated
create, edit, or complete actions in the chore interface.

Run the Django system checks and automated tests with:

```bash
uv run python manage.py check
uv run python manage.py test
uv run python manage.py test chores.tests_integration
```

The full test command includes the integration tests; the final command runs
the integration tests alone when iterating on household, claiming, insights,
or demo-seed behavior.

The demo data is installed automatically by `migrate` and is deterministic and
idempotent. The `seed_demo` management command remains available if you need to
restore the demo dataset manually.
