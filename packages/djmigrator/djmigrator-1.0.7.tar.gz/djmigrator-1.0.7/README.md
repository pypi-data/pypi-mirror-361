# djmigrator

djmigrator is a Django management extension that provides smart migration handling by deeply comparing Django models with the actual database schema. It automates missing migrations generation and applies them safely, ensuring that the models and database remain consistent without manually tracking changes.

---

## Introduction

In large Django projects, inconsistencies between models and the actual database often happen due to missing migrations, manual database edits, or legacy systems. Traditional Django commands such as `makemigrations` and `migrate` assume perfect sync between models and the database.

djmigrator solves this by:

- Performing deep inspections of your actual database schema.
- Comparing models and fields directly against database tables and columns.
- Identifying missing tables or missing columns.
- Generating and applying only necessary migrations.
- Using smart application strategies to avoid common errors like "table already exists" or "column already exists".

---

## Key Features

- Automatic detection of missing tables or missing columns based on model comparison.
- Safe skipping of already existing tables and fields during migration.
- Automatic generation of migration files only when necessary.
- Application of migrations with `--fake-initial` to synchronize existing tables.
- Clear reporting of discrepancies between models and database.
- Minimal downtime and human intervention required for database synchronization.

---

## How It Works

1. The `smart_makemigrations` command inspects all Django models and their respective tables in the connected database.
2. It identifies:
    - Tables missing in the database.
    - Columns missing inside an existing table.
    - Extra columns existing in the database but not defined in the Django models (reported but not modified).
3. If discrepancies are found:
    - `makemigrations` is automatically triggered to generate new migration files.
    - `migrate --fake-initial` is applied to safely sync without duplicating existing tables.
4. If no discrepancies are found, the command reports a clean synchronization status.

---

## Installation and Setup

To install and set up djmigrator, follow these steps:

### 1. Install the Package

```bash
pip install djmigrator


### 2. Add to Django Settings

Add `djmigrator` to your Django project's `INSTALLED_APPS` in `settings.py`:

```python
INSTALLED_APPS = [
    ...
    'djmigrator',
]

### 3. Migration Command

```bash
python manage.py smart_makemigrations
