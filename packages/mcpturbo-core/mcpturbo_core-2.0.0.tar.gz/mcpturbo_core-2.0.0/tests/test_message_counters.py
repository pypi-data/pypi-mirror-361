import pytest
from mcpturbo_core.protocol import MCPProtocol
from mcpturbo_agents.base_agent import LocalAgent, AgentConfig, AgentType
from unittest.mock import AsyncMock


@pytest.fixture
async def protocol():
    protocol = MCPProtocol()
    await protocol.start()
    yield protocol
    await protocol.stop()


@pytest.fixture
def mock_agent():
    config = AgentConfig(
        agent_id="test_agent",
        name="Test Agent",
        agent_type=AgentType.LOCAL,
    )
    agent = LocalAgent("test_agent", "Test Agent")
    agent.handle_request = AsyncMock(return_value={"ok": True})
    return agent


@pytest.mark.asyncio
async def test_message_counters(protocol, mock_agent):
    protocol.register_agent(mock_agent.config.agent_id, mock_agent)
    assert protocol.messages_sent == 0
    assert protocol.messages_received == 0

    response = await protocol.send_request(
        sender_id="tester",
        target_id="test_agent",
        action="do",
    )

    assert response.success
    assert protocol.messages_sent == 1
    assert protocol.messages_received == 1
