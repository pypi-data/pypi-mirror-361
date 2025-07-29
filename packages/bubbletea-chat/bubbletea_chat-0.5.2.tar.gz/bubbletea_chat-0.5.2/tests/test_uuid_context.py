"""
Test UUID context functionality in BubbleTea
"""
import pytest
import bubbletea_chat as bt
from bubbletea_chat.schemas import ComponentChatRequest


def test_chatbot_with_uuid_parameters():
    """Test that chatbot can accept UUID parameters"""
    received_user_uuid = None
    received_conversation_uuid = None
    
    @bt.chatbot
    def test_bot(message: str, user_uuid: str = None, conversation_uuid: str = None):
        nonlocal received_user_uuid, received_conversation_uuid
        received_user_uuid = user_uuid
        received_conversation_uuid = conversation_uuid
        yield bt.Text(f"Message: {message}")
        if user_uuid:
            yield bt.Text(f"User UUID: {user_uuid}")
        if conversation_uuid:
            yield bt.Text(f"Conversation UUID: {conversation_uuid}")
    
    # Create a request with UUIDs
    request = ComponentChatRequest(
        type="user",
        message="Hello",
        user_uuid="550e8400-e29b-41d4-a716-446655440000",
        conversation_uuid="6ba7b810-9dad-11d1-80b4-00c04fd430c8"
    )
    
    # Test async execution
    import asyncio
    
    async def run_test():
        response = await test_bot.handle_request(request)
        assert hasattr(response, 'responses')
        assert len(response.responses) == 3
        assert response.responses[0].content == "Message: Hello"
        assert response.responses[1].content == "User UUID: 550e8400-e29b-41d4-a716-446655440000"
        assert response.responses[2].content == "Conversation UUID: 6ba7b810-9dad-11d1-80b4-00c04fd430c8"
    
    asyncio.run(run_test())
    
    # Verify the UUIDs were received
    assert received_user_uuid == "550e8400-e29b-41d4-a716-446655440000"
    assert received_conversation_uuid == "6ba7b810-9dad-11d1-80b4-00c04fd430c8"


def test_chatbot_without_uuid_parameters():
    """Test backward compatibility - chatbot without UUID parameters"""
    @bt.chatbot
    def simple_bot(message: str):
        yield bt.Text(f"You said: {message}")
    
    request = ComponentChatRequest(
        type="user",
        message="Hello",
        user_uuid="550e8400-e29b-41d4-a716-446655440000",
        conversation_uuid="6ba7b810-9dad-11d1-80b4-00c04fd430c8"
    )
    
    # Test that it still works without errors
    import asyncio
    
    async def run_test():
        response = await simple_bot.handle_request(request)
        assert hasattr(response, 'responses')
        assert len(response.responses) == 1
        assert response.responses[0].content == "You said: Hello"
    
    asyncio.run(run_test())


def test_chatbot_with_partial_parameters():
    """Test chatbot that only accepts user_uuid but not conversation_uuid"""
    received_user_uuid = None
    
    @bt.chatbot
    def partial_bot(message: str, user_uuid: str = None):
        nonlocal received_user_uuid
        received_user_uuid = user_uuid
        yield bt.Text(f"Hello {user_uuid[:8] if user_uuid else 'anonymous'}!")
    
    request = ComponentChatRequest(
        type="user",
        message="Hi",
        user_uuid="550e8400-e29b-41d4-a716-446655440000",
        conversation_uuid="6ba7b810-9dad-11d1-80b4-00c04fd430c8"
    )
    
    import asyncio
    
    async def run_test():
        response = await partial_bot.handle_request(request)
        assert hasattr(response, 'responses')
        assert len(response.responses) == 1
        assert response.responses[0].content == "Hello 550e8400!"
    
    asyncio.run(run_test())
    
    assert received_user_uuid == "550e8400-e29b-41d4-a716-446655440000"


if __name__ == "__main__":
    test_chatbot_with_uuid_parameters()
    print("✓ Test with UUID parameters passed")
    
    test_chatbot_without_uuid_parameters()
    print("✓ Test without UUID parameters (backward compatibility) passed")
    
    test_chatbot_with_partial_parameters()
    print("✓ Test with partial parameters passed")
    
    print("\nAll tests passed! 🎉")