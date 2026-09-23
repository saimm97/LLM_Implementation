from queue import Empty

from sqlalchemy import Null
from config.database_connection import get_sqlalchemy_session
from models import EvalResult
from sqlalchemy.exc import SQLAlchemyError
from schemas.eval_result import EvalResultModel
from fastapi.encoders import jsonable_encoder


db_session = get_sqlalchemy_session()


def get_eval_results(eval_result: EvalResult) -> [EvalResult]:

    try:
        eval_results = db_session.query(EvalResult).all()
        if eval_results == []:
            result = "No Record found"
        else:
            return eval_results
    except SQLAlchemyError as e:
        raise e
    return eval_results


def show_eval_result(eval_result_id):

    try:
        eval_result = db_session.query(EvalResult).get(eval_result_id)
        if eval_result:
            return eval_result
        else:
            return f"No Record found with Id: {eval_result_id} "
    except SQLAlchemyError as e:
        raise e


def update_eval_result(
    eval_result_id, eval_result_model: EvalResultModel
) -> EvalResult:
    try:
        pre_updated_obj = db_session.get(EvalResult,eval_result_id)
        # stored_item_data = items[item_id]
        if pre_updated_obj:
            dict_ = pre_updated_obj.__dict__
            stored_eval_result_model = EvalResultModel(**dict_)
            update_data = eval_result_model.model_dump(exclude_unset=True)

            updated_obj = stored_eval_result_model.model_copy(update=update_data)
            # pre_updated_obj = jsonable_encoder(updated_obj) # why commented ?

            for key, value in update_data.items():
                setattr(pre_updated_obj, key, value)

            db_session.commit()
            db_session.refresh(pre_updated_obj)

            response = pre_updated_obj
        else:
            response = None
        return response

    except SQLAlchemyError:
        raise


def delete_eval_results(eval_result: EvalResult) -> [EvalResult]:

    try:
        eval_results = db_session.query(EvalResult).all()
        if eval_results == []:
            result = "No Record found"
        else:
            return eval_results
    except SQLAlchemyError as e:
        raise e
    return eval_results


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
