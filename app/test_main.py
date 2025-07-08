from fastapi.testclient import TestClient
from main import app
from schemas import Token

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
    
    
    