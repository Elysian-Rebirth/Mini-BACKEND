from fastapi import APIRouter

router = APIRouter()

@router.get("/all")
def get_all_components():
    # Returning a minimal structure to prevent frontend crash
    # The frontend expects a dictionary of component categories wrapped in standard response
    return {
        "status_code": 200,
        "status_message": "success",
        "data": {}
    }

@router.get("/env")
def get_env():
    # Return mock environment configuration
    return {
        "status_code": 200,
        "status_message": "success",
        "data": {
            "version": "lite-0.1.0",
            "mode": "community",
        }
    }

@router.get("/workstation/config")
def get_workstation_config():
    # Helper endpoint for Linsight/Workstation config
    return {
        "status_code": 200,
        "status_message": "success",
        "data": {
            "features": [],
            "version": "1.0.0"
        }
    }
