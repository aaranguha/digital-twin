#Health Check Point to see if it is running

from fastapi import APIRouter

router = APIRouter(prefix="/api")

@router.get("/health")
def health():
    return {"status": "ok"}
