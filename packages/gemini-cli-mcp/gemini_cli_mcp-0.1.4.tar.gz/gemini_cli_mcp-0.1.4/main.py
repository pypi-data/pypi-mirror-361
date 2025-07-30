import os
import sys
import subprocess
from importlib.metadata import version, PackageNotFoundError

from .core.services import GeminiToolService
from .infrastructure.command_runner import SubprocessGeminiCommandRunner
from .infrastructure.logging_config import setup_logging
from .presentation.mcp_server import create_mcp_server

def get_cli_version():
    try:
        return version("gemini-cli-mcp")
    except PackageNotFoundError:
        return "unknown"

def print_version_and_exit():
    print(f"gemini-cli-mcp version: {get_cli_version()}")
    try:
        result = subprocess.run(["gemini", "--version"], check=True, capture_output=True, text=True)
        print(f"gemini version: {result.stdout.strip()}")
    except Exception:
        pass
    sys.exit(0)

def main():
    """
    Main entry point for the application.
    Initializes dependencies, sets up the server, and starts it.
    """
    if "--version" in sys.argv or "-V" in sys.argv:
        print_version_and_exit()

    if "--verbose" in sys.argv or "-v" in sys.argv:
        os.environ["DEBUG"] = "true"

    setup_logging()

    config = {
        "GEMINI_MODEL": os.environ.get("GEMINI_MODEL", "gemini-2.5-flash"),
        "GEMINI_ALL_FILES": os.environ.get("GEMINI_ALL_FILES", "true").lower() == "true",
        "GEMINI_SANDBOX": os.environ.get("GEMINI_SANDBOX", "true").lower() == "true",
        "GEMINI_API_KEY": os.environ.get("GEMINI_API_KEY"),
        "PROJECT_ROOT": os.environ.get("PROJECT_ROOT"),
        "QUERY_TIMEOUT": int(os.environ.get("QUERY_TIMEOUT", 300)),
        "USE_SHELL": os.environ.get("USE_SHELL", "false").lower() == "true",
    }

    command_runner = SubprocessGeminiCommandRunner(config)
    tool_service = GeminiToolService(command_runner)
    mcp_server = create_mcp_server(tool_service)

    if "--http" in sys.argv:
        mcp_server.run(transport="streamable-http")
    else:
        mcp_server.run()

if __name__ == "__main__":
    main()
