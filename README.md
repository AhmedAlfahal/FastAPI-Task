# FastAPI Authentication API

A RESTful API built with FastAPI that provides user authentication functionality including user registration and JWT token-based authentication.

## Table of Contents

- [Overview](#overview)
- [Live Deployment](#live-deployment)
- [Setup and Installation](#setup-and-installation)
- [Environment Variables](#environment-variables)
- [Authentication Guide](#authentication-guide)
- [API Endpoints](#api-endpoints)
  - [Hello World](#hello-world)
  - [User Registration](#user-registration)
  - [User Authentication](#user-authentication)
  - [Task Management](#task-management)
    - [Create Task](#create-task)
    - [Get All Tasks](#get-all-tasks)
    - [Get Task by ID](#get-task-by-id)
    - [Update Task](#update-task)
    - [Delete Task](#delete-task)
- [Error Handling](#error-handling)
- [Examples](#examples)

## Overview

This API provides basic authentication features with secure password hashing and JWT token authentication. It uses SQLAlchemy with SQLite for data persistence and includes validation for usernames and passwords.

## Live Deployment

The API is deployed and accessible at: [https://fastapi-task-7jmn.onrender.com](https://fastapi-task-7jmn.onrender.com)

## Setup and Installation

### Prerequisites

- Python 3.10+
- pip package manager

### Installation Steps

1. Clone the repository

```bash
git clone https://github.com/AhmedAlfahal/FastAPI-Task.git
cd FastAPI-Task
```

2. Create and activate a virtual environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies

```bash
pip install -r requirements.txt
```

4. Set up environment variables (see [Environment Variables](#environment-variables) section)

5. Run the application

```bash
uvicorn app.main:app --reload
```

The API will be available at http://localhost:8000

## Environment Variables

Create a `.env` file in the root directory with the following variables:

```
SECRET_KEY=your_secret_key_here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

- `SECRET_KEY`: A secret key used for signing JWT tokens
- `ALGORITHM`: The algorithm used for token signing (HS256 recommended)
- `ACCESS_TOKEN_EXPIRE_MINUTES`: Token expiration time in minutes

## Authentication Guide

This API uses a dual authentication system with JWT tokens and API Keys. All protected endpoints require both authentication methods.

### Step 1: Create a User Account

First, create a user account through the registration endpoint:

```bash
curl -X 'POST' \
  'http://localhost:8000/signup' \
  -H 'Content-Type: application/json' \
  -d '{
  "username": "example_user",
  "password": "StrongP@ss123"
}'
```

Response (201 Created):
```json
{
  "message": "User created successfully"
}
```

### Step 2: Obtain JWT Token

After creating an account, obtain a JWT token by logging in:

```bash
curl -X 'POST' \
  'http://localhost:8000/token' \
  -H 'Content-Type: application/json' \
  -d '{
  "username": "example_user",
  "password": "StrongP@ss123"
}'
```

Response (200 OK):
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

Save the access token for use in subsequent requests.

### Step 3: Access Protected Endpoints

To access protected endpoints, include both:
1. The JWT token in the `Authorization` header (format: `Bearer <token>`)
2. The API Key in the `X-API-Key` header

Example:
```bash
curl -X 'GET' \
  'http://localhost:8000/tasks' \
  -H 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...' \
  -H 'X-API-Key: 123456'
```

> **Note**: For this demo application, the API Key is hardcoded to `123456`. In a production environment, you would generate and manage secure API keys for each client.

## API Endpoints

### Hello World

```
GET /
```

A simple endpoint that returns a greeting message.

**Response**

```json
{
  "Hello": "World"
}
```

### User Registration

```
POST /signup
```

Registers a new user with username and password.

**Request Body**

```json
{
  "username": "example_user",
  "password": "StrongP@ss123"
}
```

**Validation Rules**
- Username must be at least 3 characters long
- Username must contain at least one letter or number
- Password must be at least 8 characters long
- Password must contain at least one uppercase letter
- Password must contain at least one lowercase letter
- Password must contain at least one number
- Password must contain at least one special character

**Response (Success - 201 Created)**

```json
{
  "message": "User created successfully"
}
```

### User Authentication

```
POST /token
```

Authenticates a user and returns a JWT token.

**Request Body**

```json
{
  "username": "example_user",
  "password": "StrongP@ss123"
}
```

**Response (Success - 200 OK)**

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

## Error Handling

The API returns appropriate HTTP status codes and error messages for different scenarios:

### Common Error Responses

**400 Bad Request**

- User already exists (during registration)
- User not found (during authentication)
- Incorrect password (during authentication)
- Username or password validation failures

```json
{
  "error": "Error message details"
}
```

**500 Internal Server Error**

```json
{
  "error": "Internal Server Error"
}
```

## Task Management

These endpoints require authentication. You must include the JWT token in the `Authorization` header with the format `Bearer <token>` for all requests.

### Create Task

```
POST /tasks
```

Create a new task for the authenticated user.

**Request Body**

```json
{
  "title": "Complete project",
  "description": "Finish the FastAPI project implementation"
}
```

**Response (Success - 200 OK)**

```json
{
  "id": 1,
  "title": "Complete project",
  "description": "Finish the FastAPI project implementation",
  "status": "pending"
}
```

### Get All Tasks

```
GET /tasks
```

Retrieve all tasks belonging to the authenticated user.

**Response (Success - 200 OK)**

```json
[
  {
    "id": 1,
    "title": "Complete project",
    "description": "Finish the FastAPI project implementation",
    "status": "pending"
  },
  {
    "id": 2,
    "title": "Learn Docker",
    "description": "Study Docker containerization",
    "status": "pending"
  }
]
```

### Get Task by ID

```
GET /tasks/{task_id}
```

Retrieve a specific task by its ID.

**Response (Success - 200 OK)**

```json
{
  "id": 1,
  "title": "Complete project",
  "description": "Finish the FastAPI project implementation",
  "status": "pending"
}
```

### Update Task

```
PUT /tasks/{task_id}
```

Update an existing task. Note: This also marks the task as completed.

**Request Body**

```json
{
  "title": "Complete project",
  "description": "FastAPI project implementation completed"
}
```

**Response (Success - 200 OK)**

```json
{
  "id": 1,
  "title": "Complete project",
  "description": "FastAPI project implementation completed",
  "status": "completed"
}
```

### Delete Task

```
DELETE /tasks/{task_id}
```

Delete a specific task by its ID.

**Response (Success - 200 OK)**

```json
{
  "message": "Task deleted successfully"
}
```

## Examples

### Register a New User

```bash
curl -X 'POST' \
  'http://localhost:8000/signup' \
  -H 'Content-Type: application/json' \
  -d '{
  "username": "john_doe",
  "password": "P@ssw0rd123"
}'
```

### Authenticate a User

```bash
curl -X 'POST' \
  'http://localhost:8000/token' \
  -H 'Content-Type: application/json' \
  -d '{
  "username": "john_doe",
  "password": "P@ssw0rd123"
}'
```

### Create a New Task

```bash
curl -X 'POST' \
  'http://localhost:8000/tasks' \
  -H 'Content-Type: application/json' \
  -H 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...' \
  -H 'X-API-Key: 123456' \
  -d '{
  "title": "Complete documentation",
  "description": "Finish the API documentation"
}'
```

### Retrieve All Tasks

```bash
curl -X 'GET' \
  'http://localhost:8000/tasks' \
  -H 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...' \
  -H 'X-API-Key: 123456'
```

### Retrieve a Specific Task

```bash
curl -X 'GET' \
  'http://localhost:8000/tasks/1' \
  -H 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...' \
  -H 'X-API-Key: 123456'
```

### Update a Task

```bash
curl -X 'PUT' \
  'http://localhost:8000/tasks/1' \
  -H 'Content-Type: application/json' \
  -H 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...' \
  -H 'X-API-Key: 123456' \
  -d '{
  "title": "Complete documentation",
  "description": "Finish the API documentation"
}'
```

### Delete a Task

```bash
curl -X 'DELETE' \
  'http://localhost:8000/tasks/1' \
  -H 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...' \
  -H 'X-API-Key: 123456'
```

---