# tavily_server.py
# This script implements a Model Context Protocol (MCP) server for the Tavily Search API.
# It uses the Flask web framework to create endpoints that an AI agent can call to perform searches.
# The server is designed with the principles of atomicity and clarity, providing distinct tools for specific search tasks.

# --- Core Imports ---
import os       # Used to securely access environment variables (like the API key).
import json     # Used for handling JSON data, though Flask handles most of it automatically.
from flask import Flask, request, jsonify  # Core components of the Flask framework.
                                           # Flask: The main application object.
                                           # request: Represents the incoming HTTP request.
                                           # jsonify: Converts Python dictionaries to JSON responses.
import requests # Used to make HTTP requests to the external Tavily API.


# --- Flask App Initialization ---
# This creates an instance of the Flask application.
# `__name__` is a special Python variable that gets the name of the current module.
app = Flask(__name__)


# --- Tool Definition ---
# This dictionary acts as a manifest or a "vocabulary" for the AI agent.
# It clearly defines every tool the server offers, its purpose, and the Python function that executes it.
# The "description" is critical, as it's what the AI uses to decide which tool to use for a given task.
tools = {
    # Tool #1: Standard Search
    "search": {
        "description": "Performs a standard, fast search using the Tavily AI search engine. Best for general queries and recent events.",
        "function": "tavily_search"  # Maps this tool to the tavily_search() Python function.
    },
    # Tool #2: Deep Search
    "deep_search": {
        "description": "Performs a comprehensive, in-depth search using the Tavily AI search engine. Slower but more thorough. Use for research or complex topics.",
        "function": "tavily_deep_search" # Maps to the tavily_deep_search() function.
    },
    # Tool #3: Get Direct Answer
    "get_direct_answer": {
        "description": "Searches for a direct, conversational answer to a user's question. Use this when the user asks a direct question like 'What is...?' or 'How do I...?'.",
        "function": "tavily_get_direct_answer" # Maps to the tavily_get_direct_answer() function.
    },
    # Tool #4: Domain-Specific Search
    "search_specific_domains": {
        "description": "Performs a search focused only on a specific list of domains. Provide the query and a list of websites to search within.",
        "function": "tavily_search_specific_domains" # Maps to the tavily_search_specific_domains() function.
    }
}


# --- Tool Implementation ---
# This section contains the actual Python functions that perform the work for each tool.

def _tavily_base_search(payload: dict):
    """
    A private base function to handle all communications with the Tavily API.
    This avoids code duplication by centralizing API key handling, request sending, and error management.

    Args:
        payload: A dictionary containing the specific parameters for the Tavily API call.

    Returns:
        A dictionary with the API response or an error message.
    """
    # Security: Retrieve the API key from environment variables. This prevents hardcoding secrets in the code.
    api_key = os.environ.get("TAVILY_API_KEY")
    if not api_key:
        # Robustness: Gracefully handle the case where the API key is not configured.
        return {"error": "TAVILY_API_KEY environment variable not set."}

    # Add the API key to the payload for every request.
    payload["api_key"] = api_key
    
    # The official Tavily API endpoint for searching.
    url = "https://api.tavily.com/search"

    try:
        # Make the POST request to the Tavily API with the JSON payload.
        response = requests.post(url, json=payload)
        # Raise an exception for HTTP error codes (e.g., 401 Unauthorized, 429 Rate Limit, 500 Server Error).
        response.raise_for_status()
        # If the request was successful, return the JSON response from the API.
        return response.json()
    except requests.exceptions.RequestException as e:
        # Robustness: Catch any network or HTTP errors and return a clear error message.
        return {"error": f"API request failed: {str(e)}"}

# --- Public-Facing Tool Functions ---

def tavily_search(query: str):
    """Executes a standard Tavily search by setting 'search_depth' to 'basic'."""
    payload = {"query": query, "search_depth": "basic", "max_results": 5}
    return _tavily_base_search(payload)

def tavily_deep_search(query: str):
    """Executes a deep Tavily search by setting 'search_depth' to 'advanced'."""
    payload = {"query": query, "search_depth": "advanced", "max_results": 8}
    return _tavily_base_search(payload)

def tavily_get_direct_answer(query: str):
    """Gets a direct answer by setting 'include_answer' to True."""
    payload = {"query": query, "include_answer": True}
    return _tavily_base_search(payload)

def tavily_search_specific_domains(query: str, domains: list):
    """Restricts a search to a list of domains via the 'include_domains' parameter."""
    payload = {"query": query, "include_domains": domains, "max_results": 5}
    return _tavily_base_search(payload)


# --- MCP Server Endpoints ---
# This section defines the web routes (URLs) that the Flask server will respond to.

@app.route('/.well-known/ai-plugin.json', methods=['GET'])
def get_plugin_info():
    """
    Provides a standard metadata file for AI plugins (like ChatGPT Plugins).
    It describes what the server does in a machine-readable format.
    """
    return jsonify({
        "schema_version": "v1",
        "name_for_human": "Tavily Search MCP",
        "name_for_model": "tavily_search",
        "description_for_human": "Server for interacting with the Tavily Search API.",
        "description_for_model": "This server provides tools to search the web using the Tavily AI search engine. Use it to find current information.",
        "api": {
            "type": "open_api",
            "url": "/openapi.yaml" # Points to an OpenAPI spec (optional for this server).
        }
    })

@app.route('/tools', methods=['POST'])
def handle_tool_call():
    """
    This is the main endpoint for the AI agent. It receives a request to execute a tool,
    calls the appropriate Python function, and returns the result.
    """
    # Get the JSON data sent by the AI agent.
    data = request.get_json()
    tool_name = data.get('tool')
    params = data.get('params', {}) # Parameters for the function call.

    # Validate that the requested tool exists in our `tools` dictionary.
    if tool_name not in tools:
        return jsonify({"error": f"Tool '{tool_name}' not found."}), 404

    # Dynamically find the correct Python function to call based on the tool name.
    function_name = tools[tool_name]['function']
    function_to_call = globals().get(function_name)

    # Ensure the function actually exists in the code.
    if not function_to_call:
        return jsonify({"error": f"Function implementation for '{tool_name}' not found."}), 500

    try:
        # The core of the dynamic dispatch: call the found function with the provided parameters.
        # The `**params` syntax unpacks the dictionary of parameters into keyword arguments.
        result = function_to_call(**params)
        return jsonify(result)
    except TypeError as e:
        # Handle cases where the AI provides incorrect parameters (e.g., wrong name or type).
        return jsonify({"error": f"Invalid parameters for tool '{tool_name}': {e}"}), 400


# --- Main Execution Block ---
# This standard Python construct ensures that the Flask development server runs only when the script
# is executed directly (e.g., `python tavily_server.py`), not when it's imported as a module.
if __name__ == '__main__':
    # Starts the Flask development server.
    # port=3434: Specifies the port number.
    # debug=True: Enables debug mode, which provides detailed error pages and auto-reloads the server on code changes.
    app.run(port=3434, debug=True)
