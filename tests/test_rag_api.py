"""Tests for Pinecone + Groq Agricultural RAG Chatbot API endpoints."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from api.main import app

client = TestClient(app)


def test_rag_query_endpoint_schema_validation() -> None:
    """Verify that requests with invalid schemas or too-short questions are rejected."""
    # Too short question
    res = client.post("/rag/query", json={"question": "a"})
    assert res.status_code == 422

    # Missing question
    res2 = client.post("/rag/query", json={"crop": "banana"})
    assert res2.status_code == 422


def test_rag_query_endpoint_response_structure() -> None:
    """Verify that /rag/query and /chat return structured responses with required fields."""
    payload = {
        "question": "When and why should gypsum be applied to groundnut?",
        "crop": "groundnut",
        "top_k": 3,
        "language": "en",
    }
    # Test /rag/query
    res = client.post("/rag/query", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert "question" in data
    assert "answer" in data
    assert "grounded" in data
    assert "sources" in data
    assert "confidence" in data
    assert "disclaimer" in data
    assert isinstance(data["sources"], list)
    assert len(data["sources"]) > 0

    # Test /chat alias
    res_chat = client.post("/chat", json=payload)
    assert res_chat.status_code == 200
    data_chat = res_chat.json()
    assert "answer" in data_chat
    assert len(data_chat["answer"]) > 10
