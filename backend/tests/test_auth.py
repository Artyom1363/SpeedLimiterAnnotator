# Path: backend/tests/test_auth.py
import pytest
from httpx import AsyncClient
from datetime import datetime
from app.models import User

class TestAuth:
    async def test_register(self, client: AsyncClient):
        response = await client.post(
            "/api/auth/register",
            json={
                "email": "new@example.com",
                "username": "newuser",
                "password": "password123"
            }
        )
        assert response.status_code == 201
        data = response.json()
        assert data["message"] == "User registered successfully"
        assert "user_id" in data

    async def test_login(self, client: AsyncClient, test_user):
        response = await client.post(
            "/api/auth/login",
            json={
                "email": "test@example.com",
                "password": "password123"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data