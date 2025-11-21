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


class DeveloperAgentExecutor(BaseAgent):
    """Developer Agent Executor with A2A protocol support and full project generation"""
    
    def __init__(self):
        super().__init__(name="Developer")
        
        # Ensure API key is set in environment
        api_key = os.getenv("GOOGLE_API_KEY")
        if api_key:
            os.environ["GOOGLE_API_KEY"] = api_key
            
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            temperature=0.7
        )
        
    async def execute(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute task based on input data"""
        # Handle standard A2A message format
        content = task_data.get("content", {})
        action = content.get("action")
        parameters = content.get("parameters", {})
        
        if action == "generate_code":
            task = parameters.get("task", "")
            return await self.generate_complete_project(task)
            
        elif action == "modify_code":
            current_files = parameters.get("current_files", {})
            modification_request = parameters.get("modification_request", "")
            task_context = parameters.get("task_context", "")
            return await self.modify_code(current_files, modification_request, task_context)
            
        elif action == "fix_bug":
            files = parameters.get("files", {})
            errors = parameters.get("errors", [])
            return await self.fix_bug(files, errors)
            
        return {"error": f"Unknown action: {action}"}
    
    async def generate_complete_project(self, task: str) -> Dict[str, Any]:
        """Generate complete React project with all necessary files"""
        
        # Generate App.js
        app_code = await self._generate_app_code(task)
        
        # Generate index.js
        index_code = """import React from 'react';
import { createRoot } from 'react-dom/client';
import App from './App';
import './styles.css';

const root = createRoot(document.getElementById('root'));
root.render(<App />);
"""
        
        # Generate package.json
        package_json = {
            "name": "generated-app",
            "version": "1.0.0",
            "dependencies": {
                "react": "^18.3.0",
                "react-dom": "^18.3.0"
            },
            "devDependencies": {},
            "scripts": {
                "start": "react-scripts start",
                "build": "react-scripts build"
            }
        }
        
        # Generate index.html
        html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Generated App</title>
</head>
<body>
    <div id="root"></div>
</body>
</html>"""
        
        # Generate styles.css
        styles = await self._generate_styles(task, app_code)
        
        return {
            "files": {
                "/App.js": app_code,
                "/index.js": index_code,
                "/package.json": json.dumps(package_json, indent=2),
                "/index.html": html,
                "/styles.css": styles
            },
            "status": "success"
        }
    
    async def _generate_app_code(self, task: str) -> str:
        """Generate App.js code"""
        prompt = f"""Generate a complete, working React component for this task:

Task: {task}

IMPORTANT RULES:
1. Generate ONLY pure JavaScript/React code - NO markdown, NO code fences, NO explanations
2. Start directly with imports (e.g., "import React...")
3. Export a default function component named "App"
4. Use modern React hooks (useState, useEffect, etc.)
5. Make it functional and complete
6. Use className for styling (CSS classes will be in styles.css)
7. Do NOT include any text before or after the code
8. Do NOT wrap code in ```react or ``` blocks

Example format:
import React, {{ useState }} from 'react';

export default function App() {{
  const [count, setCount] = useState(0);
  return (
    <div className="app-container">
      <h1>Counter: {{count}}</h1>
      <button onClick={{() => setCount(count + 1)}}>Increment</button>
    </div>
  );
}}

Now generate code for the task above:"""
        
        result = await self.llm.ainvoke(prompt)
        code = result.content if hasattr(result, 'content') else str(result)
        
        return self._clean_code(code, task)
    
    async def _generate_styles(self, task: str, app_code: str = "") -> str:
        """Generate CSS styles"""
        prompt = f"""Generate modern CSS for this React app.

Task: {task}

App Code Structure:
{app_code[:500]}...

Generate clean, modern CSS with:
- Responsive design
- Good color scheme (use CSS variables)
- Proper spacing and typography
- Hover effects and transitions
- Mobile-first approach

Return ONLY CSS code, no explanations, no markdown fences."""
        
        result = await self.llm.ainvoke(prompt)
        css = result.content if hasattr(result, 'content') else str(result)
        
        # Clean CSS
        css = css.strip()
        if css.startswith("```"):
            lines = css.split('\n')
            if lines[0].startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]
            css = '\n'.join(lines)
        
        if not css or len(css) < 20:
            css = """/* Default styles */
:root {
  --primary-color: #6366f1;
  --secondary-color: #8b5cf6;
  --bg-color: #ffffff;
  --text-color: #1f2937;
}

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif;
  background: var(--bg-color);
  color: var(--text-color);
}

.app-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
}

button {
  background: var(--primary-color);
  color: white;
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 0.5rem;
  cursor: pointer;
  font-size: 1rem;
  transition: all 0.2s;
}

button:hover {
  background: var(--secondary-color);
  transform: translateY(-2px);
}
"""
        
        return css
    
    def _clean_code(self, code: str, task: str = "") -> str:
        """Clean generated code"""
        code = code.strip()
        
        # Remove markdown code fences
        if code.startswith("```"):
            lines = code.split('\n')
            if lines[0].startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]
            code = '\n'.join(lines)
        
        # Fallback if code is invalid
        if not code or len(code) < 20:
            code = f"""import React from 'react';

export default function App() {{
  return (
    <div className="app-container">
      <h1>Task: {task}</h1>
      <p>Code generation in progress...</p>
    </div>
  );
}}"""
        
        return code
    
    async def modify_code(self, current_files: Dict[str, str], 
                         modification_request: str, task_context: str) -> Dict[str, Any]:
        """Modify existing code based on user request"""
        current_app = current_files.get("/App.js", "")
        current_css = current_files.get("/styles.css", "")
        
        # Determine if this is a styling request
        is_styling = any(keyword in modification_request.lower() for keyword in [
            'css', 'style', 'color', 'design', 'look', 'appearance', 'đẹp', 'màu'
        ])
        
        if is_styling:
            # Generate new CSS
            new_css = await self._generate_styles(modification_request, current_app)
            return {
                "files": {
                    **current_files,
                    "/styles.css": new_css
                },
                "status": "modified"
            }
        else:
            # Modify App.js
            prompt = f"""You are modifying an existing React application.

Current App Code:
{current_app}

User's modification request: {modification_request}

Context: {task_context}

IMPORTANT RULES:
1. Generate ONLY pure JavaScript/React code - NO markdown, NO code fences
2. Start directly with imports
3. Keep all existing functionality and ADD the requested modifications
4. Export a default function component named "App"
5. Use className for styling
6. Do NOT include any text before or after the code
7. Do NOT wrap code in ```react or ``` blocks

Provide the complete modified code:"""
            
            result = await self.llm.ainvoke(prompt)
            modified_code = result.content if hasattr(result, 'content') else str(result)
            modified_code = self._clean_code(modified_code)
            
            return {
                "files": {
                    **current_files,
                    "/App.js": modified_code
                },
                "status": "modified"
            }
    
    async def fix_bug(self, files: Dict[str, str], errors: List[str]) -> Dict[str, Any]:
        """Fix bugs in the code"""
        current_code = files.get("/App.js", "")
        error_description = "\n".join(errors)
        
        prompt = f"""Fix the bugs in this React code.

Current Code:
{current_code}

Errors Found:
{error_description}

IMPORTANT RULES:
1. Generate ONLY pure JavaScript/React code - NO markdown, NO code fences
2. Start directly with imports
3. Fix all the errors mentioned
4. Keep the same functionality but make it work correctly
5. Do NOT include any text before or after the code
6. Do NOT wrap code in ```react or ``` blocks

Provide the corrected code:"""
        
        result = await self.llm.ainvoke(prompt)
        fixed_code = result.content if hasattr(result, 'content') else str(result)
        fixed_code = self._clean_code(fixed_code)
        
        return {
            "files": {
                **files,
                "/App.js": fixed_code
            },
            "status": "fixed"
        }
