import os
import logging
from typing import Optional
import subprocess
from mcp.server.fastmcp import FastMCP
import sys
import shlex
from datetime import datetime

try:
    from importlib.metadata import version, PackageNotFoundError
except ImportError:
    from importlib_metadata import version, PackageNotFoundError  # for Python <3.8

def get_version():
    try:
        return version("gemini-cli-mcp")
    except PackageNotFoundError:
        return "unknown"

def print_help():
    print("""Usage: gemini-cli-mcp [options]\n\nOptions:\n  --version, -V    Show version information\n  --verbose, -v    Enable debug mode (set DEBUG=true)\n  --help, -h       Show this help message\n""")

def print_version_and_exit():
    print(f"gemini-cli-mcp version: {get_version()}")
    try:
        result = subprocess.run(["gemini", "--version"], check=True, capture_output=True, text=True)
        gemini_version = result.stdout.strip()
        if gemini_version:
            print(f"gemini version: {gemini_version}")
    except Exception:
        pass
    sys.exit(0)

# Parse CLI options
args = sys.argv[1:]
if "--help" in args or "-h" in args:
    print_help()
    sys.exit(0)
if "--version" in args or "-V" in args:
    print_version_and_exit()
if "--verbose" in args or "-v" in args:
    os.environ["DEBUG"] = "true"

# Setup logging based on DEBUG env
DEBUG = os.environ.get("DEBUG", "false").lower() == "true"

if DEBUG:
    log_dir = os.path.join(os.path.dirname(__file__), "log")
    os.makedirs(log_dir, exist_ok=True)
    log_path = os.path.join(log_dir, f"{datetime.now().strftime('%Y-%m-%d')}.log")
    logging.basicConfig(
        level=logging.DEBUG,
        format="[%(asctime)s] %(levelname)s %(message)s",
        filename=log_path,
        filemode="a"
    )
else:
    logging.basicConfig(level=logging.CRITICAL)  # Suppress all logs
    logging.disable(logging.CRITICAL)

logger = logging.getLogger("gemini-cli-mcp")

# Set environment variables and default values
QUERY_TIMEOUT = int(os.environ.get("QUERY_TIMEOUT", 300))
GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")
GEMINI_ALL_FILES = os.environ.get("GEMINI_ALL_FILES", "true").lower() == "true"
GEMINI_SANDBOX = os.environ.get("GEMINI_SANDBOX", "true").lower() == "true"
# Only allow --model, --prompt, --all_files, and --sandbox
# GEMINI_API_KEY is used internally by the gemini CLI, so it is only passed as an environment variable

USE_SHELL = os.environ.get("USE_SHELL", "false").lower() == "true"

mcp = FastMCP("gemini-cli-mcp")

def extra_flags() -> list[str]:
    flags = []
    if GEMINI_MODEL:
        flags.extend(["--model", GEMINI_MODEL])
    if GEMINI_ALL_FILES:
        flags.extend(["--all-files"])  # Use the correct flag
    if GEMINI_SANDBOX:
        flags.extend(["--sandbox"])
    return flags

def process_gemini_output(output: str) -> str:
    lines = output.splitlines()
    filtered_lines = [
        line for line in lines 
        if "Loaded cached credentials." not in line.strip() and 
        not line.strip().startswith("[DEBUG]") and 
        "Flushing log events to Clearcut." not in line.strip()
    ]
    return "\n".join(filtered_lines).strip()

def run_gemini_command(prompt: str, extra: list[str] = None, yolo: bool = False) -> dict:
    # Determine the effective project root from environment variable
    effective_project_root = os.environ.get("PROJECT_ROOT")

    # Verify gemini executable is in PATH
    try:
        subprocess.run(["which", "gemini"], check=True, capture_output=True)
    except FileNotFoundError:
        logger.error("gemini executable not found in PATH. Please ensure gemini-cli is installed and in your system's PATH.")
        return {"stdout": "", "stderr": "Error: gemini executable not found in PATH", "returncode": -1}
    except subprocess.CalledProcessError as e:
        logger.error(f"Error checking gemini executable: {e.stderr.decode().strip()}")
        return {"stdout": "", "stderr": f"Error: Could not verify gemini executable: {e.stderr.decode().strip()}", "returncode": -1}

    cmd = ["gemini"]
    cmd.extend(extra_flags())
    if extra:
        cmd.extend(extra)
    if yolo:
        cmd.extend(["--yolo"])
    if prompt:
        if USE_SHELL:
            # For shell=True, wrap in double quotes and escape
            safe_prompt = prompt.replace('"', '\\"').replace('`', '\\`').replace('$', '\\$').replace('\n', '\\n').replace('\r', '')
            cmd.extend(["--prompt", f'"{safe_prompt}"'])
        else:
            # For shell=False, just escape newlines and carriage returns
            safe_prompt = prompt.replace('\n', ' ').replace('\r', '')
            cmd.extend(["--prompt", safe_prompt])

    full_env = os.environ.copy()
    # If GEMINI_API_KEY is set, pass it to the subprocess. Otherwise, rely on gemini-cli's default credential loading.
    if "GEMINI_API_KEY" in os.environ:
        full_env["GEMINI_API_KEY"] = os.environ["GEMINI_API_KEY"]
    full_env["PYTHONUNBUFFERED"] = "1"
    full_env["LC_ALL"] = "C.UTF-8"
    full_env["LANG"] = "C.UTF-8"
    full_env["HOME"] = os.environ.get("HOME", "/tmp")
    full_env["TERM"] = os.environ.get("TERM", "xterm-256color")
    full_env["COLORTERM"] = os.environ.get("COLORTERM", "truecolor")
    full_env["NODE_OPTIONS"] = "--no-warnings"
    logger.debug(f"DEBUG: {DEBUG}")
    
    if DEBUG:
        logger.debug(f"USE_SHELL: {USE_SHELL}")
        logger.debug(f"Running command: {' '.join(cmd)}")
        logger.debug(f"Environment variables: {full_env}")
        logger.debug("Processes before gemini command:")
        try:
            ps_before = subprocess.run(["ps", "aux"], capture_output=True, text=True, check=True)
            logger.debug(ps_before.stdout)
        except Exception as e:
            logger.debug(f"Could not run ps before: {e}")

    try:
        if USE_SHELL:
            if project_root and not os.path.isdir(project_root):
                logger.error(f"Invalid project_root directory: {project_root}")
                return {"stdout": "", "stderr": f"Error: Invalid project_root directory: {project_root}", "returncode": -1}
            result = subprocess.run(
                ' '.join(cmd),
                capture_output=True,
                text=True,
                env=full_env,
                timeout=QUERY_TIMEOUT,
                shell=True,
                cwd=effective_project_root
            )
        else:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                env=full_env,
                timeout=QUERY_TIMEOUT,
                shell=False,
                cwd=effective_project_root
            )
        if DEBUG:
            logger.debug(f"stdout: {result.stdout}")
            logger.debug(f"stderr: {result.stderr}")
            logger.debug(f"returncode: {result.returncode}")
        return {
            "stdout": process_gemini_output(result.stdout),
            "stderr": result.stderr.strip(),
            "returncode": result.returncode
        }
    except subprocess.TimeoutExpired:
        logger.error(f"Command timed out after {QUERY_TIMEOUT}s: {' '.join(cmd)}")
        return {"stdout": "", "stderr": f"Error: Command timed out after {QUERY_TIMEOUT}s", "returncode": -1}
    except subprocess.CalledProcessError as e:
        logger.error(f"Command failed with error: {e.stderr}")
        return {"stdout": "", "stderr": e.stderr.strip(), "returncode": e.returncode}
    except Exception as e:
        logger.error(f"Error running command: {e}")
        return {"stdout": "", "stderr": f"Error: {str(e)}", "returncode": -1}
    finally:
        if DEBUG:
            logger.debug("Processes after gemini command:")
            try:
                ps_after = subprocess.run(["ps", "aux"], capture_output=True, text=True, check=True)
                logger.debug(ps_after.stdout)
            except Exception as e:
                logger.debug(f"Could not run ps after: {e}")

@mcp.tool()
def gemini_ask(question: str) -> dict:
    """Ask a simple question to the Gemini model."""
    return run_gemini_command(question)

@mcp.tool()
def gemini_agent(prompt: str) -> dict:
    """Run a complex prompt with Gemini Agent in auto-execution (--yolo) mode."""
    return run_gemini_command(prompt, yolo=True)

# @mcp.tool()
def gemini_git_diff(diff_args: Optional[str] = None) -> dict:
    """Summarize code changes using Gemini AI."""
    prompt = "Summarize the code changes."
    if diff_args:
        prompt += f" Use git diff arguments: '{diff_args}'."
    return run_gemini_command(prompt)
    
# @mcp.tool()
def gemini_git_commit(branch_name: Optional[str] = None) -> dict:
    """Generate a conventional commit message from staged changes and perform a git commit."""
    prompt = "Generate a conventional commit message for the current staged changes and commit them."
    if branch_name:
        prompt += f" Use the branch '{branch_name}'."
    return run_gemini_command(prompt)

# @mcp.tool()
def gemini_git_pr(commit_message: Optional[str] = None, branch_name: Optional[str] = None, pr_title: Optional[str] = None) -> dict:
    """Automatically commit, push, and create a PR with a conventional commit message."""
    prompt = "Create a pull request with a conventional commit message."
    if commit_message:
        prompt += f" Use this commit message: '{commit_message}'."
    if branch_name:
        prompt += f" Use the branch '{branch_name}'."
    if pr_title:
        prompt += f" PR title: '{pr_title}'."
    return run_gemini_command(prompt)

def main():
    if "--http" in sys.argv:
        mcp.run(transport="streamable-http")
    else:
        mcp.run()

if __name__ == "__main__":
    main()