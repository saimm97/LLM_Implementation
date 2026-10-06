from fastapi import APIRouter
import crud.prompt_family as prompt_family_crud
import exceptions as exceptions
from schemas.prompt_families import PromptFamilyCreateSchema, PromptFamilyResponseSchema

router = APIRouter()

@router.get("/prompt_families")
def get_prompt_families():
    return prompt_family_crud.get_prompt_families()

@router.get("/prompt_families/{prompt_family_id}")
def show_prompt_family(prompt_family_id: int):
    prompt_family_obj = prompt_family_crud.show_prompt_family(prompt_family_id)
    if prompt_family_obj is None:
        exceptions.raise_404_not_found("PromptFamily", prompt_family_id)
    return prompt_family_obj

@router.post(
    "/prompt_families", response_model=PromptFamilyResponseSchema, status_code=201
)
def create_prompt_family(prompt_family_obj: PromptFamilyCreateSchema):
   return prompt_family_crud.create_prompt_family(prompt_family_obj)

@router.patch(
    "/prompt_families/{prompt_family_id}", response_model=PromptFamilyResponseSchema
)
def update_prompt_family(
    prompt_family_id: int, prompt_family_update_obj: PromptFamilyCreateSchema
):
    prompt_family = prompt_family_crud.update_prompt_family(
        prompt_family_id, prompt_family_update_obj
    )
    if prompt_family is None:
        exceptions.raise_404_not_found("PromptFamily", prompt_family_id)
    return prompt_family

@router.delete("/prompt_families/{prompt_family_id}")
def delete_prompt_family(prompt_family_id: int):
    return prompt_family_crud.delete_prompt_family(prompt_family_id)
