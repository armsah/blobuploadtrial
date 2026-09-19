from fastapi.testclient import TestClient

import app

client = TestClient(app.app)

def test_account_url():
    assert app.ACCOUNT_URL == "https://starmenlearning2026.blob.core.windows.net"


def test_container_name():
    assert app.CONTAINER_NAME == "documents"


def test_blob_name():
    assert app.BLOB_NAME == "hello.txt"
    
def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {
        "status": "healthy"
    }
    
def test_root_endpoint():
    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == {
        "message": "Azure Blob Storage Demo API"
    }   
    
def test_blob_endpoint(monkeypatch):
    class FakeDownloadStream:
        def readall(self):
            return b"Test blob content"

    class FakeBlobClient:
        def download_blob(self):
            return FakeDownloadStream()

    class FakeContainerClient:
        def get_blob_client(self, blob_name):
            assert blob_name == "hello.txt"
            return FakeBlobClient()

    class FakeBlobServiceClient:
        def get_container_client(self, container_name):
            assert container_name == "documents"
            return FakeContainerClient()

    monkeypatch.setattr(
        app,
        "get_blob_service_client",
        lambda: FakeBlobServiceClient()
    )

    response = client.get("/blob")

    assert response.status_code == 200
    assert response.json() == {
        "container": "documents",
        "blob": "hello.txt",
        "content": "Test blob content"
    }
    
def test_ci_failure_demo():
    assert False, "Intentional CI failure demonstration"