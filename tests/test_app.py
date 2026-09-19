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