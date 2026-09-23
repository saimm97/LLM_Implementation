from fastapi import APIRouter, HTTPException, status
from sqlalchemy import Null
from models import EvalResult
from schemas.eval_result import EvalResultModel
import crud.eval_result as eval_result_crud
import exceptions as exceptions

router = APIRouter()


@router.get("/eval_results")
def get_eval_results():
    return "hello world"


@router.get("/eval_results/{eval_result_id}")
def show_eval_result(eval_result_id: int):
    try:
        response = eval_result_crud.show_eval_result(eval_result_id)
    except HTTPException as e:
        raise e
    return response


@router.patch("/eval_results/{eval_result_id}")
def update_eval_result(eval_result_id: int, eval_result_model: EvalResultModel):
    response = eval_result_crud.update_eval_result(eval_result_id, eval_result_model)
    if response is None:
        exceptions.raise_404_not_found("EvalResult", eval_result_id)
    return response

@router.post("/eval_results")
def create_eval_results(eval_result: EvalResultModel):
    try:
        response = eval_result_crud.create_eval_result(eval_result)
    except HTTPException as e:
        raise e
    return response
