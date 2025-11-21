from typing import Dict, Any
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph, END
from typing_extensions import TypedDict
from dotenv import load_dotenv
import os
from agents.base_agent import BaseAgent

load_dotenv()


class AnalystState(TypedDict):
    user_request: str
    analysis: str
    task: str


class AnalystAgentExecutor(BaseAgent):
    """Analyst Agent Executor with A2A protocol support"""
    
    def __init__(self):
        super().__init__(name="Analyst")
        
        # Ensure API key is set in environment
        api_key = os.getenv("GOOGLE_API_KEY")
        if api_key:
            os.environ["GOOGLE_API_KEY"] = api_key
            
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash"
        )
        
    async def execute(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute task based on input data"""
        # Handle standard A2A message format
        content = task_data.get("content", {})
        action = content.get("action")
        parameters = content.get("parameters", {})
        
        if action == "analyze_request":
            user_request = parameters.get("user_request", "")
            return await self.process(user_request)
        
        return {"error": f"Unknown action: {action}"}
    
    async def process(self, user_request: str) -> Dict[str, Any]:
        """Process user request and create development task"""
        
        prompt = f"""You are a System Analyst Agent. Analyze this user request and create a clear development task.

User Request: {user_request}

Provide:
1. A brief analysis of what the user wants
2. A clear, detailed task description for the Developer agent

Keep it concise but complete."""
        
        result = await self.llm.ainvoke(prompt)
        response = result.content if hasattr(result, 'content') else str(result)
        
        # Extract task (simple heuristic: last paragraph or full response)
        lines = response.strip().split('\n')
        task = '\n'.join(lines[-3:]) if len(lines) > 3 else response
        
        return {
            "message": response,
            "task": task,
            "status": "analyzed"
        }
