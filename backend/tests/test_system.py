
import pytest
import os
from services.ai_router import AIRouter
from services.data_service import DataService
from dotenv import load_dotenv

load_dotenv()

@pytest.mark.asyncio
async def test_new_system():
    openai_key = os.getenv("OPENAI_API_KEY")
    assert openai_key, "❌ OPENAI_API_KEY not found"

    data_service = DataService()
    sales_data = data_service.get_sales_data()
    assert "salesReps" in sales_data

    router = AIRouter(openai_key, sales_data)

    test_questions = [
        "hello",
        "who is Alice?",
        "what is machine learning?",
        "tell me about sales performance"
    ]

    for question in test_questions:
        decision = await router.route_question(question, "test_session")
        assert hasattr(decision, "route_type")
        assert hasattr(decision, "confidence")
