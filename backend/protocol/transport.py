"""
Network Transport Layer for A2A Protocol

Provides HTTP-based communication between distributed agents.
"""

import httpx
import asyncio
from typing import Dict, Any, Optional
from .protocol import Message, Request, Response, Notification
import logging

logger = logging.getLogger(__name__)


class NetworkTransport:
    """HTTP-based transport for A2A messages"""
    
    def __init__(self, timeout: float = 30.0, max_retries: int = 3):
        self.timeout = timeout
        self.max_retries = max_retries
        self.client = httpx.AsyncClient(timeout=timeout)
    
    async def send_message(self, message: Message, target_url: str) -> Dict[str, Any]:
        """
        Send A2A message to target agent via HTTP POST
        
        Args:
            message: A2A message to send
            target_url: Base URL of target agent (e.g., http://localhost:8001)
            
        Returns:
            Response data from target agent
        """
        endpoint = f"{target_url}/message"
        payload = message.to_dict()
        
        for attempt in range(self.max_retries):
            try:
                logger.info(f"Sending {message.type} from {message.from_agent} to {message.to_agent} at {endpoint}")
                
                response = await self.client.post(
                    endpoint,
                    json=payload,
                    headers={"Content-Type": "application/json"}
                )
                
                response.raise_for_status()
                result = response.json()
                
                logger.info(f"Received response from {message.to_agent}: {result.get('status', 'unknown')}")
                return result
                
            except httpx.HTTPError as e:
                logger.error(f"HTTP error on attempt {attempt + 1}/{self.max_retries}: {e}")
                
                if attempt == self.max_retries - 1:
                    raise
                
                # Exponential backoff
                await asyncio.sleep(2 ** attempt)
        
        raise Exception(f"Failed to send message after {self.max_retries} attempts")
    
    async def check_health(self, agent_url: str) -> bool:
        """
        Check if agent is healthy
        
        Args:
            agent_url: Base URL of agent
            
        Returns:
            True if agent is healthy, False otherwise
        """
        try:
            response = await self.client.get(f"{agent_url}/health", timeout=5.0)
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Health check failed for {agent_url}: {e}")
            return False
    
    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()


class AgentRegistry:
    """Registry of agent URLs for network communication"""
    
    def __init__(self):
        self.agents: Dict[str, str] = {}
    
    def register(self, agent_name: str, url: str):
        """Register an agent with its URL"""
        self.agents[agent_name] = url
        logger.info(f"Registered agent {agent_name} at {url}")
    
    def get_url(self, agent_name: str) -> Optional[str]:
        """Get URL for an agent"""
        return self.agents.get(agent_name)
    
    def list_agents(self) -> Dict[str, str]:
        """List all registered agents"""
        return self.agents.copy()
    
    async def check_all_health(self, transport: NetworkTransport) -> Dict[str, bool]:
        """Check health of all registered agents"""
        results = {}
        for name, url in self.agents.items():
            results[name] = await transport.check_health(url)
        return results


# Global instances
network_transport = NetworkTransport()
agent_registry = AgentRegistry()
