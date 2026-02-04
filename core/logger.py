import json
import os
from datetime import datetime
from slugify import slugify

def save_debate(topic: str, transcript: list):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    # Use robust slugify
    safe_topic = slugify(topic, max_length=50, word_boundary=True, separator="_")
    if not safe_topic:
        safe_topic = "debate"
        
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
