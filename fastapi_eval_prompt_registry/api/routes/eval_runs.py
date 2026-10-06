from fastapi import APIRouter
from schemas.eval_run import EvalRunCreateSchema, EvalRunResponseSchema
import crud.eval_run as eval_run_crud
import exceptions as exceptions

router = APIRouter()

@router.get("/eval_runs")
def get_eval_runs():
    return eval_run_crud.get_eval_runs()

@router.get("/eval_runs/{eval_run_id}", response_model=EvalRunResponseSchema)
def show_eval_run(eval_run_id: int):
    eval_run_obj = eval_run_crud.show_eval_run(eval_run_id)
    if eval_run_obj is None:
        exceptions.raise_404_not_found("EvalRun", eval_run_id)
    return eval_run_obj

@router.post("/eval_runs", response_model=EvalRunResponseSchema, status_code=201)
def create_eval_runs(eval_run_schema: EvalRunCreateSchema):
    return eval_run_crud.create_eval_run(eval_run_schema)

@router.patch("/eval_runs/{eval_run_id}", response_model=EvalRunResponseSchema)
def update_eval_run(eval_run_id: int, eval_run_object: EvalRunCreateSchema):
    eval_run_obj = eval_run_crud.update_eval_run(eval_run_id, eval_run_object)
    if eval_run_obj is None: 
      exceptions.raise_404_not_found("EvalRun",eval_run_id)
    return eval_run_obj

@router.delete("/eval_runs/{eval_run_id}",response_model=EvalRunResponseSchema)
def delete_eval_run(eval_run_id: int):
    eval_run_deleted_object = eval_run_crud.delete_eval_run(eval_run_id)
    if eval_run_deleted_object is None:
        exceptions.raise_404_not_found("EvalRun",eval_run_id)
    return eval_run_deleted_object
