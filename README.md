# usual-chores

Usual Chores is a simple tool for organizing recurring household tasks.

## Status

The MVP is implemented with Django. It supports one-off and recurring chores,
due dates, assignment, ownership-aware editing, completion history, and a simple
responsive web interface. See [_docs/backlog.md](_docs/backlog.md) for the
completed implementation backlog.

## How to run

Prerequisites:

- Python 3.14 or newer
- [UV](https://docs.astral.sh/uv/)

Install the dependencies and initialize the database:

```bash
uv sync
uv run python manage.py migrate
```

The database migration automatically creates the development admin account so
you can sign in to Django admin and manage users, chores, and completion
history.

Development admin credentials:

- Username: `admin`
- Password: `usual-chores-admin`
- Admin URL: <http://127.0.0.1:8000/admin/>

These credentials are for local development only. Change the password or use
`createsuperuser` before deploying anywhere.

Start the development server:

```bash
uv run python manage.py runserver
```

Open <http://127.0.0.1:8000/> to view chores. The available pages are:

- `/` — upcoming incomplete chores
- `/new/` — create a chore (requires authentication)
- `/accounts/login/` — sign in to the application
- `/accounts/logout/` — sign out of the application
- `/admin/` — manage users, chores, and completion history

Sign in at `/accounts/login/` or `/admin/` before using the authenticated
create, edit, or complete actions in the chore interface.

Run the Django system checks and automated tests with:

```bash
uv run python manage.py check
uv run python manage.py test
```
