"""
Tester Agent Service

Independent FastAPI service for the Tester agent.
Runs on port 8003.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from tester_agent import TesterAgentExecutor
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
        id='tester',
        name='Tester Agent',
        description='Tests React application code',
        tags=['testing', 'qa', 'react'],
        examples=['Test this component', 'Verify app structure']
    )

    agent_card = AgentCard(
        name='Tester Agent',
        description='QA Tester',
        url='http://localhost:8003/',
        version='1.0.0',
        default_input_modes=['text'],
        default_output_modes=['text'],
        capabilities=AgentCapabilities(streaming=False),
        skills=[skill],
    )

    # Initialize Executor and Handler
    executor = TesterAgentExecutor()
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
    logger.info("Starting Tester Agent Service on port 8003")
    uvicorn.run(server.build(), host="0.0.0.0", port=8003)
