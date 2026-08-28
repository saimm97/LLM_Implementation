from fastapi import FastAPI
from config.database_connection import get_sqlalchemy_session

app = FastAPI()

@app.get("/")
def home():
  return {"HELLO":"WORLD!!!"}

session = get_sqlalchemy_session()