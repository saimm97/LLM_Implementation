import datetime
# from pydoc import text
from enum import Enum
from pydantic import BaseModel
from sqlalchemy.sql import func
from models import OutputCategories, EvalResultStatusEnum


class EvalResultModel(BaseModel):
    input: str
    predicted_category: OutputCategories = OutputCategories.SPT
    raw_output: str
    input_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0
    passed: bool
    latency_ms: int = 0
    cost: float = 0
    error_message: str
    status: EvalResultStatusEnum
    created_at: datetime.date = func.now()
    updated_at: datetime.date = func.now()
    golden_example_id: int
    eval_run_id: int
