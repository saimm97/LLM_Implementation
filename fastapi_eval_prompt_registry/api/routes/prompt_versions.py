from fastapi import APIRouter
from schemas.prompt_versions import (
    PromptVersionCreateSchema,
    PromptVersionResponseSchema,
)
import exceptions as exceptions
import crud.prompt_version as prompt_version_crud
from fastapi import HTTPException
from domain_exceptions import PromptVersionInUseError

router = APIRouter()


@router.get("/prompt_versions")
def get_prompt_versions():
    return prompt_version_crud.get_all_prompt_versions()


@router.get("/prompt_versions/{prompt_version_id}")
def show_prompt_version(prompt_version_id: int):
    prompt_version = prompt_version_crud.show_prompt_version(prompt_version_id)
    if prompt_version is None:
        exceptions.raise_404_not_found("PromptVersion", prompt_version_id)
    return prompt_version


@router.post(
    "/prompt_versions", response_model=PromptVersionResponseSchema, status_code=201
)
def create_prompt_version(
    new_prompt_version: PromptVersionCreateSchema,
) -> PromptVersionResponseSchema:
    return prompt_version_crud.create_prompt_version(new_prompt_version)


@router.patch(
    "/prompt_versions/{prompt_version_id}", response_model=PromptVersionResponseSchema
)
def update_prompt_version(
    prompt_version_id: int, prompt_version_schema: PromptVersionCreateSchema
) -> PromptVersionResponseSchema:
    prompt_version = prompt_version_crud.update_prompt_version(
        prompt_version_id, prompt_version_schema
    )

    return prompt_version


@router.delete("/prompt_versions/{prompt_version_id}")
def delete_prompt_version(prompt_version_id: int):
    try:
        prompt_version = prompt_version_crud.delete_prompt_version(prompt_version_id)
        if prompt_version is None:
            exceptions.raise_404_not_found("PromptVersion", prompt_version_id)
        return prompt_version
    except PromptVersionInUseError as error:
        raise HTTPException(status_code=409, detail=str(error)) from error
