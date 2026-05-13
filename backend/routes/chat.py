from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from fastapi import Depends
from database import get_db
import models
from rag.embedder import Embedder
from rag.vectorstore import VectorStore
from rag.chain import RAGChain
from uuid import UUID  # ← added this import

router = APIRouter()

embedder = Embedder()
vectorstore = VectorStore()
chain = RAGChain()

class ChatRequest(BaseModel):
    chatbot_id: str
    session_id: str
    message: str

@router.post("/chat")
def chat(data: ChatRequest, db: Session = Depends(get_db)):
    # Convert string to UUID for database query  ← fix 1
    try:
        chatbot_uuid = UUID(data.chatbot_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid chatbot_id format")

    # Verify chatbot exists and is ready
    chatbot = db.query(models.Chatbot).filter(
        models.Chatbot.id == chatbot_uuid  # ← fix 2: use chatbot_uuid not data.chatbot_id
    ).first()

    if not chatbot:
        raise HTTPException(status_code=404, detail="Chatbot not found")

    if chatbot.scrape_status != "done":
        raise HTTPException(
            status_code=400,
            detail=f"Chatbot is not ready. Status: {chatbot.scrape_status}"
        )

    # Save user message  ← fix 3: use chatbot_uuid not data.chatbot_id
    user_msg = models.Message(
        chatbot_id=chatbot_uuid,
        session_id=data.session_id,
        role="user",
        content=data.message
    )
    db.add(user_msg)
    db.commit()

    # RAG: embed question → find chunks → generate answer
    question_embedding = embedder.embed(data.message)
    chunks = vectorstore.query(data.chatbot_id, question_embedding, n_results=5)
    response = chain.answer(data.message, chunks, chatbot.welcome_message)

    # Save assistant message  ← fix 4: use chatbot_uuid not data.chatbot_id
    assistant_msg = models.Message(
        chatbot_id=chatbot_uuid,
        session_id=data.session_id,
        role="assistant",
        content=response["answer"]
    )
    db.add(assistant_msg)
    db.commit()

    return {
        "answer": response["answer"],
        "sources": response["sources"],
        "session_id": data.session_id
    }