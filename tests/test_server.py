"""Tests for the Lovdata MCP server tools."""

from __future__ import annotations

import json
import os
from unittest.mock import AsyncMock, patch

import httpx
import pytest

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

MOCK_USER_INFO = {
    "username": "testuser",
    "name": "Test User",
    "roles": ["api"],
    "rateLimit": {"requestsPerMinute": 60},
}

MOCK_SEARCH_RESULTS = {
    "total": 2,
    "results": [
        {
            "id": "LOV-2005-06-17-90",
            "title": "Lov om arbeidsmiljø, arbeidstid og stillingsvern mv. (arbeidsmiljøloven)",
            "date": "2005-06-17",
            "type": "lov",
            "url": "/document/NL/lov/2005-06-17-90",
        },
        {
            "id": "LOV-2004-06-04-15",
            "title": "Lov om arbeidsmarkedstjenester (arbeidsmarkedsloven)",
            "date": "2004-06-04",
            "type": "lov",
            "url": "/document/NL/lov/2004-06-04-15",
        },
    ],
}

MOCK_DOCUMENT = {
    "id": "LOV-2005-06-17-90",
    "title": "Arbeidsmiljøloven",
    "date": "2005-06-17",
    "type": "lov",
    "content": "<section>...</section>",
}

MOCK_METADATA = {
    "id": "LOV-2005-06-17-90",
    "title": "Arbeidsmiljøloven",
    "date": "2005-06-17",
    "type": "lov",
    "lastModified": "2024-01-01",
}


# ---------------------------------------------------------------------------
# Client tests
# ---------------------------------------------------------------------------


class TestLovdataClient:
    """Unit tests for the Lovdata API client module."""

    @pytest.mark.asyncio
    async def test_list_public_datasets_returns_all(self):
        from lovdata_mcp.client import PUBLIC_DATASETS, list_public_datasets

        result = await list_public_datasets()

        assert isinstance(result, list)
        assert len(result) == len(PUBLIC_DATASETS)
        for item in result:
            assert "name" in item
            assert "description" in item
            assert "url" in item
            from urllib.parse import urlparse
            parsed = urlparse(item["url"])
            assert parsed.scheme == "https"
            assert parsed.netloc == "api.lovdata.no"
            assert item["url"].endswith(".tar.bz2")
            assert item["format"] == "tar.bz2"
            assert item["license"] == "NLOD 2.0"

    @pytest.mark.asyncio
    async def test_get_public_dataset_url_valid(self):
        from lovdata_mcp.client import get_public_dataset_url

        url = await get_public_dataset_url("gjeldende-lover")

        assert url == "https://api.lovdata.no/v1/publicData/get/gjeldende-lover.tar.bz2"

    @pytest.mark.asyncio
    async def test_get_public_dataset_url_invalid_raises(self):
        from lovdata_mcp.client import get_public_dataset_url

        with pytest.raises(ValueError, match="Unknown dataset"):
            await get_public_dataset_url("does-not-exist")

    @pytest.mark.asyncio
    async def test_search_documents_sends_correct_params(self, httpx_mock):
        from lovdata_mcp.client import search_documents

        httpx_mock.add_response(
            method="GET",
            url="https://api.lovdata.no/v1/search?q=arbeidsmilj%C3%B8&from=0&size=5",
            json=MOCK_SEARCH_RESULTS,
        )

        result = await search_documents(query="arbeidsmiljø", size=5)

        assert result["total"] == 2
        assert len(result["results"]) == 2

    @pytest.mark.asyncio
    async def test_search_documents_with_type_filter(self, httpx_mock):
        from lovdata_mcp.client import search_documents

        httpx_mock.add_response(
            method="GET",
            url="https://api.lovdata.no/v1/search?q=skatt&from=0&size=10&type=lov",
            json=MOCK_SEARCH_RESULTS,
        )

        result = await search_documents(query="skatt", document_type="lov")

        assert result["total"] == 2

    @pytest.mark.asyncio
    async def test_get_document_returns_content(self, httpx_mock):
        from lovdata_mcp.client import get_document

        httpx_mock.add_response(
            method="GET",
            url="https://api.lovdata.no/v1/document/LOV-2005-06-17-90",
            json=MOCK_DOCUMENT,
        )

        result = await get_document("LOV-2005-06-17-90")

        assert result["id"] == "LOV-2005-06-17-90"
        assert result["title"] == "Arbeidsmiljøloven"

    @pytest.mark.asyncio
    async def test_get_document_metadata_returns_metadata(self, httpx_mock):
        from lovdata_mcp.client import get_document_metadata

        httpx_mock.add_response(
            method="GET",
            url="https://api.lovdata.no/v1/document/LOV-2005-06-17-90/metadata",
            json=MOCK_METADATA,
        )

        result = await get_document_metadata("LOV-2005-06-17-90")

        assert result["id"] == "LOV-2005-06-17-90"
        assert "lastModified" in result

    @pytest.mark.asyncio
    async def test_get_user_info_returns_user(self, httpx_mock):
        from lovdata_mcp.client import get_user_info

        httpx_mock.add_response(
            method="GET",
            url="https://api.lovdata.no/v1/userinfo",
            json=MOCK_USER_INFO,
        )

        result = await get_user_info()

        assert result["username"] == "testuser"
        assert "api" in result["roles"]

    @pytest.mark.asyncio
    async def test_api_key_auth_sends_header(self, httpx_mock, monkeypatch):
        from lovdata_mcp import client

        monkeypatch.setenv("LOVDATA_API_KEY", "test-key-123")

        httpx_mock.add_response(
            method="GET",
            url="https://api.lovdata.no/v1/userinfo",
            match_headers={"X-API-Key": "test-key-123"},
            json=MOCK_USER_INFO,
        )

        result = await client.get_user_info()

        assert result["username"] == "testuser"

    @pytest.mark.asyncio
    async def test_http_404_raises(self, httpx_mock):
        from lovdata_mcp.client import get_document

        httpx_mock.add_response(
            method="GET",
            url="https://api.lovdata.no/v1/document/NONEXISTENT-123",
            status_code=404,
        )

        with pytest.raises(httpx.HTTPStatusError):
            await get_document("NONEXISTENT-123")


# ---------------------------------------------------------------------------
# MCP server tool tests
# ---------------------------------------------------------------------------


class TestMCPTools:
    """Tests for MCP tool handlers in server.py."""

    @pytest.mark.asyncio
    async def test_list_public_datasets_tool(self):
        from lovdata_mcp.server import list_public_datasets

        result = await list_public_datasets()

        assert isinstance(result, list)
        assert len(result) > 0
        assert all("name" in d and "url" in d for d in result)

    @pytest.mark.asyncio
    async def test_get_public_dataset_url_tool_valid(self):
        from lovdata_mcp.server import get_public_dataset_url

        result = await get_public_dataset_url("gjeldende-lover")

        assert result["dataset"] == "gjeldende-lover"
        assert result["url"].endswith(".tar.bz2")
        assert result["license"] == "NLOD 2.0"

    @pytest.mark.asyncio
    async def test_get_public_dataset_url_tool_invalid(self):
        from lovdata_mcp.server import get_public_dataset_url

        result = await get_public_dataset_url("invalid-dataset")

        assert "error" in result
        assert "Unknown dataset" in result["error"]

    @pytest.mark.asyncio
    async def test_search_documents_tool_http_error(self, httpx_mock):
        from lovdata_mcp.server import search_documents

        httpx_mock.add_response(
            method="GET",
            url="https://api.lovdata.no/v1/search?q=test&from=0&size=10",
            status_code=401,
        )

        result = await search_documents(query="test")

        assert "error" in result
        assert "401" in result["error"] or "Authentication" in result["error"]

    @pytest.mark.asyncio
    async def test_search_documents_tool_rate_limit(self, httpx_mock):
        from lovdata_mcp.server import search_documents

        httpx_mock.add_response(
            method="GET",
            url="https://api.lovdata.no/v1/search?q=test&from=0&size=10",
            status_code=429,
        )

        result = await search_documents(query="test")

        assert "error" in result
        assert "429" in result["error"] or "Rate limit" in result["error"]

    @pytest.mark.asyncio
    async def test_get_document_tool_not_found(self, httpx_mock):
        from lovdata_mcp.server import get_document

        httpx_mock.add_response(
            method="GET",
            url="https://api.lovdata.no/v1/document/MISSING-DOC",
            status_code=404,
        )

        result = await get_document("MISSING-DOC")

        assert "error" in result
        assert "404" in result["error"] or "not found" in result["error"].lower()

    @pytest.mark.asyncio
    async def test_get_document_tool_success(self, httpx_mock):
        from lovdata_mcp.server import get_document

        httpx_mock.add_response(
            method="GET",
            url="https://api.lovdata.no/v1/document/LOV-2005-06-17-90",
            json=MOCK_DOCUMENT,
        )

        result = await get_document("LOV-2005-06-17-90")

        assert result["id"] == "LOV-2005-06-17-90"

    @pytest.mark.asyncio
    async def test_get_user_info_tool_success(self, httpx_mock):
        from lovdata_mcp.server import get_user_info

        httpx_mock.add_response(
            method="GET",
            url="https://api.lovdata.no/v1/userinfo",
            json=MOCK_USER_INFO,
        )

        result = await get_user_info()

        assert result["username"] == "testuser"

    @pytest.mark.asyncio
    async def test_get_user_info_tool_unauthenticated(self, httpx_mock):
        from lovdata_mcp.server import get_user_info

        httpx_mock.add_response(
            method="GET",
            url="https://api.lovdata.no/v1/userinfo",
            status_code=401,
        )

        result = await get_user_info()

        assert "error" in result
        assert "Authentication" in result["error"] or "401" in result["error"]

    @pytest.mark.asyncio
    async def test_get_document_metadata_tool_success(self, httpx_mock):
        from lovdata_mcp.server import get_document_metadata

        httpx_mock.add_response(
            method="GET",
            url="https://api.lovdata.no/v1/document/LOV-2005-06-17-90/metadata",
            json=MOCK_METADATA,
        )

        result = await get_document_metadata("LOV-2005-06-17-90")

        assert result["id"] == "LOV-2005-06-17-90"
        assert "lastModified" in result

    @pytest.mark.asyncio
    async def test_search_documents_tool_success(self, httpx_mock):
        from lovdata_mcp.server import search_documents

        httpx_mock.add_response(
            method="GET",
            url="https://api.lovdata.no/v1/search?q=arbeidsmilj%C3%B8&from=0&size=10",
            json=MOCK_SEARCH_RESULTS,
        )

        result = await search_documents(query="arbeidsmiljø")

        assert result["total"] == 2
        assert len(result["results"]) == 2

    @pytest.mark.asyncio
    async def test_search_with_court_decisions_type(self, httpx_mock):
        """Test searching specifically for court decisions (avgjørelser)."""
        from lovdata_mcp.server import search_documents

        mock_decisions = {
            "total": 1,
            "results": [
                {
                    "id": "HR-2024-123-A",
                    "title": "Høyesteretts dom",
                    "date": "2024-03-15",
                    "type": "avgjorelse",
                }
            ],
        }

        httpx_mock.add_response(
            method="GET",
            url="https://api.lovdata.no/v1/search?q=erstatning&from=0&size=10&type=avgjorelse",
            json=mock_decisions,
        )

        result = await search_documents(query="erstatning", document_type="avgjorelse")

        assert result["total"] == 1
        assert result["results"][0]["id"] == "HR-2024-123-A"
