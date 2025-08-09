
import pytest
from services.conversation_memory import conversation_memory

@pytest.mark.asyncio
async def test_conversation_memory():
    session_id = "test-session-123"

    has_history = await conversation_memory.has_session(session_id)
    assert has_history is False

    await conversation_memory.add_exchange(
        session_id,
        "Hello, tell me about Alice",
        "Alice is a sales representative known for excellent customer service."
    )

    has_history = await conversation_memory.has_session(session_id)
    context = await conversation_memory.get_conversation_context(session_id)
    assert has_history is True
    assert isinstance(context, str)

    await conversation_memory.add_exchange(
        session_id,
        "What about Charlie?",
        "Charlie is also a sales representative with strong negotiation skills."
    )

    context = await conversation_memory.get_conversation_context(session_id)
    assert "Charlie" in context

    await conversation_memory.clear_session(session_id)
    has_history = await conversation_memory.has_session(session_id)
    assert has_history is False
