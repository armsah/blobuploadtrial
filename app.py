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