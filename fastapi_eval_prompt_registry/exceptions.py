from pyexpat import model
from fastapi import HTTPException


def raise_404_not_found(model, record_id: int | None=None):
    if record_id is None:
        raise HTTPException(
            status_code=404, detail=f"{model} Object with Id: {record_id} not found"
        )
    else:
        raise HTTPException(status_code=404, detail=f"{model} Records not found")
