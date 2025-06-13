# Python MCP Weather Server with Key-Based Authentication & Azure Deployment

A **production-ready** Model Context Protocol (MCP) server built with FastAPI that provides weather information using the National Weather Service API. Features comprehensive API key authentication, role-based permissions, and streamable HTTP transport for real-time communication.

## Features

- **FastAPI Framework**: Modern, fast web framework for building APIs
- **MCP Protocol Compliance**: Full support for JSON-RPC 2.0 MCP protocol
- **Streamable HTTP Transport**: HTTP-based streaming for MCP Inspector connectivity
- **Weather Tools**: 
  - `get_alerts`: Get weather alerts for any US state
  - `get_forecast`: Get detailed weather forecast for any location
- **API Key Authentication**: Role-based access control with permissions
- **Azure Ready**: Pre-configured for Azure App Service deployment
- **Web Test Interface**: Built-in HTML interface for testing
- **National Weather Service API**: Real-time weather data from official US government source

## Local Development

### Prerequisites
- Python 3.8+
- pip (Python package installer)

### Setup & Run

1. **Clone and install dependencies:**
   ```powershell
   git clone <your-repo-url>
   cd remote-mcp-webapp-python-auth
   python -m venv venv
   .\venv\Scripts\Activate.ps1  # Windows PowerShell
   # or
   source venv/bin/activate     # macOS/Linux
   pip install -r requirements.txt
   ```

2. **Start the development server:**
   ```powershell
   .\start_server.ps1  # Windows
   # or manually:
   uvicorn main:app --host 0.0.0.0 --port 8000 --reload
   ```

3. **Access the server:**
   - Server: [http://localhost:8000/](http://localhost:8000/)
   - Health Check: [http://localhost:8000/health](http://localhost:8000/health)
   - Test Interface: [http://localhost:8000/test](http://localhost:8000/test)
   - API Documentation: [http://localhost:8000/docs](http://localhost:8000/docs)

The server will automatically use placeholder API keys for local development. See the Authentication section below for details.

## Authentication & API Keys

This MCP server uses **API key authentication** for security with dual configuration modes:

### Local Development (Automatic)
- Server automatically uses placeholder keys:
  - `<YOUR-DEMO-API-KEY>` - Full access (tools + resources)  
  - `<YOUR-LIMITED-API-KEY>` - Limited access (tools only)
- These placeholders are visible but **will not work** for actual requests
- Shows clear warnings in startup logs
- Perfect for testing MCP Inspector connectivity and development

### Production Setup (Required for Real Use)
For production deployment or real API access, you must provide your own API keys:

**Environment Variable Format:**
```powershell
# Windows PowerShell
$env:MCP_API_KEYS = "key1:client_name:permission1,permission2;key2:client_name:permission1"

# Example
$env:MCP_API_KEYS = "<key-1-name>:Production:tools,resources;<key-2-name>:Dev:tools"
```

**Key Format:** `api_key:client_name:permission1,permission2`

### Permission Types
- **tools**: Access to weather tools (`get_alerts`, `get_forecast`)
- **resources**: Access to server resources

### Security Features
- No hardcoded production keys in source code
- Placeholder keys are visually obvious and non-functional
- Environment variable configuration for secure deployment
- Clear warnings when running with placeholder keys
- Server logs indicate configuration mode at startup

## Connect to the Local MCP Server

### Using VS Code - Copilot Agent Mode
1. Add MCP Server from command palette and add the URL to your running server's HTTP endpoint:
   ```
   http://localhost:8000
   ```
2. List MCP Servers from command palette and start the server
3. In Copilot chat agent mode, enter a prompt to trigger the tool:
   ```
   What's the weather forecast for San Francisco?
   ```
4. When prompted to run the tool, consent by clicking Continue

### Using MCP Inspector
1. In a new terminal window, install and run MCP Inspector:
   ```bash
   npx @modelcontextprotocol/inspector
   ```
2. CTRL+click the URL displayed by the app (e.g. http://localhost:5173/#resources)
3. Set the transport type to `HTTP`
4. Set the URL to your running server's HTTP endpoint and Connect:
   ```
   http://localhost:8000/mcp/stream
   ```
5. **Add Authentication Header**: `Authorization: <YOUR-DEMO-API-KEY>`
6. List Tools, click on a tool, and Run Tool

### Configuration File for MCP Inspector
Save this as `mcp-config.json`:
```json
{
  "mcpServers": {
    "weather-mcp-server-local": {
      "transport": {
        "type": "http",
        "url": "http://localhost:8000/",
        "headers": {
          "Authorization": "<YOUR-DEMO-API-KEY>"
        }
      },
      "name": "Weather MCP Server (Local with Auth)",
      "description": "MCP Server with weather forecast and alerts tools running locally with authentication"
    }
  }
}
```

## Quick Deploy to Azure

### Prerequisites
- [Azure CLI](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli)
- [Azure Developer CLI (azd)](https://learn.microsoft.com/en-us/azure/developer/azure-developer-cli/install-azd)
- Active Azure subscription

### Deploy in 3 Commands

```powershell
# 1. Login to Azure
azd auth login

# 2. Initialize the project
azd init

# 3. Set your API keys (REQUIRED - replace with your actual keys)
azd env set MCP_API_KEYS "your-production-key:Production Client:tools,resources;your-dev-key:Development Client:tools"

# 4. Deploy to Azure
azd up
```

After deployment, your MCP server will be available at:
- Health Check: `https://<your-app>.azurewebsites.net/health`
- MCP Capabilities: `https://<your-app>.azurewebsites.net/mcp/capabilities`
- Test Interface: `https://<your-app>.azurewebsites.net/test`

**⚠️ CRITICAL**: You must configure your own API keys before deployment. Never use placeholder keys like `<YOUR-API-KEY>` in production.

## Connect to the Remote MCP Server

Follow the same guidance as above, but use your App Service URL instead:

**Configuration for Azure deployment:**
```json
{
  "mcpServers": {
    "weather-mcp-server-azure": {
      "transport": {
        "type": "http",
        "url": "https://your-app-name.azurewebsites.net/mcp/stream",
        "headers": {
          "Authorization": "<YOUR-PRODUCTION-API-KEY>"
        }
      },
      "name": "Weather MCP Server (Azure with Auth)",
      "description": "MCP Server with weather forecast and alerts tools hosted on Azure with authentication"
    }
  }
}
```

## 🌦️ Data Source

This server uses the National Weather Service (NWS) API:
- Real-time weather alerts and warnings
- Detailed weather forecasts
- Official US government weather data
- No API key required
- High reliability and accuracy

## 🛠️ Development

### API Endpoints
- **Health Check**: `GET /health` (no auth required)
- **API Documentation**: `GET /docs` (no auth required)
- **Tools List**: `GET /tools` (auth required)
- **Tool Execution**: `POST /tools/call` (auth required)
- **MCP Capabilities**: `GET /mcp/capabilities` (auth required)
- **Authentication Info**: `GET /auth/info` (auth required)
- **Test Interface**: `GET /test` (no auth required)

### Local Development Features
- **Auto-reload**: Server automatically restarts on code changes
- **Interactive API docs**: Available at `/docs`
- **Request logging**: All authenticated requests are logged
- **Health monitoring**: Status endpoint at `/health`
- **Placeholder API keys**: Automatic setup for development

## Troubleshooting

### Common Issues

1. **Authentication failures**: Make sure you're using the correct API key format and header
2. **CORS errors**: The server is configured for local development and Azure deployment
3. **Tool execution errors**: Check that the National Weather Service API is accessible
4. **Environment variable issues**: Restart the server after setting environment variables

### Local Development Debug Commands
```bash
# Check server health
curl http://localhost:8000/health

# Test authentication
curl -X GET "http://localhost:8000/auth/info" -H "Authorization: <YOUR-DEMO-API-KEY>"

# List available tools
curl -X GET "http://localhost:8000/tools" -H "Authorization: <YOUR-DEMO-API-KEY>"
```

### Azure Deployment Issues

1. **Deployment Fails**
   ```bash
   azd logs
   ```
   Check for dependency or configuration errors.

2. **Authentication Issues**
   - Verify API keys are set: `azd env get-values | grep MCP_API_KEYS`
   - If empty: `azd env set MCP_API_KEYS "your-key:Your Client:tools,resources"` then `azd deploy`
   - Check Azure Portal: App Service → Environment Variables → App Settings → MCP_API_KEYS

3. **Application Won't Start**
   - Check Application Insights logs in Azure Portal
   - Verify `requirements.txt` includes all dependencies

### Cleanup Azure Resources
```bash
# Remove all Azure resources
azd down
```

This removes the entire resource group and all associated resources.

## 🔒 Security Considerations

- **API Keys**: Stored securely in Azure App Service environment variables
- **HTTPS**: Automatically enforced by Azure App Service
- **Network Security**: Azure App Service provides built-in DDoS protection
- **Monitoring**: Application Insights tracks all requests and errors
- **No hardcoded secrets**: All sensitive data via environment variables

For production deployments, consider:
- Azure Key Vault for API key storage
- Custom domains with SSL certificates
- Azure Front Door for global distribution
- Rate limiting and request throttling

## 📄 Additional Documentation

- **Azure Infrastructure**: See `infra/` directory for Bicep templates
- **Test Files**: Various test configurations in `test_*.json` and `test_*.html`
- **PowerShell Scripts**: `start_server.ps1` for easy local development