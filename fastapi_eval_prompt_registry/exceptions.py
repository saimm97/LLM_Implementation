from pyexpat import model
from fastapi import HTTPException

def raise_404_not_found(model,record_id):

  raise HTTPException(status_code=404, detail=f"{model} with Id: {record_id} not found")

