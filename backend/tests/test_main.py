import pytest
from fastapi.testclient import TestClient
from main import app
from unittest.mock import MagicMock
import openai
import os
import logging
import requests

client = TestClient(app)

def test_get_sales_reps():
    response = client.get("/api/sales-reps")
    assert response.status_code == 200
    assert "salesReps" in response.json()

def test_sales_reps_response_structure():
    response = client.get("/api/sales-reps")
    assert response.status_code == 200
    data = response.json()
    assert "salesReps" in data
    for rep in data["salesReps"]:
        assert "name" in rep
        assert "role" in rep
        assert "region" in rep

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


def test_env_file_exists():
    # Check if the .env file exists in the backend folder
    env_path = os.path.join(os.path.dirname(__file__), "../.env")
    assert os.path.isfile(env_path), f".env file not found at {env_path}"

def test_ai_endpoint_with_malformed_json():
    response = client.post("/api/ai", content="not a json")  # Use 'content' instead of 'data'
    assert response.status_code == 422  # FastAPI validation error

def test_ai_endpoint_with_invalid_question_type():
    response = client.post("/api/ai", json={"question": 12345})
    assert response.status_code == 422  # FastAPI validation error

def test_ai_response_structure():
    response = client.post("/api/ai", json={"question": "Who are the sales reps?"})
    assert response.status_code == 200
    data = response.json()
    assert "answer" in data
    assert isinstance(data["answer"], str)
