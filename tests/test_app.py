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
    
def test_execute_ai_tool_allows_read_blob(monkeypatch):
    def fake_read_blob_tool(blob_name):
        assert blob_name == "hello.txt"
        return "Mock blob content"

    monkeypatch.setattr(app, "read_blob_tool", fake_read_blob_tool)

    result = app.execute_ai_tool(
        "read_blob",
        {"blob_name": "hello.txt"}
    )

    assert result == "Mock blob content"
    
def test_execute_ai_tool_denies_unknown_tool():
    result = app.execute_ai_tool(
        "delete_all_blobs",
        {}
    )

    assert result == "DENIED: tool 'delete_all_blobs' is not permitted."

def test_ai_endpoint_tool_call(monkeypatch):
    class FakeUsage:
        input_tokens = 10
        output_tokens = 5
        total_tokens = 15

    class FakeFunctionCall:
        type = "function_call"
        name = "read_blob"
        arguments = '{"blob_name":"hello.txt"}'
        call_id = "call-test-123"

    class FakeFirstResponse:
        id = "response-1"
        output = [FakeFunctionCall()]
        usage = FakeUsage()

    class FakeFinalResponse:
        output_text = "The file contains: Mock blob content"
        usage = FakeUsage()

    class FakeResponses:
        def __init__(self):
            self.call_count = 0

        def create(self, **kwargs):
            self.call_count += 1

            if self.call_count == 1:
                assert kwargs["model"] == app.AI_DEPLOYMENT
                assert kwargs["input"] == (
                    "Read hello.txt and tell me exactly what it contains."
                )
                assert kwargs["tools"] == app.AI_TOOLS
                return FakeFirstResponse()

            assert kwargs["model"] == app.AI_DEPLOYMENT
            assert kwargs["previous_response_id"] == "response-1"

            tool_outputs = kwargs["input"]

            assert len(tool_outputs) == 1
            assert tool_outputs[0]["type"] == "function_call_output"
            assert tool_outputs[0]["call_id"] == "call-test-123"
            assert tool_outputs[0]["output"] == "Mock blob content"

            return FakeFinalResponse()

    class FakeAIClient:
        def __init__(self):
            self.responses = FakeResponses()

    monkeypatch.setattr(
        app,
        "get_ai_client",
        lambda: FakeAIClient()
    )

    monkeypatch.setattr(
        app,
        "read_blob_tool",
        lambda blob_name: "Mock blob content"
    )

    response = client.post(
        "/ai",
        json={
            "message": "Read hello.txt and tell me exactly what it contains."
        }
    )

    assert response.status_code == 200

    body = response.json()
    print(body)

    assert body["answer"] == "The file contains: Mock blob content"
    assert body["usage"]["input_tokens"] == 10
    assert body["usage"]["output_tokens"] == 5
    assert body["usage"]["total_tokens"] == 15
