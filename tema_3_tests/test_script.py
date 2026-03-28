import requests
import httpx
import sys
import pytest

sys.stdout.reconfigure(encoding="utf-8")

BASE_URL = "http://localhost:8000"


def test_root():
    """Test that the root endpoint is reachable and returns expected message."""
    r = requests.get(f"{BASE_URL}/", timeout=5)
    assert r.status_code == 200
    data = r.json()
    assert "message" in data


def test_chat_relevant_security_policy():
    """Test that a PAN-OS security policy question returns a relevant response."""
    payload = {"message": "How do I configure a security policy rule on PAN-OS?"}
    r = requests.post(f"{BASE_URL}/chat/", json=payload, timeout=45)
    assert r.status_code == 200
    body = r.json()
    assert "response" in body
    response_text = body["response"].lower()
    assert any(kw in response_text for kw in ["security", "policy", "zone", "pan-os", "rule"])


def test_chat_globalprotect():
    """Test that a GlobalProtect VPN question returns a relevant response."""
    payload = {"message": "What are the steps to configure a GlobalProtect Gateway?"}
    r = requests.post(f"{BASE_URL}/chat/", json=payload, timeout=45)
    assert r.status_code == 200
    body = r.json()
    assert "response" in body
    response_text = body["response"].lower()
    assert any(kw in response_text for kw in ["globalprotect", "gateway", "vpn", "tunnel", "portal"])


def test_chat_cortex_xdr():
    """Test that a Cortex XDR question returns a relevant response."""
    payload = {"message": "How do I investigate a malware alert in Cortex XDR?"}
    r = requests.post(f"{BASE_URL}/chat/", json=payload, timeout=45)
    assert r.status_code == 200
    body = r.json()
    assert "response" in body
    response_text = body["response"].lower()
    assert any(kw in response_text for kw in ["cortex", "xdr", "alert", "malware", "endpoint", "incident"])


def test_chat_irrelevant_question():
    """Test that an irrelevant question is rejected with a redirection message."""
    payload = {"message": "Give me a pasta recipe with tomato sauce."}
    r = requests.post(f"{BASE_URL}/chat/", json=payload, timeout=45)
    assert r.status_code == 200
    body = r.json()
    assert "response" in body
    response_text = body["response"].lower()
    assert any(kw in response_text for kw in [
        "palo alto", "pan-os", "ngfw", "globalprotect", "cortex xdr", "specialize"
    ])


def test_chat_empty_message():
    """Test that an empty message returns a prompt to ask a Palo Alto question."""
    payload = {"message": ""}
    r = requests.post(f"{BASE_URL}/chat/", json=payload, timeout=45)
    assert r.status_code == 200
    body = r.json()
    assert "response" in body
    response_text = body["response"].lower()
    assert any(kw in response_text for kw in ["palo alto", "pan-os", "globalprotect", "cortex"])


@pytest.mark.asyncio
async def test_chat_async_app_id():
    """Async test: App-ID question returns a relevant technical response."""
    payload = {"message": "What is App-ID and how does it work in PAN-OS?"}
    async with httpx.AsyncClient(timeout=45.0) as client:
        response = await client.post(f"{BASE_URL}/chat/", json=payload)
    assert response.status_code == 200
    body = response.json()
    assert "response" in body
    response_text = body["response"].lower()
    assert any(kw in response_text for kw in ["app-id", "application", "traffic", "classification", "policy"])


@pytest.mark.asyncio
async def test_chat_with_integer_invalid():
    """Test that sending an integer as message returns HTTP 422 Unprocessable Entity."""
    payload = {"message": 42}
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.post(f"{BASE_URL}/chat/", json=payload)
    assert response.status_code == 422