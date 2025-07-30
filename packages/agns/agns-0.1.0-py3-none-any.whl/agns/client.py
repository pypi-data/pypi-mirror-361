import requests
from typing import Optional, List
from .agent_card import AgentCard
from .agent import Agent

class AgentNameServiceClient:
    DEFAULT_SERVICE_URL = "https://app.clearentitlement.com"
    PATH_GET_AGENTS = "/ce/admin/Agents"

    def __init__(self, service_url: Optional[str] = None):
        self.service_url = (service_url or self.DEFAULT_SERVICE_URL).rstrip("/")

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
    
    def get_agents(self) -> List[Agent]:
        url = f"{self.service_url}{self.PATH_GET_AGENTS}"
        headers = {"ApiKey": "CXurddJ/ZG7sPeM9ASSvBQ==_ZYadI2rgSwzuHLSstzFFBiiPKm7+gWClc666Xn51xGR32mo2GT8NosljvWziugqaxo7hK+nfnoC0f93PEMhrxZKUSUscpUnCRbmrNrXPyfA="}
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        agents_json = response.json()
        print("API response:", agents_json)
        agent_cards = []
        for agent in agents_json:
            try:
                converted = self._convert_agent_api_response(agent)
                agent_cards.append(AgentCard(**converted))
            except Exception as e:
                print(f"Skipping agent due to error: {e}, data: {agent}")
        return [Agent(endpoint=card.endpoint) for card in agent_cards]
    
    def _convert_agent_api_response(self, agent: dict) -> dict:
        """
        Convert API agent dict to AgentCard-compatible dict.
        Adjust the mapping as needed based on your API response.
        """
        return {
            "id": agent.get("id"),
            "name": agent.get("name"),
            "description": agent.get("description"),
            "endpoint": agent.get("url"),  # Map 'url' from API to 'endpoint'
            "capabilities": agent.get("capabilities", []),
            "tags": agent.get("tags", []),
            "avatar_url": agent.get("avatar_url"),
        }