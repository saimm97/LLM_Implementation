from typing import Annotated
import json
import redis
from fastapi import FastAPI,Depends
from dotenv import load_dotenv
from sqlmodel import Session
from db.repository import create_analysis
from db.models import Analysis , get_session , create_db_and_tables 
from configurations.llm_configuration import get_anthropic_client,get_openai_client, call_model
from utils import make_key

app = FastAPI()
redis_client = redis.Redis(host='localhost', port=6379, db=0)
SessionDep = Annotated[Session, Depends(get_session)]
connect_args = {"check_same_thread": False}
parameters = {"temperature": 0.7,"max_tokens": 500,"top_p": 1.0,}

@app.on_event("startup")
def on_startup():
    create_db_and_tables()

load_dotenv()

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/chat")
def chat_with_model(model_name: str, prompt: str,session: SessionDep):

    key = make_key(model_name, prompt, parameters)
    cached = redis_client.get(key)
    response = {}

    if cached:
        return json.loads(cached)
         
    else:
        if model_name == 'claude':
            client = get_anthropic_client()
            call_model("claude-opus-4-8",prompt,client)

        elif model_name == 'openai':
            client = get_openai_client()
            response = call_model("gpt-5.5",prompt,client)     
        
        analysis = Analysis (
            model= model_name,
            prompt= prompt,
            output_text=response.output_text,
            input_tokens=response.usage.input_tokens,
            output_tokens=response.usage.output_tokens,
            cost_in_USD=0
        )
        create_analysis(analysis,session)
        return {"hello" : response}