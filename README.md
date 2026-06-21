# SoftDesk Support API

Welcome to the SoftDesk Support RESTful API repository. This API allows managing issues from various projects for contributors, featuring secure JWT authentication.

## Prerequisites

- **Python 3.10+**
- **Poetry** (for dependency management)

If you haven't installed Poetry yet, you can install it via:

```bash
pip install poetry
```

## Installation

1. Clone this repository locally (if you haven't already).
2. Install the project dependencies using Poetry:

```bash
poetry install

```

*(This will create a virtual environment and install Django, DRF, etc.)*

3. (Optional) If you want to activate the virtual environment in your current shell:

```bash
poetry shell
```

## Running Locally

1. First, make sure the database migrations (SQLite by default) are applied:

```bash
poetry run python manage.py migrate
```

2. Start the Django development server:

```bash
poetry run python manage.py runserver
```

The API will be accessible at the following address: `http://127.0.0.1:8000/`

## Features Included

- Initial project setup with Django REST Framework.
- Dependency management using Poetry (`pyproject.toml`).
- Database Models Architecture:
  - User (`User`) with GDPR checks (`age`, `can_be_contacted`, `can_data_be_shared`).
  - Project (`Project`).
  - Contributor (`Contributor`).
  - Issue/Task (`Issue`).
  - Comment (`Comment`).
- Basic JWT setup for future authentication endpoints.
