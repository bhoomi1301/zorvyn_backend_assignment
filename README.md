# Finance Data Processing and Access Control Backend

Django + Django REST Framework backend for finance dashboard assignment.

## Features

- User role management (Viewer / Analyst / Admin)
- JWT auth with access / refresh tokens
- Financial record CRUD with filtering and soft delete
- Dashboard summaries: total income/expense/net balance, category totals, recent items, monthly trends
- Role-based access control on all endpoints
- Validation/error handling on date filters and required fields

## Stack

- Python 3.13+
- Django 6.0.3
- djangorestframework
- djangorestframework-simplejwt
- SQLite (default; easily switched to PostgreSQL via DATABASES settings)

## Setup

1. Create/activate virtualenv:

```powershell
cd D:\Projects\Zorvyn_assignment
venv\Scripts\activate
```

2. Install deps:

```powershell
pip install -r requirements.txt
```

3. Migrate:

```powershell
python manage.py makemigrations
python manage.py migrate
```

4. Create admin:

```powershell
python manage.py createsuperuser
```

5. Run server:

```powershell
python manage.py runserver
```

## API endpoints

`/api/token/` (POST):
- body: `{'username', 'password'}`

`/api/token/refresh/` (POST):
- body: `{'refresh'}`

`/api/users/` (Admin only): list/create/update/delete users
`/api/records/` (analyst/admin for view, admin for change)
`/api/dashboard/` (viewer/analyst/admin)

## Roles behavior

- Viewer: can only access `/api/dashboard/`
- Analyst: can access `/api/records/` read + `/api/dashboard/`
- Admin: full access (users and records operations)

## Example role creation

1. Create user (admin) in admin UI or API.
2. Create user with `role` set to `analyst` or `viewer`.

## Assumptions

- Role is part of `User.role` to simplify checks.
- `FinancialRecord.deleted` is soft-delete flag.
- Dashboard endpoints produce basic trends and recent activity.

