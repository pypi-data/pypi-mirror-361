# my_sdk/agent_card.py

from pydantic import BaseModel, HttpUrl
from typing import List, Optional, Dict, Any

class AgentCard(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    endpoint: HttpUrl
    capabilities: List[str] = []
    tags: List[str] = []
    avatar_url: Optional[HttpUrl] = None

    def ask(self, question: Dict[str, Any]) -> Dict[str, Any]:
        """
        Simulate asking a question to the agent.
        Args:
            question (dict): The question as a JSON object.
        Returns:
            dict: The response as a JSON object.
        """
        # Placeholder implementation
        return {"answer": "This is a mock response.", "question": question}
