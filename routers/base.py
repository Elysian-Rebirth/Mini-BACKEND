from fastapi import APIRouter

router = APIRouter()

@router.get("/all")
def get_all_components():
    # Returning a minimal structure to prevent frontend crash
    # The frontend expects a dictionary of component categories
    return {}

@router.get("/env")
def get_env():
    # Return mock environment configuration
    return {
        "code": 200,
        "data": {
            "version": "lite-0.1.0",
            "mode": "community",
            "files": {}
        }
    }
