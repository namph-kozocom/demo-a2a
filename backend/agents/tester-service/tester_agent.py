from typing import Dict, Any, List
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain.tools import tool
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv
import os
import json
from agents.base_agent import BaseAgent

load_dotenv()


@tool
def verify_code(code: str) -> str:
    """Verify React code structure"""
    if "export default" in code and "function" in code:
        return json.dumps({"status": "valid", "errors": []})
    return json.dumps({"status": "invalid", "errors": ["Missing export or function"]})


@tool
def run_playwright_test(code: str) -> str:
    """Run Playwright browser tests (simulated)"""
    # Simulated test results
    return json.dumps({
        "status": "passed",
        "tests_run": 5,
        "tests_passed": 5,
        "tests_failed": 0,
        "errors": []
    })


class TesterAgentExecutor(BaseAgent):
    """Tester Agent Executor with A2A protocol support"""
    
    def __init__(self):
        super().__init__(name="Tester")
        
        # Ensure API key is set in environment
        api_key = os.getenv("GOOGLE_API_KEY")
        if api_key:
            os.environ["GOOGLE_API_KEY"] = api_key
            
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            temperature=0.3
        )
        
        self.tools = [verify_code, run_playwright_test]
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a Tester Agent specialized in testing React applications.
Your role is to:
1. Verify code structure and syntax
2. Run tests to ensure functionality
3. Report any issues found

Be thorough but concise in your testing."""),
            ("human", "{input}"),
            ("placeholder", "{agent_scratchpad}"),
        ])
        
        self.agent = create_tool_calling_agent(self.llm, self.tools, prompt)
        self.executor = AgentExecutor(agent=self.agent, tools=self.tools, verbose=True)
        
    async def execute(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute task based on input data"""
        # Handle standard A2A message format
        content = task_data.get("content", {})
        action = content.get("action")
        parameters = content.get("parameters", {})
        
        if action == "test_code":
            files = parameters.get("files", {})
            return await self.test_code(files)
            
        return {"error": f"Unknown action: {action}"}
    
    async def test_code(self, files: Dict[str, Any]) -> Dict[str, Any]:
        """Test the generated code"""
        
        # Get main app code
        app_code = files.get("/App.js", "")
        
        if not app_code:
            return {
                "status": "failed",
                "errors": ["No code to test"],
                "tests_run": 0,
                "tests_passed": 0,
                "tests_failed": 1
            }
        
        # Simple validation
        errors = []
        
        # Check for basic React structure
        if "import" not in app_code:
            errors.append("Missing import statements")
        
        if "export default" not in app_code:
            errors.append("Missing default export")
        
        if "function" not in app_code and "const" not in app_code:
            errors.append("Missing component function")
        
        # Check for common issues
        if app_code.startswith("```"):
            errors.append("Code contains markdown fences")
        
        if errors:
            return {
                "status": "failed",
                "errors": errors,
                "tests_run": len(errors),
                "tests_passed": 0,
                "tests_failed": len(errors)
            }
        
        # All tests passed
        return {
            "status": "passed",
            "errors": [],
            "tests_run": 3,
            "tests_passed": 3,
            "tests_failed": 0
        }
