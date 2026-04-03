# Finance Data Processing Backend - Architecture and Design

This file summarizes system design, architecture, stacks, decisions, implementation details, and future enhancements.

## 1. Overview

Project objective: build a role-based finance dashboard backend with record management, summary analytics, access control, validation, and optional enhancements.

### Core functional areas
- User and role management
- Financial transaction CRUD and filters
- Dashboard summary analytics
- Access control enforcement per role
- Validation and reliable error handling
- Persistence and ORM-based operations
- API documentation + testing

## 2. Technology stack

- Python 3.13+ (language)
- Django 6.0.3 (web framework)
- Django REST Framework (API toolkit)
- djangorestframework-simplejwt (JWT auth)
- drf-yasg (Swagger/OpenAPI docs)
- SQLite (development DB; PostgreSQL possible by config)
- psycopg2-binary (for Postgres driver support)

### Why these stacks?
- Django provides built-in user model, auth, admin interface, migrations, and good structure.
- DRF gives reusable API views, viewsets, permissions, serializers, and request parsing.
- JWT is needed for token-based auth in typical modern SPAs.
- drf-yasg provides standardized API docs for easy review and manual/auto testing.
- SQLite is easy local dev; DB-agnostic ORM uses same code for Postgres or others.

## 3. Project structure

- `finance_backend/` - Django project configuration
  - `settings.py` - INSTALLED_APPS, REST_FRAMEWORK settings, DB config
  - `urls.py` - root URL routes + swagger/redoc
- `core/` app
  - `models.py` - User, FinancialRecord
  - `serializers.py` - UserSerializer, FinancialRecordSerializer
  - `views.py` - UserViewSet, FinancialRecordViewSet, DashboardSummaryView
  - `permissions.py` - role-based permission classes
  - `urls.py` - API router registration
  - `admin.py` - admin views
  - `tests.py` - integration tests
- `README.md` - usage and setup documentation
- `requirements.txt` - dependencies
- `ARCHITECTURE.md` - design explanation (this file)

## 4. Data modeling

### User model
- extends `AbstractUser`
- adds `role` with choices: `viewer`, `analyst`, `admin`
- `is_active` is inherited for status control

### FinancialRecord model
- `user` - foreign key to user who created the record
- `amount`, `type` (income|expense), `category`, `date`, `notes`
- `created_at`, `updated_at` for tracking
- `deleted` for soft delete

## 5. API design and behavior

### Auth
- `/api/token/` - GET JWT pair
- `/api/token/refresh/` - refresh token

### Users (admin-only)
- `/api/users/` CRUD user management
  - role assignment and active status via serializer

### Financial records
- `/api/records/` list/create
- `/api/records/{id}/` retrieve/update/delete
- `/api/records/{id}/restore/` restore soft deleted record

### Dashboard summary
- `/api/dashboard/`
- returns
  - total_income
  - total_expense
  - net_balance
  - category_totals
  - recent_activity
  - monthly_trends
- filters on query params: `start_date`, `end_date`, `category`, `type`

## 6. Access control strategy

Permissions classes in `core/permissions.py`:
- `IsAdmin` for admin-only operations
- `IsAnalystOrAdmin` for read-record operations
- `IsViewerAnalystAdmin` for dashboard and viewer access

`FinancialRecordViewSet.get_permissions()` ensures per-action policy:
- list/retrieve -> analyst/admin
- create/update/delete/restore -> admin

## 7. Features implemented (requirements tracking)

### 1. User and role management
- user CRUD + role assignment
- active/inactive is supported through default user fields
- role-based authorization in `permissions.py`

### 2. Financial records
- record model includes all fields
- create/read/update/delete
- soft delete (`deleted=True`)
- filtering/search/pagination

### 3. Dashboard summaries
- aggregation functions using ORM `Sum()`
- category totals
- recent activities
- monthly trends computed by group by year/month

### 4. Access control
- strict role enforcement in viewsets
- explicit guest-access restrictions

### 5. Validation and error handling
- invalid date returns 400
- clean status codes
- missing or unauthorized requests return 403/404

### 6. Persistence
- SQLite migrations completed
- model relationships and DB concepts enforced

### 7. Optional enhancements
- token auth, pagination, search, soft delete restore
- rate limit configuration
- tests and API docs via drf-yasg

## 8. System flow (end-to-end)

1. Client obtains JWT from `/api/token/`
2. Requests include `Authorization: Bearer <token>`
3. For `/api/users/` and `/api/records/`, DRF checks viewset permission
4. For full summary `/api/dashboard/` anyone with role can query
5. Records are filtered on query args at `get_queryset`
6. `DELETE` sets `deleted` flag, record excluded from list
7. `POST /api/records/{id}/restore/` clears `deleted`
8. All DB transactions done via Django ORM

## 9. Testing strategy

- Unit/integration tests in `core/tests.py` cover:
  - role-based access
  - record create/update/delete/restore
  - search filter
  - dashboard response structure

- execute with: `python manage.py test`

## 10. Future improvements

1. Multi-tenant data scoping (`user` vs team scope)
2. Stronger role policy engine and permissions table
3. audit logs for record changes
4. full-text search (Elasticsearch or PostgreSQL tsvector)
5. rate-limit per endpoint + protection for login
6. soft delete purge routine + restore timeline
7. OpenAPI test harness / contract tests
8. switch DB to PostgreSQL in prod with migrations
9. support CSV upload for bulk financial records
10. add support for recurring entries and forecast analytics

## 11. Why this approach

- Django + DRF is the quickest path to reliable and maintainable backend.
- Model-based approach ensures correct data integrity and built-in admin support.
- Viewsets and routers provide standard REST patterns and keep endpoints easy to follow.
- Custom permission classes make logic explicit and interview-ready.
- Endpoint-level docs via `drf-yasg` make review and QA easy.
- Tests provide evidence of correctness and guard against regressions.

## 12. How to verify in future interviews

- run `python manage.py runserver` and open `/swagger/`
- authenticate and test each role with sample data
- show `/api/dashboard/` with filters and analytics
- demonstrate soft delete + restore
- show test suite success

---

