from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from config.database_connection import get_sqlalchemy_session
from models import PromptVersion
from schemas.prompt_versions import (
    PromptVersionCreateSchema,
    PromptVersionResponseSchema,
)
from domain_exceptions import PromptVersionInUseError

Session = get_sqlalchemy_session()


def get_all_prompt_versions():
    return Session.scalars(select(PromptVersion)).all()


def show_prompt_version(prompt_version_id: int):
    try:
        return Session.get(PromptVersion, prompt_version_id)
    except SQLAlchemyError:
        raise


def create_prompt_version(
    prompt_version_schema: PromptVersionCreateSchema,
) -> PromptVersionResponseSchema:
    try:
        new_prompt_version = PromptVersion(**prompt_version_schema.model_dump())
        Session.add(new_prompt_version)
        Session.commit()
        Session.refresh(new_prompt_version)
        return new_prompt_version
    except SQLAlchemyError:
        Session.rollback()
        raise


def update_prompt_version(
    prompt_version_id: int, prompt_version_schema: PromptVersionCreateSchema
):
    try:
        pre_update_obj = Session.get(PromptVersion, prompt_version_id)
        update_data = prompt_version_schema.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(pre_update_obj, key, value)
        Session.add(pre_update_obj)
        Session.commit()
        Session.refresh(pre_update_obj)
        return pre_update_obj
    except SQLAlchemyError:
        Session.rollback()
        raise


def delete_prompt_version(prompt_version_id: int):
    try:
        prompt_version = Session.get(PromptVersion, prompt_version_id)
        if prompt_version is not None:
            if not prompt_version.eval_runners:
                Session.delete(prompt_version)
                Session.commit()
                return prompt_version
            else:
                raise PromptVersionInUseError(
                    "PromptVersion cannot be deleted because evaluation runs reference it."
                )
        else:
            return None
    except SQLAlchemyError:
        Session.rollback()
        raise
