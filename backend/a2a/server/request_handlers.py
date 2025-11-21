from typing import Any, Dict
from fastapi import Request

class DefaultRequestHandler:
    def __init__(self, agent_executor, task_store):
        self.agent_executor = agent_executor
        self.task_store = task_store
        
    async def handle(self, request: Request):
        """Handle incoming HTTP request"""
        body = await request.json()
        
        # Pass full body to executor
        result = await self.agent_executor.execute(body)
        
        return result
