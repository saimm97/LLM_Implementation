from fastapi import APIRouter
from schemas.eval_result import EvalResultModel
import crud.eval_result as eval_result_crud
import exceptions as exceptions

router = APIRouter()

@router.get("/eval_results")
def get_eval_results():
    return eval_result_crud.get_eval_results()

@router.get("/eval_results/{eval_result_id}")
def show_eval_result(eval_result_id: int):
    response = eval_result_crud.show_eval_result(eval_result_id)
    if response is None:
        exceptions.raise_404_not_found("EvalResult", eval_result_id)
    return response

@router.patch("/eval_results/{eval_result_id}")
def update_eval_result(eval_result_id: int, eval_result_model: EvalResultModel):
    response = eval_result_crud.update_eval_result(eval_result_id, eval_result_model)
    if response is None:
        exceptions.raise_404_not_found("EvalResult", eval_result_id)
    return response

@router.post("/eval_results",status_code=201)
def create_eval_results(eval_result: EvalResultModel):
    return eval_result_crud.create_eval_result(eval_result)

@router.delete("/eval_results/{eval_result_id}")
def delete_eval_result(eval_result_id: int):
    response = eval_result_crud.delete_eval_result(eval_result_id)
    if response is None:
        exceptions.raise_404_not_found("EvalResult", eval_result_id)
    return response
