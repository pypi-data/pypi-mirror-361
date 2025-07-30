import requests
from typing import Optional, List
from .agent_card import AgentCard
from .agent import Agent

class AgentNameServiceClient:
    def __init__(self, service_url: str):
        self.service_url = service_url.rstrip("/")

    def get_agent_card(self, name: str) -> AgentCard:
        response = requests.get(f"{self.service_url}/agents/{name}")
        response.raise_for_status()
        return AgentCard(**response.json())

    def list_agents(self) -> List[AgentCard]:
        response = requests.get(f"{self.service_url}/agents")
        response.raise_for_status()
        return [AgentCard(**agent) for agent in response.json()]

    def get_agent(self, name: Optional[str] = None) -> Agent:
        card = self.get_agent_card(name) if name else self.list_agents()[0]
        return Agent(endpoint=card.endpoint)
