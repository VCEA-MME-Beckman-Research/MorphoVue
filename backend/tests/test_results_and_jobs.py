import os
import pytest
from fastapi.testclient import TestClient

os.environ.setdefault("FIREBASE_DISABLE_INIT", "1")
from app.main import app


@pytest.fixture(autouse=True)
def mock_fb(monkeypatch):
    store = {
        "scans": {},
        "segmentations": {},
        "quantification_results": {},
        "kamiak_jobs": {},
    }

    import uuid

    class DocRef:
        def __init__(self, col, id):
            self.col = col
            self.id = id
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
            data = store[self.col].get(self.id)
            return Snap(data is not None, data)
        def set(self, data):
            store[self.col][self.id] = data
        def update(self, data):
            store[self.col][self.id].update(data)
    class ColRef:
        def __init__(self, name):
            self.name = name
        def document(self, id):
            return DocRef(self.name, id)
        def where(self, *args, **kwargs):
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
    class DB:
        def collection(self, name):
            return ColRef(name)
    class Blob:
        def __init__(self, path):
            self.path = path
        def upload_from_string(self, *args, **kwargs):
            return None
        def generate_signed_url(self, **kwargs):
            return f"https://signed.example/{self.path}"
    class Bucket:
        def blob(self, path):
            return Blob(path)
    class Client:
        @property
        def db(self):
            return DB()
        @property
        def bucket(self):
            return Bucket()
        def verify_token(self, token):
            return {"uid": "u1"} if token == "valid" else None

    import app.firebase_client as fc
    monkeypatch.setattr(fc, "firebase_client", Client())


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def auth_headers():
    return {"Authorization": "Bearer valid"}


def test_upload_results_and_fetch(client, auth_headers):
    # Create dummy scan doc that endpoints expect
    import uuid
    scan_id = str(uuid.uuid4())
    # Insert via Firestore mock directly through endpoint not necessary here

    payload = {
        "scan_id": scan_id,
        "segmentation_url": "segmentations/scan/mask.nrrd",
        "volume_url": "segmentations/scan/volume.nrrd",
        "model_version": "v1",
        "metrics": {"dice": 0.9},
        "quantification": [
            {"organ_name": "organ1", "volume": 1.0, "surface_area": 2.0, "centroid": [1,2,3]}
        ]
    }
    r = client.post("/api/results/upload", headers=auth_headers, json=payload)
    assert r.status_code == 200
    seg_id = r.json()["segmentation_id"]

    r = client.get(f"/api/scans/{scan_id}/segmentations", headers=auth_headers)
    assert r.status_code == 200
    segs = r.json()
    assert len(segs) == 1
    assert segs[0]["volume_url"] == "segmentations/scan/volume.nrrd"

    r = client.get(f"/api/segmentations/{seg_id}", headers=auth_headers)
    assert r.status_code == 200

    r = client.get(f"/api/quantification/{seg_id}", headers=auth_headers)
    assert r.status_code == 200
    assert len(r.json()) == 1

    r = client.get(f"/api/segmentations/{seg_id}/download-url", headers=auth_headers, params={"file_type": "mask"})
    assert r.status_code == 200
    assert r.json()["download_url"].startswith("https://signed.example/")

    r = client.get(f"/api/segmentations/{seg_id}/download-url", headers=auth_headers, params={"file_type": "volume"})
    assert r.status_code == 200
