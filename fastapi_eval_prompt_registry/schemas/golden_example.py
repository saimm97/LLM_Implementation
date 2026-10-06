from pydantic import BaseModel
from enum import Enum
from models import OutputCategories
import datetime


class GoldenExampleCreateSchema(BaseModel):
    input: str
    expected_output: OutputCategories
    is_active: bool


class GoldenExampleResponseScehma(BaseModel):
    id: int
    input: str
    expected_output: OutputCategories
    is_active: bool
    created_at: datetime.datetime
