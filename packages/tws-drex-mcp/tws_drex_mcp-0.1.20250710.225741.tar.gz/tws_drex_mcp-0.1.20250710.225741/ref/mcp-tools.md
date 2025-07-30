# Title: mcp

URL Source: https://pypi.org/project/mcp/

MCP Python SDK
--------------

Table of Contents
-----------------

* [MCP Python SDK](https://pypi.org/project/mcp/#mcp-python-sdk)
  * [Overview](https://pypi.org/project/mcp/#overview)
  * [Installation](https://pypi.org/project/mcp/#installation)
    * [Adding MCP to your python project](https://pypi.org/project/mcp/#adding-mcp-to-your-python-project)
    * [Running the standalone MCP development tools](https://pypi.org/project/mcp/#running-the-standalone-mcp-development-tools)
  * [Quickstart](https://pypi.org/project/mcp/#quickstart)
  * [What is MCP?](https://pypi.org/project/mcp/#what-is-mcp)
  * [Core Concepts](https://pypi.org/project/mcp/#core-concepts)
    * [Server](https://pypi.org/project/mcp/#server)
    * [Resources](https://pypi.org/project/mcp/#resources)
    * [Tools](https://pypi.org/project/mcp/#tools)
    * [Prompts](https://pypi.org/project/mcp/#prompts)
    * [Images](https://pypi.org/project/mcp/#images)
    * [Context](https://pypi.org/project/mcp/#context)
  * [Running Your Server](https://pypi.org/project/mcp/#running-your-server)
    * [Development Mode](https://pypi.org/project/mcp/#development-mode)
    * [Claude Desktop Integration](https://pypi.org/project/mcp/#claude-desktop-integration)
    * [Direct Execution](https://pypi.org/project/mcp/#direct-execution)
    * [Mounting to an Existing ASGI Server](https://pypi.org/project/mcp/#mounting-to-an-existing-asgi-server)
  * [Examples](https://pypi.org/project/mcp/#examples)
    * [Echo Server](https://pypi.org/project/mcp/#echo-server)
    * [SQLite Explorer](https://pypi.org/project/mcp/#sqlite-explorer)
  * [Advanced Usage](https://pypi.org/project/mcp/#advanced-usage)
    * [Low-Level Server](https://pypi.org/project/mcp/#low-level-server)
    * [Writing MCP Clients](https://pypi.org/project/mcp/#writing-mcp-clients)
    * [MCP Primitives](https://pypi.org/project/mcp/#mcp-primitives)
    * [Server Capabilities](https://pypi.org/project/mcp/#server-capabilities)
  * [Documentation](https://pypi.org/project/mcp/#documentation)
  * [Contributing](https://pypi.org/project/mcp/#contributing)
  * [License](https://pypi.org/project/mcp/#license)

Overview
--------

The Model Context Protocol allows applications to provide context for LLMs in a standardized way, separating the concerns of providing context from the actual LLM interaction. This Python SDK implements the full MCP specification, making it easy to:

* Build MCP clients that can connect to any MCP server
* Create MCP servers that expose resources, prompts and tools
* Use standard transports like stdio and SSE
* Handle all MCP protocol messages and lifecycle events

Installation
------------

### Adding MCP to your python project

We recommend using [uv](https://docs.astral.sh/uv/) to manage your Python projects.

If you haven't created a uv-managed project yet, create one:

uv init mcp-server-demo
cd mcp-server-demo

Then add MCP to your project dependencies:

uv add "mcp\[cli\]"

Alternatively, for projects using pip for dependencies:

pip install "mcp\[cli\]"

### Running the standalone MCP development tools

To run the mcp command with uv:

uv run mcp

Quickstart
----------

Let's create a simple MCP server that exposes a calculator tool and some data:

\# server.py
from mcp.server.fastmcp import FastMCP

\# Create an MCP server
mcp \= FastMCP("Demo")

\# Add an addition tool
@mcp.tool()
def add(a: int, b: int) \-\> int:
    """Add two numbers"""
    return a + b

\# Add a dynamic greeting resource
@mcp.resource("greeting://{name}")
def get\_greeting(name: str) \-\> str:
    """Get a personalized greeting"""
    return f"Hello, {name}!"

You can install this server in [Claude Desktop](https://claude.ai/download) and interact with it right away by running:

mcp install server.py

Alternatively, you can test it with the MCP Inspector:

mcp dev server.py

What is MCP?
------------

The [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) lets you build servers that expose data and functionality to LLM applications in a secure, standardized way. Think of it like a web API, but specifically designed for LLM interactions. MCP servers can:

* Expose data through **Resources** (think of these sort of like GET endpoints; they are used to load information into the LLM's context)
* Provide functionality through **Tools** (sort of like POST endpoints; they are used to execute code or otherwise produce a side effect)
* Define interaction patterns through **Prompts** (reusable templates for LLM interactions)
* And more!

Core Concepts
-------------

### Server

The FastMCP server is your core interface to the MCP protocol. It handles connection management, protocol compliance, and message routing:

\# Add lifespan support for startup/shutdown with strong typing
from contextlib import asynccontextmanager
from collections.abc import AsyncIterator
from dataclasses import dataclass

from fake\_database import Database  \# Replace with your actual DB type

from mcp.server.fastmcp import Context, FastMCP

\# Create a named server
mcp \= FastMCP("My App")

\# Specify dependencies for deployment and development
mcp \= FastMCP("My App", dependencies\=\["pandas", "numpy"\])

@dataclass
class AppContext:
    db: Database

@asynccontextmanager
async def app\_lifespan(server: FastMCP) \-\> AsyncIterator\[AppContext\]:
    """Manage application lifecycle with type-safe context"""
    \# Initialize on startup
    db \= await Database.connect()
    try:
        yield AppContext(db\=db)
    finally:
        \# Cleanup on shutdown
        await db.disconnect()

\# Pass lifespan to server
mcp \= FastMCP("My App", lifespan\=app\_lifespan)

\# Access type-safe lifespan context in tools
@mcp.tool()
def query\_db(ctx: Context) \-\> str:
    """Tool that uses initialized resources"""
    db \= ctx.request\_context.lifespan\_context.db
    return db.query()

### Resources

Resources are how you expose data to LLMs. They're similar to GET endpoints in a REST API - they provide data but shouldn't perform significant computation or have side effects:

from mcp.server.fastmcp import FastMCP

mcp \= FastMCP("My App")

@mcp.resource("config://app")
def get\_config() \-\> str:
    """Static configuration data"""
    return "App configuration here"

@mcp.resource("users://{user\_id}/profile")
def get\_user\_profile(user\_id: str) \-\> str:
    """Dynamic user data"""
    return f"Profile data for user {user\_id}"

### Tools

Tools let LLMs take actions through your server. Unlike resources, tools are expected to perform computation and have side effects:

import httpx
from mcp.server.fastmcp import FastMCP

mcp \= FastMCP("My App")

@mcp.tool()
def calculate\_bmi(weight\_kg: float, height\_m: float) \-\> float:
    """Calculate BMI given weight in kg and height in meters"""
    return weight\_kg / (height\_m\*\*2)

@mcp.tool()
async def fetch\_weather(city: str) \-\> str:
    """Fetch current weather for a city"""
    async with httpx.AsyncClient() as client:
        response \= await client.get(f"https://api.weather.com/{city}")
        return response.text

### Prompts

Prompts are reusable templates that help LLMs interact with your server effectively:

from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp.prompts import base

mcp \= FastMCP("My App")

@mcp.prompt()
def review\_code(code: str) \-\> str:
    return f"Please review this code:\\n\\n{code}"

@mcp.prompt()
def debug\_error(error: str) \-\> list\[base.Message\]:
    return \[
        base.UserMessage("I'm seeing this error:"),
        base.UserMessage(error),
        base.AssistantMessage("I'll help debug that. What have you tried so far?"),
    \]

### Images

FastMCP provides an `Image` class that automatically handles image data:

from mcp.server.fastmcp import FastMCP, Image
from PIL import Image as PILImage

mcp \= FastMCP("My App")

@mcp.tool()
def create\_thumbnail(image\_path: str) \-\> Image:
    """Create a thumbnail from an image"""
    img \= PILImage.open(image\_path)
    img.thumbnail((100, 100))
    return Image(data\=img.tobytes(), format\="png")

### Context

The Context object gives your tools and resources access to MCP capabilities:

from mcp.server.fastmcp import FastMCP, Context

mcp \= FastMCP("My App")

@mcp.tool()
async def long\_task(files: list\[str\], ctx: Context) \-\> str:
    """Process multiple files with progress tracking"""
    for i, file in enumerate(files):
        ctx.info(f"Processing {file}")
        await ctx.report\_progress(i, len(files))
        data, mime\_type \= await ctx.read\_resource(f"file://{file}")
    return "Processing complete"

### Authentication

Authentication can be used by servers that want to expose tools accessing protected resources.

`mcp.server.auth` implements an OAuth 2.0 server interface, which servers can use by providing an implementation of the `OAuthServerProvider` protocol.

```
mcp = FastMCP("My App",
        auth_provider=MyOAuthServerProvider(),
        auth=AuthSettings(
            issuer_url="https://myapp.com",
            revocation_options=RevocationOptions(
                enabled=True,
            ),
            client_registration_options=ClientRegistrationOptions(
                enabled=True,
                valid_scopes=["myscope", "myotherscope"],
                default_scopes=["myscope"],
            ),
            required_scopes=["myscope"],
        ),
)
```

See [OAuthServerProvider](https://pypi.org/project/mcp/mcp/server/auth/provider.py) for more details.

Running Your Server
-------------------

### Development Mode

The fastest way to test and debug your server is with the MCP Inspector:

mcp dev server.py

\# Add dependencies
mcp dev server.py \--with pandas \--with numpy

\# Mount local code
mcp dev server.py \--with-editable .

### Claude Desktop Integration

Once your server is ready, install it in Claude Desktop:

mcp install server.py

\# Custom name
mcp install server.py \--name "My Analytics Server"

\# Environment variables
mcp install server.py \-v API\_KEY\=abc123 \-v DB\_URL\=postgres://...
mcp install server.py \-f .env

### Direct Execution

For advanced scenarios like custom deployments:

from mcp.server.fastmcp import FastMCP

mcp \= FastMCP("My App")

if \_\_name\_\_ \== "\_\_main\_\_":
    mcp.run()

Run it with:

python server.py
\# or
mcp run server.py

### Mounting to an Existing ASGI Server

You can mount the SSE server to an existing ASGI server using the `sse_app` method. This allows you to integrate the SSE server with other ASGI applications.

from starlette.applications import Starlette
from starlette.routing import Mount, Host
from mcp.server.fastmcp import FastMCP

mcp \= FastMCP("My App")

\# Mount the SSE server to the existing ASGI server
app \= Starlette(
    routes\=\[
        Mount('/', app\=mcp.sse\_app()),
    \]
)

\# or dynamically mount as host
app.router.routes.append(Host('mcp.acme.corp', app\=mcp.sse\_app()))

For more information on mounting applications in Starlette, see the [Starlette documentation](https://www.starlette.io/routing/#submounting-routes).

Examples
--------

### Echo Server

A simple server demonstrating resources, tools, and prompts:

from mcp.server.fastmcp import FastMCP

mcp \= FastMCP("Echo")

@mcp.resource("echo://{message}")
def echo\_resource(message: str) \-\> str:
    """Echo a message as a resource"""
    return f"Resource echo: {message}"

@mcp.tool()
def echo\_tool(message: str) \-\> str:
    """Echo a message as a tool"""
    return f"Tool echo: {message}"

@mcp.prompt()
def echo\_prompt(message: str) \-\> str:
    """Create an echo prompt"""
    return f"Please process this message: {message}"

### SQLite Explorer

A more complex example showing database integration:

import sqlite3

from mcp.server.fastmcp import FastMCP

mcp \= FastMCP("SQLite Explorer")

@mcp.resource("schema://main")
def get\_schema() \-\> str:
    """Provide the database schema as a resource"""
    conn \= sqlite3.connect("database.db")
    schema \= conn.execute("SELECT sql FROM sqlite\_master WHERE type='table'").fetchall()
    return "\\n".join(sql\[0\] for sql in schema if sql\[0\])

@mcp.tool()
def query\_data(sql: str) \-\> str:
    """Execute SQL queries safely"""
    conn \= sqlite3.connect("database.db")
    try:
        result \= conn.execute(sql).fetchall()
        return "\\n".join(str(row) for row in result)
    except Exception as e:
        return f"Error: {str(e)}"

Advanced Usage
--------------

### Low-Level Server

For more control, you can use the low-level server implementation directly. This gives you full access to the protocol and allows you to customize every aspect of your server, including lifecycle management through the lifespan API:

from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

from fake\_database import Database  \# Replace with your actual DB type

from mcp.server import Server

@asynccontextmanager
async def server\_lifespan(server: Server) \-\> AsyncIterator\[dict\]:
    """Manage server startup and shutdown lifecycle."""
    \# Initialize resources on startup
    db \= await Database.connect()
    try:
        yield {"db": db}
    finally:
        \# Clean up on shutdown
        await db.disconnect()

\# Pass lifespan to server
server \= Server("example-server", lifespan\=server\_lifespan)

\# Access lifespan context in handlers
@server.call\_tool()
async def query\_db(name: str, arguments: dict) \-\> list:
    ctx \= server.request\_context
    db \= ctx.lifespan\_context\["db"\]
    return await db.query(arguments\["query"\])

The lifespan API provides:

* A way to initialize resources when the server starts and clean them up when it stops
* Access to initialized resources through the request context in handlers
* Type-safe context passing between lifespan and request handlers

import mcp.server.stdio
import mcp.types as types
from mcp.server.lowlevel import NotificationOptions, Server
from mcp.server.models import InitializationOptions

\# Create a server instance
server \= Server("example-server")

@server.list\_prompts()
async def handle\_list\_prompts() \-\> list\[types.Prompt\]:
    return \[
        types.Prompt(
            name\="example-prompt",
            description\="An example prompt template",
            arguments\=\[
                types.PromptArgument(
                    name\="arg1", description\="Example argument", required\=True
                )
            \],
        )
    \]

@server.get\_prompt()
async def handle\_get\_prompt(
    name: str, arguments: dict\[str, str\] | None
) \-\> types.GetPromptResult:
    if name != "example-prompt":
        raise ValueError(f"Unknown prompt: {name}")

    return types.GetPromptResult(
        description\="Example prompt",
        messages\=\[
            types.PromptMessage(
                role\="user",
                content\=types.TextContent(type\="text", text\="Example prompt text"),
            )
        \],
    )

async def run():
    async with mcp.server.stdio.stdio\_server() as (read\_stream, write\_stream):
        await server.run(
            read\_stream,
            write\_stream,
            InitializationOptions(
                server\_name\="example",
                server\_version\="0.1.0",
                capabilities\=server.get\_capabilities(
                    notification\_options\=NotificationOptions(),
                    experimental\_capabilities\={},
                ),
            ),
        )

if \_\_name\_\_ \== "\_\_main\_\_":
    import asyncio

    asyncio.run(run())

### Writing MCP Clients

The SDK provides a high-level client interface for connecting to MCP servers:

from mcp import ClientSession, StdioServerParameters, types
from mcp.client.stdio import stdio\_client

\# Create server parameters for stdio connection
server\_params \= StdioServerParameters(
    command\="python",  \# Executable
    args\=\["example\_server.py"\],  \# Optional command line arguments
    env\=None,  \# Optional environment variables
)

\# Optional: create a sampling callback
async def handle\_sampling\_message(
    message: types.CreateMessageRequestParams,
) \-\> types.CreateMessageResult:
    return types.CreateMessageResult(
        role\="assistant",
        content\=types.TextContent(
            type\="text",
            text\="Hello, world! from model",
        ),
        model\="gpt-3.5-turbo",
        stopReason\="endTurn",
    )

async def run():
    async with stdio\_client(server\_params) as (read, write):
        async with ClientSession(
            read, write, sampling\_callback\=handle\_sampling\_message
        ) as session:
            \# Initialize the connection
            await session.initialize()

    \# List available prompts
            prompts \= await session.list\_prompts()

    \# Get a prompt
            prompt \= await session.get\_prompt(
                "example-prompt", arguments\={"arg1": "value"}
            )

    \# List available resources
            resources \= await session.list\_resources()

    \# List available tools
            tools \= await session.list\_tools()

    \# Read a resource
            content, mime\_type \= await session.read\_resource("file://some/path")

    \# Call a tool
            result \= await session.call\_tool("tool-name", arguments\={"arg1": "value"})

if \_\_name\_\_ \== "\_\_main\_\_":
    import asyncio

    asyncio.run(run())

### MCP Primitives

The MCP protocol defines three core primitives that servers can implement:

| Primitive | Control                | Description                                       | Example Use                  |
| --------- | ---------------------- | ------------------------------------------------- | ---------------------------- |
| Prompts   | User-controlled        | Interactive templates invoked by user choice      | Slash commands, menu options |
| Resources | Application-controlled | Contextual data managed by the client application | File contents, API responses |
| Tools     | Model-controlled       | Functions exposed to the LLM to take actions      | API calls, data updates      |

### Server Capabilities

MCP servers declare capabilities during initialization:

| Capability      | Feature Flag                  | Description                     |
| --------------- | ----------------------------- | ------------------------------- |
| `prompts`     | `listChanged`               | Prompt template management      |
| `resources`   | `subscribe`                 |                                 |
| `listChanged` | Resource exposure and updates |                                 |
| `tools`       | `listChanged`               | Tool discovery and execution    |
| `logging`     | \-                            | Server logging configuration    |
| `completion`  | \-                            | Argument completion suggestions |

Documentation
-------------

* [Model Context Protocol documentation](https://modelcontextprotocol.io/)
* [Model Context Protocol specification](https://spec.modelcontextprotocol.io/)
* [Officially supported servers](https://github.com/modelcontextprotocol/servers)

Contributing
------------

We are passionate about supporting contributors of all levels of experience and would love to see you get involved in the project. See the [contributing guide](https://pypi.org/project/mcp/CONTRIBUTING.md) to get started.

License
-------

This project is licensed under the MIT License - see the LICENSE file for details.
