from dataclasses import dataclass, field
from typing import Dict, Any, Optional
from datetime import datetime
from enum import Enum
import uuid

class MessageType(str, Enum):
    REQUEST = "request"
    RESPONSE = "response"
    EVENT = "event"

class Priority(int, Enum):
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4

@dataclass
class Message:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    type: MessageType = MessageType.REQUEST
    sender: str = ""
    timestamp: datetime = field(default_factory=datetime.utcnow)
    data: Dict[str, Any] = field(default_factory=dict)
    priority: Priority = Priority.NORMAL
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "type": self.type.value,
            "sender": self.sender,
            "timestamp": self.timestamp.isoformat(),
            "data": self.data,
            "priority": self.priority.value
        }

@dataclass
class Request(Message):
    type: MessageType = MessageType.REQUEST
    target: str = ""
    action: str = ""
    timeout: int = 30
    correlation_id: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        base = super().to_dict()
        base.update({
            "target": self.target,
            "action": self.action,
            "timeout": self.timeout,
            "correlation_id": self.correlation_id
        })
        return base

@dataclass
class Response(Message):
    type: MessageType = MessageType.RESPONSE
    target: str = ""
    request_id: str = ""
    success: bool = True
    result: Any = None
    error: Optional[str] = None
    execution_time: Optional[float] = None
    
    def to_dict(self) -> Dict[str, Any]:
        base = super().to_dict()
        base.update({
            "target": self.target,
            "request_id": self.request_id,
            "success": self.success,
            "result": self.result,
            "error": self.error,
            "execution_time": self.execution_time
        })
        return base

@dataclass
class Event(Message):
    type: MessageType = MessageType.EVENT
    event: str = ""
    scope: str = "all"
    recipients: Optional[list] = None
    
    def to_dict(self) -> Dict[str, Any]:
        base = super().to_dict()
        base.update({
            "event": self.event,
            "scope": self.scope,
            "recipients": self.recipients
        })
        return base

# Mensajes específicos para agentes de IA

@dataclass
class AIRequest(Request):
    model: Optional[str] = None
    temperature: float = 0.7
    max_tokens: Optional[int] = None
    system_prompt: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        base = super().to_dict()
        base.update({
            "model": self.model,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "system_prompt": self.system_prompt
        })
        return base

@dataclass
class AIResponse(Response):
    model_used: Optional[str] = None
    tokens_used: Optional[int] = None
    cost: Optional[float] = None
    
    def to_dict(self) -> Dict[str, Any]:
        base = super().to_dict()
        base.update({
            "model_used": self.model_used,
            "tokens_used": self.tokens_used,
            "cost": self.cost
        })
        return base

# Factory functions para crear mensajes comunes

def create_request(sender: str, target: str, action: str, **kwargs) -> Request:
    return Request(
        sender=sender,
        target=target,
        action=action,
        data=kwargs.get('data', {}),
        timeout=kwargs.get('timeout', 30),
        priority=kwargs.get('priority', Priority.NORMAL)
    )

def create_ai_request(sender: str, target: str, prompt: str, **kwargs) -> AIRequest:
    return AIRequest(
        sender=sender,
        target=target,
        action="generate",
        data={"prompt": prompt, **kwargs.get('data', {})},
        model=kwargs.get('model'),
        temperature=kwargs.get('temperature', 0.7),
        max_tokens=kwargs.get('max_tokens'),
        system_prompt=kwargs.get('system_prompt')
    )

def create_response(request: Request, success: bool = True, **kwargs) -> Response:
    return Response(
        sender=request.target,
        target=request.sender,
        request_id=request.id,
        success=success,
        result=kwargs.get('result'),
        error=kwargs.get('error'),
        execution_time=kwargs.get('execution_time')
    )

def create_event(sender: str, event: str, **kwargs) -> Event:
    return Event(
        sender=sender,
        event=event,
        data=kwargs.get('data', {}),
        scope=kwargs.get('scope', 'all'),
        recipients=kwargs.get('recipients')
    )