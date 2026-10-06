import datetime
from enum import Enum
from pydantic import BaseModel
from sqlalchemy.sql import func

class EvalRunCreateSchema(BaseModel): # Modifications
    p95_latency_ms: float
    accuracy: float
    average_cost: float
    model_used: str
    prompt_version_id: int

class EvalRunResponseSchema(BaseModel): # Modifications
    id: int
    p95_latency_ms: float
    accuracy: float
    average_cost: float
    model_used: str
    prompt_version_id: int
    created_at:  datetime.datetime
    updated_at:  datetime.datetime
