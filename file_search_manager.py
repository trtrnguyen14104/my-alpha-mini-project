import logging
import time

from google import genai

logger = logging.getLogger("file_search_manager")

_POLL_INTERVAL_SECONDS = 2
_POLL_TIMEOUT_SECONDS = 180


def get_client(api_key: str) -> genai.Client:
    return genai.Client(api_key=api_key)


def get_or_create_store(client: genai.Client, store_name: str, display_name: str):
    if store_name:
        try:
            store = client.file_search_stores.get(name=store_name)
            logger.info(f"Using existing File Search store: {store.name}")
            return store
        except Exception as e:
            logger.warning(
                f"{store_name} not found ({e})"
            )

    store = client.file_search_stores.create(config={"display_name": display_name})
    logger.info(f"Created new File Search store: {store.name}")
    return store


def _wait_for_operation(client: genai.Client, operation):
    """Polls a long-running upload/import operation until it's done."""
    waited = 0
    while not operation.done:
        if waited >= _POLL_TIMEOUT_SECONDS:
            raise TimeoutError("Timed out waiting for File Search upload to finish")
        time.sleep(_POLL_INTERVAL_SECONDS)
        waited += _POLL_INTERVAL_SECONDS
        operation = client.operations.get(operation)
    return operation


def upload_article(client: genai.Client, store, article, filepath: str) -> str:
    operation = client.file_search_stores.upload_to_file_search_store(
        file_search_store_name=store.name,
        file=filepath,
        config={
            "mime_type": "text/markdown",
            "display_name": article["slug"],
            "custom_metadata": [
                {"key": "article_id", "string_value": article["id"]},
                {"key": "article_url", "string_value": article["url"]},
                {"key": "title", "string_value": article["title"]},
            ],
        },
    )
    operation = _wait_for_operation(client, operation)
    document_name = operation.response.document_name if operation.response else None
    if not document_name:
        raise RuntimeError("File Search upload finished but did not return a document name")
    return document_name


def delete_document(client: genai.Client, document_name: str):
    try:
        client.file_search_stores.documents.delete(name=document_name, config={"force": True})
        logger.info(f"Deleted document: {document_name}")
    except Exception as e:
        logger.warning(f"Could not delete document {document_name} (may already be gone): {e}")
