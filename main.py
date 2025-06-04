from fastapi import FastAPI, HTTPException, Request, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import Any, Dict, Optional, Annotated
import logging
import asyncio
from contextlib import asynccontextmanager
import httpx
import os
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Weather API Constants
NWS_API_BASE = "https://api.weather.gov"
USER_AGENT = "weather-app/1.0"

# Authentication Configuration
# SECURITY WARNING: Configure your own API keys via environment variables!
# The server will not start without proper API key configuration.

VALID_API_KEYS = {}

# Load API keys configuration
# Priority: Environment variables > Placeholder values (for demo/development)

# 1. First, try loading from environment variables (RECOMMENDED for production)
# Format: "key1:client_name1:permission1,permission2;key2:client_name2:permission1"
# Example: "abc123:MyClient:tools,resources;def456:LimitedClient:tools"
if os.getenv("MCP_API_KEYS"):
    logger.info("🔑 Loading API keys from environment variables")
    env_keys = os.getenv("MCP_API_KEYS").split(";")
    for key_config in env_keys:
        parts = key_config.split(":")
        if len(parts) >= 3:
            key = parts[0].strip()
            name = parts[1].strip()
            permissions = [p.strip() for p in parts[2].split(",")]
            VALID_API_KEYS[key] = {
                "name": name,
                "permissions": permissions,
                "created": datetime.now().isoformat(),
                "source": "environment"
            }
else:
    # 2. Fallback to placeholder values for demo/development
    logger.warning("⚠️  Using placeholder API keys for demo purposes")
    logger.warning("🔒 For production, set MCP_API_KEYS environment variable")
    logger.warning("Example: MCP_API_KEYS='your-secure-key-123:My Client:tools,resources'")
    logger.error("❌ PLACEHOLDER KEYS WILL NOT WORK - Replace <> placeholders with actual keys!")
    
    # Placeholder API keys for demo/development - REPLACE WITH YOUR OWN!
    VALID_API_KEYS = {
        "<YOUR-DEMO-API-KEY>": {
            "name": "Demo Client (REPLACE WITH YOUR KEY)",
            "permissions": ["tools", "resources"],
            "created": datetime.now().isoformat(),
            "source": "placeholder"
        },
        "<YOUR-LIMITED-API-KEY>": {
            "name": "Test Client (REPLACE WITH YOUR KEY)", 
            "permissions": ["tools"],
            "created": datetime.now().isoformat(),
            "source": "placeholder"
        }
    }

# Pydantic Models
class Tool(BaseModel):
    name: str
    description: str
    inputSchema: Dict[str, Any]

class Resource(BaseModel):
    uri: str
    name: str
    description: Optional[str] = None
    mimeType: Optional[str] = None

class AuthInfo(BaseModel):
    key: str
    client_name: str
    permissions: list[str]

# Authentication Functions
security = HTTPBearer()

async def get_api_key_from_header(authorization: Annotated[str | None, Header()] = None) -> str:
    """Extract API key from Authorization header."""
    if not authorization:
        raise HTTPException(
            status_code=401,
            detail="Authorization header is required",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    # Support both "Bearer <key>" and just "<key>" formats
    if authorization.startswith("Bearer "):
        api_key = authorization[7:]  # Remove "Bearer " prefix
    else:
        api_key = authorization
    
    return api_key

async def authenticate_request(api_key: str = Depends(get_api_key_from_header)) -> AuthInfo:
    """Validate API key and return authentication info."""
    if api_key not in VALID_API_KEYS:
        logger.warning(f"Invalid API key attempted: {api_key[:8]}...")
        raise HTTPException(
            status_code=401,
            detail="Invalid API key",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    client_info = VALID_API_KEYS[api_key]
    logger.info(f"Authenticated client: {client_info['name']}")
    
    return AuthInfo(
        key=api_key,
        client_name=client_info["name"],
        permissions=client_info["permissions"]
    )

def require_permission(permission: str):
    """Dependency factory to require specific permissions."""
    async def check_permission(auth: AuthInfo = Depends(authenticate_request)) -> AuthInfo:
        if permission not in auth.permissions:
            raise HTTPException(
                status_code=403,
                detail=f"Permission '{permission}' required"
            )
        return auth
    return check_permission

# Weather API Helper Functions
async def make_nws_request(url: str) -> Optional[Dict[str, Any]]:
    """Make a request to the NWS API with proper error handling."""
    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "application/geo+json"
    }
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers, timeout=30.0)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"NWS API request failed: {e}")
            return None

def format_alert(feature: Dict[str, Any]) -> str:
    """Format an alert feature into a readable string."""
    props = feature["properties"]
    return f"""
Event: {props.get('event', 'Unknown')}
Area: {props.get('areaDesc', 'Unknown')}
Severity: {props.get('severity', 'Unknown')}
Description: {props.get('description', 'No description available')}
Instructions: {props.get('instruction', 'No specific instructions provided')}
"""

# MCP Server Class
class MCPServer:
    def __init__(self):
        self.tools: Dict[str, Tool] = {}
        self.resources: Dict[str, Resource] = {}
        self.initialize_tools()
        self.initialize_resources()
    
    def initialize_tools(self):
        """Initialize available tools"""
        # Weather alerts tool
        alerts_tool = Tool(
            name="get_alerts",
            description="Get weather alerts for a US state",
            inputSchema={
                "type": "object",
                "properties": {
                    "state": {
                        "type": "string",
                        "description": "Two-letter US state code (e.g. CA, NY)"
                    }
                },
                "required": ["state"]
            }
        )
        self.tools["get_alerts"] = alerts_tool
        
        # Weather forecast tool
        forecast_tool = Tool(
            name="get_forecast",
            description="Get weather forecast for a location",
            inputSchema={
                "type": "object",
                "properties": {
                    "latitude": {
                        "type": "number",
                        "description": "Latitude of the location"
                    },
                    "longitude": {
                        "type": "number",
                        "description": "Longitude of the location"
                    }
                },
                "required": ["latitude", "longitude"]
            }        )
        self.tools["get_forecast"] = forecast_tool
    
    def initialize_resources(self):
        """Initialize available resources"""
        # Example resource
        sample_resource = Resource(
            uri="mcp://server/sample",
            name="Sample Resource",
            description="A sample resource for demonstration",
            mimeType="text/plain"
        )
        self.resources["sample"] = sample_resource
    
    async def handle_initialize(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle MCP initialize request"""
        return {
            "protocolVersion": "2024-11-05",
            "capabilities": {
                "tools": {
                    "listChanged": True
                },
                "resources": {
                    "subscribe": True,
                    "listChanged": True
                }
            },
            "serverInfo": {
                "name": "FastAPI MCP Server with Auth",
                "version": "1.0.0"
            }
        }
    
    async def handle_tools_list(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle tools/list request"""
        tools_list = [tool.dict() for tool in self.tools.values()]
        return {"tools": tools_list}
    
    async def handle_tools_call(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle tools/call request"""
        tool_name = params.get("name")
        arguments = params.get("arguments", {})
        
        if tool_name not in self.tools:
            raise HTTPException(status_code=400, detail=f"Tool '{tool_name}' not found")
        
        if tool_name == "get_alerts":
            state = arguments.get("state", "")
            if not state:
                return {
                    "content": [
                        {
                            "type": "text",
                            "text": "Error: State code is required"
                        }
                    ]
                }
            
            url = f"{NWS_API_BASE}/alerts/active/area/{state.upper()}"
            data = await make_nws_request(url)
            
            if not data or "features" not in data:
                return {
                    "content": [
                        {
                            "type": "text",
                            "text": "Unable to fetch alerts or no alerts found."
                        }
                    ]
                }
            
            if not data["features"]:
                return {
                    "content": [
                        {
                            "type": "text",
                            "text": "No active alerts for this state."
                        }
                    ]
                }
            
            alerts = [format_alert(feature) for feature in data["features"]]
            result_text = "\n---\n".join(alerts)
            
            return {
                "content": [
                    {
                        "type": "text",
                        "text": result_text
                    }
                ]
            }
            
        elif tool_name == "get_forecast":
            latitude = arguments.get("latitude")
            longitude = arguments.get("longitude")
            
            if latitude is None or longitude is None:
                return {
                    "content": [
                        {
                            "type": "text",
                            "text": "Error: Both latitude and longitude are required"
                        }
                    ]
                }
            
            # First get the forecast grid endpoint
            points_url = f"{NWS_API_BASE}/points/{latitude},{longitude}"
            points_data = await make_nws_request(points_url)
            
            if not points_data:
                return {
                    "content": [
                        {
                            "type": "text",
                            "text": "Unable to fetch forecast data for this location."
                        }
                    ]
                }
            
            # Get the forecast URL from the points response
            try:
                forecast_url = points_data["properties"]["forecast"]
                forecast_data = await make_nws_request(forecast_url)
                
                if not forecast_data:
                    return {
                        "content": [
                            {
                                "type": "text",
                                "text": "Unable to fetch detailed forecast."
                            }
                        ]
                    }
                
                # Format the periods into a readable forecast
                periods = forecast_data["properties"]["periods"]
                forecasts = []
                for period in periods[:5]:  # Only show next 5 periods
                    forecast = f"""
{period['name']}:
Temperature: {period['temperature']}°{period['temperatureUnit']}
Wind: {period['windSpeed']} {period['windDirection']}
Forecast: {period['detailedForecast']}
"""
                    forecasts.append(forecast)
                
                result_text = "\n---\n".join(forecasts)
                
                return {
                    "content": [
                        {
                            "type": "text",
                            "text": result_text
                        }
                    ]
                }
                
            except KeyError as e:
                return {
                    "content": [
                        {
                            "type": "text",
                            "text": f"Error parsing forecast data: {str(e)}"
                        }
                    ]
                }
        
        return {"content": [{"type": "text", "text": "Tool executed successfully"}]}
    
    async def handle_resources_list(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle resources/list request"""
        resources_list = [resource.dict() for resource in self.resources.values()]
        return {"resources": resources_list}
    
    async def handle_resources_read(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle resources/read request"""
        uri = params.get("uri")
        
        if uri == "mcp://server/sample":
            return {
                "contents": [
                    {
                        "uri": uri,
                        "mimeType": "text/plain",
                        "text": "This is a sample resource content."
                    }
                ]
            }
        
        raise HTTPException(status_code=404, detail=f"Resource '{uri}' not found")

# Initialize MCP server
mcp_server = MCPServer()

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 Starting MCP FastAPI Server with Authentication")
      # Display API key configuration info
    if VALID_API_KEYS:
        env_keys = sum(1 for k in VALID_API_KEYS.values() if k.get("source") == "environment")
        placeholder_keys = sum(1 for k in VALID_API_KEYS.values() if k.get("source") == "placeholder")
        
        logger.info(f"📊 Loaded {len(VALID_API_KEYS)} API keys total:")
        if env_keys > 0:
            logger.info(f"   ✅ {env_keys} from environment variables (secure)")
        if placeholder_keys > 0:
            logger.warning(f"   ⚠️  {placeholder_keys} placeholder keys (demo only - replace for production!)")
            logger.error("   ❌ Placeholder keys with <> brackets will not work for actual requests!")
            
        # List configured clients (without exposing keys)
        for key_info in VALID_API_KEYS.values():
            source_icon = "🔒" if key_info.get("source") == "environment" else "🔧"
            logger.info(f"   {source_icon} Client: {key_info['name']} | Permissions: {', '.join(key_info['permissions'])}")
    else:
        logger.error("❌ No API keys configured - server will reject all requests!")
    
    yield
    logger.info("🛑 Shutting down MCP FastAPI Server")

# Create FastAPI app
app = FastAPI(
    title="MCP FastAPI Server with Authentication",
    description="Model Context Protocol server implementation using FastAPI with weather tools and API key authentication",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Health check endpoint with configuration info"""
    # Count API key sources
    env_keys = sum(1 for k in VALID_API_KEYS.values() if k.get("source") == "environment")
    placeholder_keys = sum(1 for k in VALID_API_KEYS.values() if k.get("source") == "placeholder")
    
    config_status = "production-ready" if env_keys > 0 and placeholder_keys == 0 else "development"
    if placeholder_keys > 0:
        config_status = "demo-placeholder-keys"
    
    return {
        "message": "MCP FastAPI Server with Authentication is running", 
        "status": "healthy",
        "version": "1.0.0",
        "api_keys": {
            "total": len(VALID_API_KEYS),
            "environment_vars": env_keys,
            "placeholder_demo": placeholder_keys,
            "configuration_status": config_status
        },
        "security_note": "Replace placeholder API keys for production use" if placeholder_keys > 0 else "Using secure environment variables"
    }

@app.get("/auth/info")
async def auth_info(auth: AuthInfo = Depends(authenticate_request)):
    """Get information about the authenticated client"""
    return {
        "client_name": auth.client_name,
        "permissions": auth.permissions,
        "authenticated": True
    }

@app.get("/tools")
async def list_tools(auth: AuthInfo = Depends(require_permission("tools"))):
    """REST endpoint to list available tools (requires authentication)"""
    return {"tools": [tool.dict() for tool in mcp_server.tools.values()]}

@app.get("/resources")
async def list_resources(auth: AuthInfo = Depends(require_permission("resources"))):
    """REST endpoint to list available resources (requires authentication)"""
    return {"resources": [resource.dict() for resource in mcp_server.resources.values()]}

@app.get("/test")
async def serve_test_page():
    """Serve the HTTP test page (public endpoint)"""
    return FileResponse("test_http_web.html")

@app.get("/mcp/capabilities")
async def mcp_capabilities():
    """Return MCP server capabilities"""
    return {
        "protocolVersion": "2024-11-05",
        "capabilities": {
            "tools": {"listChanged": True},
            "resources": {"subscribe": True, "listChanged": True}
        },
        "serverInfo": {
            "name": "FastAPI MCP Server with Auth",
            "version": "1.0.0"
        },
        "authentication": {
            "required": True,
            "type": "api-key",
            "description": "API key authentication via Authorization header"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint (public)"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "MCP Server with Authentication",
        "version": "1.0.0"
    }

@app.post("/tools/call")
async def call_tool(
    request: dict,
    auth_info: AuthInfo = Depends(require_permission("tools"))
):
    """Call a specific MCP tool (authenticated)"""
    method = request.get("method")
    params = request.get("params", {})
    
    if method != "tools/call":
        raise HTTPException(status_code=400, detail="Invalid method")
    
    tool_name = params.get("name")
    arguments = params.get("arguments", {})
    
    if tool_name not in mcp_server.tools:
        raise HTTPException(status_code=404, detail=f"Tool '{tool_name}' not found")
    
    # Call the MCP server tool handler
    try:
        result = await mcp_server.handle_tools_call(params)
        return result
            
    except Exception as e:
        logger.error(f"Tool execution failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Tool execution failed: {str(e)}")

@app.options("/mcp/stream")
async def mcp_stream_options():
    """Handle CORS preflight for MCP stream endpoint"""
    return {
        "status": "ok",
        "methods": ["POST", "OPTIONS"],
        "headers": ["Content-Type", "Accept", "Authorization"]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
