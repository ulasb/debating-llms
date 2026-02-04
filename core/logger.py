import json
import os
from datetime import datetime

def save_debate(topic: str, transcript: list):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_topic = "".join([c if c.isalnum() else "_" for c in topic])[:30]
    filename = f"debate_{timestamp}_{safe_topic}.json"
    
    # Ensure logs directory exists
    os.makedirs("logs", exist_ok=True)
    
    data = {
        "topic": topic,
        "timestamp": timestamp,
        "transcript": transcript
    }
    
    with open(os.path.join("logs", filename), "w") as f:
        json.dump(data, f, indent=4)
