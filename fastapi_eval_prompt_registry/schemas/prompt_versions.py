from sys import version
from pydantic import BaseModel
import datetime


class PromptVersionCreateSchema(BaseModel):
    text: str
    version: str
    is_active: bool
    prompt_family_id: int


class PromptVersionResponseSchema(BaseModel):
    id: int
    text: str
    version: str
    is_active: bool
    prompt_family_id: int
    created_at: datetime.datetime
    updated_at: datetime.datetime
