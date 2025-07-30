# django-unmigrated-sql

A Django management command to execute and fake all unmigrated SQL migrations for any or all apps, ignoring errors and not using transactions. Useful for advanced migration troubleshooting and legacy database integration.

## Features
- Runs unmigrated SQL for all or a specific app
- Ignores SQL errors
- Marks migrations as fake
- No transaction wrapping

## Installation

    pip install django-unmigrated-sql

## Django Integration

Add to your `INSTALLED_APPS`:

    INSTALLED_APPS = [
        ...
        'django_unmigrated_sql',
        ...
    ]

## Usage

Run for all apps:

    python manage.py unmigrated-sql

Run for a specific app:

    python manage.py unmigrated-sql <app_label>

## Release Notes

### 0.3.0
- Added human-friendly logging using Python's logging module for all actions and statuses.
- Added MANIFEST.in to ensure README.md is included in PyPI package.
- Improved PyPI long description rendering.
- Added .gitignore for Python, Django, and build artifacts.
- Added command-line flags: `--no-sql-run` (do not execute SQL) and `--no-fake` (do not mark as fake).
- Support for outputting and running SQL for a specific migration (by app and migration id).

### 0.2.0
- Added support for outputting SQL for a specific migration (by app and migration id).
- Improved setup.py and README.md for PyPI compatibility.

### 0.1.0
- Initial release: Run and fake all unmigrated SQL migrations for any or all apps, ignoring errors and not using transactions.
- Marks migrations as fake after running SQL.
- Supports running for all apps or a specific app.

## License

MIT

---

Maintained by [mahiti.org](https://mahiti.org) | Contact: opensource@mahiti.org 