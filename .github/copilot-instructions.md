# GitHub Copilot Instructions

## Project context

This repository implements a **Model Context Protocol (MCP) server** that exposes the [Lovdata](https://lovdata.no) legal API to AI tools (e.g. GitHub Copilot, Claude, ChatGPT).  
The implementation language is **Go (1.23+)**.

## Coding guidelines

- Follow standard Go idioms: `gofmt`/`goimports` formatting, effective Go style, and the [Uber Go Style Guide](https://github.com/uber-go/guide/blob/master/style.md).
- Keep packages small and focused; prefer multiple small packages over one large one.
- Return errors explicitly – never panic in library code.
- Write table-driven tests using the standard `testing` package.
- Use context propagation (`context.Context`) for all I/O operations.
- Prefer interfaces over concrete types in function signatures to make code testable.

## MCP-specific conventions

- All MCP tools must be registered in `cmd/server/main.go` (or the equivalent entrypoint).
- Each tool should live in its own file under `internal/tools/`.
- Tool names follow the pattern `lovdata_<action>` (e.g. `lovdata_search`, `lovdata_get_document`).
- Tool descriptions must be concise and written in English so that AI assistants can understand them.
- Input/output schemas are defined using `encoding/json` struct tags; keep them flat where possible.

## Lovdata API

- Base URL: `https://api.lovdata.no/` (see official docs for endpoints).
- Authentication: Bearer token passed via `LOVDATA_API_TOKEN` environment variable.
- Always handle HTTP 429 (rate-limit) with exponential back-off.
- Never log or expose the API token.

## What to suggest

- When asked to add a new MCP tool, scaffold the file under `internal/tools/` with proper struct, `Execute` method, and tests.
- When asked to handle a new Lovdata endpoint, add a typed client method in `internal/lovdata/client.go`.
- Suggest `//nolint` directives only when the lint warning is a confirmed false positive – always add a reason comment.

## What to avoid

- Do **not** add `vendor/` directory commits; use Go modules (`go.mod`/`go.sum`).
- Do **not** store secrets or credentials in source code.
- Do **not** use `os.Exit` outside of `main`.
