# Lovdata MCP

A [Model Context Protocol (MCP)](https://modelcontextprotocol.io) server that
exposes the [Lovdata API](https://api.lovdata.no/om-api-tjenesten/) to LLM
applications such as Claude Desktop.

Lovdata is the authoritative Norwegian legal database, containing laws,
regulations, court decisions (avgjørelser), treaties, and other legal sources.

---

## Features

| MCP Tool | Description |
|---|---|
| `search_documents` | Search across Norwegian laws, regulations, and court decisions |
| `get_document` | Retrieve a specific document by its Lovdata identifier |
| `get_document_metadata` | Fetch lightweight metadata for a document |
| `get_user_info` | Return information about the authenticated API user |
| `list_public_datasets` | List freely available bulk-download datasets (no auth needed) |
| `get_public_dataset_url` | Get the download URL for a specific public dataset |

---

## Installation

### Requirements

- Python 3.10 or newer
- A [Lovdata API key](https://api.lovdata.no/om-api-tjenesten/) or Lovdata username/password
  (required for `search_documents`, `get_document`, `get_document_metadata`, `get_user_info`)
- Public-dataset tools work without authentication

### Install with pip

```bash
pip install "mcp[cli]" httpx
pip install -e .
```

### Install with uv (recommended)

```bash
uv add "mcp[cli]" httpx
```

---

## Configuration

Set credentials via environment variables before starting the server:

| Variable | Description |
|---|---|
| `LOVDATA_API_KEY` | Your Lovdata API key (takes priority over Basic Auth) |
| `LOVDATA_USERNAME` | Your Lovdata username (used when no API key is set) |
| `LOVDATA_PASSWORD` | Your Lovdata password |

---

## Usage

### Run with stdio transport (Claude Desktop / standard MCP clients)

```bash
python -m lovdata_mcp
# or
lovdata-mcp
```

### Run with HTTP transport

```bash
python -m lovdata_mcp.server --transport streamable-http
```

The HTTP server starts on `http://127.0.0.1:8000/mcp` by default.

---

## Claude Desktop configuration

Add the following to your Claude Desktop `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "lovdata": {
      "command": "python",
      "args": ["-m", "lovdata_mcp"],
      "env": {
        "LOVDATA_API_KEY": "<your-api-key>"
      }
    }
  }
}
```

---

## Example interactions

Once connected, you can ask Claude questions such as:

- *"Search for Norwegian laws related to employment."*
- *"What does document LOV-2005-06-17-90 say?"*
- *"Find recent Supreme Court decisions (avgjørelser) about contract law."*
- *"List the publicly available Lovdata datasets."*
- *"Download the current laws dataset."*

---

## Public datasets (no authentication required)

The following datasets are freely available under the
[NLOD 2.0](https://data.norge.no/nlod/en/2.0) open license:

| Dataset key | Description |
|---|---|
| `gjeldende-lover` | Current laws |
| `gjeldende-sentrale-forskrifter` | Current central regulations |
| `gjeldende-lokale-forskrifter` | Current local regulations |
| `gjeldende-traktater` | Current treaties |
| `gjeldende-andre-sentrale-rettskilder` | Other current central legal sources |

Download URL format:
```
https://api.lovdata.no/v1/publicData/get/<dataset-key>.tar.bz2
```

---

## Development

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest tests/ -v
```

---

## Resources

- [Lovdata API documentation](https://api.lovdata.no/om-api-tjenesten/)
- [Lovdata court decisions register](https://lovdata.no/register/avgjørelser)
- [Model Context Protocol specification](https://modelcontextprotocol.io/specification/latest)
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)
