from fastapi import APIRouter
from schemas import message

router = APIRouter()

@router.get("/", response_model=message.Message)
def read_root() -> message.Message:
    return message.Message(hello="World")

@router.post("/", response_model=message.Message)
def write_root() -> message.Message:
    return message.Message(hello="World")
