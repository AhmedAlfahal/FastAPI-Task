# FastAPI Authentication API

A RESTful API built with FastAPI that provides user authentication functionality including user registration and JWT token-based authentication.

## Table of Contents

- [Overview](#overview)
- [Setup and Installation](#setup-and-installation)
- [Environment Variables](#environment-variables)
- [API Endpoints](#api-endpoints)
  - [Hello World](#hello-world)
  - [User Registration](#user-registration)
  - [User Authentication](#user-authentication)
- [Error Handling](#error-handling)
- [Examples](#examples)

## Overview

This API provides basic authentication features with secure password hashing and JWT token authentication. It uses SQLAlchemy with SQLite for data persistence and includes validation for usernames and passwords.

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

---