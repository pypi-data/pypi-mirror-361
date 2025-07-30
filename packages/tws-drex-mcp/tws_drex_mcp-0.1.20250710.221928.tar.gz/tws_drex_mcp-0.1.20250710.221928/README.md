# TWS DREX MCP Server

This MCP server provides tools to interact with the DREX document extraction AI API and LoginRadius authentication.

## 🚀 Get Started

This guide will help you install and run the TWS DREX MCP server.

We recommend using [uv](https://docs.astral.sh/uv/) to manage your Python environment and run the server.

### Install uv

If you don't have `uv` installed, you can install it by following the instructions on the official documentation: [Installation | uv](https://docs.astral.sh/uv/getting-started/installation/)

A common way to install uv is using curl (for Linux/macOS) or by downloading the executable (for Windows):

```bash
# For Linux/macOS
curl -fsSL https://astral.sh/uv/install.sh | sh
# For Windows
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### Install the TWS DREX MCP Server

Once you have `uv` installed, you can install the `tws-drex-mcp` package:

```bash
uv pip install tws-drex-mcp
```

Alternatively, using pip:

```bash
pip install tws-drex-mcp
```

### Run the standalone Server

You can run the installed server using `uv run`:

```bash
uv run -m tws_drex_mcp
# or
# uvx tws-drex-mcp
```

### Claude Desktop Configuration

To use the DREX MCP server with Claude Desktop, you need to add it to your Claude Desktop configuration file. The location of this file varies by operating system.

Here is an example configuration for the TWS DREX MCP server:

```json
{
  "mcpServers": {
    "DREX": {
      "command": "uv",
      "args": ["tws-drex-mcp"],
      "env": {
        "DREX_BASE_URL": "<YOUR_DREX_BASE_URL>",
        "LR_API_KEY": "<YOUR_LR_API_KEY>",
        "LR_API_SECRET": "<YOUR_LR_API_SECRET>"
      },
      "transportType": "stdio"
    }
  }
}
```

Replace `<YOUR_DREX_BASE_URL>`, `<YOUR_LR_API_KEY>`, and `<YOUR_LR_API_SECRET>` with your actual values.

## Configuration

Before using the server's tools, ensure the following environment variables are set:

* `DREX_BASE_URL`: The base URL of the target DREX API instance.
* `LR_API_KEY`: Your LoginRadius API key.
* `LR_API_SECRET`: Your LoginRadius API secret.

The MCP framework will automatically pick up these variables when running the server's tools.

## Functionality

The following tools are provided by the server:

* `get_token`: Obtains an authentication token from LoginRadius using a username and password.
* `file_upload`: Uploads files to the DREX API.
* `get_status`: Retrieves the processing status of a file in the DREX API.
* `get_file_results`: Retrieves the processed results of a file in the DREX API.

## Usage

### `get_token`

This tool obtains an authentication token from LoginRadius using a username and password.

Example:

```json
{
    "username": "your_username",
    "password": "your_password"
}
```

### `file_upload`

This tool uploads files or directories to DREX API. The processing time will take 10 - 80 seconds for each file.

Example:

```json
{
    "file_paths": ["path/to/file1.txt", "path/to/dir"],
    "uploaded_by": "user_name",
    "token": "your_access_token"
}
```

### `get_status`

This tool retrieves the processing status of a file in the DREX API.

Example:

```json
{
    "file_id": "file_id_1",
    "token": "your_access_token"
}
```

### `get_file_results`

This tool retrieves the processed results of a file in the DREX API.

Example:

```json
{
    "file_id": "file_id_1",
    "token": "your_access_token"
  }
```

## LoginRadius Initialization

The LoginRadius SDK is initialized using the `LR_API_KEY` and `LR_API_SECRET` environment variables.

## Dependencies

The dependencies required to run this server are listed in the `pyproject.toml` file.
