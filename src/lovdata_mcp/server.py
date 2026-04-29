"""MCP server exposing the Lovdata API as tools for LLM applications.

Run with stdio transport (default, for Claude Desktop / MCP clients):

    python -m lovdata_mcp.server

Or with HTTP transport:

    python -m lovdata_mcp.server --transport streamable-http

Environment variables
---------------------
LOVDATA_API_KEY   – Lovdata API key (takes priority over Basic Auth)
LOVDATA_USERNAME  – Lovdata username  (used when no API key is set)
LOVDATA_PASSWORD  – Lovdata password
"""

from __future__ import annotations

import sys
from typing import Any

import httpx
from mcp.server.fastmcp import FastMCP

from lovdata_mcp import client as lovdata

mcp = FastMCP(
    "Lovdata MCP",
    instructions=(
        "This server provides access to the Lovdata API – the authoritative "
        "Norwegian legal database. It contains laws, regulations, court "
        "decisions, and other legal sources. Use the tools to search and "
        "retrieve Norwegian legal documents."
    ),
)


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------


def _http_error_message(exc: httpx.HTTPStatusError) -> str:
    status = exc.response.status_code
    if status == 401:
        return (
            "Authentication failed (HTTP 401). "
            "Set LOVDATA_API_KEY or LOVDATA_USERNAME / LOVDATA_PASSWORD."
        )
    if status == 403:
        return (
            "Access forbidden (HTTP 403). "
            "Your account may not have the required permissions."
        )
    if status == 404:
        return f"Resource not found (HTTP 404): {exc.request.url}"
    if status == 429:
        return (
            "Rate limit exceeded (HTTP 429). "
            "Please slow down requests. "
            "Check X-RateLimit-* headers for quota information."
        )
    return f"HTTP error {status}: {exc.response.text}"


# ---------------------------------------------------------------------------
# Tools
# ---------------------------------------------------------------------------


@mcp.tool()
async def search_documents(
    query: str,
    document_type: str | None = None,
    from_index: int = 0,
    size: int = 10,
    sort: str | None = None,
) -> dict[str, Any]:
    """Search for legal documents in the Lovdata database.

    Searches across Norwegian laws, regulations, court decisions and other
    legal sources.

    Parameters
    ----------
    query:
        Free-text search query, e.g. "arbeidsmiljø" or "oppsigelse".
    document_type:
        Optional document type filter. Common values:
        - "lov"         – Laws (lover)
        - "forskrift"   – Regulations (forskrifter)
        - "avgjorelse"  – Court decisions (avgjørelser)
        - "traktat"     – Treaties (traktater)
    from_index:
        Pagination offset (0-based). Default: 0.
    size:
        Number of results to return (1–100). Default: 10.
    sort:
        Sort order: "date" (newest first) or "relevance" (best match first).
    """
    try:
        return await lovdata.search_documents(
            query=query,
            document_type=document_type,
            from_index=from_index,
            size=size,
            sort=sort,
        )
    except httpx.HTTPStatusError as exc:
        return {"error": _http_error_message(exc)}
    except httpx.RequestError as exc:
        return {"error": f"Network error: {exc}"}


@mcp.tool()
async def get_document(document_id: str) -> dict[str, Any]:
    """Retrieve a specific legal document from Lovdata by its identifier.

    Returns the full document content and metadata.

    Parameters
    ----------
    document_id:
        Lovdata document identifier. Examples:
        - "LOV-2005-06-17-90"   – the Working Environment Act
        - "FOR-2022-06-17-990"  – a regulation
        - "HR-2024-123-A"       – a Supreme Court decision
        - "LB-2023-456789"      – a Court of Appeal decision
    """
    try:
        return await lovdata.get_document(document_id)
    except httpx.HTTPStatusError as exc:
        return {"error": _http_error_message(exc)}
    except httpx.RequestError as exc:
        return {"error": f"Network error: {exc}"}


@mcp.tool()
async def get_document_metadata(document_id: str) -> dict[str, Any]:
    """Retrieve metadata for a specific legal document.

    Returns metadata such as title, date, document type, and references
    without fetching the full document text.

    Parameters
    ----------
    document_id:
        Lovdata document identifier. Examples:
        - "LOV-2005-06-17-90"   – the Working Environment Act
        - "HR-2024-123-A"       – a Supreme Court decision
    """
    try:
        return await lovdata.get_document_metadata(document_id)
    except httpx.HTTPStatusError as exc:
        return {"error": _http_error_message(exc)}
    except httpx.RequestError as exc:
        return {"error": f"Network error: {exc}"}


@mcp.tool()
async def get_user_info() -> dict[str, Any]:
    """Retrieve information about the authenticated Lovdata API user.

    Returns details about the current API user, including available
    permissions and rate-limit quotas.

    Requires either LOVDATA_API_KEY or LOVDATA_USERNAME/LOVDATA_PASSWORD
    to be configured.
    """
    try:
        return await lovdata.get_user_info()
    except httpx.HTTPStatusError as exc:
        return {"error": _http_error_message(exc)}
    except httpx.RequestError as exc:
        return {"error": f"Network error: {exc}"}


@mcp.tool()
async def list_public_datasets() -> list[dict[str, str]]:
    """List all freely available public datasets from Lovdata.

    These datasets do not require authentication and are available under
    the NLOD 2.0 open license. They include bulk downloads of current
    laws, regulations, treaties and other legal sources.

    Returns a list of datasets with their name, description, download URL,
    format (tar.bz2) and license.
    """
    return await lovdata.list_public_datasets()


@mcp.tool()
async def get_public_dataset_url(dataset_name: str) -> dict[str, str]:
    """Return the download URL for a named public Lovdata dataset.

    The dataset is a compressed tar.bz2 archive containing legal documents
    in XML format.  No authentication is required.

    Parameters
    ----------
    dataset_name:
        Dataset identifier. Use list_public_datasets() to see all options.
        Common values:
        - "gjeldende-lover"                      – Current laws
        - "gjeldende-sentrale-forskrifter"       – Current central regulations
        - "gjeldende-lokale-forskrifter"         – Current local regulations
        - "gjeldende-traktater"                  – Current treaties
        - "gjeldende-andre-sentrale-rettskilder" – Other central legal sources
    """
    try:
        url = await lovdata.get_public_dataset_url(dataset_name)
        return {
            "dataset": dataset_name,
            "url": url,
            "format": "tar.bz2",
            "license": "NLOD 2.0",
            "note": "No authentication required to download this dataset.",
        }
    except ValueError as exc:
        return {"error": str(exc)}


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def main() -> None:
    transport = "stdio"
    if "--transport" in sys.argv:
        idx = sys.argv.index("--transport")
        if idx + 1 < len(sys.argv):
            transport = sys.argv[idx + 1]

    mcp.run(transport=transport)


if __name__ == "__main__":
    main()
