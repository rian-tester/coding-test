import pytest
from fastapi.testclient import TestClient
from main import app
from unittest.mock import MagicMock

client = TestClient(app)

def test_get_sales_reps():
    response = client.get("/api/sales-reps")
    assert response.status_code == 200
    assert "salesReps" in response.json()

def test_ai_endpoint_with_valid_question():
    response = client.post("/api/ai", json={"question": "Who are the sales reps?"})
    assert response.status_code == 200
    assert "answer" in response.json()

def test_ai_endpoint_with_empty_question():
    response = client.post("/api/ai", json={"question": ""})
    assert response.status_code == 400  # Expecting 400 Bad Request
    assert response.json() == {"detail": "The 'question' field cannot be empty."}

def test_ai_endpoint_with_missing_question():
    response = client.post("/api/ai", json={})
    assert response.status_code == 422  # FastAPI will return a validation error

def test_ai_endpoint_with_invalid_api_key(monkeypatch):
    # Mock the OpenAI client to raise an error
    mock_openai_client = MagicMock()
    mock_openai_client.chat.completions.create.side_effect = Exception("Invalid API key")
    monkeypatch.setattr("main.openai_client", mock_openai_client)

    # Make the request
    response = client.post("/api/ai", json={"question": "Who are the sales reps?"})

    # Assert the response
    assert response.status_code == 500  # Expecting 500 Internal Server Error
    assert response.json()["detail"] == "Failed to process the AI request. Please try again later."