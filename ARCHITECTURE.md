# PROJECT SPECIFICATION: Voice-Enabled AI Kiosk

## 1. High-Level Mission
Build a Dual-View Voice AI Kiosk.

Customer View (Chat): A Voice-to-Voice interface where customers place orders using natural language. The AI uses RAG to check the menu and inserts confirmed orders into Postgres.

Admin View (Dashboard): A real-time table displaying the state of the Postgres orders database (Pending vs. Confirmed orders) to prove that the voice commands actually triggered a database transaction.

- Input: User speaks to Angular Frontend.

- Knowledge (RAG): The AI retrieves relevant menu items (descriptions, prices, allergens) from a Postgres Vector Database based on the user's query.

- Logic (LLM): The AI answers questions or constructs an order.

- Action (SQL): If the user confirms an order, the system inserts the order row into the Postgres relational table.

- Output: The AI replies via Text-to-Speech (TTS).

## 2. Technology Stack & Constraints
We are adhering to a strict Local-First / Open Source stack.

Frontend (Client)
Framework: Angular v21 (Standalone Components, scss, non SSG/SSR, Signals-based architecture, use latest structure flow @if, @for).

Style System: TailwindCSS, dark theme (for rapid UI).

Layout Strategy:

AppComponent: Acts as the shell. Contains a "View Switcher" (Segmented Control or Tabs) to toggle between:

View A: Kiosk Mode (The Chat Interface).

View B: Kitchen Display (The Order Table).

Audio Capture: Native Browser MediaStream API (No 3rd party audio recorders).

State Management: Angular Signals.

Backend (Server)
Runtime: Python 3.11+.

Framework: FastAPI (Async support is mandatory).

Containerization: Docker (The backend must run inside a container).

API Protocol: REST for control, sending multipart/form-data for audio upload.

AI Services (Infrastructure)
LLM Host: LM Studio running locally (emulating OpenAI API at http://localhost:1234/v1).

Speech-to-Text (STT): Faster-Whisper (running inside the Python backend container).

Text-to-Speech (TTS): Qwen3-TTS (specifically the Open Source release).

Database (The Core Change)
Image: pgvector/pgvector:pg16 (Official Postgres image with vector extension pre-installed).

Role 1 (Vector Store): Stores menu embeddings (Semantic Search).

Role 2 (Relational Store): Stores confirmed customer orders (Transactional).

Backend (Python/FastAPI)
ORM: SQLAlchemy or asyncpg for database interactions.

Embedding Model: sentence-transformers/all-MiniLM-L6-v2 (Runs locally in Python container using sentence_transformers lib).

Role: Converts user voice text -> Vector -> Search Postgres.

3. Architecture Breakdown
A. Frontend Architecture (Angular)

Layout Strategy:

AppComponent: Acts as the shell. Contains a "View Switcher" (Segmented Control or Tabs) to toggle between:

View A: Kiosk Mode (The Chat Interface: ChatWindowComponent).

View B: Kitchen Display (The Order Table: OrderDashboardComponent).

Component: OrderDashboardComponent (Standalone)

Responsibility: Fetches and displays the raw content of the orders database table.

UI Structure:

A clean HTML Table (Tailwind styled).

Columns: Order ID, Session ID, Items (JSON), Total Price, Status, Timestamp.

"Refresh" Button: Manually re-triggers the API fetch to see new orders appearing.

 Service Logic:

OrderService:

getOrders(): Observable that calls GET /api/orders.

placeOrder(orderData): Calls POST /api/orders (Used by the Chat component when AI confirms intent).

ChatWindowComponent: A typical LLM chat interface, displays the scrolling list of user (text) and AI (text) messages.
User able to send text messages or record voice.

VoiceInputComponent:

UI: A "Push-to-Talk" mic button.

Behavior:

mousedown / touchstart: Initialize microphone stream, show "Listening" visualizer.

mouseup / touchend: Stop stream, convert blob to .wav, submit to Backend.

Visualizer: Simple CSS-based waveform animation when active.

Noise Cancellation: Use the web browser's native noise suppression: navigator.mediaDevices.getUserMedia({ audio: { echoCancellation: true, noiseSuppression: true } }).

Services:

AudioService: Handles navigator.mediaDevices.getUserMedia and MediaRecorder.

KioskApiService: Handles POST requests to the backend.

B. Backend Architecture (Python/FastAPI)
Endpoints:

POST /api/conversation

Input: Multipart form data (file: audio blob OR text: string).

Logic:

If Audio: Pass to STT Engine -> Get Text.

Send Text to LLM (LM Studio) with System Prompt -> Get JSON Response.

Extract "reply_text" from JSON.

Send "reply_text" to TTS Engine -> Get Audio Bytes.

Output: JSON Object containing:

user_text: (String) What the user said.

ai_text: (String) The text reply.

audio_base64: (String) The TTS audio to play immediately.

C. AI Pipeline Details
The Ear (STT): Use faster-whisper with distil-large-v3 model (Int8 quantization) for sub-second latency on CPU.

The Brain (LLM): Connect to http://host.docker.internal:1234/v1.

System Prompt: "You are a helpful kiosk assistant. Keep answers under 2 sentences. Always return valid JSON."

The Mouth (TTS): Qwen3-TTS.

Input: Text string.

Output: PCM/WAV bytes.

4. Data Flow (Step-by-Step)
User holds "Mic Button" -> Angular records audio.

User releases button -> Angular POSTs blob to /api/conversation.

FastAPI receives file -> Saves temp .wav.

FastAPI calls model.transcribe("temp.wav") -> Gets "I want a burger."

FastAPI POSTs to localhost:1234/v1/chat/completions:

Content: "User said: I want a burger."

LM Studio replies: "Which sauce would you like?"

FastAPI calls Qwen3TTS.synthesize("Which sauce would you like?").

FastAPI returns JSON { "user": "...", "ai": "...", "audio": "<base64>" }.

Angular receives JSON -> Adds text bubbles to UI -> Auto-plays audio.

5. Development Plan (Agent Instructions)
Scaffold Backend: Create backend/ folder, Dockerfile, requirements.txt (fastapi, faster-whisper, python-multipart, openai, requests).

Scaffold Frontend: Create frontend/ (Angular 21 new app).

Docker Setup: Create docker-compose.yml to run the Backend and map ports.

Implementation:

Implement STT in Python.

Implement LLM connection in Python.

Implement TTS in Python.

Build Angular Chat Interface.

Wire up Audio Recording logic.

6. Context Management Rule: The Backend must maintain an in-memory dictionary to store conversation history, keyed by a session_id.

The Angular Frontend must generate a UUID on startup and send it as a form field session_id in every API call.

The Backend must retrieve the history list for that session_id, append the new user message, and pass the entire list to the LM Studio API messages parameter.

The Backend must append the LLM's response to the history list before returning.

7. Database Schema Strategy
The agent must create two primary tables in Postgres:

Table A: menu_items (The Knowledge Base)

id: Serial (PK)

name: Text (e.g., "Volcano Burger")

description: Text (e.g., "Spicy beef burger with jalapeños")

price: Decimal

embedding: vector(384) (Stores the semantic meaning of the name + description)

Table B: orders (The Transaction Log)

id: Serial (PK)

session_id: Text (Links to user session)

items_json: JSONB (Stores the list of items ordered, e.g., [{"item": "Burger", "qty": 2}])

total_price: Decimal

status: Text (e.g., "PENDING", "CONFIRMED")

created_at: Timestamp

8. The New Data Flow (RAG + Order Logic)
StT: Backend receives audio -> Whisper converts to text: "Do you have anything spicy?"

Embedding: Python uses all-MiniLM-L6-v2 to convert "Do you have anything spicy?" into a Vector array [0.1, -0.5, ...].

RAG Retrieval (SQL): Python runs a vector similarity query on Postgres:

SQL
SELECT name, description, price FROM menu_items
ORDER BY embedding <-> '[0.1, -0.5, ...]' LIMIT 3;
Result: "Volcano Burger ($15), Spicy Wings ($10)."

LLM Context Injection: Python constructs the prompt:

"System: You are a waiter. Here is the relevant menu info: [Volcano Burger, Spicy Wings]. User asks: 'Do you have anything spicy?'"

LLM Response: "Yes! We have a Volcano Burger for $15."

User Reply: "Okay, I'll take one Volcano Burger."

Logic Branch (Order Placement):

LLM recognizes intent to buy.

LLM outputs structured JSON: { "action": "insert_order", "items": ["Volcano Burger"], "price": 15 }.

Python Logic: Detects "action": "insert_order" -> Runs SQL INSERT INTO orders....

TTS: Backend generates audio: "Order confirmed. One Volcano Burger coming up."

9. Agent Instructions (Step-by-Step)
Docker Update: Update docker-compose.yml to add a db service using pgvector/pgvector:pg16.

Seeding Script: Create a Python script seed_menu.py that:

Connects to Postgres.

Creates the vector extension.

Creates tables.

Loads a dummy menu (JSON), generates embeddings using sentence_transformers, and inserts them into menu_items.

Backend RAG Logic:

Install sentence_transformers and sqlalchemy.

On every chat request, generate vector for user input -> Query DB -> Append results to System Prompt.

Backend Order Logic:

If LLM JSON indicates an order, execute INSERT statement to orders table.

