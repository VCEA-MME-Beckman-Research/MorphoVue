import os
import json
import pytest
from fastapi.testclient import TestClient
from datetime import datetime

os.environ.setdefault("FIREBASE_DISABLE_INIT", "1")

from app.main import app


@pytest.fixture(autouse=True)
def mock_fb(monkeypatch):
    store = {"projects": {}, "scans": {}}

    class DummyDocRef:
        def __init__(self, col, doc_id):
            self.col = col
            self.doc_id = doc_id
        def get(self):
            class Snap:
                def __init__(self, exists, data):
                    self._exists = exists
                    self._data = data
                @property
                def exists(self):
                    return self._exists
                def to_dict(self):
                    return self._data
            data = store[self.col].get(self.doc_id)
            return Snap(data is not None, data)
        def set(self, data):
            store[self.col][self.doc_id] = data
        def update(self, data):
            store[self.col][self.doc_id].update(data)
    class DummyColRef:
        def __init__(self, name):
            self.name = name
        def document(self, doc_id):
            return DummyDocRef(self.name, doc_id)
        def where(self, field, op, value):
            return self
        def order_by(self, *args, **kwargs):
            return self
        def stream(self):
            class Snap:
                def __init__(self, d):
                    self._d = d
                def to_dict(self):
                    return self._d
            return [Snap(v) for v in store[self.name].values()]
    class DummyDB:
        def collection(self, name):
            return DummyColRef(name)
    class DummyBlob:
        def __init__(self, path):
            self.path = path
        def upload_from_string(self, *args, **kwargs):
            return None
        def generate_signed_url(self, **kwargs):
            return f"https://signed.example/{self.path}"
    class DummyBucket:
        def blob(self, path):
            return DummyBlob(path)
    class DummyClient:
        @property
        def db(self):
            return DummyDB()
        @property
        def bucket(self):
            return DummyBucket()
        def verify_token(self, token):
            return {"uid": "u1"} if token == "valid" else None

    import app.firebase_client as fc
    monkeypatch.setattr(fc, "firebase_client", DummyClient())


@pytest.fixture
def auth_headers():
    return {"Authorization": "Bearer valid"}


@pytest.fixture
def client():
    return TestClient(app)


def test_create_and_list_project(client, auth_headers):
    payload = {"name": "P1", "description": "desc"}
    r = client.post("/api/projects", headers=auth_headers, json=payload)
    assert r.status_code == 200
    proj = r.json()
    assert proj["name"] == "P1"

    r = client.get("/api/projects", headers=auth_headers)
    assert r.status_code == 200
    assert len(r.json()) == 1


def test_upload_scan_and_signed_url(client, auth_headers):
    # Create project id to use
    import uuid
    project_id = str(uuid.uuid4())
    # Insert a dummy project in store via endpoint
    client.post("/api/projects", headers=auth_headers, json={"name": "Test", "description": ""})

    # Upload a minimal TIFF (fake bytes accepted by our mocked storage)
    files = {
        'file': ('test.tiff', b'II*\x00dummy'),
    }
    data = {'project_id': project_id}
    r = client.post("/api/scans/upload", headers=auth_headers, files=files, data=data)
    assert r.status_code == 200
    scan = r.json()
    assert scan["project_id"] == project_id

    r = client.get(f"/api/scans/{scan['id']}/download-url", headers=auth_headers)
    assert r.status_code == 200
    assert r.json()["download_url"].startswith("https://signed.example/")
