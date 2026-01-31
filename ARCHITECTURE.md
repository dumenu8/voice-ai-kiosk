# 🏗️ Architecture Specification: Voice-Enabled AI Kiosk

This document outlines the technical architecture, data flows, and infrastructure for the Voice AI Kiosk system. The project follows a **Local-First / Open Source** principle, ensuring all AI processing happens on-premise without reliance on external cloud APIs.

---

## 🚀 1. High-Level Mission
The system provides a **Dual-View** interface for a restaurant/retail environment:

1.  **Customer View (Chat):** A Voice-to-Voice interface where customers place orders using natural language. It uses RAG (Retrieval-Augmented Generation) to query the menu and process orders.
2.  **Admin View (Dashboard):** A real-time kitchen display showing the state of the Postgres orders database (Pending vs. Confirmed).

---

## 🛠️ 2. Technology Stack

### Frontend (Client)
- **Framework:** Angular v21 (Standalone Components, Signals-based architecture).
- **Styling:** TailwindCSS with a sleek Dark Mode theme.
- **Audio:** Native Browser MediaStream API & MediaRecorder.

### Backend (Server)
- **Runtime:** Python 3.11+.
- **Framework:** FastAPI (Asynchronous).
- **Database:** PostgreSQL + `pgvector` (Vector similarity search).
- **ORM:** SQLAlchemy (Async).

### AI Engine (Local Infrastructure)
- **STT (Speech-to-Text):** Faster-Whisper (`distil-large-v3` with Int8 quantization).
- **LLM (Brain):** Local LLM (via LM Studio/Ollama) emulating OpenAI API.
- **TTS (Text-to-Speech):** Qwen3-TTS.
- **Embeddings:** `all-MiniLM-L6-v2` (via `sentence-transformers`).

---

## 📐 3. Component Breakdown

### A. Frontend Architecture
The app uses a single shell (`AppComponent`) with a view switcher to toggle between modes.

#### 1. Kiosk Mode (`ChatWindowComponent`)
- **VoiceInputComponent:** A "Push-to-Talk" button using `mousedown` and `mouseup` events.
- **Visualizer:** A CSS-based waveform animation that reacts when the microphone is active.
- **Audio processing:** Captures 16kHz mono audio, converts to `.wav` blob, and transmits via `multipart/form-data`.

#### 2. Kitchen Display (`OrderDashboardComponent`)
- **Responsibility:** Fetches and displays the raw orders from the database.
- **Features:** Real-time refresh button, order status tracking (Pending/Confirmed), and item breakdown.

### B. Backend Architecture
The FastAPI server handles logic orchestration, AI pipeline management, and database transactions.

#### Primary Endpoint: `POST /api/conversation`
1.  **Input:** Multipart form (audio file or text string + `session_id`).
2.  **Orchestration:** 
    - STT -> Transcription.
    - RAG -> Vector search in `menu_items`.
    - LLM -> Intent analysis and response generation.
    - Database -> Insert order if intent confirmed.
    - TTS -> Convert reply text to audio.
3.  **Output:** JSON `{ user_text, ai_text, audio_base64 }`.

---

## 🗄️ 4. Database Schema

The system uses **PostgreSQL** with the `pgvector` extension to handle both relational and semantic data.

### Table: `menu_items` (The Knowledge Base)
Used for RAG to provide context to the LLM.

| Column | Type | Description |
| :--- | :--- | :--- |
| `id` | Serial (PK) | Unique item ID |
| `name` | Text | Name (e.g., "Volcano Burger") |
| `description`| Text | Ingredients/Description |
| `price` | Decimal | Cost in USD |
| `embedding` | `vector(384)`| Semantic vector of name + description |

### Table: `orders` (The Transaction Log)
Tracks customer purchases in real-time.

| Column | Type | Description |
| :--- | :--- | :--- |
| `id` | Serial (PK) | Order number |
| `session_id` | Text | Links to the frontend session |
| `items_json` | JSONB | List of items (e.g., `[{"item": "Burger", "qty": 1}]`) |
| `total_price`| Decimal | Final total |
| `status` | Text | `PENDING` or `CONFIRMED` |
| `created_at` | Timestamp | Order timestamp |

---

## 🔄 5. Detailed Data Flow

1.  **Input:** User says *"I'd like a spicy burger."*
2.  **Transcription:** `faster-whisper` converts audio to text.
3.  **Semantic Search:**
    - System generates a vector for *"spicy burger"*.
    - SQL Query: `SELECT * FROM menu_items ORDER BY embedding <-> '[vector]' LIMIT 3;`
    - Result: *Volcano Burger ($15)*.
4.  **Reasoning (LLM):**
    - **Context:** System prompt + Menu RAG results + Session history.
    - **Output:** AI decides to recommend the Volcano Burger and formats a response.
5.  **Action:**
    - If user says *"Yes, I want that"*, the LLM triggers a structured JSON action: `{ "action": "insert_order", "items": [...] }`.
    - Backend executes `INSERT INTO orders`.
6.  **Response:** TTS generates audio of the AI's reply ("Order confirmed!") and sends it back to Angular.

---

## 🐳 6. Deployment & Infrastructure
The entire stack is containerized for portability.

- **`db` service:** Postgres + pgvector.
- **`backend` service:** FastAPI + AI models.
- **`frontend` service:** Nginx serving the Angular build (optional for production).
- **Communication:** Services interact over a shared Docker bridge network.

---

*Last Updated: January 2026*
