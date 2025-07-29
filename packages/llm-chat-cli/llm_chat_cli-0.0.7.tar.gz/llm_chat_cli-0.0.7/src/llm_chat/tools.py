"""
Tool implementations for LLM CLI including web search and terminal execution
"""

import subprocess
import requests
from typing import List, Dict, Any
from termcolor import colored
from rich.console import Console
from rich.markdown import Markdown

# Constants for web search
DEFAULT_SEARCH_COUNT = 5
SERPER_API_URL = "https://google.serper.dev/search"


def execute_terminal_command(
    command: str, capture_output: bool = True
) -> Dict[str, Any]:
    """
    Execute a terminal command and return its output.

    Args:
        command (str): The command to execute
        capture_output (bool): Whether to capture and return the output

    Returns:
        dict: A dictionary containing success status, stdout, stderr, and return code
    """
    try:
        # Print command being executed
        print(colored(f"\nExecuting: {command}", "cyan"))
        print("-" * 70)

        # Execute the command
        if capture_output:
            result = subprocess.run(command, shell=True, text=True, capture_output=True)
            stdout = result.stdout
            stderr = result.stderr
            return_code = result.returncode
        else:
            # If not capturing output, let it stream to the terminal
            return_code = subprocess.call(command, shell=True)
            stdout = None
            stderr = None

        # Create result dictionary
        success = return_code == 0
        result_data = {
            "success": success,
            "stdout": stdout,
            "stderr": stderr,
            "return_code": return_code,
        }

        # Display results nicely
        display_command_results(result_data)

        return result_data

    except Exception as e:
        error_data = {
            "success": False,
            "error": str(e),
            "stdout": None,
            "stderr": None,
            "return_code": -1,
        }
        display_command_results(error_data)
        return error_data


def display_command_results(result: Dict[str, Any]) -> None:
    """
    Display command execution results in a formatted way.

    Args:
        result (dict): Command execution result dictionary
    """
    console = Console()
    print("-" * 70)

    # Check if there was an error
    if "error" in result and result["error"]:
        print(colored(f"Error: {result['error']}", "red"))
        return

    # Display success/failure status
    status = "Success" if result["success"] else "Failed"
    status_color = "green" if result["success"] else "red"
    print(
        colored(f"Command {status} (exit code: {result['return_code']})", status_color)
    )

    # Display stdout if available
    if result["stdout"]:
        stdout = result["stdout"].strip()
        if stdout:
            print(colored("\nOutput:", "green"))
            console.print(Markdown(f"```\n{stdout}\n```"))

    # Display stderr if available
    if result["stderr"]:
        stderr = result["stderr"].strip()
        if stderr:
            print(colored("\nError Output:", "yellow"))
            console.print(Markdown(f"```\n{stderr}\n```"))


def web_search(
    query: str, api_key: str, result_count: int = DEFAULT_SEARCH_COUNT
) -> List[Dict[str, Any]]:
    """
    Perform a web search using the Serper API.

    Args:
        query (str): The search query
        api_key (str): The Serper API key
        result_count (int): Number of results to return

    Returns:
        list: A list of search result dictionaries
    """
    if not api_key:
        print(
            colored(
                "Error: No Serper API key provided. Run 'lmci setup' to configure.",
                "red",
            )
        )
        return []

    headers = {"X-API-KEY": api_key, "Content-Type": "application/json"}

    payload = {"q": query, "num": result_count}

    try:
        print(colored(f"\nSearching the web for: {query}", "cyan"))
        response = requests.post(SERPER_API_URL, headers=headers, json=payload)
        response.raise_for_status()  # Raise exception for non-200 status codes

        results = response.json()

        # Extract the organic search results
        organic_results = results.get("organic", [])

        # Transform results into a more usable format
        transformed_results = []
        for result in organic_results:
            transformed_results.append(
                {
                    "title": result.get("title", ""),
                    "link": result.get("link", ""),
                    "snippet": result.get("snippet", ""),
                    "position": result.get("position", 0),
                }
            )

        return transformed_results

    except requests.exceptions.RequestException as e:
        print(colored(f"Error performing web search: {str(e)}", "red"))
        return []


def display_search_results(results: List[Dict[str, Any]]) -> None:
    """
    Display search results in a formatted way.

    Args:
        results (list): List of search result dictionaries
    """
    if not results:
        print(colored("No search results found.", "yellow"))
        return

    console = Console()

    print(colored(f"\nFound {len(results)} results:", "green"))
    print("-" * 70)

    for i, result in enumerate(results, 1):
        title = result.get("title", "No title")
        link = result.get("link", "")
        snippet = result.get("snippet", "No description available")

        # Format and display each result
        console.print(f"[bold cyan]{i}. {title}[/bold cyan]")
        console.print(f"[blue underline]{link}[/blue underline]")
        console.print(f"{snippet}\n")

        if i < len(results):
            print("-" * 70)
