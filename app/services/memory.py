from typing import List, Dict

class MemoryManager:
    def __init__(self, max_history: int =4):
        self.store : Dict[str, List[Dict[str, str]]] = {}
        self.max_history = max_history
    
    def get_history(self,session_id: str) -> List[Dict[str, str]]:
        return self.store.get(session_id, [])

    def add_message(self, session_id: str, role: str, content: str):
        if session_id not in self.store:
            self.store[session_id] = []

        self.store[session_id].append({"role": role, "content": content})

        if len(self.store[session_id]) > self.max_history:
            self.store[session_id] = self.store[session_id][-self.max_history:]

memory_manager = MemoryManager(max_history=6)