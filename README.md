# FastAPI MCP Server with Weather Tools & Authentication

A **production-ready** Model Context Protocol (MCP) server built with FastAPI that provides weather information using the National Weather Service API. Features comprehensive API key authentication, role-based permissions, and streamable HTTP transport for real-time communication.

## 🌐 Azure Deployment

- **Azure URL**: https://`APP-SERVICE-NAME`.azurewebsites.net/
- **API Documentation**: https://`APP-SERVICE-NAME`.azurewebsites.net/docs
- **Health Check**: https://`APP-SERVICE-NAME`.azurewebsites.net/health
- **MCP Endpoint**: https://`APP-SERVICE-NAME`.azurewebsites.net/mcp/stream
- **Tools Endpoint**: https://`APP-SERVICE-NAME`.azurewebsites.net/tools/call
- **Interactive Test Interface**: [test_azure_web.html](./test_azure_web.html)

### 🧪 Live Testing Examples

You can test the authenticated weather tools:

```bash
# Test weather alerts for California (using full access key)
curl -X POST "https://`APP-SERVICE-NAME`.azurewebsites.net/tools/call" \
  -H "Authorization: mcp-client-key-123" \
  -H "Content-Type: application/json" \
  -d '{"method": "tools/call", "params": {"name": "get_alerts", "arguments": {"state": "CA"}}}'

# Test weather forecast for San Francisco  
curl -X POST "https://`APP-SERVICE-NAME`.azurewebsites.net/tools/call" \
  -H "Authorization: mcp-client-key-123" \
  -H "Content-Type: application/json" \
  -d '{"method": "tools/call", "params": {"name": "get_forecast", "arguments": {"latitude": 37.7749, "longitude": -122.4194}}}'

# Test authentication (should return 401)
curl -X GET "https://`APP-SERVICE-NAME`.azurewebsites.net/tools" \
  -H "Authorization: invalid-key"
```

## Features

- **FastAPI Framework**: Modern, fast web framework for building APIs
- **MCP Protocol Compliance**: Full support for JSON-RPC 2.0 MCP protocol
- **Streamable HTTP Transport**: HTTP-based streaming for MCP Inspector connectivity
- **Weather Tools**: 
  - `get_alerts`: Get weather alerts for any US state
  - `get_forecast`: Get 5-day weather forecast for any location (latitude/longitude)
- **Sample Resources**: Basic resource handling demonstration
- **Virtual Environment**: Properly isolated Python environment
- **Auto-reload**: Development server with automatic reloading
- **National Weather Service API**: Real-time weather data from official US government source

## 🔐 Authentication

This MCP server now includes **API key authentication** for enhanced security. All MCP endpoints (except health checks and documentation) require a valid API key.

### Authentication Methods

1. **Bearer Token Format** (Recommended):
   ```
   Authorization: Bearer your-api-key-here
   ```

2. **Direct API Key Format**:
   ```
   Authorization: your-api-key-here
   ```

### Default API Keys

The server comes with two pre-configured API keys for testing:

- **Full Access**: `mcp-client-key-123` (tools + resources permissions)
- **Limited Access**: `test-key-456` (tools only)

### Environment Variable Configuration

You can add custom API keys via environment variables:

```powershell
# Format: "key1:client_name1,key2:client_name2"
$env:MCP_API_KEYS = "my-key-123:My Client,another-key-456:Another Client"
```

### Testing Authentication

```bash
# Test with authentication
curl -X POST "http://localhost:8000/mcp/stream" \
  -H "Authorization: Bearer mcp-client-key-123" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2024-11-05", "capabilities": {}, "clientInfo": {"name": "test", "version": "1.0"}}}'

# Check authentication info
curl -X GET "http://localhost:8000/auth/info" \
  -H "Authorization: Bearer mcp-client-key-123"
```

### Permission System

- **tools**: Access to weather tools (`get_alerts`, `get_forecast`)
- **resources**: Access to server resources

Clients receive different permissions based on their API key configuration.

## Prerequisites

- Python 3.8+
- pip (Python package installer)

## Setup

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
   
   Or manually:
   ```powershell
   .\venv\Scripts\python.exe -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
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
        "url": "https://app-web-7ahzyo2sd4ery.azurewebsites.net/mcp/stream",
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

Visit http://localhost:8000/test (local) or https://`APP-SERVICE-NAME`.azurewebsites.net/test (Azure) to use the built-in web interface for testing HTTP connectivity.

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

#### Call Weather Alert Tool
```json
{
  "jsonrpc": "2.0",
  "method": "tools/call",
  "params": {
    "name": "get_alerts",
    "arguments": {
      "state": "CA"
    }
  },
  "id": 3
}
```

#### Call Weather Forecast Tool
```json
{
  "jsonrpc": "2.0",
  "method": "tools/call",
  "params": {
    "name": "get_forecast",
    "arguments": {
      "latitude": 37.7749,
      "longitude": -122.4194
    }
  },
  "id": 4
}
```

## Testing

### Test with Python client:
```powershell
.\venv\Scripts\python.exe test_http_client.py  # Streamable HTTP client
```

### Test with web interface:
Open http://localhost:8000/test in your browser

## Available Tools

1. **get_alerts**: Get weather alerts for a US state
   ```json
   {
     "name": "get_alerts",
     "arguments": {
       "state": "CA"
     }
   }
   ```
   - **Parameter**: `state` (string) - Two-letter US state code (e.g., CA, NY, TX)
   - **Returns**: Active weather alerts including severity, description, and instructions

2. **get_forecast**: Get weather forecast for a location
   ```json
   {
     "name": "get_forecast", 
     "arguments": {
       "latitude": 37.7749,
       "longitude": -122.4194
     }
   }
   ```
   - **Parameters**: 
     - `latitude` (number) - Latitude coordinate
     - `longitude` (number) - Longitude coordinate
   - **Returns**: 5-day weather forecast with temperature, wind, and detailed conditions

### 🔧 Production Recommendations

1. **API Key Management**:
   ```bash
   # Store keys in Azure App Service environment variables
   az webapp config appsettings set --resource-group myResourceGroup --name myApp --settings MCP_API_KEYS="prod-key-123:Production Client"
   ```

2. **Monitoring & Logging**:
   - Enable Azure Application Insights for detailed logging
   - Set up alerts for 4xx/5xx errors
   - Monitor `/health` endpoint for uptime

3. **Security Enhancements**:
   - Rotate API keys regularly
   - Implement rate limiting for production traffic
   - Add request/response logging for audit trails
   - Consider HTTPS certificate pinning for critical clients

4. **Scaling**:
   - Current deployment handles moderate concurrent users
   - Can scale horizontally using Azure App Service scaling rules
   - Consider Azure Front Door for global distribution

## Weather Data Source

This server uses the **National Weather Service (NWS) API**, which provides:
- Real-time weather alerts and warnings
- Detailed weather forecasts
- Official US government weather data
- No API key required
- High reliability and accuracy

## Available Resources

- **mcp://server/sample**: Sample resource for demonstration

## Troubleshooting

### Azure Deployment Issues:
1. **Authentication failures**: Verify API keys in environment variables
2. **Tool execution errors**: Check Azure App Service logs via `az webapp log tail`
3. **Connection timeouts**: Ensure Azure App Service is running and not sleeping

### MCP Inspector Connection Issues:
1. Ensure the server is running on http://localhost:8000
2. Verify MCP endpoint is accessible: http://localhost:8000/mcp/stream
3. Check capabilities endpoint: http://localhost:8000/mcp/capabilities
4. Try the web test interface first: http://localhost:8000/test

### Common Issues:
- **Port already in use**: Change the port in startup commands
- **Virtual environment not activated**: Run `.\venv\Scripts\Activate.ps1`
- **Dependencies missing**: Run `pip install -r requirements.txt`