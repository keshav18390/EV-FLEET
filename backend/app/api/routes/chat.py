from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.fleet import ChatRequest, ChatResponse
from app.core.deps import get_current_user
from app.agents.graph import run_chat_agent

router = APIRouter(prefix="/api/chat", tags=["AI Chat"])


@router.post("", response_model=ChatResponse)
def chat(payload: ChatRequest, db: Session = Depends(get_db), _user=Depends(get_current_user)):
    result = run_chat_agent(db, payload.message)
    return ChatResponse(reply=result["reply"], agent=result["agent"])
