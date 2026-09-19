import os

from fastapi import FastAPI
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient


ACCOUNT_NAME = os.getenv("AZURE_STORAGE_ACCOUNT_NAME", "starmenlearning2026")
ACCOUNT_URL = f"https://{ACCOUNT_NAME}.blob.core.windows.net"
CONTAINER_NAME = os.getenv("AZURE_STORAGE_CONTAINER_NAME", "documents")
BLOB_NAME = os.getenv("AZURE_STORAGE_BLOB_NAME", "hello.txt")

app = FastAPI(
    title="Azure Blob Storage Demo",
    version="1.0.0",
)

@app.get("/")
def root():
    return {
        "message": "Azure Blob Storage Demo API"
    }
    
@app.get("/health")
def health():
    return {
        "status": "healthy"
    }
    
def get_blob_service_client():
    credential = DefaultAzureCredential()

    return BlobServiceClient(
        account_url=ACCOUNT_URL,
        credential=credential
    )
    
@app.get("/blob")
def get_blob():
    blob_service_client = get_blob_service_client()

    container_client = blob_service_client.get_container_client(
        CONTAINER_NAME
    )

    blob_client = container_client.get_blob_client(
        BLOB_NAME
    )

    download_stream = blob_client.download_blob()
    content = download_stream.readall()

    return {
        "container": CONTAINER_NAME,
        "blob": BLOB_NAME,
        "content": content.decode("utf-8")
    }