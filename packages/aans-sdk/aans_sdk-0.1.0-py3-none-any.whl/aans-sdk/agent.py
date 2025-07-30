# src/aans_sdk/agent.py
from typing import Any, Dict
import requests
from .agent_card import AgentCard

class Agent:
    def __init__(self, card: AgentCard):
        self.card = card
        self.endpoint = card.endpoint

    def ask(self, question: Dict[str, Any]) -> Dict[str, Any]:
        response = requests.post(self.endpoint, json=question)
        response.raise_for_status()
        return response.json()

    def describe(self) -> Dict[str, Any]:
        return self.card.dict()
