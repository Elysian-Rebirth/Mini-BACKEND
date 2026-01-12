from fastapi import APIRouter
from typing import List

router = APIRouter()

@router.get("/")
def get_components():
    # Return empty list or mock components if needed
    # Frontend expects {data: ...} or list?
    # flow.ts: return await axios.get(`/api/v1/component`); -> components.ts likely expects list
    return []
