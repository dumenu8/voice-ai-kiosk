import os
import json
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from sentence_transformers import SentenceTransformer
from models import MenuItem
from openai import OpenAI
import numpy as np

# Load embedding model once (global)
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

# Setup OpenAI Client for Local LLM
client = OpenAI(
    base_url=os.getenv("OPENAI_BASE_URL", "http://host.docker.internal:1234/v1"),
    api_key=os.getenv("OPENAI_API_KEY", "lm-studio")
)

LLM_MODEL = os.getenv("LLM_MODEL", "qwen3-vl-4b-instruct-abliterated-v2")

SYSTEM_PROMPT_TEMPLATE = """You are a helpful and friendly Voice Kiosk Assistant for a fast-food restaurant.
Your goal is to help users place orders from the menu.
Keep your responses concise (under 2 sentences) and conversational.
Always output your response in strict JSON format.

MENU CONTEXT:
{menu_context}

INSTRUCTIONS:
1. Answer the user's questions based *only* on the menu context provided.
2. If the user wants to order something, confirm the item and price.
3. If the user confirms an order, set "action" to "insert_order" and list the items.
4. Otherwise, set "action" to "continue".

JSON OUTPUT FORMAT:
{{
  "reply_text": "Your query response here.",
  "action": "continue" | "insert_order",
  "items": [ {{"name": "Item Name", "price": 10.0, "qty": 1}} ] (only if action is insert_order, otherwise empty)
}}
"""

def get_menu_context(db: Session, query: str) -> str:
    """
    Embeds the user query and searches for relevant menu items in Postgres.
    """
    # Generate embedding
    query_embedding = embedding_model.encode(query).tolist()
    
    # Search in DB using pgvector (L2 distance <->)
    results = db.query(MenuItem).order_by(
        MenuItem.embedding.l2_distance(query_embedding)
    ).limit(3).all()
    
    context_lines = []
    for item in results:
        context_lines.append(f"- {item.name}: {item.description} (${item.price})")
    
    return "\n".join(context_lines)

def process_conversation(db: Session, session_id: str, user_text: str, history: List[Dict]) -> Dict[str, Any]:
    """
    Main logic pipeline:
    1. RAG Retrieve
    2. Construct Prompt
    3. Call LLM
    4. Return structured response
    """
    # 1. RAG
    menu_context = get_menu_context(db, user_text)
    
    # 2. Construct System Prompt
    system_prompt = SYSTEM_PROMPT_TEMPLATE.format(menu_context=menu_context)
    
    # 3. Build Message Chain
    messages = [{"role": "system", "content": system_prompt}]
    # Add history (limit to last 10 to fit context)
    messages.extend(history[-10:])
    # Add current user message
    messages.append({"role": "user", "content": user_text})
    
    try:
        completion = client.chat.completions.create(
            model=LLM_MODEL,
            messages=messages,
            temperature=0.7
        )
        
        llm_response_text = completion.choices[0].message.content
        
        # Parse JSON
        try:
            parsed_response = json.loads(llm_response_text)
        except json.JSONDecodeError:
            # Fallback if LLM messes up JSON
            parsed_response = {
                "reply_text": llm_response_text,
                "action": "continue",
                "items": []
            }
            
        return parsed_response

    except Exception as e:
        print(f"LLM Error: {e}")
        print(f"DEBUG: URL={client.base_url}, KEY={client.api_key}, MODEL={LLM_MODEL}")
        return {
            "reply_text": "I'm having trouble connecting to my brain right now. Please try again.",
            "action": "continue",
            "items": []
        }
