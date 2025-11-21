from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from ..types import AgentCard

class A2AStarletteApplication:
    def __init__(self, agent_card: AgentCard, http_handler):
        self.agent_card = agent_card
        self.http_handler = http_handler
        self.app = FastAPI(title=agent_card.name, version=agent_card.version)
        
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        self.setup_routes()
    
    def setup_routes(self):
        @self.app.get("/")
        async def root():
            return {
                "name": self.agent_card.name,
                "description": self.agent_card.description,
                "version": self.agent_card.version,
                "status": "running"
            }
            
        @self.app.get("/health")
        async def health():
            return {"status": "healthy"}
            
        @self.app.post("/")
        async def handle_request(request: Request):
            return await self.http_handler.handle(request)
            
        @self.app.post("/message")
        async def handle_message(request: Request):
            # Alias for / for compatibility
            return await self.http_handler.handle(request)
            
    def build(self):
        return self.app
