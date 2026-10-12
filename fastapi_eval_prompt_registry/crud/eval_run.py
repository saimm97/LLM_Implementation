from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from config.database_connection import get_sqlalchemy_session
from models import EvalRunner
from schemas.eval_run import EvalRunCreateSchema, EvalRunResponseSchema

session = get_sqlalchemy_session()

def get_eval_runs():
    return session.scalars(select(EvalRunner)).all()

def create_eval_run(eval_run_schema: EvalRunCreateSchema):
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

def update_eval_run(eval_run_id: int, eval_run_object: EvalRunCreateSchema):
    try:
        pre_updated_eval_run_obj = session.get(EvalRunner, eval_run_id)
        if pre_updated_eval_run_obj:
            update_data = eval_run_object.model_dump(exclude_unset=True)
            for key, value in update_data.items():
                setattr(pre_updated_eval_run_obj, key, value)
            session.commit()
            session.refresh(pre_updated_eval_run_obj)
        return pre_updated_eval_run_obj

    except SQLAlchemyError:
        raise

def delete_eval_run(eval_run_id: int):
    try:
        eval_run_obj = session.get(EvalRunner,eval_run_id)
        if eval_run_obj is not None:
            session.delete(eval_run_obj)
            session.commit()
            return eval_run_obj
        else: 
            return None
    except SQLAlchemyError:
        raise