from fastapi import APIRouter
from typing import List

router = APIRouter()

@router.get("/list")
def get_variables(flow_id: str, node_id: str):
    return []

@router.post("/")
def save_variable(data: dict):
    return {"id": "mock-variable-id"}
