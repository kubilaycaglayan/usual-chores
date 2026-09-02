# Backlog

A small, prioritized backlog for building Usual Chores with Django.

## MVP

### task-1 — Create the `chores` Django app ✅

Run `uv run python manage.py startapp chores` and add `chores` to `INSTALLED_APPS`.

**Done when:** Django recognizes the app and `uv run python manage.py check` passes.

### task-2 — Define the chore model ✅

Create a `Chore` model with a name, description, recurrence, due date, completion status, and timestamps.

**Done when:** The model is migrated successfully and has useful `__str__` behavior.

### task-3 — Register chores in the admin ✅

Register `Chore` with the Django admin and configure useful list and search fields.

**Done when:** A staff user can view, add, edit, and filter chores in the admin site.

### task-4 — Build the chore list page ✅

Create a view, URL, and template that display upcoming and incomplete chores.

**Done when:** Visiting the chore list URL shows the relevant chores in a readable format.

### task-5 — Add chore creation and editing ✅

Provide forms and views for creating and updating chores with server-side validation.

**Done when:** Users can submit valid chore data and receive helpful validation errors for invalid data.

### task-6 — Mark a chore complete ✅

Add an action that records completion and updates the chore’s status and completion timestamp.

**Done when:** A user can mark a chore complete from the application and see the updated state.

### task-7 — Add automated tests ✅

Test model behavior, validation, list rendering, and completion behavior.

**Done when:** The test suite passes with `uv run python manage.py test`.

## Later improvements

### task-8 — Add user ownership and assignment ✅

Associate chores with users and restrict editing to authorized users.

### task-9 — Implement recurring due dates ✅

Calculate the next due date when a recurring chore is completed.

### task-10 — Improve the interface ✅

Add navigation, empty states, responsive styling, and clear feedback messages.

## Plan follow-ups

The following items are tracked from [_docs/plan.md](_docs/plan.md) and are not
part of the initial MVP.

### task-11 — Add application authentication ✅

Provide login and logout pages so users can use the authenticated chore actions
without relying on the Django admin.

### task-12 — Add households and membership

Allow users to create and join public, discoverable households with a maximum
of ten members.

### task-13 — Add household personas and seed data

Support seeded themed households and famous-person personas alongside real
users.

### task-14 — Add claim-based chore statuses

Implement Open → Claimed → Done states, one claimant at a time, and household
member access to create and edit chores.

### task-15 — Add chore claiming and unclaiming

Allow members to claim chores and unclaim them only before the deadline.

### task-16 — Add deadline alerts

Highlight overdue chores and show page alerts for claimed chores approaching or
past their deadline.

### task-17 — Add contribution statistics

Show each member’s completed-chore count and transparently recommend chores to
members with lower contributions.

### task-18 — Add deterministic themed demo data

After the household, claiming, and statistics features are available, add
idempotent deterministic seed data for themed public households, persona
members, themed chores, recurring occurrences, deadlines, claims, and
completion history. Follow the detailed requirements in
[_docs/seed-data.md](_docs/seed-data.md).
