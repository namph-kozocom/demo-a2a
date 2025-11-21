"""
Agent-to-Agent Protocol Implementation

This module implements the standardized protocol for agent communication.
"""

from dataclasses import dataclass, field, asdict
from typing import Dict, Any, Optional, Literal
from datetime import datetime
import uuid
import json


@dataclass
class Message:
    """Base message structure"""
    type: Literal["request", "response", "notification"]
    from_agent: str
    to_agent: str
    message_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    content: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary"""
        return {
            "type": self.type,
            "from": self.from_agent,
            "to": self.to_agent,
            "message_id": self.message_id,
            "timestamp": self.timestamp,
            "content": self.content,
            "metadata": self.metadata
        }
    
    def to_json(self) -> str:
        """Convert message to JSON string"""
        return json.dumps(self.to_dict(), indent=2)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Message':
        """Create message from dictionary"""
        return cls(
            type=data["type"],
            from_agent=data["from"],
            to_agent=data["to"],
            message_id=data.get("message_id", str(uuid.uuid4())),
            timestamp=data.get("timestamp", datetime.utcnow().isoformat()),
            content=data.get("content", {}),
            metadata=data.get("metadata", {})
        )


class Request(Message):
    """Request message"""
    type: Literal["request"] = "request"
    
    def __init__(self, from_agent: str, to_agent: str, action: str, 
                 parameters: Dict[str, Any] = None, context: Dict[str, Any] = None,
                 conversation_id: str = None, parent_message_id: str = None):
        super().__init__(
            type="request",
            from_agent=from_agent,
            to_agent=to_agent,
            content={
                "action": action,
                "parameters": parameters or {},
                "context": context or {}
            },
            metadata={
                "conversation_id": conversation_id,
                "parent_message_id": parent_message_id
            }
        )


class Response(Message):
    """Response message"""
    type: Literal["response"] = "response"
    
    def __init__(self, from_agent: str, to_agent: str, status: str,
                 result: Any = None, error: str = None,
                 request_id: str = None, conversation_id: str = None):
        super().__init__(
            type="response",
            from_agent=from_agent,
            to_agent=to_agent,
            content={
                "status": status,
                "result": result,
                "error": error
            },
            metadata={
                "request_id": request_id,
                "conversation_id": conversation_id
            }
        )


class Notification(Message):
    """Notification message"""
    type: Literal["notification"] = "notification"
    
    def __init__(self, from_agent: str, to_agent: str, event: str,
                 data: Dict[str, Any] = None, conversation_id: str = None):
        super().__init__(
            type="notification",
            from_agent=from_agent,
            to_agent=to_agent,
            content={
                "event": event,
                "data": data or {}
            },
            metadata={
                "conversation_id": conversation_id
            }
        )


class MessageBus:
    """Message bus for routing messages between agents"""
    
    def __init__(self):
        self.message_history: list[Message] = []
        self.subscribers: Dict[str, callable] = {}
    
    def subscribe(self, agent_name: str, callback: callable):
        """Subscribe an agent to receive messages"""
        self.subscribers[agent_name] = callback
    
    def publish(self, message: Message):
        """Publish a message to the bus"""
        # Store in history
        self.message_history.append(message)
        
        # Route to recipient
        if message.to_agent in self.subscribers:
            self.subscribers[message.to_agent](message)
    
    def get_history(self, conversation_id: str = None) -> list[Message]:
        """Get message history, optionally filtered by conversation"""
        if conversation_id:
            return [
                msg for msg in self.message_history
                if msg.metadata.get("conversation_id") == conversation_id
            ]
        return self.message_history
    
    def clear_history(self):
        """Clear message history"""
        self.message_history.clear()


# Global message bus instance
message_bus = MessageBus()
