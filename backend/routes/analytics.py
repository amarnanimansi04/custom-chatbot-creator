from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from database import get_db
from auth import get_current_user
import models

router = APIRouter()

@router.get("/analytics/{chatbot_id}")
def get_analytics(
    chatbot_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    # Verify ownership
    chatbot = db.query(models.Chatbot).filter(
        models.Chatbot.id == chatbot_id,
        models.Chatbot.user_id == current_user.id
    ).first()

    if not chatbot:
        raise HTTPException(status_code=404, detail="Chatbot not found")

    # Total messages
    total_messages = db.query(models.Message).filter(
        models.Message.chatbot_id == chatbot_id,
        models.Message.role == "user"
    ).count()

    # Total unique sessions
    unique_sessions = db.query(
        func.count(func.distinct(models.Message.session_id))
    ).filter(models.Message.chatbot_id == chatbot_id).scalar()

    # Last 10 questions asked
    recent_questions = db.query(models.Message).filter(
        models.Message.chatbot_id == chatbot_id,
        models.Message.role == "user"
    ).order_by(models.Message.created_at.desc()).limit(10).all()

    return {
        "chatbot_id": chatbot_id,
        "total_questions": total_messages,
        "unique_sessions": unique_sessions,
        "recent_questions": [
            {
                "question": m.content,
                "asked_at": m.created_at
            }
            for m in recent_questions
        ]
    }