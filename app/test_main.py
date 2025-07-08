from fastapi.testclient import TestClient
from main import app
from schemas import Token
from datetime import datetime
client = TestClient(app)

def test_hello_world():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"Hello": "World"}

def test_signup():
    ## invalid request parameters
    response = client.post("/signup", json={"username": "test"})
    assert response.status_code == 422
    response = client.post("/signup", json={"password": "Test"})
    assert response.status_code == 422
    ## Password must be at least 8 characters long
    response = client.post("/signup", json={"username": "test", "password": "Test"})
    assert response.status_code == 400
    assert response.json() == {"error": "Password must be at least 8 characters long"}
    ## Password must contain at least one uppercase letter
    response = client.post("/signup", json={"username": "test", "password": "testtest"})
    assert response.status_code == 400
    assert response.json() == {"error": "Password must contain at least one uppercase letter"}
    ## Password must contain at least one lowercase letter
    response = client.post("/signup", json={"username": "test", "password": "TESTTEST"})
    assert response.status_code == 400
    assert response.json() == {"error": "Password must contain at least one lowercase letter"}
    ## Password must contain at least one number
    response = client.post("/signup", json={"username": "test", "password": "TestTest"})
    assert response.status_code == 400
    assert response.json() == {"error": "Password must contain at least one number"}
    ## Password must contain at least one special character
    response = client.post("/signup", json={"username": "test", "password": "TestTest1"})
    assert response.status_code == 400
    assert response.json() == {"error": "Password must contain at least one special character"}
    ## Username must be at least 3 characters long
    response = client.post("/signup", json={"username": "te", "password": "Test@123"})
    assert response.status_code == 400
    assert response.json() == {"error": "Username must be at least 3 characters long"}
    ## Username must contain at least one letter or number
    response = client.post("/signup", json={"username": "!#$", "password": "Test@123"})
    assert response.status_code == 400
    assert response.json() == {"error": "Username must contain at least one letter or number"}
    ## Valid user
    response = client.post("/signup", json={"username": "test", "password": "Test@123"})
    assert response.status_code == 201
    assert response.json() == {"message": "User created successfully"}
    ## User Already exists
    response = client.post("/signup", json={"username": "test", "password": "Test@123"})
    assert response.status_code == 400
    assert response.json() == {"error": "User already exists"}

def test_token():
    response = client.post("/token", json={"username": "test", "password": "Test@123"})
    assert response.status_code == 200
    token_data = response.json()
    # Validate it matches the Token model structure
    token_instance = Token(**token_data)
    assert token_instance.token_type == "bearer"
    assert token_instance.access_token is not None
    response = client.post("/token", json={"username": "test", "password": "Test@1234"})
    assert response.status_code == 400
    assert response.json() == {"error": "Incorrect password"}
    response = client.post("/token", json={"username": "test1", "password": "Test@123"})
    assert response.status_code == 400
    assert response.json() == {"error": "User not found"}
    
def test_create_task():
    ## get user token
    response = client.post("/token", json={"username": "test", "password": "Test@123"})
    assert response.status_code == 200
    token_data = response.json()
    ## create a valid task
    response = client.post("/tasks", json={"title": "test", "description": "test"}, headers={"Authorization": f"Bearer {token_data['access_token']}", "X-API-Key": "123456"})
    assert response.status_code == 200
    assert response.json() == {"id": 1, "title": "test", "description": "test", "status": "pending"}
    ## create a task with invalid token
    response = client.post("/tasks", json={"title": "test", "description": "test"}, headers={"Authorization": "Bearer invalid_token", "X-API-Key": "123456"})
    assert response.status_code == 401
    assert response.json() == {"error": "Unauthorized"}
    ## create a task with invalid api key
    response = client.post("/tasks", json={"title": "test", "description": "test"}, headers={"Authorization": f"Bearer {token_data['access_token']}", "X-API-Key": "invalid_api_key"})
    assert response.status_code == 401
    assert response.json() == {"error": "Unauthorized"}
    ## create a task with invalid authorization header
    response = client.post("/tasks", json={"title": "test", "description": "test"}, headers={"Authorization": "invalid_authorization", "X-API-Key": "123456"})
    assert response.status_code == 401
    assert response.json() == {"error": "Unauthorized"}
    ## create another user
    response = client.post("/signup", json={"username": "test2", "password": "Test@123"})
    assert response.status_code == 201
    assert response.json() == {"message": "User created successfully"}
    ## get another user token
    response = client.post("/token", json={"username": "test2", "password": "Test@123"})
    assert response.status_code == 200
    token_data = response.json()
    ## create a task with another user
    response = client.post("/tasks", json={"title": "test2", "description": "test2"}, headers={"Authorization": f"Bearer {token_data['access_token']}", "X-API-Key": "123456"})
    assert response.status_code == 200
    assert response.json() == {"id": 2, "title": "test2", "description": "test2", "status": "pending"}


def test_get_tasks():
    ## get user token
    response = client.post("/token", json={"username": "test", "password": "Test@123"})
    assert response.status_code == 200
    token_data = response.json()
    ## get tasks
    response = client.get("/tasks", headers={"Authorization": f"Bearer {token_data['access_token']}", "X-API-Key": "123456"})
    assert response.status_code == 200
    assert response.json() == [{"id": 1, "title": "test", "description": "test", "status": "pending"}]
    
def test_get_task():
    ## get user token
    response = client.post("/token", json={"username": "test", "password": "Test@123"})
    assert response.status_code == 200
    token_data = response.json()
    ## get task
    response = client.get("/tasks/1", headers={"Authorization": f"Bearer {token_data['access_token']}", "X-API-Key": "123456"})
    assert response.status_code == 200
    assert response.json() == {"id": 1, "title": "test", "description": "test", "status": "pending"}
    ## get task with invalid token
    response = client.get("/tasks/1", headers={"Authorization": "Bearer invalid_token", "X-API-Key": "123456"})
    assert response.status_code == 401
    assert response.json() == {"error": "Unauthorized"}
    ## get task with invalid api key
    response = client.get("/tasks/1", headers={"Authorization": f"Bearer {token_data['access_token']}", "X-API-Key": "invalid_api_key"})
    assert response.status_code == 401
    assert response.json() == {"error": "Unauthorized"}
    ## get task with invalid authorization header
    response = client.get("/tasks/1", headers={"Authorization": "invalid_authorization", "X-API-Key": "123456"})
    assert response.status_code == 401
    assert response.json() == {"error": "Unauthorized"}
    ## get task with invalid task id
    response = client.get("/tasks/2", headers={"Authorization": f"Bearer {token_data['access_token']}", "X-API-Key": "123456"})
    assert response.status_code == 404
    assert response.json() == {"error": "Task not found"}

def test_update_task():
    ## get user token
    response = client.post("/token", json={"username": "test", "password": "Test@123"})
    assert response.status_code == 200
    token_data = response.json()
    ## update task with invalid token
    response = client.put("/tasks/1", json={"title": "test", "description": "test"}, headers={"Authorization": "Bearer invalid_token", "X-API-Key": "123456"})
    assert response.status_code == 401
    assert response.json() == {"error": "Unauthorized"}
    ## update task with invalid api key
    response = client.put("/tasks/1", json={"title": "test", "description": "test"}, headers={"Authorization": f"Bearer {token_data['access_token']}", "X-API-Key": "invalid_api_key"})
    assert response.status_code == 401
    assert response.json() == {"error": "Unauthorized"}
    ## update task with invalid authorization header
    response = client.put("/tasks/1", json={"title": "test", "description": "test"}, headers={"Authorization": "invalid_authorization", "X-API-Key": "123456"})
    assert response.status_code == 401
    assert response.json() == {"error": "Unauthorized"}
    ## update task with invalid task id
    response = client.put("/tasks/2", json={"title": "test", "description": "test"}, headers={"Authorization": f"Bearer {token_data['access_token']}", "X-API-Key": "123456"})
    assert response.status_code == 404
    assert response.json() == {"error": "Task not found"}
    ## update task
    response = client.put("/tasks/1", json={"title": "test", "description": "test"}, headers={"Authorization": f"Bearer {token_data['access_token']}", "X-API-Key": "123456"})
    assert response.status_code == 200
    assert response.json() == {"id": 1, "title": "test", "description": "test", "status": "completed"}


def test_delete_task():
    ## get user token
    response = client.post("/token", json={"username": "test", "password": "Test@123"})
    assert response.status_code == 200
    token_data = response.json()
    ## delete task with invalid token
    response = client.delete("/tasks/1", headers={"Authorization": "Bearer invalid_token", "X-API-Key": "123456"})
    assert response.status_code == 401
    assert response.json() == {"error": "Unauthorized"}
    ## delete task with invalid api key
    response = client.delete("/tasks/1", headers={"Authorization": f"Bearer {token_data['access_token']}", "X-API-Key": "invalid_api_key"})
    assert response.status_code == 401
    assert response.json() == {"error": "Unauthorized"}
    ## delete task with invalid authorization header
    response = client.delete("/tasks/1", headers={"Authorization": "invalid_authorization", "X-API-Key": "123456"})
    assert response.status_code == 401
    assert response.json() == {"error": "Unauthorized"}
    ## delete task with invalid task id
    response = client.delete("/tasks/2", headers={"Authorization": f"Bearer {token_data['access_token']}", "X-API-Key": "123456"})
    assert response.status_code == 404
    assert response.json() == {"error": "Task not found"}
    ## delete task
    response = client.delete("/tasks/1", headers={"Authorization": f"Bearer {token_data['access_token']}", "X-API-Key": "123456"})
    assert response.status_code == 200
    assert response.json() == {"message": "Task deleted successfully"}