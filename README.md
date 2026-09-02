# usual-chores

Usual Chores is a simple tool for organizing recurring household tasks.

## Status

Project setup is in progress. See [_docs/plan.md](_docs/plan.md) for the initial implementation plan.

## How to run

Prerequisites:

- Python 3.14 or newer
- [UV](https://docs.astral.sh/uv/)

Install the dependencies and initialize the database:

```bash
uv sync
uv run python manage.py migrate
```

Start the development server:

```bash
uv run python manage.py runserver
```

Open <http://127.0.0.1:8000/> in a browser. Run the Django system checks with:

```bash
uv run python manage.py check
```
