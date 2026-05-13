from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from database import get_db
from auth import get_current_user
import models
from tasks.scrape_task import process_url

router = APIRouter()

class CreateChatbotRequest(BaseModel):
    name: str
    website_url: str
    welcome_message: Optional[str] = "Hi! How can I help you today?"
    widget_color: Optional[str] = "#6366f1"

class UpdateChatbotRequest(BaseModel):
    name: Optional[str] = None
    welcome_message: Optional[str] = None
    widget_color: Optional[str] = None

# --- Create Chatbot ---
@router.post("/chatbots")
def create_chatbot(
    data: CreateChatbotRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    chatbot = models.Chatbot(
        user_id=current_user.id,
        name=data.name,
        website_url=data.website_url,
        welcome_message=data.welcome_message,
        widget_color=data.widget_color,
        scrape_status="pending"
    )
    db.add(chatbot)
    db.commit()
    db.refresh(chatbot)

    # Fire background job without waiting
    process_url.delay(str(chatbot.id), data.website_url)

    return {
        "id": str(chatbot.id),
        "name": chatbot.name,
        "website_url": chatbot.website_url,
        "scrape_status": chatbot.scrape_status,
        "welcome_message": chatbot.welcome_message,
        "widget_color": chatbot.widget_color,
        "created_at": chatbot.created_at
    }

# --- List All Chatbots ---
@router.get("/chatbots")
def list_chatbots(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    chatbots = db.query(models.Chatbot).filter(
        models.Chatbot.user_id == current_user.id
    ).order_by(models.Chatbot.created_at.desc()).all()

    return [
        {
            "id": str(c.id),
            "name": c.name,
            "website_url": c.website_url,
            "scrape_status": c.scrape_status,
            "welcome_message": c.welcome_message,
            "widget_color": c.widget_color,
            "created_at": c.created_at
        }
        for c in chatbots
    ]

# --- Get Single Chatbot ---
@router.get("/chatbots/{chatbot_id}")
def get_chatbot(
    chatbot_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    chatbot = db.query(models.Chatbot).filter(
        models.Chatbot.id == chatbot_id,
        models.Chatbot.user_id == current_user.id
    ).first()

    if not chatbot:
        raise HTTPException(status_code=404, detail="Chatbot not found")

    return {
        "id": str(chatbot.id),
        "name": chatbot.name,
        "website_url": chatbot.website_url,
        "scrape_status": chatbot.scrape_status,
        "welcome_message": chatbot.welcome_message,
        "widget_color": chatbot.widget_color,
        "created_at": chatbot.created_at
    }

# --- Update Chatbot ---
@router.patch("/chatbots/{chatbot_id}")
def update_chatbot(
    chatbot_id: str,
    data: UpdateChatbotRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    chatbot = db.query(models.Chatbot).filter(
        models.Chatbot.id == chatbot_id,
        models.Chatbot.user_id == current_user.id
    ).first()

    if not chatbot:
        raise HTTPException(status_code=404, detail="Chatbot not found")

    if data.name: chatbot.name = data.name
    if data.welcome_message: chatbot.welcome_message = data.welcome_message
    if data.widget_color: chatbot.widget_color = data.widget_color

    db.commit()
    db.refresh(chatbot)

    return {"message": "Chatbot updated", "id": str(chatbot.id)}

# --- Delete Chatbot ---
@router.delete("/chatbots/{chatbot_id}")
def delete_chatbot(
    chatbot_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    chatbot = db.query(models.Chatbot).filter(
        models.Chatbot.id == chatbot_id,
        models.Chatbot.user_id == current_user.id
    ).first()

    if not chatbot:
        raise HTTPException(status_code=404, detail="Chatbot not found")

    # Delete ChromaDB collection too
    from rag.vectorstore import VectorStore
    VectorStore().delete_collection(chatbot_id)

    db.delete(chatbot)
    db.commit()

    return {"message": "Chatbot deleted successfully"}

# --- Get Widget Script Tag ---
@router.get("/chatbots/{chatbot_id}/widget")
def get_widget_script(
    chatbot_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    chatbot = db.query(models.Chatbot).filter(
        models.Chatbot.id == chatbot_id,
        models.Chatbot.user_id == current_user.id
    ).first()

    if not chatbot:
        raise HTTPException(status_code=404, detail="Chatbot not found")

    if chatbot.scrape_status != "done":
        raise HTTPException(
            status_code=400,
            detail=f"Chatbot is not ready yet. Status: {chatbot.scrape_status}"
        )

    script_tag = f'<script src="https://cdn.yourchatbot.com/widget.js" data-chatbot-id="{chatbot_id}"></script>'

    return {
        "chatbot_id": chatbot_id,
        "script_tag": script_tag,
        "status": chatbot.scrape_status
    }