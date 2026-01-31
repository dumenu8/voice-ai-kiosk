
from fastapi import FastAPI, UploadFile, File, Form, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db, engine, Base
from models import Order, MenuItem
import services.order_service as order_service
import services.llm_service as llm_service
from typing import List, Optional
from pydantic import BaseModel
import uuid

# Initialize Tables (if not already done by init_db.py)
Base.metadata.create_all(bind=engine)

app = FastAPI()

# Temporary In-Memory Session Storage
# Key: session_id, Value: List of messages
session_history = {}

class ChatRequest(BaseModel):
    session_id: str
    user_text: str

class OrderResponse(BaseModel):
    id: int
    session_id: str
    total_price: float
    status: str
    items_json: List[dict]

class MenuItemResponse(BaseModel):
    id: int
    name: str
    description: str
    price: float
    category: Optional[str] = None
    image_url: Optional[str] = None
    embedding: Optional[List[float]] = None

    class Config:
        orm_mode = True 

def read_root():
    return {"message": "Voice Kiosk Backend is running"}

@app.get("/api/status")
def health_check():
    return {"status": "ok", "service": "backend"}

@app.post("/api/conversation")
async def conversation(
    session_id: str = Form(...),
    text: Optional[str] = Form(None),
    audio: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db)
):
    """
    Handles voice or text interaction.
    1. Transcribes audio (TODO) or uses text.
    2. Calls LLM with RAG context.
    3. Places order if intent detected.
    4. Returns JSON response + TTS (TODO).
    """
    user_input = text
    if audio:
        print(f"Received audio file: {audio.filename}")
        import services.stt_service as stt_service
        try:
            transcribed_text = stt_service.transcribe(audio)
            print(f"Transcribed: '{transcribed_text}'")
            if transcribed_text:
                user_input = transcribed_text
            else:
                return {"error": "Could not understand audio"}
        except Exception as e:
            print(f"STT Error: {e}")
            return {"error": "Transcription failed"}
    
    if not user_input:
        return {"error": "No input provided"}

    # Retrieve history
    if session_id not in session_history:
        session_history[session_id] = []
    
    # Process with LLM
    response_data = llm_service.process_conversation(
        db, 
        session_id, 
        user_input, 
        session_history[session_id]
    )
    
    # Update History
    # Handle Order Action
    if response_data.get("action") == "insert_order":
        items = response_data.get("items", [])
        total_price = sum(item.get("price", 0) * item.get("qty", 1) for item in items)
        
        # Create Order in DB
        new_order = order_service.create_order(db, session_id, items, total_price)
        
        # Append order confirmation to response
        response_data["order_id"] = new_order.id
        response_data["order_status"] = "confirmed"

    # Generate Audio Response (TTS)
    import services.tts_service as tts_service
    import base64
    
    ai_text = response_data.get("reply_text", "")
    if ai_text:
        audio_bytes = tts_service.synthesize(ai_text)
        if audio_bytes:
            # Encode to base64 for JSON transport
            audio_b64 = base64.b64encode(audio_bytes).decode('utf-8')
            response_data["audio_base64"] = audio_b64

    # Include transcribed text for the frontend to display
    if audio and user_input:
        response_data["user_transcript"] = user_input

    return response_data

@app.get("/api/menu", response_model=List[MenuItemResponse])
def get_menu(db: Session = Depends(get_db)):
    return db.query(MenuItem).all()

@app.get("/api/orders", response_model=List[OrderResponse])
def get_orders(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    orders = order_service.get_orders(db, skip=skip, limit=limit)
    return orders
