# Tavily Search MCP Server

This project is a Model Context Protocol (MCP) server for the **Tavily AI Search Engine**. It acts as a bridge between a Large Language Model (LLM) or AI agent and the Tavily API, providing a set of clear, atomic tools for performing advanced web searches.

The server is built with Python and Flask, following the development philosophy outlined in the Klavis AI contributor guidelines.

## 📜 Features & Available Tools

This server exposes the core functionality of the Tavily API through four distinct, atomic tools:

* **`search`**: Performs a standard, fast search. Ideal for general-purpose queries, fact-checking, or finding information on recent events.
* **`deep_search`**: Conducts a more comprehensive, in-depth search that is slower but returns more thorough results. This is best suited for research tasks or complex topics that require detailed information.
* **`get_direct_answer`**: Searches for and returns a direct, conversational answer to a specific question. This tool is most effective when the user asks a direct question (e.g., "What is the capital of France?").
* **`search_specific_domains`**: Restricts a search to a predefined list of websites. This is useful for finding information within trusted or specific sources (e.g., searching only on `wikipedia.org` and `reuters.com`).

## ⚙️ Setup and Installation

Follow these steps to get the server running on your local machine.

### 1. Prerequisites

* You must have **Python 3.7+** and `pip` installed on your system.
* You will need a **Tavily API Key**.

### 2. Clone the Repository

First, clone the repository containing this project to your local machine.

```bash
# This is a placeholder; you would clone the main Klavis AI repo
git clone [https://github.com/Klavis-Al/klavis.git](https://github.com/Klavis-Al/klavis.git)
cd path/to/this/server
```

✅ Testing the Tools
You can test each tool to confirm the server is working correctly. Use a tool like curl to send POST requests to the /tools endpoint. Make sure the server is running in another terminal window.
Test search
```bash
curl -X POST http://127.0.0.1:3434/tools -H "Content-Type: application/json" -d '{"tool": "search", "params": {"query": "latest news on generative AI"}}'
```

Test deep_search
```bash
curl -X POST http://127.0.0.1:3434/tools -H "Content-Type: application/json" -d '{"tool": "deep_search", "params": {"query": "Explain the technical details of Retrieval-Augmented Generation"}}'
```

Test get_direct_answer
```bash
curl -X POST http://127.0.0.1:3434/tools -H "Content-Type: application/json" -d '{"tool": "get_direct_answer", "params": {"query": "How does photosynthesis work?"}}'
```

Test search_specific_domains
```bash
curl -X POST http://127.0.0.1:3434/tools -H "Content-Type: application/json" -d '{"tool": "search_specific_domains", "params": {"query": "open source models", "domains": ["github.com", "huggingface.co"]}}'
```