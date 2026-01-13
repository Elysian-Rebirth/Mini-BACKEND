from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

@router.get("/config")
def get_web_config():
    # Mock config response
    return {
        "status_code": 200,
        "status_message": "success",
        "data": {
            "login_methods": ["password"],
            "system_version": "v1.0.0",
            "logo": "",
            "title": "Bisheng Lite"
        }
    }
