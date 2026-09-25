from fastapi import APIRouter
from schemas.eval_run import EvalRunSchema
import crud.eval_run as eval_run_crud
import exceptions as exceptions

router = APIRouter()

@router.get("/eval_runs")
def get_eval_runs():
    eval_run_records = eval_run_crud.get_eval_runs()
    if eval_run_records is None:
        exceptions.raise_404_not_found("EvalRun")
    return eval_run_records

@router.get("/eval_runs/{eval_run_id}")
def show_eval_run(eval_run_id: int):
    eval_run_obj = eval_run_crud.show_eval_run(eval_run_id)
    if eval_run_obj is None:
        exceptions.raise_404_not_found("EvalRun", eval_run_id)

@router.post("/eval_runs")
def create_eval_runs(eval_run_schema: EvalRunSchema):
    return eval_run_crud.create_eval_run(eval_run_schema)

