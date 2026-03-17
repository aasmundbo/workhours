"""Tests for authentication routes."""

import os
import sys

import pytest
from werkzeug.security import generate_password_hash

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import storage
from app import create_app

_TEST_PASSWORD = "hunter2"
_TEST_HASH = generate_password_hash(_TEST_PASSWORD)


@pytest.fixture
def auth_client(tmp_path, monkeypatch):
    """Test client with auth enforced (TESTING flag NOT set)."""
    data_file = str(tmp_path / "hours.json")
    monkeypatch.setattr(storage, "DEFAULT_PATH", data_file)
    monkeypatch.setenv("SECRET_KEY", "test-secret-key-for-auth-tests")
    monkeypatch.setenv("APP_PASSWORD_HASH", _TEST_HASH)
    app = create_app()
    with app.test_client() as c:
        yield c


class TestAuthRoutes:
    def test_status_unauthenticated(self, auth_client):
        resp = auth_client.get("/api/auth/status")
        assert resp.status_code == 200
        assert resp.get_json() == {"authenticated": False}

    def test_login_correct_password(self, auth_client):
        resp = auth_client.post("/api/auth/login", json={"password": _TEST_PASSWORD})
        assert resp.status_code == 200
        assert resp.get_json() == {"authenticated": True}

    def test_login_wrong_password(self, auth_client):
        resp = auth_client.post("/api/auth/login", json={"password": "wrongpass"})
        assert resp.status_code == 401
        assert "error" in resp.get_json()

    def test_login_missing_body(self, auth_client):
        resp = auth_client.post("/api/auth/login")
        assert resp.status_code == 401

    def test_status_after_login(self, auth_client):
        auth_client.post("/api/auth/login", json={"password": _TEST_PASSWORD})
        resp = auth_client.get("/api/auth/status")
        assert resp.get_json() == {"authenticated": True}

    def test_logout_clears_session(self, auth_client):
        auth_client.post("/api/auth/login", json={"password": _TEST_PASSWORD})
        auth_client.post("/api/auth/logout")
        resp = auth_client.get("/api/auth/status")
        assert resp.get_json() == {"authenticated": False}

    def test_protected_route_without_auth(self, auth_client):
        resp = auth_client.get("/api/entries")
        assert resp.status_code == 401

    def test_protected_route_with_auth(self, auth_client):
        auth_client.post("/api/auth/login", json={"password": _TEST_PASSWORD})
        resp = auth_client.get("/api/entries")
        assert resp.status_code == 200

    def test_unconfigured_server(self, tmp_path, monkeypatch):
        """Login fails with 500 when APP_PASSWORD_HASH is not set."""
        data_file = str(tmp_path / "hours.json")
        monkeypatch.setattr(storage, "DEFAULT_PATH", data_file)
        monkeypatch.setenv("SECRET_KEY", "test-secret-key")
        monkeypatch.delenv("APP_PASSWORD_HASH", raising=False)
        app = create_app()
        with app.test_client() as c:
            resp = c.post("/api/auth/login", json={"password": "anything"})
            assert resp.status_code == 500


class TestDisableAuth:
    @pytest.fixture
    def no_auth_client(self, tmp_path, monkeypatch):
        """Test client with DISABLE_AUTH=true."""
        data_file = str(tmp_path / "hours.json")
        monkeypatch.setattr(storage, "DEFAULT_PATH", data_file)
        monkeypatch.setenv("DISABLE_AUTH", "true")
        monkeypatch.delenv("SECRET_KEY", raising=False)
        app = create_app()
        with app.test_client() as c:
            yield c

    def test_status_returns_authenticated_when_disabled(self, no_auth_client):
        resp = no_auth_client.get("/api/auth/status")
        assert resp.status_code == 200
        assert resp.get_json() == {"authenticated": True}

    def test_protected_route_accessible_without_login(self, no_auth_client):
        resp = no_auth_client.get("/api/entries")
        assert resp.status_code == 200
