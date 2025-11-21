"""
Base Agent class with protocol support
"""

from typing import Dict, Any, Optional, Callable
from protocol import Message, Request, Response, Notification, message_bus
import asyncio


class BaseAgent:
    """Base class for all agents with protocol support"""
    
    def __init__(self, name: str):
        self.name = name
        self.message_queue = asyncio.Queue()
        self.handlers: Dict[str, Callable] = {}
        
        # Subscribe to message bus
        message_bus.subscribe(self.name, self._on_message_received)
    
    def _on_message_received(self, message: Message):
        """Callback when message is received"""
        # Add to queue for async processing
        asyncio.create_task(self.message_queue.put(message))
    
    async def send_request(self, to_agent: str, action: str, 
                          parameters: Dict[str, Any] = None,
                          context: Dict[str, Any] = None,
                          conversation_id: str = None) -> Request:
        """Send a request to another agent"""
        request = Request(
            from_agent=self.name,
            to_agent=to_agent,
            action=action,
            parameters=parameters,
            context=context,
            conversation_id=conversation_id
        )
        
        message_bus.publish(request)
        return request
    
    async def send_response(self, to_agent: str, status: str,
                           result: Any = None, error: str = None,
                           request_id: str = None,
                           conversation_id: str = None) -> Response:
        """Send a response to another agent"""
        response = Response(
            from_agent=self.name,
            to_agent=to_agent,
            status=status,
            result=result,
            error=error,
            request_id=request_id,
            conversation_id=conversation_id
        )
        
        message_bus.publish(response)
        return response
    
    async def send_notification(self, to_agent: str, event: str,
                               data: Dict[str, Any] = None,
                               conversation_id: str = None) -> Notification:
        """Send a notification to another agent"""
        notification = Notification(
            from_agent=self.name,
            to_agent=to_agent,
            event=event,
            data=data,
            conversation_id=conversation_id
        )
        
        message_bus.publish(notification)
        return notification
    
    def register_handler(self, action: str, handler: Callable):
        """Register a handler for a specific action"""
        self.handlers[action] = handler
    
    async def handle_message(self, message: Message):
        """Handle incoming message"""
        if message.type == "request":
            action = message.content.get("action")
            if action in self.handlers:
                handler = self.handlers[action]
                try:
                    result = await handler(message.content.get("parameters", {}))
                    await self.send_response(
                        to_agent=message.from_agent,
                        status="success",
                        result=result,
                        request_id=message.message_id,
                        conversation_id=message.metadata.get("conversation_id")
                    )
                except Exception as e:
                    await self.send_response(
                        to_agent=message.from_agent,
                        status="error",
                        error=str(e),
                        request_id=message.message_id,
                        conversation_id=message.metadata.get("conversation_id")
                    )
    
    async def process_messages(self):
        """Process messages from queue"""
        while True:
            message = await self.message_queue.get()
            await self.handle_message(message)
