from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def hello_world():
  """Hello World Example First FastAPI"""
  return {"Hello": "World"}