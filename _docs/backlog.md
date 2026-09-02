# Backlog

A small, prioritized backlog for building Usual Chores with Django.

## MVP

### CHORE-001 — Create the `chores` Django app

Run `uv run python manage.py startapp chores` and add `chores` to `INSTALLED_APPS`.

**Done when:** Django recognizes the app and `uv run python manage.py check` passes.

### CHORE-002 — Define the chore model

Create a `Chore` model with a name, description, recurrence, due date, completion status, and timestamps.

**Done when:** The model is migrated successfully and has useful `__str__` behavior.

### CHORE-003 — Register chores in the admin

Register `Chore` with the Django admin and configure useful list and search fields.

**Done when:** A staff user can view, add, edit, and filter chores in the admin site.

### CHORE-004 — Build the chore list page

Create a view, URL, and template that display upcoming and incomplete chores.

**Done when:** Visiting the chore list URL shows the relevant chores in a readable format.

### CHORE-005 — Add chore creation and editing

Provide forms and views for creating and updating chores with server-side validation.

**Done when:** Users can submit valid chore data and receive helpful validation errors for invalid data.

### CHORE-006 — Mark a chore complete

Add an action that records completion and updates the chore’s status and completion timestamp.

**Done when:** A user can mark a chore complete from the application and see the updated state.

### CHORE-007 — Add automated tests

Test model behavior, validation, list rendering, and completion behavior.

**Done when:** The test suite passes with `uv run python manage.py test`.

## Later improvements

### CHORE-008 — Add user ownership and assignment

Associate chores with users and restrict editing to authorized users.

### CHORE-009 — Implement recurring due dates

Calculate the next due date when a recurring chore is completed.

### CHORE-010 — Improve the interface

Add navigation, empty states, responsive styling, and clear feedback messages.
