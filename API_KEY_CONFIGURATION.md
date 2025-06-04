# API Key Configuration Reference

Technical reference for the MCP server's dual-mode API key authentication system.

## Configuration Methods

### Environment Variables (Production)
```bash
MCP_API_KEYS="key1:client_name:permission1,permission2;key2:client_name:permission1"
```

### Placeholder Keys (Development)
When no environment variable is set, placeholder keys are used:
- `<YOUR-DEMO-API-KEY>` - Full access (tools + resources)
- `<YOUR-LIMITED-API-KEY>` - Limited access (tools only)

**Note**: Placeholder keys will fail authentication and cannot be used for actual requests.

## API Key Format

**Environment Variable Format:**
```
key1:client_name:permission1,permission2;key2:client_name:permission1
```

**Example:**
```powershell
$env:MCP_API_KEYS = "abc123:Production:tools,resources;xyz789:Dev:tools"
```

## Implementation Details

### Server Behavior
- Environment variables take precedence over placeholder values
- Placeholder keys (`<YOUR-*-API-KEY>`) will fail authentication
- Server logs indicate configuration mode at startup
- Health endpoint reports current configuration status

### Authentication Flow
1. Server checks for `MCP_API_KEYS` environment variable
2. If found, parses and loads production keys
3. If not found, uses placeholder keys with warnings
4. Requests must include `Authorization: Bearer <api-key>` header
5. Server validates key and returns client permissions

### Permissions
- `tools`: Access to weather tools (`get_alerts`, `get_forecast`)
- `resources`: Access to sample resources
- Multiple permissions separated by commas

## Security Features
- No hardcoded production keys in source code
- Placeholder keys are visually obvious and non-functional
- Environment variable configuration for secure deployment
- Clear warnings when running with placeholder keys

For deployment instructions, see [DEPLOY.md](./DEPLOY.md).  
For local development setup, see [README.md](./README.md).
