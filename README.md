# FastAPI MCP Server with Weather Tools & Authentication

A **production-ready** Model Context Protocol (MCP) server built with FastAPI that provides weather information using the National Weather Service API. Features comprehensive API key authentication, role-based permissions, and streamable HTTP transport for real-time communication.

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- pip (Python package installer)

### Local Development Setup

1. **Create and activate virtual environment:**
   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   ```

2. **Install dependencies:**
   ```powershell
   pip install -r requirements.txt
   ```

3. **Start the server:**
   ```powershell
   .\start_server.ps1
   ```
   
   The server will start at `http://localhost:8000` with placeholder API keys for testing.

### 🌐 Azure Deployment

For production Azure deployment, see **[DEPLOY.md](./DEPLOY.md)** for complete instructions.

- **Live Demo**: https://`<YOUR-APP-SERVICE-NAME>`.azurewebsites.net/
- **API Documentation**: https://`<YOUR-APP-SERVICE-NAME>`.azurewebsites.net/docs
- **Interactive Testing**: [test_azure_web.html](./test_azure_web.html)

## Features

- **FastAPI Framework**: Modern, fast web framework for building APIs
- **MCP Protocol Compliance**: Full support for JSON-RPC 2.0 MCP protocol
- **Streamable HTTP Transport**: HTTP-based streaming for MCP Inspector connectivity
- **Weather Tools**: 
  - `get_alerts`: Get weather alerts for any US state
  - `get_forecast`: Get 5-day weather forecast for any location (latitude/longitude)
- **API Key Authentication**: Role-based access control with permissions
- **Sample Resources**: Basic resource handling demonstration
- **Auto-reload**: Development server with automatic reloading
- **National Weather Service API**: Real-time weather data from official US government source

## 🔐 Authentication

This MCP server uses **API key authentication** for security. 

### Local Development (Automatic)
- Server automatically uses placeholder keys: `<YOUR-DEMO-API-KEY>` and `<YOUR-LIMITED-API-KEY>`
- These placeholders are visible but **will not work** for actual requests
- Shows clear warnings in startup logs

### Production Setup
For production deployment, you must provide real API keys via environment variables:

```powershell
$env:MCP_API_KEYS = "your-secure-key:Client Name:tools,resources"
```

**For complete authentication details, see [API_KEY_CONFIGURATION.md](./API_KEY_CONFIGURATION.md)**

### Permission Types
- **tools**: Access to weather tools (`get_alerts`, `get_forecast`)
- **resources**: Access to server resources

## Testing the Server

### 1. Basic Health Check
```bash
curl http://localhost:8000/health
```

### 2. List Available Tools
```bash
curl -X GET "http://localhost:8000/tools" \
  -H "Authorization: <YOUR-DEMO-API-KEY>"
```

### 3. Test Weather Forecast
```bash
curl -X POST "http://localhost:8000/tools/call" \
  -H "Authorization: <YOUR-DEMO-API-KEY>" \
  -H "Content-Type: application/json" \
  -d '{"method": "tools/call", "params": {"name": "get_forecast", "arguments": {"latitude": 40.7128, "longitude": -74.0060}}}'
```

**Note**: These examples use placeholder keys. For actual testing, replace with your own API keys.
   ```

## Connecting to MCP Inspector

### Method 1: Azure-Hosted Server (No Setup Required)

Connect directly to the live Azure deployment:

**Configuration for MCP Inspector:**
```json
{
  "mcpServers": {
    "weather-mcp-server-azure": {
      "transport": {
        "type": "http",
        "url": "https://your-app-name.azurewebsites.net/mcp/stream",
        "headers": {
          "Authorization": "mcp-client-key-123"
        }
      },
      "name": "Weather MCP Server (Azure with Auth)",
      "description": "MCP Server with weather forecast and alerts tools hosted on Azure with authentication"
    }
  }
}
```

### Method 2: Local Development Server

1. **Start the MCP server** (it will run on http://localhost:8000)

2. **In MCP Inspector v0.13.0:**
   - Add a new server connection
   - Use HTTP transport type
   - URL: `http://localhost:8000/mcp/stream`
   - **Add Authentication Header**: `Authorization: mcp-client-key-123`

3. **Configuration file** (`mcp-config.json`):
   ```json
   {
     "mcpServers": {
       "weather-mcp-server-local": {
         "transport": {
           "type": "http",
           "url": "http://localhost:8000/mcp/stream",
           "headers": {
             "Authorization": "mcp-client-key-123"
           }
         },
         "name": "Weather MCP Server (Local with Auth)",
         "description": "MCP Server with weather forecast and alerts tools running locally with authentication"
       }
     }
   }
   ```

### Method 3: Web Test Interface

Visit http://localhost:8000/test (local) or https://`<APP-SERVICE-NAME>`.azurewebsites.net/test (Azure) to use the built-in web interface for testing HTTP connectivity.

## API Endpoints

- **GET /health**: Server health check
- **POST /mcp/stream**: Main MCP endpoint with streamable HTTP
- **GET /mcp/capabilities**: Get server capabilities
- **GET /test**: Web-based HTTP test interface
- **POST /mcp**: HTTP MCP endpoint (legacy)

## Usage

### Start the server:
```bash
pip install -r requirements.txt
python main.py
```

The server will start on http://localhost:8000

### Example MCP requests:

#### Initialize
```json
{
  "jsonrpc": "2.0",
  "method": "initialize",
  "params": {},
  "id": 1
}
```

#### List Tools
```json
{
  "jsonrpc": "2.0",
  "method": "tools/list",
  "params": {},
  "id": 2
}
```

## MCP Inspector Connection

To connect MCP Inspector to your local server:

1. **Start the server** (it will use placeholder keys automatically)
2. **In MCP Inspector**, add a new server connection:
   - **Transport**: HTTP
   - **URL**: `http://localhost:8000/mcp/stream`
   - **Headers**: `Authorization: <YOUR-DEMO-API-KEY>`

3. **Connect and test** the weather tools

## Available Endpoints

- **Health Check**: `GET /health` (no auth required)
- **API Documentation**: `GET /docs` (no auth required)  
- **Tools List**: `GET /tools` (auth required)
- **Tool Execution**: `POST /tools/call` (auth required)
- **MCP Stream**: `POST /mcp/stream` (auth required)
- **Authentication Info**: `GET /auth/info` (auth required)

## Weather Tools

### `get_alerts`
Get weather alerts for any US state.

**Parameters:**
- `state`: Two-letter US state code (e.g., "CA", "TX", "NY")

**Example:**
```bash
curl -X POST "http://localhost:8000/tools/call" \
  -H "Authorization: <YOUR-DEMO-API-KEY>" \
  -H "Content-Type: application/json" \
  -d '{"method": "tools/call", "params": {"name": "get_alerts", "arguments": {"state": "CA"}}}'
```

### `get_forecast`
Get 5-day weather forecast for any location.

**Parameters:**
- `latitude`: Latitude coordinate (number)
- `longitude`: Longitude coordinate (number)

**Example:**
```bash
curl -X POST "http://localhost:8000/tools/call" \
  -H "Authorization: <YOUR-DEMO-API-KEY>" \
  -H "Content-Type: application/json" \
  -d '{"method": "tools/call", "params": {"name": "get_forecast", "arguments": {"latitude": 37.7749, "longitude": -122.4194}}}'
```

## Development

### File Structure
```
├── main.py                 # FastAPI server with MCP implementation
├── requirements.txt        # Python dependencies
├── start_server.ps1       # PowerShell startup script
├── test_azure_auth.py     # Authentication testing script
├── test_azure_web.html    # Interactive web testing interface
├── mcp-config.json        # MCP Inspector configuration
├── DEPLOY.md              # Azure deployment guide
└── API_KEY_CONFIGURATION.md # Authentication implementation details
```

### Local Development Features
- **Auto-reload**: Server automatically restarts on code changes
- **Interactive API docs**: Available at `/docs`
- **Request logging**: All authenticated requests are logged
- **Health monitoring**: Status endpoint at `/health`

## Production Deployment

For production Azure deployment:
1. **Read [DEPLOY.md](./DEPLOY.md)** for complete deployment instructions
2. **Configure real API keys** via environment variables
3. **Deploy using Azure Developer CLI**

## Troubleshooting

### Common Issues

1. **Authentication failures**: Make sure you're using the correct API key format
2. **CORS errors**: The server is configured for local development and Azure deployment
3. **Tool execution errors**: Check that the National Weather Service API is accessible
4. **Environment variable issues**: Restart the server after setting environment variables

### Debug Commands
```bash
# Check server health
curl http://localhost:8000/health

# Test authentication
curl -X GET "http://localhost:8000/auth/info" -H "Authorization: <YOUR-DEMO-API-KEY>"

# List available tools
curl -X GET "http://localhost:8000/tools" -H "Authorization: <YOUR-DEMO-API-KEY>"
```