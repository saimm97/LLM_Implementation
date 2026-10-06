import uvicorn
from fastapi import FastAPI
from api.routes import eval_results, eval_runs, golden_examples, prompt_families

app = FastAPI()

app.include_router(eval_results.router)
app.include_router(eval_runs.router)
app.include_router(golden_examples.router)
app.include_router(prompt_families.router)

@app.get("/")

def home():
  return {"HELLO":"WORLD!!!"}

# session = get_sqlalchemy_session()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)