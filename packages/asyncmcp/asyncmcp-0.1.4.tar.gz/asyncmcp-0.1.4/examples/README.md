# MCP Local CLI Testing

This directory contains an interactive CLI client example showing how asyncmcp can be used. 
The CLI allows to take actions and the server is an asyncmcp version of MCP's [fetch server example](https://github.com/modelcontextprotocol/servers/tree/main/src/fetch)

> [!CAUTION]
> This server can access local/internal IP addresses and may represent a security risk. Exercise caution when using this MCP server to ensure this does not expose any sensitive data.


## Prerequisites

- **LocalStack** - Running on `localhost:4566`

## Steps

### 1. Run [localstack](https://www.localstack.cloud/)

```bash
pip install localstack
```

```bash
localstack start
```

### 2. Setup LocalStack Resources
Sets up the infrastructure on localstack - topics, queues and subscriptions for requests and responses.

```bash
uv run setup.py cleanup # cleans up resources
uv run setup.py
```

### 3. Start the MCP Transport Server (Terminal 1)

```bash
# Using SNS-SQS transport (default)
uv run website_server.py

# Using SQS-only transport
uv run website_server.py --transport sqs
```

### 4. Start the CLI (Terminal 2) 

```bash
# Using SNS-SQS transport (default)
uv run website_client.py

# Using SQS-only transport
uv run website_client.py --transport sqs
```

### 5. Try the workflow

In the interactive client (Terminal 2):
```
Quick Interactive MCP Client
Commands: init, tools, call <tool_name> <params...>, quit
Example: call fetch url=https://google.com
🔗 Connected to MCP transport
>
init
📤 Sending initialize request...
✅ Initialized with server: mcp-website-fetcher
📤 Sent initialized notification
>
tools
📤 Sending tools/list request...
✅ Found 1 tools:
   • fetch: Fetches a website and returns its content
>
call fetch url=https://google.com
📤 Sending tools/call request...
✅ Tool result:
   📄 <!doctype html><html itemscope="" ...
```

The whole MCP communication happened through queues and topics.
