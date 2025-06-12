---

# Developer Reference Guide

## Project Overview

This project is a modular application structured for scalability and maintainability. It follows common Python project conventions and supports testing, configuration management, and service-based architecture.

---

## Directory Structure & Purpose

```
.
├── app/                 # Core application logic and structure
├── config/              # Application configuration (app settings, database, logging)
├── database/            # Migrations and seed data
├── docs/                # Documentation files and assets
├── handlers/            # Interfaces for inference or main entry logic
├── storage/             # Persistent data (e.g., logs, cache, traces)
├── tests/               # Automated tests (unit, integration, E2E)
```

---

## Detailed Structure

### `app/`

Contains the business logic and domain services.

* `exceptions/` – Custom exception classes
* `helpers/` – Utility functions used throughout the app
* `middlewares/` – Middleware components (e.g., for request/response processing)
* `models/` – Domain models or data schemas
* `requests/` – Request validation and schema definitions
* `responses/` – Standardized API response formatters
* `services/` – Core application logic and reusable service functions

### `config/`

Handles configuration management.

* `app.py` – Main application settings (e.g., environment, debug mode)
* `database.py` – DB connection configuration
* `log.py` – Logging formatters and handlers

### `database/`

Database versioning and initialization.

* `migrations/` – Versioned migration scripts
* `seeders/` – Seed data for local/dev environments

### `docs/`

Documentation and branding.

* `CODE_OF_CONDUCT.md` – Behavior guidelines for contributors
* `CONTRIBUTING.md` – Instructions for contributing
* `logo.png` – Project logo or branding asset

### `handlers/`

This module handles requests or entry points for the app (e.g., API endpoints, inference models).

* `inference.py` – Main entry point for model inference logic

### `storage/`

Filesystem storage for runtime artifacts.

* `core/` – Application-level persistent storage
* `logs/` – Application logs
* `traces/` – Distributed tracing data

### `tests/`

Testing suite organized by scope.

* `unit/` – Isolated unit tests
* `integration/` – Integration tests across components
* `e2e/` – End-to-end tests simulating full user flows
* `conftest.py` – Pytest fixtures and test config

---

## Dependency Management

* `pyproject.toml` – Project metadata and dependency definitions (Poetry)
* `poetry.lock` – Locked dependency versions
* `requirements.txt` – Optional pip-compatible list for environments not using Poetry

---

## Testing & Linting

* Use `pytest` for running tests:

  ```bash
  pytest tests/
  ```

---

## Logging & Tracing

Logs are saved in `storage/logs`. Traces, if applicable (e.g., for performance profiling or observability), are stored in `storage/traces`.

Configuration can be adjusted in `config/log.py`.

---

## Environment Configuration

The app settings are defined in `config/app.py`. Use `.env` files or environment variables to manage secrets and config overrides for different environments.

---

## Development Tips

* Follow PEP8 and project linting rules.
* Add type hints where possible for better code quality.
* Document your modules and functions using docstrings.
* Prefer services in `app/services` for business logic to keep handlers lean.

---

Let me know if you'd like this customized for a Flask/FastAPI/Django/ML project or add diagrams like architecture or request flow.
