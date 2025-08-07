import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.conversation_memory import conversation_memory

async def test_conversation_memory():
    print("Testing Conversation Memory Service...")
    
    session_id = "test-session-123"
    
    print(f"\n1. Testing initial session state:")
    has_history = await conversation_memory.has_session(session_id)
    print(f"   Has history: {has_history}")
    
    print(f"\n2. Adding first exchange:")
    await conversation_memory.add_exchange(
        session_id, 
        "Hello, tell me about Alice", 
        "Alice is a sales representative known for excellent customer service."
    )
    
    has_history = await conversation_memory.has_session(session_id)
    context = await conversation_memory.get_conversation_context(session_id)
    print(f"   Has history: {has_history}")
    print(f"   Context: {context}")
    
    print(f"\n3. Adding second exchange:")
    await conversation_memory.add_exchange(
        session_id,
        "What about Charlie?",
        "Charlie is also a sales representative with strong negotiation skills."
    )
    
    context = await conversation_memory.get_conversation_context(session_id)
    print(f"   Updated context:\n{context}")
    
    print(f"\n4. Testing session cleanup:")
    await conversation_memory.clear_session(session_id)
    has_history = await conversation_memory.has_session(session_id)
    print(f"   Has history after clear: {has_history}")
    
    print(f"\n✅ Conversation memory test completed successfully!")

if __name__ == "__main__":
    asyncio.run(test_conversation_memory())
