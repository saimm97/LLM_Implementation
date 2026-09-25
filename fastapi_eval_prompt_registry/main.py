import uvicorn
from fastapi import FastAPI
from api.routes import eval_results, eval_runs
from config.database_connection import get_sqlalchemy_session

app = FastAPI()

app.include_router(eval_results.router)
app.include_router(eval_runs.router)

@app.get("/")

def home():
  return {"HELLO":"WORLD!!!"}

# session = get_sqlalchemy_session()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)