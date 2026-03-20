"""
Tests des endpoints Health
"""
import pytest
from fastapi.testclient import TestClient


class TestHealthEndpoints:
    """Tests pour les routes /health/*"""

    def test_root_returns_200(self, client: TestClient):
        """GET / doit retourner 200 avec les infos de l'API"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data
        assert "docs" in data

    def test_health_basic(self, client: TestClient):
        """GET /health/ doit retourner 200"""
        response = client.get("/health/")
        assert response.status_code == 200
        data = response.json()
        assert data.get("status") in ("ok", "healthy", "up")

    def test_health_live(self, client: TestClient):
        """GET /health/live doit retourner 200 (liveness probe Kubernetes)"""
        response = client.get("/health/live")
        assert response.status_code == 200

    def test_health_ready(self, client: TestClient):
        """GET /health/ready — l'API est prête (readiness probe)"""
        response = client.get("/health/ready")
        # Peut retourner 200 ou 503 si les services externes sont absents
        assert response.status_code in (200, 503)
