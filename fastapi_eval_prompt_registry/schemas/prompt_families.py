import datetime

from pydantic import BaseModel

class PromptFamilyCreateSchema(BaseModel):
    name: str

class PromptFamilyResponseSchema(BaseModel):
    id: int
    name: str
    created_at: datetime.datetime
    updated_at: datetime.datetime
