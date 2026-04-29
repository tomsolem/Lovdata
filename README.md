# Lovdata

Lovdata API & MCP server — exposes the [Lovdata](https://lovdata.no) legal database to AI tools via the [Model Context Protocol](https://modelcontextprotocol.io/).

Built with **Go 1.23+**.

---

## Getting started

### Option 1 – GitHub Codespaces (recommended)

The repository ships with a pre-configured Dev Container so you can start coding immediately without installing anything locally.

1. Click the green **Code** button on the GitHub repository page.
2. Select the **Codespaces** tab.
3. Click **Create codespace on main** (or your branch).
4. GitHub will build the container (first time ~2–3 min) and open VS Code in the browser.
5. The Go toolchain, `gopls`, `golangci-lint`, `goimports`, and all recommended VS Code extensions are installed automatically.

> **Tip:** You can also open the Codespace in your local VS Code by clicking **Open in VS Code Desktop** from the Codespaces menu.

### Option 2 – Local Dev Container (VS Code)

Requirements: [Docker](https://www.docker.com/products/docker-desktop) and the [Dev Containers extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers).

1. Clone the repository:
   ```bash
   git clone https://github.com/tomsolem/Lovdata.git
   cd Lovdata
   ```
2. Open the folder in VS Code.
3. When prompted *"Reopen in Container"*, click **Reopen in Container**.  
   Alternatively, open the Command Palette (`Ctrl/Cmd+Shift+P`) and run **Dev Containers: Reopen in Container**.
4. VS Code will build and start the container automatically.

### Option 3 – Local setup (without Dev Container)

1. Install [Go 1.23+](https://go.dev/dl/).
2. Clone the repository and run:
   ```bash
   go mod tidy
   go build ./...
   go test ./...
   ```

---

## Environment variables

| Variable | Description | Required |
|---|---|---|
| `LOVDATA_API_TOKEN` | Bearer token for the Lovdata API | Yes |

Copy `.env.example` to `.env` and fill in your values (never commit `.env`).

---

## Project structure (planned)

```
.
├── cmd/
│   └── server/        # MCP server entrypoint
├── internal/
│   ├── lovdata/       # Lovdata HTTP client
│   └── tools/         # MCP tool implementations
├── .devcontainer/     # Dev Container configuration
├── .github/
│   └── copilot-instructions.md
└── go.mod
```

---

## Copilot instructions

Suggested GitHub Copilot behaviour for this project is defined in [`.github/copilot-instructions.md`](.github/copilot-instructions.md).  
GitHub Copilot picks these up automatically when working inside the repository.

---

## License

MIT – see [LICENSE](LICENSE).
