from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient
from azure.core.exceptions import ResourceExistsError

ACCOUNT_NAME = "starmenlearning2026"
ACCOUNT_URL = f"https://{ACCOUNT_NAME}.blob.core.windows.net"
CONTAINER_NAME = "documents"
BLOB_NAME = "hello.txt"

def main():

    credential = DefaultAzureCredential()

    blob_service_client = BlobServiceClient(
        account_url=ACCOUNT_URL, 
        credential=credential
    )

    print(f"Connected client configured for: {ACCOUNT_URL}")

    container_client = blob_service_client.get_container_client(CONTAINER_NAME)

    try:
        container_client.create_container()
        print(f"Created container: {CONTAINER_NAME}")
    except ResourceExistsError:
        print(f"Container already exists: {CONTAINER_NAME}")

    blob_client = container_client.get_blob_client(BLOB_NAME)

    with open("hello.txt", "rb") as data:
        blob_client.upload_blob(data, overwrite=True)
    
    print(f"Uploaded blob: {BLOB_NAME}")

    print("Containers:")

    for container in blob_service_client.list_containers():
        print(f" - {container['name']}")
    
    print("Blobs:")

    for blob in container_client.list_blobs():
        print(f" - {blob['name']}")
    
    download_stream = blob_client.download_blob()
    content = download_stream.readall()

    print("Downloaded content:")
    print(content.decode("utf-8"))
    
if __name__ == "__main__":
    main()