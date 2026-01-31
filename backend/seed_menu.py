import json
from sentence_transformers import SentenceTransformer
from database import SessionLocal
from models import MenuItem
import os

# Sample Menu Data
MENU_DATA = [
    {
        "name": "Volcano Burger",
        "description": "A spicy beef burger with jalapeños, pepper jack cheese, and hot sauce.",
        "price": 15.00
    },
    {
        "name": "Classic Cheeseburger",
        "description": "A classic beef patty with cheddar cheese, lettuce, tomato, and pickles.",
        "price": 12.00
    },
    {
        "name": "Spicy Chicken Wings",
        "description": "Crispy chicken wings tossed in a spicy buffalo sauce.",
        "price": 10.00
    },
    {
        "name": "Caesar Salad",
        "description": "Fresh romaine lettuce with parmesan cheese, croutons, and caesar dressing.",
        "price": 9.00
    },
    {
        "name": "Chocolate Lava Cake",
        "description": "Warm chocolate cake with a molten chocolate center, served with vanilla ice cream.",
        "price": 8.00
    }
]

def seed_menu():
    print("Loading embedding model...")
    model = SentenceTransformer('all-MiniLM-L6-v2')
    
    db = SessionLocal()
    try:
        # Check if menu already exists
        if db.query(MenuItem).count() > 0:
            print("Menu items already exist. Skipping seed.")
            return

        print("Seeding menu items...")
        for item in MENU_DATA:
            # Generate embedding for name + description
            text_to_embed = f"{item['name']} {item['description']}"
            embedding = model.encode(text_to_embed).tolist()
            
            menu_item = MenuItem(
                name=item['name'],
                description=item['description'],
                price=item['price'],
                embedding=embedding
            )
            db.add(menu_item)
        
        db.commit()
        print("Menu seeded successfully!")
        
    except Exception as e:
        print(f"Error seeding menu: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_menu()
