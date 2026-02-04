import os
import asyncio
import json
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from core.debate_manager import DebateManager

app = FastAPI()

# Global State
debate_manager = DebateManager()

class StartRequest(BaseModel):
    topic: str
    rounds: int
    model_mod: str = "gemma3:1b"
    model_prop: str = "gemma3:1b"
    model_opp: str = "gemma3:1b"

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def read_index():
    return FileResponse('static/index.html')
@app.get("/models")
async def get_models():
    try:
        from ollama import list as list_models
        response = list_models()
        # response is typically ListResponse(models=[ModelResponse(name='...', ...)])
        # We need to extract the names.
        model_names = [m.model for m in response.models]
        return {"models": model_names}
    except Exception as e:
        print(f"Error fetching models: {e}")
        # Fallback
        return {"models": ["gemma3:1b"]}

@app.post("/start")
async def start_debate(req: StartRequest):
    prompt_dir = os.path.abspath("prompts")
    success, message = debate_manager.start_debate(
        req.topic, 
        req.rounds, 
        req.model_mod,
        req.model_prop,
        req.model_opp,
        prompt_dir
    )
    return {"success": success, "message": message}

@app.post("/stop")
async def stop_debate():
    debate_manager.stop_debate()
    return {"message": "Debate stopping..."}


active_connections = set()

async def broadcast_status(data):
    """
    Pushes status update to all connected clients queues.
    """
    for queue in active_connections:
        await queue.put(json.dumps(data))

global_loop = None

@app.on_event("startup")
async def startup_event():
    global global_loop
    global_loop = asyncio.get_running_loop()
    
    def callback(data):
        if global_loop:
             # Schedule the broadcast coroutine
             asyncio.run_coroutine_threadsafe(broadcast_status(data), global_loop)
            
    debate_manager.on_update = callback

@app.get("/stream")
async def stream(request: Request):
    queue = asyncio.Queue()
    active_connections.add(queue)
    
    # Send initial state
    with debate_manager.lock:
        initial_data = {
            "status": debate_manager.status,
            "transcript": debate_manager.transcript,
            "current_speaker": debate_manager.current_speaker,
            "current_stream": debate_manager.current_stream,
            "rounds_current": debate_manager.rounds_current,
            "rounds_total": debate_manager.rounds_total,
            "topic": debate_manager.topic,
            "error": debate_manager.error_message
        }
    await queue.put(json.dumps(initial_data))
    
    async def event_generator():
        try:
            while True:
                if await request.is_disconnected():
                    break
                # Wait for next update
                data = await queue.get()
                yield f"data: {data}\n\n"
        except asyncio.CancelledError:
            pass
        finally:
            active_connections.remove(queue)
            
    return StreamingResponse(event_generator(), media_type="text/event-stream")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
