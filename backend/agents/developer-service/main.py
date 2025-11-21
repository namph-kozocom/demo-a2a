"""
Developer Agent Service

Independent FastAPI service for the Developer agent.
Runs on port 8002.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from developer_agent import DeveloperAgentExecutor
from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import AgentCard, AgentCapabilities, AgentSkill
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    # Define Agent Metadata
    skill = AgentSkill(
        id='developer',
        name='Developer Agent',
        description='Generates and modifies React application code',
        tags=['coding', 'react', 'javascript'],
        examples=['Create a counter component', 'Fix the bug in App.js']
    )

    agent_card = AgentCard(
        name='Developer Agent',
        description='Software Developer',
        url='http://localhost:8002/',
        version='1.0.0',
        default_input_modes=['text'],
        default_output_modes=['text'],
        capabilities=AgentCapabilities(streaming=False),
        skills=[skill],
    )

    # Initialize Executor and Handler
    executor = DeveloperAgentExecutor()
    request_handler = DefaultRequestHandler(
        agent_executor=executor,
        task_store=InMemoryTaskStore(),
    )

    # Create Server
    server = A2AStarletteApplication(
        agent_card=agent_card, 
        http_handler=request_handler
    )
    
    import uvicorn
    logger.info("Starting Developer Agent Service on port 8002")
    uvicorn.run(server.build(), host="0.0.0.0", port=8002)
