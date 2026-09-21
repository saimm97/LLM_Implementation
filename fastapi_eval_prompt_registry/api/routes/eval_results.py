from fastapi import APIRouter, HTTPException, status
from schemas.eval_results import EvalResultModel
from crud.eval_result import create_eval_result


router = APIRouter()


@router.get("/eval_results")
def get_eval_results():

    return "hello world"

@router.post("/eval_results")
def create_eval_results(eval_result: EvalResultModel):
    try:
        response = create_eval_result(eval_result)
    except HTTPException as e:
        raise e
    return response
