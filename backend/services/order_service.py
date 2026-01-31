from sqlalchemy.orm import Session
from models import Order
from typing import List, Dict
import json

def create_order(db: Session, session_id: str, items: List[Dict], total_price: float) -> Order:
    db_order = Order(
        session_id=session_id,
        items_json=items,
        total_price=total_price
    )
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    return db_order

def get_orders(db: Session, skip: int = 0, limit: int = 100) -> List[Order]:
    return db.query(Order).order_by(Order.created_at.desc()).offset(skip).limit(limit).all()
