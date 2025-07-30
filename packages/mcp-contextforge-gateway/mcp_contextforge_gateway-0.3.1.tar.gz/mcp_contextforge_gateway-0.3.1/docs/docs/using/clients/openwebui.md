# OpenWebUI Integration with MCP Gateway

OpenWebUI is a self-hosted, extensible interface for interacting with large language models (LLMs). Integrating OpenWebUI with the Model Context Protocol (MCP) allows you to enhance your AI workflows by leveraging tools and resources provided by MCP servers.

---

## 🔌 Integration Overview

OpenWebUI supports integration with external tools via OpenAPI specifications. MCP Gateway exposes its tools through OpenAPI-compatible endpoints, enabling seamless integration with OpenWebUI.

---

## 🛠️ Prerequisites

- **OpenWebUI**: Ensure you have OpenWebUI installed and running. Refer to the [OpenWebUI documentation](https://docs.openwebui.com/) for installation instructions.
- **MCP Gateway**: Set up and run the MCP Gateway. Detailed setup instructions can be found in the [MCP Gateway documentation](https://modelcontextprotocol.io/).

---

## 🔗 Connecting MCP Tools to OpenWebUI

### 1. Launch MCP Gateway

Start the MCP Gateway to expose its tools via OpenAPI endpoints. For example:

```bash
uv run mcpgateway
```

Ensure that the MCP Gateway is accessible at a known URL, such as `http://localhost:4444`.

### 2. Identify MCP Tool Endpoints

Determine the specific tool endpoints provided by the MCP Gateway. These endpoints follow the OpenAPI specification and are typically accessible at URLs like:

```
http://localhost:4444/tools/<tool-name>
```

Replace `<tool-name>` with the actual name of the tool you wish to integrate.

### 3. Add MCP Tools to OpenWebUI

#### a. Access OpenWebUI Settings

* Navigate to the OpenWebUI interface in your browser.
* Click on the ⚙️ **Settings** icon.

#### b. Add a New Tool Server

* In the **Settings** menu, locate the **Tools** section.
* Click on the ➕ **Add Tool Server** button.
* Enter the URL of the MCP tool endpoint (e.g., `http://localhost:4444/tools/<tool-name>`).
* Click **Save** to register the tool.

Repeat this process for each MCP tool you wish to integrate.

---

## 🧪 Using MCP Tools in OpenWebUI

Once the MCP tools are registered:

* **Enable Tools in Chat**: In the chat interface, click on the ➕ icon to view available tools. Toggle the desired MCP tools to enable them for the current session.
* **Invoke Tools**: Interact with the AI model as usual. When appropriate, the model will utilize the enabled MCP tools to fulfill your requests.

---

## ⚙️ Advanced Configuration

### Global Tool Servers

To make MCP tools available to all users:

* Navigate to **Admin Settings** > **Tools**.
* Add the MCP tool endpoints as described above.
* These tools will now be accessible to all users, subject to individual activation in their chat sessions.

### Native Function Calling

OpenWebUI supports native function calling for tools:

* In the chat interface, go to **Chat Controls** > **Advanced Params**.
* Set the **Function Calling** parameter to `Native`.
* This enables more structured interactions between the AI model and the tools.

---

## 🧰 Additional Resources

* [OpenWebUI Documentation](https://docs.openwebui.com/)
* [MCP Gateway Documentation](https://modelcontextprotocol.io/)
* [OpenWebUI GitHub Repository](https://github.com/open-webui/open-webui)
* [MCP Gateway GitHub Repository](https://github.com/mcp-ecosystem/mcp-gateway)

---

By integrating MCP tools into OpenWebUI, you can enhance your AI assistant's capabilities, enabling it to perform a wider range of tasks by leveraging the diverse tools provided by the MCP ecosystem.
