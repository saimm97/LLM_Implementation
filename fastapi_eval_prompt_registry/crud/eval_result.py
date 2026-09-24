from sqlalchemy import select
from config.database_connection import get_sqlalchemy_session
from models import EvalResult
from sqlalchemy.exc import SQLAlchemyError
from schemas.eval_result import EvalResultModel

db_session = get_sqlalchemy_session()


def get_eval_results() -> [EvalResult]:
    return db_session.scalars(select(EvalResult)).all()


def show_eval_result(eval_result_id: int):
    return db_session.get(EvalResult, eval_result_id)


def update_eval_result(
    eval_result_id: int, eval_result_model: EvalResultModel
) -> EvalResult:
    try:
        pre_updated_obj = db_session.get(EvalResult, eval_result_id)
        if pre_updated_obj:
            dict_ = pre_updated_obj.__dict__
            stored_eval_result_model = EvalResultModel(**dict_)
            updated_obj = eval_result_model.model_dump(exclude_unset=True)

            updated_obj = stored_eval_result_model.model_copy(update=updated_obj)
            for key, value in updated_obj.items():
                setattr(pre_updated_obj, key, value)

            db_session.commit()
            db_session.refresh(pre_updated_obj)

            result = pre_updated_obj
        else:
            result = None
        return result
    except SQLAlchemyError:
        raise


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


def delete_eval_result(eval_result_id) -> EvalResult | None:
    try:
        eval_result_object = db_session.get(EvalResult, eval_result_id)
        if eval_result_object is not None:
            db_session.delete(eval_result_object)
            db_session.commit()
            return eval_result_object
        else:
            return None
    except SQLAlchemyError:
        db_session.rollback()
        raise
