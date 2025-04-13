import pytest
from fastapi.testclient import TestClient
from main import app

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
    assert response.status_code == 200
    assert response.json() == {"error": "Question is required"}