# `gemini-cli-mcp` Python Server

This directory contains the Python implementation of the `gemini-cli-mcp` server. It uses FastAPI to expose `gemini-cli` functionalities as MCP-compliant tools.

## 1. Features

This server exposes the following `gemini-cli` commands as MCP Tools:

*   `gemini_ask`: Ask a question to the Gemini model.
*   `gemini_yolo`: Run a complex prompt with Gemini Agent in auto-execution (`--yolo`) mode.
*   `gemini_git_commit`: Generate a conventional commit message from staged changes and perform a `git commit`.
*   `gemini_git_pr`: Automatically commit, push, and create a Pull Request.
*   `gemini_git_diff`: Summarize code changes using Gemini AI.

## 2. Technology Stack

| Category         | Technology           |
| :--------------- | :------------------- |
| **Language**     | Python 3.12+         |
| **Web Framework**| FastAPI              |
| **Process Exec** | `asyncio.subprocess` |
| **CLI Framework**| Typer (via `mcp-cli`)|
| **Packaging**    | Poetry / `pyproject.toml` |

## 3. Setup

### Prerequisites

*   Python 3.12 or higher.
*   `gemini-cli` installed globally and accessible in your system's PATH.
*   `git` installed and configured.

### Installation

1.  Navigate to the `server_py` directory:
    ```bash
    cd server_py
    ```
2.  Install dependencies using `uv` (recommended) or `pip`:
    ```bash
    uv pip install -r requirements.txt
    # or
    pip install -r requirements.txt
    ```

### Environment Variables

The server uses environment variables for configuration. You can set these in a `.env` file in the project root (`/path/to/project_root/.env`) or directly in your environment.

*   `GEMINI_MODEL`: Specifies the Gemini model to use (e.g., `gemini-2.5-flash`).
*   `GEMINI_ALL_FILES`: Set to `true` to include all files in context (`--all-files`).
*   `GEMINI_SANDBOX`: Set to `true` to enable sandbox mode (`--sandbox`).
*   `GEMINI_API_KEY`: Your Gemini API key (required for Docker/server environments).
*   `PROJECT_ROOT`: The root directory of your project (important for `gemini-cli` operations).
*   `QUERY_TIMEOUT`: Timeout for `gemini-cli` commands in seconds.
*   `USE_SHELL`: Set to `true` to execute `gemini-cli` commands via shell (defaults to `false`).
*   `DEBUG`: Set to `true` to enable detailed logging to `log/{date}.log`.

## 4. Running the Server

The user can select the execution mode via a CLI flag.

*   **STDIO Mode**: `python main.py` (for direct CLI interaction)
*   **HTTP Mode**: `uvicorn main:app --host 0.0.0.0 --port 8000` (for AI agent integration)

### Docker

A `Dockerfile` is provided to build and run the server in a container.

1.  **Build the Image:** From the project root, run:
    ```bash
    docker build -t gemini-cli-mcp-python -f server_py/Dockerfile .
    ```

2.  **Run the Container:**
    ```bash
    # Using an .env file
    docker run --env-file ../.env -p 8000:8000 gemini-cli-mcp-python

    # Passing environment variables directly
    docker run -e GEMINI_API_KEY=your_api_key -p 8000:8000 gemini-cli-mcp-python
    ```

## 5. Packaging & Distribution

The package will be distributed on PyPI. The `pyproject.toml` file defines a script entry point for the `gemini-cli-mcp` command, which will be deployed using `poetry build` and `twine`.

### CLI Usage

After installing the package via pip, you can use the CLI entry point:

```bash
$ gemini-cli-mcp
```

This will launch the server in STDIO mode. To run in HTTP mode, use:

```bash
$ gemini-cli-mcp --http
```

## 6. Tool Usage

The server acts as a smart wrapper around `gemini-cli`. It constructs and executes the appropriate `gemini-cli` command based on the MCP tool invocation.

For example:
*   `gemini_ask(question="What is AI?")` translates to `gemini ask --model {model} --all-files --sandbox --prompt "What is AI?"`
*   `gemini_yolo(prompt="Do something complex.")` translates to `gemini agent --model {model} --all-files --sandbox --yolo --prompt "Do something complex."`

## 7. Logging

Set the `DEBUG` environment variable to `true` to enable detailed logging to `server_py/log/{YYYY-MM-DD}.log`.

## 8. MCP Client Integration Guide

The `gemini-cli-mcp` server supports both HTTP and STDIO modes. Below are instructions and configuration examples for integrating as an external MCP server in clients like Cursor, Windsurf, and Claude Code.

### 8.1 Integration via HTTP Mode

1. **Start the server**
   ```bash
   gemini-cli-mcp --http
   # or
   uvicorn main:app --host 0.0.0.0 --port 8000
   ```
   - Default port is `8000`.
   - Use `--host 0.0.0.0` for remote access.

2. **Register the MCP server in your client**
   - MCP server URL: `http://localhost:8000` (or your server's IP)

#### Cursor, Windsurf Example
```json
// cursor: $HOME/.cursor/mcp.json
// windwurf: $HOME/.codeium/windsurf/mcp_config.json
```json
{
  "mcpServers": {
    "gemini-cli-mcp": {
      "url": "http://localhost:8000"
    }
  }
}
```

---

### 8.2 Integration via STDIO Mode

1. **No need to start the server manually**
   - The MCP client will launch the process and communicate via STDIO.
   - Just register the following configuration.

#### Cursor, Windsurf Example
```json
// cursor: $HOME/.cursor/mcp.json
// windwurf: $HOME/.codeium/windsurf/mcp_config.json
{
  "mcpServers": {
    "gemini-cli-mcp": {
      "type": "stdio",
      "command": "uv",
      "args": [
        "--directory",
        "/path/to/project_root/server_py/main.py"
        "run",
        "main.py"
      ],
      "env": {
        "GEMINI_MODEL": "gemini-2.5-flash",
        "PROJECT_ROOT": "/path/to/project_root"
      }
    }
  }
}
```

#### Claude Code Example
```json
// Settings > Developer > Edit Config > claude_desktop_config.json
// find command location with `which gemini-cli-mcp`
// MUST provide a Gemini API key to use with Claude Desktop
{
  "mcpServers": {
    "gemini-cli-mcp": {
      "command": "uv",
      "args": [
        "--directory",
        "/path/to/project_root/server_py/main.py"
        "run",
        "main.py"
      ],
      "env": {
        "GEMINI_API_KEY": "your_api_key",
        "GEMINI_MODEL": "gemini-2.5-flash",
        "PROJECT_ROOT": "/path/to/project_root"
      }
    }
  }
}
```

---

### 8.3 Integration via pip install

1. Install package

```
pip install gemini-cli-mcp
```

2. Register the MCP server in your client

#### Cursor, Windsurf Example
```json
{
  "mcpServers": {
    "gemini-cli-mcp": {
      "type": "stdio",
      "command": "gemini-cli-mcp",
      "args": [],
      "env": {
        "GEMINI_MODEL": "gemini-2.5-flash",
        "PROJECT_ROOT": "/path/to/project_root"
      }
    }
  }
}
```

#### Claude Code Example
```json
{
  "mcpServers": {
    "gemini-cli-mcp": {
      "command": "gemini-cli-mcp",
      "args": [],
      "env": {
        "GEMINI_API_KEY": "your_api_key",
        "GEMINI_MODEL": "gemini-2.5-flash",
        "PROJECT_ROOT": "/path/to/project_root"
      }
    }
  }
}
```

---

> **Notes:**
> - HTTP mode allows multiple clients to connect over the network.
> - STDIO mode launches a separate process per client.
> - Adjust environment variables (`env`) as needed for your use case.
> - If the server and client are on different machines, ensure firewall/port forwarding is configured appropriately.