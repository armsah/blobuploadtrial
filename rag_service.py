import os

from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from azure.search.documents import SearchClient
from azure.search.documents.models import VectorizedQuery
from openai import OpenAI


SEARCH_ENDPOINT = os.getenv(
    "AZURE_SEARCH_ENDPOINT",
    "https://search-armen-learning-2026.search.windows.net",
)
SEARCH_INDEX = os.getenv("AZURE_SEARCH_INDEX", "rag-documents")

FOUNDRY_ENDPOINT = os.getenv(
    "AZURE_AI_ENDPOINT",
    "https://foundry-armen-sweden-2026.openai.azure.com/openai/v1/",
)

EMBEDDING_DEPLOYMENT = os.getenv(
    "AZURE_AI_EMBEDDING_DEPLOYMENT",
    "embedding-learning",
)

CHAT_DEPLOYMENT = os.getenv(
    "AZURE_AI_DEPLOYMENT",
    "gpt-5-mini-learning",
)


def create_openai_client():
    token_provider = get_bearer_token_provider(
        DefaultAzureCredential(),
        "https://ai.azure.com/.default",
    )

    return OpenAI(
        base_url=FOUNDRY_ENDPOINT,
        api_key=token_provider,
    )


def create_search_client():
    return SearchClient(
        endpoint=SEARCH_ENDPOINT,
        index_name=SEARCH_INDEX,
        credential=DefaultAzureCredential(),
    )


def answer_question(question: str, top_k: int = 2):
    openai_client = create_openai_client()
    search_client = create_search_client()

    query_vector = openai_client.embeddings.create(
        model=EMBEDDING_DEPLOYMENT,
        input=question,
    ).data[0].embedding

    vector_query = VectorizedQuery(
        vector=query_vector,
        k_nearest_neighbors=top_k,
        fields="contentVector",
    )

    results = list(
        search_client.search(
            search_text=question,
            vector_queries=[vector_query],
            top=top_k,
        )
    )

    context = "\n".join(result["content"] for result in results)

    prompt = f"""
Answer the question using only the supplied context.
If the context does not contain the answer, say you don't know.

Context:
{context}

Question:
{question}
"""

    response = openai_client.responses.create(
        model=CHAT_DEPLOYMENT,
        input=prompt,
    )

    return {
        "answer": response.output_text,
        "sources": [result["source"] for result in results],
    }