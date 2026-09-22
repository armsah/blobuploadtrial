import os
import json

from pydantic import BaseModel
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from openai import OpenAI
from fastapi import FastAPI
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient


ACCOUNT_NAME = os.getenv("AZURE_STORAGE_ACCOUNT_NAME", "starmenlearning2026")
ACCOUNT_URL = f"https://{ACCOUNT_NAME}.blob.core.windows.net"
CONTAINER_NAME = os.getenv("AZURE_STORAGE_CONTAINER_NAME", "documents")
BLOB_NAME = os.getenv("AZURE_STORAGE_BLOB_NAME", "hello.txt")
AI_ENDPOINT = os.getenv(
    "AZURE_AI_ENDPOINT",
    "https://foundry-armen-sweden-2026.openai.azure.com/openai/v1/",
)
AI_DEPLOYMENT = os.getenv(
    "AZURE_AI_DEPLOYMENT",
    "gpt-5-mini-learning",
)

class AIRequest(BaseModel):
    message: str

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
    
def get_ai_client():
    credential = DefaultAzureCredential()

    token_provider = get_bearer_token_provider(
        credential,
        "https://ai.azure.com/.default",
    )

    return OpenAI(
        base_url=AI_ENDPOINT,
        api_key=token_provider,
    )
    
def read_blob_tool(blob_name: str) -> str:
    blob_service_client = get_blob_service_client()

    container_client = blob_service_client.get_container_client(
        CONTAINER_NAME
    )

    blob_client = container_client.get_blob_client(blob_name)

    return blob_client.download_blob().readall().decode("utf-8")

AI_TOOLS = [
    {
        "type": "function",
        "name": "read_blob",
        "description": "Read a blob from the application's storage container.",
        "parameters": {
            "type": "object",
            "properties": {
                "blob_name": {
                    "type": "string",
                    "description": "Name of the blob to read.",
                }
            },
            "required": ["blob_name"],
            "additionalProperties": False,
        },
        "strict": True,
    }
]

def execute_ai_tool(tool_name: str, arguments: dict) -> str:
    if tool_name != "read_blob":
        return f"DENIED: tool '{tool_name}' is not permitted."

    return read_blob_tool(**arguments)

@app.post("/ai")
def ai(request: AIRequest):
    client = get_ai_client()

    response = client.responses.create(
        model=AI_DEPLOYMENT,
        instructions=(
            "You are an Azure storage assistant. "
            "Use the read_blob tool when blob contents are needed."
        ),
        input=request.message,
        tools=AI_TOOLS,
    )

    tool_outputs = []

    for item in response.output:
        if item.type != "function_call":
            continue

        arguments = json.loads(item.arguments)

        result = execute_ai_tool(
            tool_name=item.name,
            arguments=arguments,
        )

        tool_outputs.append(
            {
                "type": "function_call_output",
                "call_id": item.call_id,
                "output": result,
            }
        )

    if tool_outputs:
        response = client.responses.create(
            model=AI_DEPLOYMENT,
            previous_response_id=response.id,
            input=tool_outputs,
            tools=AI_TOOLS,
        )

    return {
        "answer": response.output_text,
        "usage": {
            "input_tokens": response.usage.input_tokens,
            "output_tokens": response.usage.output_tokens,
            "total_tokens": response.usage.total_tokens,
        },
    }