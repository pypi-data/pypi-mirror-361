"""
Tests for MCPturbo v2 Protocol
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
import aiohttp
from aiohttp import web

from mcpturbo_core.protocol import MCPProtocol, CircuitBreaker, RateLimiter
from mcpturbo_core.messages import Request, Response, create_request
from mcpturbo_core.exceptions import MCPError, TimeoutError, CircuitBreakerError, RateLimitError
from mcpturbo_agents.base_agent import LocalAgent, ExternalAgent, AgentConfig, AgentType

pytestmark = pytest.mark.asyncio


class TestMCPProtocol:
    """Test cases for MCP Protocol v2"""
    
    @pytest.fixture
    async def protocol(self):
        """Create a test protocol instance"""
        protocol = MCPProtocol()
        await protocol.start()
        yield protocol
        await protocol.stop()
    
    @pytest.fixture
    def mock_agent(self):
        """Create a mock local agent"""
        config = AgentConfig(
            agent_id="test_agent",
            name="Test Agent", 
            agent_type=AgentType.LOCAL
        )
        agent = LocalAgent("test_agent", "Test Agent")
        
        # Mock handle_request
        agent.handle_request = AsyncMock(return_value={"result": "test_response"})
        
        return agent
    
    @pytest.fixture 
    def mock_external_agent(self):
        """Create a mock external agent"""
        agent = ExternalAgent(
            agent_id="external_agent",
            name="External Agent",
            api_url="https://api.example.com/chat",
            api_key="test_key"
        )
        return agent
    
    async def test_protocol_initialization(self, protocol):
        """Test protocol initialization"""
        assert protocol.running
        assert isinstance(protocol.agents, dict)
        assert isinstance(protocol.circuit_breakers, dict)
        assert isinstance(protocol.rate_limiters, dict)
    
    async def test_agent_registration(self, protocol, mock_agent):
        """Test agent registration"""
        protocol.register_agent(mock_agent.config.agent_id, mock_agent)
        
        assert mock_agent.config.agent_id in protocol.agents
        assert mock_agent.config.agent_id in protocol.circuit_breakers
        assert mock_agent.config.agent_id in protocol.rate_limiters
    
    async def test_local_request_success(self, protocol, mock_agent):
        """Test successful request to local agent"""
        protocol.register_agent(mock_agent.config.agent_id, mock_agent)
        
        response = await protocol.send_request(
            sender_id="test_sender",
            target_id="test_agent",
            action="test_action",
            data={"key": "value"}
        )
        
        assert response.success
        assert response.result == {"result": "test_response"}
        mock_agent.handle_request.assert_called_once()
    
    async def test_local_request_failure(self, protocol, mock_agent):
        """Test failed request to local agent"""
        mock_agent.handle_request = AsyncMock(side_effect=Exception("Test error"))
        protocol.register_agent(mock_agent.config.agent_id, mock_agent)
        
        response = await protocol.send_request(
            sender_id="test_sender",
            target_id="test_agent", 
            action="test_action"
        )
        
        assert not response.success
        assert "Test error" in response.error
    
    async def test_agent_not_found(self, protocol):
        """Test request to non-existent agent"""
        with pytest.raises(MCPError, match="Agent .* not found"):
            await protocol.send_request(
                sender_id="test_sender",
                target_id="nonexistent_agent",
                action="test_action"
            )
    
    async def test_circuit_breaker_functionality(self, protocol, mock_agent):
        """Test circuit breaker protection"""
        # Register agent with low failure threshold
        protocol.register_agent(mock_agent.config.agent_id, mock_agent, failure_threshold=2)
        
        # Make agent fail
        mock_agent.handle_request = AsyncMock(side_effect=Exception("Simulated failure"))
        
        # First failure
        response1 = await protocol.send_request("sender", "test_agent", "action")
        assert not response1.success
        
        # Second failure - should trip circuit breaker
        response2 = await protocol.send_request("sender", "test_agent", "action")
        assert not response2.success
        
        # Third request should be blocked by circuit breaker
        with pytest.raises(CircuitBreakerError):
            await protocol.send_request("sender", "test_agent", "action")
    
    async def test_rate_limiting(self, protocol, mock_agent):
        """Test rate limiting functionality"""
        # Register agent with very low rate limit
        protocol.register_agent(mock_agent.config.agent_id, mock_agent, rate_limit=1)
        
        # First request should succeed
        response1 = await protocol.send_request("sender", "test_agent", "action")
        assert response1.success
        
        # Second immediate request should hit rate limit
        with pytest.raises(RateLimitError):
            await protocol.send_request("sender", "test_agent", "action")
    
    async def test_timeout_handling(self, protocol, mock_agent):
        """Test request timeout"""
        # Make agent take too long
        async def slow_handler(request):
            await asyncio.sleep(2)
            return {"result": "slow_response"}
        
        mock_agent.handle_request = slow_handler
        protocol.register_agent(mock_agent.config.agent_id, mock_agent)
        
        with pytest.raises(MCPError):
            await protocol.send_request(
                sender_id="sender",
                target_id="test_agent", 
                action="action",
                timeout=1  # Very short timeout
            )
    
    async def test_retry_logic(self, protocol, mock_agent):
        """Test retry logic for failed requests"""
        call_count = 0
        
        async def failing_then_success(request):
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise Exception("Temporary failure")
            return {"result": "success_after_retry"}
        
        mock_agent.handle_request = failing_then_success
        protocol.register_agent(mock_agent.config.agent_id, mock_agent)
        
        # Should succeed after retries
        response = await protocol.send_request("sender", "test_agent", "action")
        assert response.success
        assert response.result == {"result": "success_after_retry"}
        assert call_count == 3
    
    @pytest.mark.asyncio
    async def test_external_api_request(self, protocol, mock_external_agent):
        """Test request to external API agent"""
        protocol.register_agent(mock_external_agent.config.agent_id, mock_external_agent)
        
        # Mock aiohttp response
        mock_response_data = {"choices": [{"message": {"content": "AI response"}}]}
        
        with patch('aiohttp.ClientSession.post') as mock_post:
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.json = AsyncMock(return_value=mock_response_data)
            mock_post.return_value.__aenter__.return_value = mock_response
            
            response = await protocol.send_request(
                sender_id="user",
                target_id="external_agent",
                action="generate",
                data={"prompt": "Hello"}
            )
            
            assert response.success
            assert response.result == mock_response_data
    
    async def test_external_api_error_handling(self, protocol, mock_external_agent):
        """Test external API error handling"""
        protocol.register_agent(mock_external_agent.config.agent_id, mock_external_agent)
        
        with patch('aiohttp.ClientSession.post') as mock_post:
            mock_response = AsyncMock()
            mock_response.status = 401
            mock_response.text = AsyncMock(return_value="Unauthorized")
            mock_post.return_value.__aenter__.return_value = mock_response
            
            response = await protocol.send_request(
                sender_id="user",
                target_id="external_agent", 
                action="generate"
            )
            
            assert not response.success
            assert "401" in response.error
    
    async def test_event_broadcasting(self, protocol):
        """Test event broadcasting functionality"""
        events_received = []
        
        def event_handler(event):
            events_received.append(event)
        
        protocol.subscribe("test_event", event_handler)
        
        await protocol.broadcast_event("sender", "test_event", {"data": "test"})
        
        # Allow event to be processed
        await asyncio.sleep(0.1)
        
        assert len(events_received) == 1
        assert events_received[0].event == "test_event"
        assert events_received[0].data == {"data": "test"}
    
    async def test_protocol_stats(self, protocol, mock_agent):
        """Test protocol statistics"""
        protocol.register_agent(mock_agent.config.agent_id, mock_agent)
        
        stats = protocol.get_stats()
        
        assert "agents" in stats
        assert "running" in stats
        assert "circuit_breakers" in stats
        assert "rate_limits" in stats
        assert stats["agents"] == 1
        assert stats["running"] is True


class TestCircuitBreaker:
    """Test cases for Circuit Breaker"""
    
    def test_circuit_breaker_states(self):
        """Test circuit breaker state transitions"""
        cb = CircuitBreaker(failure_threshold=3, recovery_timeout=60)
        
        # Should start closed
        assert cb.should_allow_request()
        
        # Record failures
        cb.record_failure()
        cb.record_failure()
        assert cb.should_allow_request()  # Still closed
        
        cb.record_failure()
        assert not cb.should_allow_request()  # Now open
        
        # Success should close it again
        cb.record_success()
        assert cb.should_allow_request()


class TestRateLimiter:
    """Test cases for Rate Limiter"""
    
    def test_rate_limiter_basic(self):
        """Test basic rate limiting"""
        limiter = RateLimiter(requests_per_minute=60)  # 1 per second
        
        # First request should succeed
        assert limiter.can_proceed()
        
        # Immediate second request should fail
        assert not limiter.can_proceed()
    
    def test_rate_limiter_refill(self):
        """Test token bucket refill"""
        import time
        
        limiter = RateLimiter(requests_per_minute=60)
        
        # Consume token
        assert limiter.can_proceed()
        assert not limiter.can_proceed()
        
        # Wait and manually advance time for testing
        limiter.last_refill = time.time() - 2  # Simulate 2 seconds passed
        
        # Should be able to proceed again
        assert limiter.can_proceed()


@pytest.mark.integration
class TestIntegration:
    """Integration tests for MCPturbo v2"""
    
    @pytest.mark.asyncio
    async def test_full_agent_workflow(self):
        """Test complete agent workflow"""
        from mcpturbo_core.protocol import protocol
        from mcpturbo_agents.base_agent import LocalAgent
        
        # Create test agent
        class TestAgent(LocalAgent):
            async def handle_request(self, request):
                action = getattr(request, 'action', '')
                data = getattr(request, 'data', {})
                
                if action == "echo":
                    return {"echo": data.get("message", "")}
                elif action == "compute":
                    a = data.get("a", 0)
                    b = data.get("b", 0)
                    return {"result": a + b}
                else:
                    return {"error": f"Unknown action: {action}"}
        
        # Setup
        await protocol.start()
        agent = TestAgent("test_compute", "Test Compute Agent")
        protocol.register_agent("test_compute", agent)
        
        try:
            # Test echo
            response = await protocol.send_request(
                sender_id="user",
                target_id="test_compute",
                action="echo",
                data={"message": "Hello World"}
            )
            
            assert response.success
            assert response.result["echo"] == "Hello World"
            
            # Test compute
            response = await protocol.send_request(
                sender_id="user", 
                target_id="test_compute",
                action="compute",
                data={"a": 10, "b": 5}
            )
            
            assert response.success
            assert response.result["result"] == 15
            
        finally:
            await protocol.stop()


if __name__ == "__main__":
    pytest.main([__file__])