from sqlalchemy import Column, String, Text, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from database import Base
import uuid
from datetime import datetime

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # One user can have many chatbots
    chatbots = relationship("Chatbot", back_populates="owner")


class Chatbot(Base):
    __tablename__ = "chatbots"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    name = Column(String, nullable=False)
    website_url = Column(String, nullable=False)
    scrape_status = Column(String, default="pending")  # pending/processing/done/failed
    widget_color = Column(String, default="#6366f1")
    welcome_message = Column(String, default="Hi! How can I help you?")
    created_at = Column(DateTime, default=datetime.utcnow)

    # Links back to the user who owns this chatbot
    owner = relationship("User", back_populates="chatbots")

    # One chatbot has many messages
    # One chatbot has many messages
    messages = relationship("Message", back_populates="chatbot", cascade="all, delete-orphan")


class Message(Base):
    __tablename__ = "messages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    chatbot_id = Column(UUID(as_uuid=True), ForeignKey("chatbots.id"), nullable=False)
    session_id = Column(String, nullable=False)
    role = Column(String, nullable=False)  # "user" or "assistant"
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Links back to the chatbot
    chatbot = relationship("Chatbot", back_populates="messages")