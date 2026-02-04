# Work Plan: Debating LLMs

Based on `PRD.md`, this plan outlines the development of a Python-based web application that facilitates and visualizes debates between LLM agents.

## Architecture

We will use a **Client-Server Architecture**:
*   **Backend (Python)**: FastAPI. Handles the core debate logic, communicates with Ollama, creates logs, and exposes APIs for the frontend.
*   **Frontend (HTML/CSS/JS)**: A modern, responsive web interface served by the backend. Uses polling or SSE (Server-Sent Events) for real-time updates.

This approach satisfies the "Python app" requirement (heavy logic/orchestration in Python) while meeting the "Rich Aesthetics" constraint by allowing full control over the frontend code.

## File Structure

```text
debating-llms/
├── app.py                  # Main entry point (FastAPI)
├── requirements.txt        # Python dependencies
├── core/
│   ├── __init__.py
│   ├── debate_manager.py   # Orchestrates the debate loop
│   ├── agent.py            # Wrapper for LLM interaction (Ollama)
│   └── logger.py           # Handles saving debate logs
├── prompts/                # Behavior definitions
│   ├── moderator.md
│   ├── proposition.md
│   └── opposition.md
└── static/                 # Frontend assets
    ├── index.html
    ├── style.css
    └── script.js
```

## Step-by-Step Implementation

### Phase 1: Preparation & Configuration
1.  **Environment Setup**: Create `requirements.txt` with `fastapi`, `uvicorn`, `ollama`.
2.  **Behavior Definitions**: Create the system prompts in `prompts/*.md`.
    *   `proposition.md`: Instructions to argue FOR a topic.
    *   `opposition.md`: Instructions to argue AGAINST a topic.
    *   `moderator.md`: Instructions to manage flow, pick winners, and synthesize.

### Phase 2: Core Logic (Python)
3.  **LLM Abstraction (`core/agent.py`)**:
    *   Class to interface with Ollama.
    *   Method to generate responses (streaming preferred).
4.  **Debate Manager (`core/debate_manager.py`)**:
    *   Manage state: `waiting`, `in_progress`, `completed`.
    *   Store history of turns.
    *   Logic for turn-taking: Moderator -> Prop -> Opp -> Moderator (repeat).
5.  **Logging (`core/logger.py`)**:
    *   Function to save the full conversation to a file (JSON or Markdown) with timestamps.

### Phase 3: API & Server (Python)
6.  **FastAPI Setup (`app.py`)**:
    *   Endpoint `POST /start`: Initialize debate (topic, rounds, models).
    *   Endpoint `GET /stream`: SSE stream for real-time conversation updates.
    *   Endpoint `POST /stop`: Abort debate.
    *   Serve static files.

### Phase 4: Frontend (UI/UX)
7.  **Structure (`index.html`)**:
    *   Setup container, controls (topic input, slider for rounds, start button), and chat window.
8.  **Styling (`style.css`)**:
    *   "Rich Aesthetics": Dark mode, glassmorphism, nice typography (Inter/Roboto), distinct colors for Prop/Opp/Mod.
    *   Thinking indicators (pulsing dots).
9.  **Logic (`script.js`)**:
    *   Fetch calls to start debate.
    *   EventSource for handling the stream and appending messages to the DOM.
    *   Scroll handling.

### Phase 5: Testing & Refinement
10. **Sanity Check**: Functionality test with local Ollama instance (Gemma3:1b).
11. **Refinement**: Ensure 10s response constraint is reasonable (asynchronous calls if needed, though local inference speed is hardware dependent).
