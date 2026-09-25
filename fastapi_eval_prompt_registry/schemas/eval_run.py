import datetime
from enum import Enum
from pydantic import BaseModel
from sqlalchemy.sql import func

class EvalRunSchema(BaseModel):
    id: int
    p95_latency_ms: float = 0.0
    accuracy: float = 0.0
    average_cost: float = 0.0
    model_used: str
    prompt_version_id: int
    created_at:  datetime.date = func.now()
    updated_at:  datetime.date = func.now()
