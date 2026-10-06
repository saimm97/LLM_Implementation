from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from config.database_connection import get_sqlalchemy_session
from models import PromptFamily
from schemas.prompt_families import PromptFamilyCreateSchema, PromptFamilyResponseSchema

Session = get_sqlalchemy_session()

def get_prompt_families():
    prompt_families = Session.scalars(select(PromptFamily)).all()
    return prompt_families

def show_prompt_family(prompt_family_id: int):
    try:
        prompt_family = Session.get(PromptFamily, prompt_family_id)
        return prompt_family
    except SQLAlchemyError:
        raise

def create_prompt_family(prompt_family_obj: PromptFamilyCreateSchema):
    try:
        new_prompt_family = PromptFamily(**prompt_family_obj.model_dump())
        Session.add(new_prompt_family)
        Session.commit()
        Session.refresh(new_prompt_family)
        return new_prompt_family
    except SQLAlchemyError:
        Session.rollback()
        raise


def update_prompt_family(
    prompt_family_id: int, prompt_family_update: PromptFamilyCreateSchema
):
    try:
        prompt_family_obj = Session.get(PromptFamily, prompt_family_id)
        if prompt_family_obj is not None:
            update_data = prompt_family_update.model_dump(exclude_unset=True)
            for key, value in update_data.items():
                setattr(prompt_family_obj, key, value)
        return prompt_family_obj
    except SQLAlchemyError:
        raise


def delete_prompt_family(prompt_family_id: int):
    try:
        prompt_family_obj = Session.get(PromptFamily, prompt_family_id)
        if prompt_family_obj is not None:
            Session.delete(prompt_family_obj)
            Session.commit()
            Session.refresh()
        return prompt_family_obj
    except SQLAlchemyError:
        Session.rollback()
        raise
