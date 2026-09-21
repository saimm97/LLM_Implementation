from config.database_connection import get_sqlalchemy_session
from models import EvalResult
from sqlalchemy.exc import SQLAlchemyError
from schemas.eval_result import EvalResultModel

db_session = get_sqlalchemy_session()

# def get_eval_results(eval_result: EvalResult) -> EvalResult:
# db_session.add(eval_result)
# db_session.commit()
# db_session.refresh(eval_result)
# return eval_result

def create_eval_result(eval_result: EvalResultModel) -> EvalResultModel:

    eval_result_db_object = EvalResult(**eval_result.model_dump())

    with db_session as session:
        session.begin()
        try:
            session.add(eval_result_db_object)
            session.commit()
            session.refresh(eval_result_db_object)
        except SQLAlchemyError:
            session.rollback()
            raise

    return eval_result_db_object
