from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from database import engine, Base
import models
import os
from routes import users, chatbots, chat, analytics

app = FastAPI(title="Custom Chatbot Creator API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)

# Register all routes
app.include_router(users.router, prefix="/api")
app.include_router(chatbots.router, prefix="/api")
app.include_router(chat.router, prefix="/api")
app.include_router(analytics.router, prefix="/api")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
app.mount("/widget", StaticFiles(directory=os.path.join(BASE_DIR, "widget")), name="widget")

@app.get("/demo")
def demo():
    return FileResponse(os.path.join(BASE_DIR, "test.html"))

@app.get("/")
def root():
    return {"message": "Custom Chatbot Creator API is running! 🚀"}