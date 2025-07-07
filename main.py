from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def hello_world():
  '''
    Hello World Example First Fast API 
  '''
  return {"Hello": "World"}