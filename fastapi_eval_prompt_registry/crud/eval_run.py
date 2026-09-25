from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from config.database_connection import get_sqlalchemy_session
from models import EvalRunner
from schemas.eval_run import EvalRunSchema

session = get_sqlalchemy_session()


def get_eval_runs():
    return session.scalars(select(EvalRunner)).all()


def create_eval_run(eval_run_schema: EvalRunSchema):
    try:
        eval_run_db_obj = EvalRunner(**eval_run_schema.model_dump())
        session.add(eval_run_db_obj)
        session.commit()
        session.refresh(eval_run_db_obj)
        return eval_run_db_obj
    except SQLAlchemyError:
        session.rollback()
        raise


def show_eval_run(eval_run_id: int):
    eval_run_obj = session.get(EvalRunner, eval_run_id)
    return eval_run_obj
