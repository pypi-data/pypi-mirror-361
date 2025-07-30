import asyncio
import aiohttp
import time
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from .messages import Request, Response, Event
from .exceptions import MCPError, TimeoutError, RateLimitError, CircuitBreakerError

class CircuitState(Enum):
    CLOSED = "closed"
    OPEN = "open" 
    HALF_OPEN = "half_open"

@dataclass
class CircuitBreaker:
    failure_threshold: int = 5
    recovery_timeout: int = 60
    state: CircuitState = CircuitState.CLOSED
    failure_count: int = 0
    last_failure_time: Optional[datetime] = None
    
    def should_allow_request(self) -> bool:
        if self.state == CircuitState.CLOSED:
            return True
        elif self.state == CircuitState.OPEN:
            if self.last_failure_time and \
               (datetime.utcnow() - self.last_failure_time).seconds >= self.recovery_timeout:
                self.state = CircuitState.HALF_OPEN
                return True
            return False
        return True
    
    def record_success(self):
        self.failure_count = 0
        self.state = CircuitState.CLOSED
        self.last_failure_time = None
    
    def record_failure(self):
        self.failure_count += 1
        self.last_failure_time = datetime.utcnow()
        if self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN

@dataclass
class RateLimiter:
    requests_per_minute: int = 50
    tokens: float = 50
    last_refill: float = field(default_factory=time.time)
    
    def can_proceed(self) -> bool:
        now = time.time()
        time_passed = now - self.last_refill
        self.tokens = min(self.requests_per_minute, self.tokens + (time_passed * self.requests_per_minute / 60))
        self.last_refill = now
        
        if self.tokens >= 1:
            self.tokens -= 1
            return True
        return False

@dataclass
class RetryConfig:
    max_attempts: int = 3
    initial_delay: float = 1.0
    max_delay: float = 30.0
    exponential_base: float = 2.0

class MCPProtocol:
    def __init__(self):
        self.agents: Dict[str, Any] = {}
        self.circuit_breakers: Dict[str, CircuitBreaker] = {}
        self.rate_limiters: Dict[str, RateLimiter] = {}
        self.event_handlers: Dict[str, List[Callable]] = {}
        self.pending_requests: Dict[str, asyncio.Future] = {}
        self.session: Optional[aiohttp.ClientSession] = None
        self.running = False
        self.messages_sent = 0
        self.messages_received = 0
        
    async def start(self):
        if not self.running:
            self.session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=60),
                connector=aiohttp.TCPConnector(limit=100)
            )
            self.running = True
    
    async def stop(self):
        if self.running:
            if self.session:
                await self.session.close()
            self.running = False
    
    def register_agent(self, agent_id: str, agent: Any, **config):
        self.agents[agent_id] = agent
        
        # Configurar circuit breaker
        self.circuit_breakers[agent_id] = CircuitBreaker(
            failure_threshold=config.get('failure_threshold', 5),
            recovery_timeout=config.get('recovery_timeout', 60)
        )
        
        # Configurar rate limiter
        self.rate_limiters[agent_id] = RateLimiter(
            requests_per_minute=config.get('rate_limit', 50)
        )
    
    def subscribe(self, event: str, handler: Callable):
        if event not in self.event_handlers:
            self.event_handlers[event] = []
        self.event_handlers[event].append(handler)
    
    async def send_request(self, sender_id: str, target_id: str, action: str, 
                          data: Dict[str, Any] = None, timeout: int = 30,
                          retry_config: Optional[RetryConfig] = None) -> Response:
        
        if not self.running:
            await self.start()
        
        # Verificar circuit breaker
        circuit_breaker = self.circuit_breakers.get(target_id)
        if circuit_breaker and not circuit_breaker.should_allow_request():
            raise CircuitBreakerError(f"Circuit breaker open for {target_id}")
        
        # Verificar rate limit
        rate_limiter = self.rate_limiters.get(target_id)
        if rate_limiter and not rate_limiter.can_proceed():
            raise RateLimitError(f"Rate limit exceeded for {target_id}")
        
        request = Request(
            sender=sender_id,
            target=target_id,
            action=action,
            data=data or {},
            timeout=timeout
        )
        
        retry_config = retry_config or RetryConfig()
        last_error = None
        
        for attempt in range(retry_config.max_attempts):
            try:
                self.messages_sent += 1
                response = await self._send_request_attempt(request)
                
                # Actualizar circuit breaker en éxito
                if circuit_breaker:
                    circuit_breaker.record_success()
                
                return response
                
            except Exception as e:
                last_error = e
                
                # Actualizar circuit breaker en fallo
                if circuit_breaker:
                    circuit_breaker.record_failure()
                
                if attempt < retry_config.max_attempts - 1:
                    delay = min(
                        retry_config.initial_delay * (retry_config.exponential_base ** attempt),
                        retry_config.max_delay
                    )
                    await asyncio.sleep(delay)
                    continue
                break
        
        raise last_error or MCPError("Request failed after all retries")
    
    async def _send_request_attempt(self, request: Request) -> Response:
        agent = self.agents.get(request.target)
        if not agent:
            raise MCPError(f"Agent {request.target} not found")
        
        try:
            if hasattr(agent, 'handle_request'):
                # Agente local
                result = await agent.handle_request(request)
            elif hasattr(agent, 'api_url'):
                # Agente externo (API)
                result = await self._send_external_request(agent, request)
            else:
                raise MCPError(f"Agent {request.target} not compatible")
            
            response = Response(
                sender=request.target,
                target=request.sender,
                request_id=request.id,
                success=True,
                result=result
            )
            self.messages_received += 1
            return response
            
        except asyncio.TimeoutError:
            raise TimeoutError(f"Request to {request.target} timed out")
        except Exception as e:
            response = Response(
                sender=request.target,
                target=request.sender,
                request_id=request.id,
                success=False,
                error=str(e)
            )
            self.messages_received += 1
            return response
    
    async def _send_external_request(self, agent: Any, request: Request) -> Any:
        if not self.session:
            await self.start()
        
        # Construir payload según el tipo de agente
        if hasattr(agent, 'build_payload'):
            payload = agent.build_payload(request)
        else:
            payload = {
                "action": request.action,
                "data": request.data
            }
        
        headers = {}
        if hasattr(agent, 'api_key'):
            headers['Authorization'] = f"Bearer {agent.api_key}"
        if hasattr(agent, 'headers'):
            headers.update(agent.headers)
        
        async with self.session.post(
            agent.api_url,
            json=payload,
            headers=headers,
            timeout=request.timeout
        ) as response:
            if response.status >= 400:
                raise MCPError(f"API error {response.status}: {await response.text()}")
            
            return await response.json()
    
    async def broadcast_event(self, sender_id: str, event: str, data: Dict[str, Any] = None):
        event_msg = Event(
            sender=sender_id,
            event=event,
            data=data or {}
        )
        
        handlers = self.event_handlers.get(event, [])
        for handler in handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(event_msg)
                else:
                    handler(event_msg)
            except Exception:
                continue
    
    def get_stats(self) -> Dict[str, Any]:
        return {
            "agents": len(self.agents),
            "running": self.running,
            "messages_sent": self.messages_sent,
            "messages_received": self.messages_received,
            "circuit_breakers": {
                agent_id: {
                    "state": cb.state.value,
                    "failure_count": cb.failure_count
                }
                for agent_id, cb in self.circuit_breakers.items()
            },
            "rate_limits": {
                agent_id: {
                    "tokens": rl.tokens,
                    "limit": rl.requests_per_minute
                }
                for agent_id, rl in self.rate_limiters.items()
            }
        }

# Instancia global
protocol = MCPProtocol()