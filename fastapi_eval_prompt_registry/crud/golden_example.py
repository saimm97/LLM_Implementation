from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from config.database_connection import get_sqlalchemy_session
from models import GoldenExample
from schemas.golden_example import GoldenExampleCreateSchema

Session = get_sqlalchemy_session()

def get_all_golden_examples():
    return Session.scalars(select(GoldenExample)).all()

def show_golden_example(golden_example_id: int):
    try:
        golden_example = Session.get(GoldenExample, golden_example_id)
        return golden_example
    except SQLAlchemyError:
        raise

def create_golden_example(golden_example: GoldenExampleCreateSchema):
    try:
        golden_example_create_obj = GoldenExample(**golden_example.model_dump())
        Session.add(golden_example_create_obj)
        Session.commit()
        Session.refresh(golden_example_create_obj)
        return golden_example_create_obj
    except SQLAlchemyError:
        Session.rollback()
        raise


def update_golden_example(
    golden_example_id: int, golden_example_schema: GoldenExampleCreateSchema
):
    try:
        golden_example_obj = Session.get(GoldenExample, golden_example_id)
        if golden_example_obj is not None:
            update_data = golden_example_schema.model_dump(exclude_unset=True)
            for key, value in update_data.items():
                setattr(golden_example_obj, key, value)
            Session.commit()
            Session.refresh(golden_example_obj)
        return golden_example_obj
    except SQLAlchemyError:
        Session.rollback()
        raise

#soft delete
def delete_golden_example(golden_example_id: int):
    try:
        golden_example_obj = Session.get(GoldenExample, golden_example_id)
        if golden_example_obj is not None:
            golden_example_obj.is_active = False
            Session.commit()
            Session.refresh(golden_example_obj)
            return golden_example_obj
    except SQLAlchemyError:
        Session.rollback()
        raise
