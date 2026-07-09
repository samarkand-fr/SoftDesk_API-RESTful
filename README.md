# SoftDesk Support API

Welcome to the SoftDesk Support RESTful API repository. This API allows managing projects, issues, and comments for contributors, featuring a secure JWT authentication system. It has been built following OWASP guidelines, GDPR standards, and the "Green Code" philosophy.

## 🌟 Key Features

- **Robust Authentication**: JWT (JSON Web Tokens) stateless authentication.
- **Granular Authorization**: Object-level permissions ensuring only authors can edit/delete their resources, while contributors have read-only access.
- **GDPR Compliance**:  
  - Age validation (users must be 15 or older).
  - Explicit consent fields (`can_be_contacted`, `can_data_be_shared`).
  - Right to be forgotten (cascade deletion of all user data upon account removal).
- **Green Code / Optimization**:  
  - Global pagination (25 items per page) to reduce payload size.
  - Resolved N+1 queries using `select_related` to minimize database hits.
- **Automated Maintenance**: Configured with GitHub Dependabot to automatically update Python dependencies.

## 🛠 Prerequisites

- **Python 3.10+**
- **Poetry** (for dependency management)

If you haven't installed Poetry yet, you can install it via:

```bash
pip install poetry
```

## 🚀 Installation & Running Locally

1. Clone this repository locally.
2. Install the project dependencies using Poetry:

```bash
poetry install
```

3.Apply database migrations:

```bash
poetry run python manage.py migrate
```

4.Start the Django development server:

```bash
poetry run python manage.py runserver
```

The API will be accessible at: `http://127.0.0.1:8000/`

## 🧪 Running Tests

A comprehensive suite of automated tests covers permissions, GDPR compliance, and right-to-be-forgotten rules. To run the tests:

```bash
poetry run python manage.py test api users
```

---

## 📡 API Endpoints (HTTP Requests)

*Note: Except for User Registration and Token generation, all endpoints require an `Authorization` header with a valid JWT token:*  
`Authorization: Bearer <your_access_token>`

### 👤 Users & Authentication

- **Register a new User**
  - `POST /api/users/`
  - Body: `{"username": "johndoe", "password": "password123", "age": 25, "can_be_contacted": true, "can_data_be_shared": true}`

- **Obtain JWT Token (Login)**
  - `POST /api/token/`
  - Body: `{"username": "johndoe", "password": "password123"}`
  - Returns: `access` and `refresh` tokens.

- **Refresh JWT Token**
  - `POST /api/token/refresh/`
  - Body: `{"refresh": "<your_refresh_token>"}`

### 📂 Projects

- **List Projects (that you contribute to)**
  - `GET /api/projects/`

- **Create a Project**
  - `POST /api/projects/`
  - Body: `{"name": "App iOS", "description": "Mobile App", "type": "iOS"}`

- **Retrieve a Project**
  - `GET /api/projects/{id}/`

- **Update a Project** *(Author only)*
  - `PATCH /api/projects/{id}/`
  - Body: `{"name": "Updated App iOS"}`

- **Delete a Project** *(Author only)*
  - `DELETE /api/projects/{id}/`

### 🤝 Contributors

- **List Contributors (from your projects)**
  - `GET /api/contributors/`
  - Optional Query Param: `?project={id}`

- **Add a Contributor to a Project** *(Project Author only)*
  - `POST /api/contributors/`
  - Body: `{"user": <user_id>, "project": <project_id>}`

- **Remove a Contributor** *(Project Author only)*
  - `DELETE /api/contributors/{id}/`

### 🐛 Issues

- **List Issues (from your projects)**
  - `GET /api/issues/`
  - Optional Query Param: `?project={id}`

- **Create an Issue**
  - `POST /api/issues/`
  - Body: `{"name": "Login bug", "description": "Crash on login", "project": <project_id>, "priority": "HIGH", "tag": "BUG", "status": "To Do"}`
  - *Optional field*: `"assignee": <user_id>` (Must be a project contributor).

- **Retrieve an Issue**
  - `GET /api/issues/{id}/`

- **Update an Issue** *(Author only)*
  - `PATCH /api/issues/{id}/`
  - Body: `{"status": "In Progress"}`

- **Delete an Issue** *(Author only)*
  - `DELETE /api/issues/{id}/`

### 💬 Comments

- **List Comments (from your projects' issues)**
  - `GET /api/comments/`
  - Optional Query Param: `?issue={id}`

- **Create a Comment**
  - `POST /api/comments/`
  - Body: `{"description": "I will fix this today.", "issue": <issue_id>}`

- **Retrieve a Comment**
  - `GET /api/comments/{uuid}/`

- **Update a Comment** *(Author only)*
  - `PATCH /api/comments/{uuid}/`
  - Body: `{"description": "Updated comment text."}`

- **Delete a Comment** *(Author only)*
  - `DELETE /api/comments/{uuid}/`
