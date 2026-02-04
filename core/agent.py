from ollama import Client

class Agent:
    def __init__(self, model_name: str, system_prompt_path: str, role_name: str):
        self.model_name = model_name
        self.role_name = role_name
        self.client = Client()
        
        with open(system_prompt_path, 'r') as f:
            self.system_prompt = f.read()

    def generate_response(self, conversation_history):
        """
        Generates a streamed response based on the conversation history.
        conversation_history should be a list of dicts: {'role': 'user'|'assistant', 'content': ...}
        We map 'user' to the other debaters/moderator context.
        """
        # Construct the messages list for Ollama
        messages = [{'role': 'system', 'content': self.system_prompt}]
        
        # Add history. 
        # Note: Ollama expects 'user' and 'assistant' roles usually. 
        # We need to format the debate history so the model understands who said what.
        # A simple way is to treat all previous turns as 'user' content prefaced with the Speaker Name,
        # or properly map them if we want to simulate a multi-agent chat.
        # Given simpler models like Gemma, distinct "Transcript" style history in a single user message 
        # or a sequence of User messages is often robust.
        # Let's try appending the Transcript to the prompt or sending the last few turns.
        
        # Strategy: Provide the context of the debate as a series of messages.
        for turn in conversation_history:
            # turn is {'speaker': 'Proposition', 'content': '...'}
            role = 'assistant' if turn['speaker'] == self.role_name else 'user'
            content = f"[{turn['speaker']}]: {turn['content']}"
            messages.append({'role': role, 'content': content})

        try:
            stream = self.client.chat(model=self.model_name, messages=messages, stream=True)
            for chunk in stream:
                yield chunk['message']['content']
        except Exception as e:
            yield f"[Error generating response: {e}]"
