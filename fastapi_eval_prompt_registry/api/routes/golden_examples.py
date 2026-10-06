from fastapi import APIRouter
import crud.golden_example as golden_example_crud
import exceptions as execeptions
from schemas.golden_example import (
    GoldenExampleCreateSchema,
    GoldenExampleResponseScehma,
)

router = APIRouter()


@router.get("/golden_examples")
def get_all_golden_examples():
    return golden_example_crud.get_all_golden_examples()


@router.get("/golden_examples/{golden_example_id}")
def show_golden_example(golden_example_id: int):
    golden_example = golden_example_crud.show_golden_example(golden_example_id)
    if golden_example is None:
        execeptions.raise_404_not_found("GoldenExample", golden_example_id)
    return golden_example

@router.post(
    "/golden_examples", response_model=GoldenExampleResponseScehma, status_code=201
)
def create_golden_example(golden_example_create: GoldenExampleCreateSchema):
    return golden_example_crud.create_golden_example(golden_example_create)

@router.patch(
    "/golden_example/{golden_example_id}", response_model=GoldenExampleResponseScehma
)
def update_golden_example(
    golden_example_id: int, golden_example_schema: GoldenExampleCreateSchema
):
    golden_example = golden_example_crud.update_golden_example(
        golden_example_id, golden_example_schema
    )
    if golden_example is None:
        execeptions.raise_404_not_found("GoldenExample", golden_example_id)
    return golden_example

@router.patch("/golden_example/{golden_example_id}",response_model=GoldenExampleResponseScehma)
def delete_golden_example(golden_example_id: int):
  return golden_example_crud.delete_golden_example(golden_example_id)
