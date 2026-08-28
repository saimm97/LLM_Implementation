import os
from anthropic import Anthropic
from openai import OpenAI
from dotenv import load_dotenv
from functools import lru_cache

load_dotenv()

@lru_cache(maxsize=None)
def get_anthropic_client() -> Anthropic :
    return  Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))


@lru_cache(maxsize=None)
def get_openai_client() -> OpenAI :
     return OpenAI(api_key=os.environ.get("OPENAI_API_KEY") )


def call_model(model_type: str,prompt: str,client: object):

    response = {}

    if client.type == Anthropic :
        response = client.messages.create(
            max_tokens=1024,
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            model=model_type,
        )
    elif client.type == OpenAI :
        response = client.responses.create(
                model=model_type,
                instructions="You are a coding assistant that talks like a pirate.",
                input=prompt,
            )

    return response
