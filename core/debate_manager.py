import threading
import time
import os
from datetime import datetime
from .agent import Agent
import logging
from .logger import save_debate

# Configure logger
logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DebateManager:
    def __init__(self):
        self.lock = threading.Lock()
        self.status = "idle"  # idle, running, completed, error
        self.transcript = []
        self.current_stream = ""
        self.current_speaker = ""
        self.stop_event = threading.Event()
        self.thread = None
        self.topic = ""
        self.rounds_total = 0
        self.rounds_current = 0

        self.error_message = None
        self.on_update = None # Callback for event-driven updates

    def start_debate(self, topic, rounds, model_mod, model_prop, model_opp, prompt_dir):
        with self.lock:
            if self.status == "running":
                return False, "Debate already running"
            
            self.status = "running"
            self.error_message = None
            self.stop_event.clear()
            self.transcript = []
            self.current_stream = ""
            self.current_speaker = ""
            self.topic = topic
            self.rounds_total = rounds
            self.rounds_current = 0
            
            # Initialize Agents with specific models
            try:
                self.moderator = Agent(model_mod, os.path.join(prompt_dir, "moderator.md"), "Moderator")
                self.proposition = Agent(model_prop, os.path.join(prompt_dir, "proposition.md"), "Proposition")
                self.opposition = Agent(model_opp, os.path.join(prompt_dir, "opposition.md"), "Opposition")
            except Exception as e:
                self.status = "error"
                return False, str(e)

            self.thread = threading.Thread(target=self._run_debate)
            self.thread.start()
            return True, "Debate started"

    def stop_debate(self):
        # Non-blocking stop. 
        # The thread will check stop_event and exit gracefully.
        self.stop_event.set()
        
    def _emit_update(self):
        if self.on_update:
            with self.lock:
                 data = {
                    "status": self.status,
                    "transcript": self.transcript,
                    "current_speaker": self.current_speaker,
                    "current_stream": self.current_stream,
                    "rounds_current": self.rounds_current,
                    "rounds_total": self.rounds_total,
                    "topic": self.topic,
                    "error": self.error_message
                }
            self.on_update(data)

    def _run_debate(self):
        try:
            # 1. Moderator Intro
            self._turn(self.moderator, f"The topic is: {self.topic}. Please introduce the debate.")
            
            # Loop rounds
            for i in range(self.rounds_total):
                if self.stop_event.is_set(): break
                self.rounds_current = i + 1
                
                # Proposition
                self._turn(self.proposition, "Please present your argument.")
                if self.stop_event.is_set(): break
                
                # Opposition
                self._turn(self.opposition, "Please present your counter-argument.")
                if self.stop_event.is_set(): break
                
                # Moderator check-in (only if NOT the last round)
                if i < self.rounds_total - 1:
                    self._turn(self.moderator, "Briefly comment on the exchange and pass to the next round.")

            # Final Decision
            if not self.stop_event.is_set():
                self._turn(self.moderator, "The debate concludes. Please summarize the key points from both sides and Declare a Winner based on the strength of arguments.")

            self.status = "completed"
            save_debate(self.topic, self.transcript)
            
        except Exception as e:
            logger.error(f"Error in debate thread: {e}", exc_info=True)
            self.error_message = str(e)
            self.status = "error"
        finally:
             if self.stop_event.is_set():
                  self.status = "idle" 
             
             self._emit_update()

    def _turn(self, agent, instruction_context):
        with self.lock:
            self.current_speaker = agent.role_name
            self.current_stream = ""
        self._emit_update()
        
        # Add a temporary system instruction or just rely on conversation history?
        # We pass the history.
        # We can append the instruction context to the last message or as a new user prompt in the generation history
        # Agent class handles sending history.
        
        # We need to pass the context of "It's your turn, do X".
        # We'll fake a "User" / "System" trigger for the agent.
        turn_history = self.transcript.copy()
        turn_history.append({'speaker': 'System', 'content': instruction_context})
        

        full_response = ""
        for chunk in agent.generate_response(turn_history):
            if self.stop_event.is_set(): break
            
            with self.lock:
                self.current_stream += chunk
            self._emit_update()
            full_response += chunk

        # Cleanup prefixes from final response
        clean_response = full_response.strip()
        # Check for various prefix formats case-insensitively
        p_len = len(agent.role_name)
        # We start checking if the response starts with the role name
        if clean_response.lower().startswith(agent.role_name.lower()):
             # potential prefix. Check for : or ] or similar
             remainder = clean_response[p_len:]
             if remainder.startswith(":") or remainder.startswith("]:"):
                 clean_response = remainder.lstrip(": ]")
        elif clean_response.startswith("[") and clean_response.lower().startswith(f"[{agent.role_name.lower()}]"):
             clean_response = clean_response.split("]", 1)[1].lstrip(" :")

        if not self.stop_event.is_set():
            with self.lock:
                self.transcript.append({'speaker': agent.role_name, 'content': clean_response})
                self.current_stream = ""
                self.current_speaker = ""
            self._emit_update()
