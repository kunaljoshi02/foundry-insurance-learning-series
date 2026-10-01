from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any


MODULE_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = MODULE_ROOT.parents[1]
SHARED_PYTHON = REPO_ROOT / "shared" / "python"
if str(SHARED_PYTHON) not in sys.path:
    sys.path.insert(0, str(SHARED_PYTHON))

from config_loader import ConfigError, load_config  # type: ignore  # noqa: E402


DATASET_PATH = REPO_ROOT / "shared" / "test-data" / "policy-wordings.json"
DATASET_LABEL = "shared/test-data/policy-wordings.json"
DEFAULT_INDEX_NAME = "policy-wordings"
VECTOR_DIMENSIONS = 1536
SCHEMA_FIELD_NAMES = [
    "id",
    "product",
    "policy_form",
    "section_ref",
    "clause_type",
    "title",
    "content",
    "content_vector",
]


class SearchIndexError(RuntimeError):
    """Raised when Search index operations fail."""


class OptionalFoundryEmbedder:
    """Optional embedding helper for vector backfill."""

    def __init__(self, project_endpoint: str, deployment_name: str) -> None:
        self.project_endpoint = project_endpoint.rstrip("/")
        self.deployment_name = deployment_name

    def _token(self) -> str:
        from azure.identity import DefaultAzureCredential

        credential = DefaultAzureCredential(exclude_interactive_browser_credential=False)
        return credential.get_token("https://ai.azure.com/.default").token

    def embed(self, texts: list[str]) -> list[list[float]]:
        if "/api/projects/" in self.project_endpoint:
            base = self.project_endpoint.split("/api/projects/", 1)[0]
        else:
            base = self.project_endpoint

        url = (
            f"{base}/openai/deployments/{urllib.parse.quote(self.deployment_name, safe='')}"
            "/embeddings?api-version=2024-02-01"
        )
        body = json.dumps({"input": texts}).encode("utf-8")
        request = urllib.request.Request(
            url,
            data=body,
            method="POST",
            headers={
                "Authorization": f"Bearer {self._token()}",
                "Content-Type": "application/json",
            },
        )
        try:
            with urllib.request.urlopen(request, timeout=180) as response:
                payload = json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            error_body = exc.read().decode("utf-8", errors="replace")
            raise SearchIndexError(
                f"Embedding request failed with HTTP {exc.code}: {error_body[:1200]}"
            ) from exc

        return [item["embedding"] for item in payload.get("data", [])]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create, verify, or delete the Module 03 Search index.")
    parser.add_argument("--config", default=str(MODULE_ROOT / "config.json"), help="Path to config.json.")
    parser.add_argument(
        "--action",
        choices=("ensure", "verify", "delete-index"),
        default="ensure",
        help="Operation to perform.",
    )
    parser.add_argument("--what-if", action="store_true", help="Preview changes without writing.")
    return parser.parse_args()


def required_config_keys(action: str) -> list[str]:
    keys = ["searchServiceName", "searchIndexName"]
    if action == "ensure":
        return ["foundryEndpoint", *keys]
    return keys


def fail(message: str, exit_code: int = 1) -> int:
    print(f"ERROR: {message}", file=sys.stderr)
    return exit_code


def load_policy_dataset() -> list[dict[str, Any]]:
    if not DATASET_PATH.exists():
        raise SearchIndexError(f"Dataset not found: {DATASET_LABEL}")

    payload = json.loads(DATASET_PATH.read_text(encoding="utf-8"))
    if not isinstance(payload, list) or not payload:
        raise SearchIndexError("Expected policy-wordings.json to contain a non-empty array.")

    return payload


def search_endpoint_from_config(config: dict[str, Any]) -> str:
    if isinstance(config.get("searchEndpoint"), str) and config["searchEndpoint"].strip():
        return str(config["searchEndpoint"]).rstrip("/")
    return f"https://{config['searchServiceName']}.search.windows.net"


def import_search_sdk() -> tuple[Any, ...]:
    try:
        from azure.identity import DefaultAzureCredential
        from azure.core.credentials import AzureKeyCredential
        from azure.core.exceptions import ResourceNotFoundError
        from azure.search.documents import SearchClient
        from azure.search.documents.indexes import SearchIndexClient
        from azure.search.documents.indexes.models import (
            HnswAlgorithmConfiguration,
            SearchField,
            SearchFieldDataType,
            SearchIndex,
            SearchableField,
            SemanticConfiguration,
            SemanticField,
            SemanticPrioritizedFields,
            SemanticSearch,
            SimpleField,
            VectorSearch,
            VectorSearchProfile,
        )
    except ImportError as exc:  # pragma: no cover - depends on author environment
        raise SearchIndexError(
            'Missing required packages. Install them with: pip install azure-identity azure-search-documents'
        ) from exc

    return (
        DefaultAzureCredential,
        AzureKeyCredential,
        ResourceNotFoundError,
        SearchClient,
        SearchIndexClient,
        SearchField,
        SearchFieldDataType,
        SearchIndex,
        SearchableField,
        SimpleField,
        VectorSearch,
        HnswAlgorithmConfiguration,
        VectorSearchProfile,
        SemanticSearch,
        SemanticConfiguration,
        SemanticPrioritizedFields,
        SemanticField,
    )


def build_index_definition(index_name: str) -> Any:
    (
        _DefaultAzureCredential,
        _AzureKeyCredential,
        _ResourceNotFoundError,
        _SearchClient,
        _SearchIndexClient,
        SearchField,
        SearchFieldDataType,
        SearchIndex,
        SearchableField,
        SimpleField,
        VectorSearch,
        HnswAlgorithmConfiguration,
        VectorSearchProfile,
        SemanticSearch,
        SemanticConfiguration,
        SemanticPrioritizedFields,
        SemanticField,
    ) = import_search_sdk()

    fields = [
        SimpleField(name="id", type=SearchFieldDataType.String, key=True, filterable=True),
        SearchableField(name="product", type=SearchFieldDataType.String, filterable=True, facetable=True),
        SearchableField(name="policy_form", type=SearchFieldDataType.String, filterable=True, facetable=True),
        SearchableField(name="section_ref", type=SearchFieldDataType.String, filterable=True),
        SearchableField(name="clause_type", type=SearchFieldDataType.String, filterable=True, facetable=True),
        SearchableField(name="title", type=SearchFieldDataType.String),
        SearchableField(name="content", type=SearchFieldDataType.String),
        SearchField(
            name="content_vector",
            type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
            searchable=True,
            vector_search_dimensions=VECTOR_DIMENSIONS,
            vector_search_profile_name="policy-vector-profile",
            hidden=True,
        ),
    ]

    return SearchIndex(
        name=index_name,
        fields=fields,
        vector_search=VectorSearch(
            algorithms=[HnswAlgorithmConfiguration(name="policy-hnsw")],
            profiles=[
                VectorSearchProfile(
                    name="policy-vector-profile",
                    algorithm_configuration_name="policy-hnsw",
                )
            ],
        ),
        semantic_search=SemanticSearch(
            default_configuration_name="policy-semantic",
            configurations=[
                SemanticConfiguration(
                    name="policy-semantic",
                    prioritized_fields=SemanticPrioritizedFields(
                        title_field=SemanticField(field_name="title"),
                        content_fields=[SemanticField(field_name="content")],
                        keywords_fields=[
                            SemanticField(field_name="product"),
                            SemanticField(field_name="clause_type"),
                            SemanticField(field_name="section_ref"),
                        ],
                    ),
                )
            ],
        ),
    )


def build_documents(config: dict[str, Any], dataset: list[dict[str, Any]]) -> list[dict[str, Any]]:
    embedding_deployment = config.get("embeddingDeploymentName")
    embedder: OptionalFoundryEmbedder | None = None
    if (
        isinstance(embedding_deployment, str)
        and embedding_deployment.strip()
        and not embedding_deployment.startswith("<")
    ):
        embedder = OptionalFoundryEmbedder(str(config["foundryEndpoint"]), embedding_deployment.strip())
    elif embedding_deployment:
        print("Embedding deployment left as a placeholder; uploading text documents without vectors.")

    vectors: list[list[float] | None] = [None] * len(dataset)
    if embedder is not None:
        batch_size = 16
        rendered = [f"{item['title']}\n\n{item['content']}" for item in dataset]
        for start in range(0, len(rendered), batch_size):
            end = start + batch_size
            batch_vectors = embedder.embed(rendered[start:end])
            for offset, vector in enumerate(batch_vectors):
                vectors[start + offset] = vector
            print(f"Embedded {min(end, len(rendered))} / {len(rendered)} records.")
    else:
        print("No embedding deployment configured; vector field remains available for future backfill.")

    documents: list[dict[str, Any]] = []
    for item, vector in zip(dataset, vectors):
        document = {
            "id": item["id"],
            "product": item["product"],
            "policy_form": item["policy_form"],
            "section_ref": item["section_ref"],
            "clause_type": item["clause_type"],
            "title": item["title"],
            "content": item["content"],
        }
        if vector is not None:
            document["content_vector"] = vector
        documents.append(document)

    return documents


def create_search_clients(config: dict[str, Any]) -> tuple[Any, Any, Any]:
    (
        DefaultAzureCredential,
        AzureKeyCredential,
        ResourceNotFoundError,
        SearchClient,
        SearchIndexClient,
        *_rest,
    ) = import_search_sdk()

    endpoint = search_endpoint_from_config(config)
    api_key = config.get("searchAdminApiKey") or os.environ.get("AZURE_SEARCH_ADMIN_KEY")
    if isinstance(api_key, str) and api_key and not api_key.startswith("<"):
        credential: Any = AzureKeyCredential(api_key)
    else:
        credential = DefaultAzureCredential(exclude_interactive_browser_credential=False)

    index_client = SearchIndexClient(endpoint=endpoint, credential=credential)
    search_client = SearchClient(endpoint=endpoint, index_name=config["searchIndexName"], credential=credential)
    return index_client, search_client, ResourceNotFoundError


def ensure_index(config: dict[str, Any], what_if: bool) -> int:
    dataset = load_policy_dataset()
    index_name = str(config.get("searchIndexName") or DEFAULT_INDEX_NAME)

    if what_if:
        print(f"WhatIf: would create or update Search index {index_name!r}.")
        print(f"WhatIf: would merge or upload {len(dataset)} documents from {DATASET_PATH.name}.")
        return 0

    index_client, search_client, ResourceNotFoundError = create_search_clients(config)
    definition = build_index_definition(index_name)

    try:
        existing = index_client.get_index(index_name)
        field_names = [field.name for field in existing.fields]
        print(f"Found existing index {index_name!r} with fields: {', '.join(field_names)}")
    except ResourceNotFoundError:
        print(f"Index {index_name!r} does not exist yet and will be created.")

    index_client.create_or_update_index(definition)
    print(f"Index {index_name!r} is ready.")

    documents = build_documents(config, dataset)
    for start in range(0, len(documents), 20):
        batch = documents[start : start + 20]
        search_client.merge_or_upload_documents(batch)
        print(f"Uploaded batch {start // 20 + 1} containing {len(batch)} documents.")

    count = search_client.get_document_count()
    print(f"Index document count: {count}")
    return 0 if count > 0 else fail("Index exists but document count is zero.")


def verify_index(config: dict[str, Any]) -> int:
    index_client, search_client, ResourceNotFoundError = create_search_clients(config)
    index_name = str(config["searchIndexName"])

    try:
        index = index_client.get_index(index_name)
    except ResourceNotFoundError:
        return fail(f"Search index {index_name!r} was not found.")

    field_names = [field.name for field in index.fields]
    missing = [field for field in SCHEMA_FIELD_NAMES if field not in field_names]
    if missing:
        return fail(f"Search index {index_name!r} is missing expected fields: {missing}")

    count = search_client.get_document_count()
    print(f"Verified Search index {index_name!r}. Document count: {count}")
    return 0 if count > 0 else fail("Expected Search index document count to be greater than zero.")


def delete_index(config: dict[str, Any], what_if: bool) -> int:
    index_name = str(config["searchIndexName"])
    if what_if:
        print(f"WhatIf: would delete Search index {index_name!r}.")
        return 0

    index_client, _search_client, ResourceNotFoundError = create_search_clients(config)
    try:
        index_client.delete_index(index_name)
        print(f"Deleted Search index {index_name!r}.")
    except ResourceNotFoundError:
        print(f"Search index {index_name!r} does not exist. Nothing to delete.")
    return 0


def main() -> int:
    args = parse_args()
    try:
        config = load_config(args.config, required_keys=required_config_keys(args.action))
    except ConfigError as exc:
        return fail(str(exc))

    if args.action == "ensure":
        return ensure_index(config, args.what_if)
    if args.action == "verify":
        return verify_index(config)
    if args.action == "delete-index":
        return delete_index(config, args.what_if)
    return fail(f"Unsupported action: {args.action}")


if __name__ == "__main__":
    raise SystemExit(main())
