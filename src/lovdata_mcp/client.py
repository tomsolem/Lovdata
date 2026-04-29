"""HTTP client for the Lovdata REST API.

Base URL: https://api.lovdata.no
API docs: https://api.lovdata.no/om-api-tjenesten/

Authentication
--------------
Two methods are supported (both optional for public-data endpoints):

* API key  – pass the key via the ``X-API-Key`` header.
* Basic Auth – supply username/password for a Lovdata user that has the
  ``api`` role.

Set the credentials through environment variables:

    LOVDATA_API_KEY   – your API key  (takes priority over Basic Auth)
    LOVDATA_USERNAME  – Lovdata username
    LOVDATA_PASSWORD  – Lovdata password
"""

from __future__ import annotations

import os
from typing import Any

import httpx

BASE_URL = "https://api.lovdata.no"
API_VERSION = "v1"

# Known public datasets (no authentication required)
PUBLIC_DATASETS: dict[str, str] = {
    "gjeldende-lover": "Current laws (gjeldende lover)",
    "gjeldende-sentrale-forskrifter": "Current central regulations (gjeldende sentrale forskrifter)",
    "gjeldende-lokale-forskrifter": "Current local regulations (gjeldende lokale forskrifter)",
    "gjeldende-traktater": "Current treaties (gjeldende traktater)",
    "gjeldende-andre-sentrale-rettskilder": "Other current central legal sources",
}


def _build_auth() -> tuple[httpx.Auth | None, dict[str, str]]:
    """Return (auth, extra_headers) based on environment variables."""
    api_key = os.getenv("LOVDATA_API_KEY", "").strip()
    if api_key:
        return None, {"X-API-Key": api_key}

    username = os.getenv("LOVDATA_USERNAME", "").strip()
    password = os.getenv("LOVDATA_PASSWORD", "").strip()
    if username and password:
        return httpx.BasicAuth(username, password), {}

    return None, {}


def _client() -> httpx.AsyncClient:
    auth, headers = _build_auth()
    return httpx.AsyncClient(
        base_url=BASE_URL,
        auth=auth,
        headers=headers,
        timeout=30.0,
        follow_redirects=True,
    )


async def get_user_info() -> dict[str, Any]:
    """Return information about the authenticated API user.

    Endpoint: GET /v1/userinfo
    Requires authentication.
    """
    async with _client() as client:
        response = await client.get(f"/{API_VERSION}/userinfo")
        response.raise_for_status()
        return response.json()


async def search_documents(
    query: str,
    document_type: str | None = None,
    from_index: int = 0,
    size: int = 10,
    sort: str | None = None,
) -> dict[str, Any]:
    """Search legal documents in the Lovdata database.

    Endpoint: GET /v1/search
    Requires authentication.

    Parameters
    ----------
    query:
        Free-text search query.
    document_type:
        Optional filter, e.g. ``lov`` (law), ``forskrift`` (regulation),
        ``avgjorelse`` (court decision).
    from_index:
        Pagination offset (0-based).
    size:
        Number of results per page (max 100).
    sort:
        Sort order – e.g. ``date`` or ``relevance``.
    """
    params: dict[str, Any] = {"q": query, "from": from_index, "size": size}
    if document_type:
        params["type"] = document_type
    if sort:
        params["sort"] = sort

    async with _client() as client:
        response = await client.get(f"/{API_VERSION}/search", params=params)
        response.raise_for_status()
        return response.json()


async def get_document(document_id: str) -> dict[str, Any]:
    """Retrieve a specific legal document by its Lovdata identifier.

    Endpoint: GET /v1/document/{dokID}
    Requires authentication.

    Parameters
    ----------
    document_id:
        Lovdata document identifier, e.g. ``LOV-2002-06-21-45`` (law),
        ``HR-2024-123-A`` (Supreme Court decision).
    """
    async with _client() as client:
        response = await client.get(f"/{API_VERSION}/document/{document_id}")
        response.raise_for_status()
        return response.json()


async def get_document_metadata(document_id: str) -> dict[str, Any]:
    """Retrieve metadata for a specific legal document.

    Endpoint: GET /v1/document/{dokID}/metadata
    Requires authentication.

    Parameters
    ----------
    document_id:
        Lovdata document identifier.
    """
    async with _client() as client:
        response = await client.get(
            f"/{API_VERSION}/document/{document_id}/metadata"
        )
        response.raise_for_status()
        return response.json()


async def get_public_dataset_url(dataset_name: str) -> str:
    """Return the download URL for a named public dataset.

    Public datasets do not require authentication and are freely available
    under the NLOD 2.0 open license.

    Endpoint: GET /v1/publicData/get/{dataset}

    Parameters
    ----------
    dataset_name:
        One of the keys in ``PUBLIC_DATASETS``, e.g.
        ``gjeldende-lover``.
    """
    if dataset_name not in PUBLIC_DATASETS:
        valid = ", ".join(PUBLIC_DATASETS.keys())
        raise ValueError(
            f"Unknown dataset '{dataset_name}'. Valid options: {valid}"
        )
    return f"{BASE_URL}/{API_VERSION}/publicData/get/{dataset_name}.tar.bz2"


async def list_public_datasets() -> list[dict[str, str]]:
    """Return information about all available public datasets.

    These datasets are freely available and do not require authentication.
    Each entry contains the dataset key and a human-readable description.
    """
    return [
        {
            "name": name,
            "description": description,
            "url": f"{BASE_URL}/{API_VERSION}/publicData/get/{name}.tar.bz2",
            "format": "tar.bz2",
            "license": "NLOD 2.0",
        }
        for name, description in PUBLIC_DATASETS.items()
    ]
