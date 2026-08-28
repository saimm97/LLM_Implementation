from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, Query
from sqlmodel import Field, Session, SQLModel, create_engine, select, table
from pydantic import BaseModel, EmailStr


class Analysis(SQLModel,table=True):

    id: int | None = Field(default=None, primary_key=True)
    model: str = Field(index=True)
    prompt: str = Field(index=False)
    output_text: str
    input_tokens: int | None = Field(default=0)
    output_tokens: int | None = Field(default=0)
    cost_in_USD: float | None = Field(default=0)

    def __init_subclass__(cls, handler=None):
        super().__init_subclass__()
        cls.handler = handler

DATABASE_URL = "postgresql://postgres:@localhost:5432/fastapi_llm_integration"
engine = create_engine(DATABASE_URL)

# # sqlite_file_name = "database.db"
# # sqlite_url = f"sqlite:///{sqlite_file_name}"
# connect_args = {"check_same_thread": False}
# engine = create_engine(DATABASE_URL, connect_args=connect_args)

def create_db_and_tables():

    # DATABASE_URL = "postgresql://postgres:@localhost:5432/fastapi_llm_integration"
    # # engine = create_engine(DATABASE_URL)
    # # sqlite_file_name = "database.db"
    # # sqlite_url = f"sqlite:///{sqlite_file_name}"
    # engine = create_engine(DATABASE_URL)
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]

app = FastAPI()


@app.on_event("startup")
def on_startup():
    create_db_and_tables()
