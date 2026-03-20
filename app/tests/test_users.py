"""
Tests des endpoints Utilisateurs
"""
import pytest
from fastapi.testclient import TestClient


class TestUserEndpoints:
    """Tests pour les routes /api/v1/users/*"""

    def test_create_user_success(self, client: TestClient):
        """POST /api/v1/users/ doit créer un utilisateur et retourner 201"""
        payload = {
            "name": "Alice Dupont",
            "email": "alice@example.com",
            "institution": "CNRS",
            "role": "researcher",
        }
        response = client.post("/api/v1/users/", json=payload)
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == payload["email"]
        assert data["name"] == payload["name"]
        assert "id" in data

    def test_create_user_duplicate_email(self, client: TestClient):
        """POST avec un email déjà existant doit retourner 409 Conflict"""
        payload = {
            "name": "Alice Dupont",
            "email": "duplicate@example.com",
            "institution": "CNRS",
        }
        client.post("/api/v1/users/", json=payload)  # Premier appel — OK
        response = client.post("/api/v1/users/", json=payload)  # Doublon
        assert response.status_code == 409

    def test_create_user_missing_email(self, client: TestClient):
        """POST sans email doit retourner 422 Unprocessable Entity"""
        payload = {"name": "Bob Martin"}
        response = client.post("/api/v1/users/", json=payload)
        assert response.status_code == 422

    def test_get_user_not_found(self, client: TestClient):
        """GET d'un UUID inexistant doit retourner 404"""
        fake_uuid = "00000000-0000-0000-0000-000000000001"
        response = client.get(f"/api/v1/users/{fake_uuid}")
        assert response.status_code == 404
