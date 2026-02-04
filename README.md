![Screenshot](https://github.com/ulasb/debating-llms/blob/main/debating-llms-screenshot.png)

# Debating LLMs

A Python-based web application where AI models debate topics in real-time.

## Features
- **Real-time Debate**: Watch Proposition vs Opposition, moderated by a Judge.
- **Customizable**: Choose topic, rounds, and models.
- **Local Privacy**: Runs entirely locally using Ollama.
- **Rich UI**: Dark mode, responsive design, and streaming responses.

## Prerequisites
1. **Ollama**: Must be installed and running.
2. **Models**: Ensure `gemma3:1b` (or your chosen model) is pulled:
   ```bash
   ollama pull gemma3:1b
   ```
3. **Python 3.10+**

## Setup & Run

1. **Install Dependencies**:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Run the App**:
   ```bash
   uvicorn app:app --reload
   ```

3. **Open in Browser**:
   Visit `http://localhost:8000`

## Structure
- `app.py`: FastAPI backend and API.
- `core/`: Logic for debate management and agents.
- `prompts/`: System prompts for the debaters.
- `static/`: Frontend assets (HTML/CSS/JS).
