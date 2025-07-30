# MCP CLI Client – Progress Updates

**Project:** Development of an MCP Server for VectorX.

---

## 1. Overview

- **Objective:** Build a MCP server for VectorX that can be integrated with different MCP clients.
- **Key Features:**
  - Client initialization
  - Index creation
  - Vector upsertion
  - Index querying
  - Index deletion
  - Query with filter
  - Deletion with filter

---

## 2. Completed Tasks

1. **Server**
   - A fastmcp server that can run on three transport modes i.e. stdio, streamable-http, sse.
   - Takes api key as env variable and creates a server instance using provided settings.

2. **Basic Tools**
   - Tools for client initialization, index creation, query and deletion working when tested through Claude(stdio), Postman(streamable-http) and CLI.
   - Tool call happens through jrpc passed as body of request.
---

## 4. Next Steps

- **Test**
  - Test the streamble-http and sse through available clients.

- **Add new tools**
  - Add tools like query with filter and deletion with filter and expand scope of current tools.

- **Documentaion for the MCP Client**
  - Write documentaion guide on usage of the client.
  - Draft user guide and CLI reference in Markdown.

---
