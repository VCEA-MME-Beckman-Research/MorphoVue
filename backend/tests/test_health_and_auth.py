import os
import pytest
from fastapi.testclient import TestClient

# Disable Firebase initialization in tests
os.environ.setdefault("FIREBASE_DISABLE_INIT", "1")

# Import after env var set
from app.main import app


@pytest.fixture(autouse=True)
def mock_auth(monkeypatch):
    class DummyFirebaseClient:
        def verify_token(self, token):
            if token == "valid":
                return {"uid": "test-user"}
            return None
        @property
        def db(self):
            class DummyDB:
                def collection(self, name):
                    class DummyCol:
                        def document(self, _id):
                            class DummyDoc:
                                def get(self):
                                    class DummySnap:
                                        @property
                                        def exists(self):
                                            return True
                                    return DummySnap()
                        def where(self, *args, **kwargs):
                            return self
                        def order_by(self, *args, **kwargs):
                            return self
                        def stream(self):
                            return []
                    return DummyCol()
            return DummyDB()
        @property
        def bucket(self):
            class DummyBucket:
                def blob(self, path):
                    class DummyBlob:
                        def upload_from_string(self, *args, **kwargs):
                            return None
                        def generate_signed_url(self, **kwargs):
                            return f"https://signed.example/{path}"
                    return DummyBlob()
            return DummyBucket()

    import app.firebase_client as fc_module
    monkeypatch.setattr(fc_module, "firebase_client", DummyFirebaseClient())


@pytest.fixture
def client():
    return TestClient(app)


def test_root_health(client):
    resp = client.get("/")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "healthy"


def test_api_health(client):
    resp = client.get("/api/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "healthy"


def test_auth_required(client):
    resp = client.get("/api/projects")
    assert resp.status_code == 401


def test_auth_valid_token(client):
    headers = {"Authorization": "Bearer valid"}
    # projects list will hit mocked firestore and return empty
    resp = client.get("/api/projects", headers=headers)
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)
