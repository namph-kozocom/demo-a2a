from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any
import json
import asyncio
import logging
from protocol import Request, Response
from protocol.transport import network_transport, agent_registry

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Web Builder API - Main Orchestrator")

# CORS middleware for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register agent URLs
agent_registry.register("Analyst", "http://localhost:8001")
agent_registry.register("Developer", "http://localhost:8002")
agent_registry.register("Tester", "http://localhost:8003")

class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []
        # Store conversation context per connection
        self.contexts: dict[WebSocket, dict] = {}
        # Store message callbacks
        self.callbacks: list[callable] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        # Initialize context for this connection
        self.contexts[websocket] = {
            "current_files": {},
            "conversation_history": [],
            "current_task": "",
            "conversation_id": f"conv_{id(websocket)}"
        }

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        if websocket in self.contexts:
            del self.contexts[websocket]

    async def send_message(self, message: Dict[str, Any], websocket: WebSocket):
        await websocket.send_text(json.dumps(message))
    
    async def broadcast_message(self, msg):
        """Broadcast message to all connected clients"""
        message = {
            "role": "system",
            "content": f"🔄 Message: {msg.from_agent} → {msg.to_agent}",
            "agent": "System",
            "message": msg.to_dict()
        }
        
        for connection in self.active_connections:
            try:
                await self.send_message(message, connection)
            except:
                pass
    
    def get_context(self, websocket: WebSocket) -> dict:
        return self.contexts.get(websocket, {
            "current_files": {},
            "conversation_history": [],
            "current_task": "",
            "conversation_id": f"conv_{id(websocket)}"
        })
    
    def update_context(self, websocket: WebSocket, **kwargs):
        if websocket in self.contexts:
            self.contexts[websocket].update(kwargs)

manager = ConnectionManager()

@app.on_event("startup")
async def startup_event():
    """Check agent health on startup"""
    logger.info("Checking agent health...")
    health_status = await agent_registry.check_all_health(network_transport)
    
    for agent_name, is_healthy in health_status.items():
        if is_healthy:
            logger.info(f"✓ {agent_name} agent is healthy")
        else:
            logger.warning(f"✗ {agent_name} agent is not responding")

@app.get("/")
async def root():
    return {
        "message": "Web Builder API - Main Orchestrator",
        "status": "running",
        "agents": agent_registry.list_agents()
    }

@app.get("/health")
async def health():
    """Check health of orchestrator and all agents"""
    agent_health = await agent_registry.check_all_health(network_transport)
    
    return {
        "status": "healthy",
        "orchestrator": "running",
        "agents": agent_health
    }

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            message = json.loads(data)
            
            user_request = message.get("content", "")
            context = manager.get_context(websocket)
            conversation_id = context["conversation_id"]
            
            # Add to conversation history
            context["conversation_history"].append({
                "role": "user",
                "content": user_request
            })
            
            # Check if user is requesting code generation or modification
            request_lower = user_request.lower()
            needs_code = any(keyword in request_lower for keyword in [
                'build', 'create', 'make', 'generate', 'code', 'app', 'component',
                'website', 'page', 'feature', 'implement', 'develop', 'tạo', 'xây dựng',
                'add', 'thêm', 'update', 'cập nhật', 'change', 'thay đổi', 'modify', 'sửa',
                'improve', 'cải thiện', 'style', 'css', 'design', 'đẹp'
            ])
            
            # Check if this is a follow-up request (has current files)
            is_followup = len(context["current_files"]) > 0
            
            if not needs_code and not is_followup:
                # Just respond conversationally
                response = "Hello! I'm here to help you build web applications. You can ask me to create components, apps, or features. For example: 'Build a todo app' or 'Create a counter component'."
                await manager.send_message({
                    "role": "assistant",
                    "content": response,
                    "agent": "Analyst"
                }, websocket)
                context["conversation_history"].append({
                    "role": "assistant",
                    "content": response
                })
                continue
            
            # Send acknowledgment
            await manager.send_message({
                "role": "assistant",
                "content": f"Analyzing your request: {user_request}",
                "agent": "Analyst"
            }, websocket)
            
            # Build context for agents
            if is_followup:
                # This is a modification request
                task_context = f"""Previous task: {context['current_task']}
Current code files:
{json.dumps(context['current_files'], indent=2)}

New request: {user_request}

Please modify the existing code to fulfill this new request."""
            else:
                # This is a new project
                task_context = user_request
                context["current_task"] = user_request
            
            # === HTTP-BASED A2A PROTOCOL COMMUNICATION ===
            
            logger.info(f"🔄 Orchestrator → Analyst: analyze_request")
            
            # 1. Orchestrator → Analyst (via HTTP)
            analyst_request = Request(
                from_agent="Orchestrator",
                to_agent="Analyst",
                action="analyze_request",
                parameters={"user_request": task_context},
                conversation_id=conversation_id
            )
            
            analyst_url = agent_registry.get_url("Analyst")
            analyst_response = await network_transport.send_message(analyst_request, analyst_url)
            analyst_response_data = analyst_response
            
            await manager.send_message({
                "role": "system",
                "content": f"📨 A2A: Orchestrator → Analyst (HTTP)",
                "agent": "System"
            }, websocket)
            
            await manager.send_message({
                "role": "assistant",
                "content": analyst_response_data["message"],
                "agent": "Analyst"
            }, websocket)
            
            logger.info(f"🔄 Analyst → Developer: {('modify_code' if is_followup else 'generate_code')}")
            
            # 2. Orchestrator → Developer (via HTTP)
            if is_followup:
                dev_request = Request(
                    from_agent="Orchestrator",
                    to_agent="Developer",
                    action="modify_code",
                    parameters={
                        "current_files": context["current_files"],
                        "modification_request": user_request,
                        "task_context": analyst_response_data["task"]
                    },
                    conversation_id=conversation_id
                )
                
                await manager.send_message({
                    "role": "assistant",
                    "content": "Modifying code...",
                    "agent": "Developer"
                }, websocket)
            else:
                dev_request = Request(
                    from_agent="Orchestrator",
                    to_agent="Developer",
                    action="generate_code",
                    parameters={"task": analyst_response_data["task"]},
                    conversation_id=conversation_id
                )
                
                await manager.send_message({
                    "role": "assistant",
                    "content": "Starting code generation...",
                    "agent": "Developer"
                }, websocket)
            
            developer_url = agent_registry.get_url("Developer")
            dev_response = await network_transport.send_message(dev_request, developer_url)
            dev_response_data = dev_response
            
            await manager.send_message({
                "role": "system",
                "content": f"📨 A2A: Orchestrator → Developer (HTTP)",
                "agent": "System"
            }, websocket)
            
            # Update context with new files
            manager.update_context(websocket, current_files=dev_response_data["files"])
            
            # Send code update to frontend
            await manager.send_message({
                "role": "assistant",
                "content": "Code generated successfully! Check the preview panel." if not is_followup else "Code updated! Check the preview.",
                "agent": "Developer",
                "files": dev_response_data["files"]
            }, websocket)
            
            logger.info(f"🔄 Developer → Tester: test_code")
            
            # 3. Orchestrator → Tester (via HTTP)
            test_request = Request(
                from_agent="Orchestrator",
                to_agent="Tester",
                action="test_code",
                parameters={"files": dev_response_data["files"]},
                conversation_id=conversation_id
            )
            
            await manager.send_message({
                "role": "assistant",
                "content": "Running tests...",
                "agent": "Tester"
            }, websocket)
            
            tester_url = agent_registry.get_url("Tester")
            test_response = await network_transport.send_message(test_request, tester_url)
            test_response_data = test_response
            
            await manager.send_message({
                "role": "system",
                "content": f"📨 A2A: Orchestrator → Tester (HTTP)",
                "agent": "System"
            }, websocket)
            
            if test_response_data["status"] == "failed":
                # Send back to developer for fixes
                await manager.send_message({
                    "role": "assistant",
                    "content": f"Tests failed. Requesting fixes...",
                    "agent": "Tester"
                }, websocket)
                
                logger.info(f"🔄 Tester → Developer: fix_bug")
                
                fix_request = Request(
                    from_agent="Orchestrator",
                    to_agent="Developer",
                    action="fix_bug",
                    parameters={
                        "files": dev_response_data["files"],
                        "errors": test_response_data["errors"]
                    },
                    conversation_id=conversation_id
                )
                
                fix_response = await network_transport.send_message(fix_request, developer_url)
                fix_response_data = fix_response["result"]
                
                await manager.send_message({
                    "role": "system",
                    "content": f"📨 A2A: Orchestrator → Developer (fix_bug via HTTP)",
                    "agent": "System"
                }, websocket)
                
                # Update context
                manager.update_context(websocket, current_files=fix_response_data["files"])
                
                # Send fixed code
                await manager.send_message({
                    "role": "assistant",
                    "content": "Bug fixed! Re-running tests...",
                    "agent": "Developer",
                    "files": fix_response_data["files"]
                }, websocket)
                
                # Re-test
                retest_request = Request(
                    from_agent="Orchestrator",
                    to_agent="Tester",
                    action="test_code",
                    parameters={"files": fix_response_data["files"]},
                    conversation_id=conversation_id
                )
                
                retest_response = await network_transport.send_message(retest_request, tester_url)
                test_response_data = retest_response["result"]
            
            await manager.send_message({
                "role": "assistant",
                "content": f"All tests passed! ✓ Your application is ready.",
                "agent": "Tester"
            }, websocket)
            
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        await manager.send_message({
            "role": "system",
            "content": f"Error: {str(e)}"
        }, websocket)
        manager.disconnect(websocket)

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting Main Orchestrator on port 8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)
