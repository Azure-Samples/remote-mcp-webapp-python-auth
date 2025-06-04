#!/usr/bin/env python3
"""
Test authentication functionality on the deployed Azure MCP server.
"""

import json
import requests
import sys
from datetime import datetime

# Azure deployment URL
# Replace with your actual Azure App Service URL after deployment
BASE_URL = "https://your-app-name.azurewebsites.net"

# Test API keys (PLACEHOLDER FORMAT - replace with your actual keys)
TEST_KEYS = {
    "full_access": "<YOUR-DEMO-API-KEY>",        # Full access (tools + resources) - PLACEHOLDER
    "limited_access": "<YOUR-LIMITED-API-KEY>",  # Limited access (tools only) - PLACEHOLDER
    "invalid": "invalid-key-999"                 # Invalid key for testing
}

def test_endpoint(endpoint, headers=None, method="GET", json_data=None):
    """Test an endpoint and return the response."""
    url = f"{BASE_URL}{endpoint}"
    try:
        if method == "GET":
            response = requests.get(url, headers=headers, timeout=30)
        elif method == "POST":
            response = requests.post(url, headers=headers, json=json_data, timeout=30)
        else:
            raise ValueError(f"Unsupported method: {method}")
        
        return {
            "status_code": response.status_code,
            "headers": dict(response.headers),
            "content": response.text[:500] + "..." if len(response.text) > 500 else response.text,
            "json": response.json() if response.headers.get('content-type', '').startswith('application/json') else None
        }
    except requests.RequestException as e:
        return {"error": str(e)}
    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}"}

def main():
    print("🚀 Testing Azure-deployed MCP Server Authentication")
    print("=" * 60)
    print(f"Base URL: {BASE_URL}")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print()

    # Test 1: Health check (public endpoint)
    print("1️⃣ Testing health endpoint (public)")
    result = test_endpoint("/health")
    print(f"   Status: {result.get('status_code', 'ERROR')}")
    if result.get('json'):
        print(f"   Response: {result['json']}")
    print()

    # Test 2: Unauthenticated MCP endpoint (should fail)
    print("2️⃣ Testing MCP endpoint without authentication (should fail)")
    result = test_endpoint("/mcp/stream")
    print(f"   Status: {result.get('status_code', 'ERROR')}")
    if result.get('json'):
        print(f"   Response: {result['json']}")
    print()

    # Test 3: Valid full access key
    print("3️⃣ Testing with full access API key")
    headers = {"Authorization": f"Bearer {TEST_KEYS['full_access']}"}
    
    # Test auth info endpoint
    result = test_endpoint("/auth/info", headers=headers)
    print(f"   Auth Info Status: {result.get('status_code', 'ERROR')}")
    if result.get('json'):
        print(f"   Auth Response: {result['json']}")
    
    # Test tools endpoint
    result = test_endpoint("/tools", headers=headers)
    print(f"   Tools Status: {result.get('status_code', 'ERROR')}")
    if result.get('json'):
        tools = result['json'].get('tools', [])
        print(f"   Available tools: {len(tools)} tools")
        for tool in tools[:2]:  # Show first 2 tools
            print(f"     - {tool.get('name', 'Unknown')}")
    
    # Test resources endpoint
    result = test_endpoint("/resources", headers=headers)
    print(f"   Resources Status: {result.get('status_code', 'ERROR')}")
    if result.get('json'):
        resources = result['json'].get('resources', [])
        print(f"   Available resources: {len(resources)} resources")
    print()

    # Test 4: Limited access key
    print("4️⃣ Testing with limited access API key")
    headers = {"Authorization": f"Bearer {TEST_KEYS['limited_access']}"}
    
    # Test tools endpoint (should work)
    result = test_endpoint("/tools", headers=headers)
    print(f"   Tools Status: {result.get('status_code', 'ERROR')}")
    
    # Test resources endpoint (should fail with 403)
    result = test_endpoint("/resources", headers=headers)
    print(f"   Resources Status: {result.get('status_code', 'ERROR')} (should be 403)")
    if result.get('json'):
        print(f"   Resources Response: {result['json']}")
    print()

    # Test 5: Invalid API key
    print("5️⃣ Testing with invalid API key")
    headers = {"Authorization": f"Bearer {TEST_KEYS['invalid']}"}
    result = test_endpoint("/tools", headers=headers)
    print(f"   Status: {result.get('status_code', 'ERROR')} (should be 401)")
    if result.get('json'):
        print(f"   Response: {result['json']}")
    print()

    # Test 6: Weather tool functionality
    print("6️⃣ Testing weather tool functionality")
    headers = {"Authorization": f"Bearer {TEST_KEYS['full_access']}"}
    
    # Test get_forecast tool
    forecast_request = {
        "method": "tools/call",
        "params": {
            "name": "get_forecast",
            "arguments": {
                "latitude": 40.7128,
                "longitude": -74.0060
            }
        }
    }
    
    result = test_endpoint("/tools/call", headers=headers, method="POST", json_data=forecast_request)
    print(f"   Weather Forecast Status: {result.get('status_code', 'ERROR')}")
    if result.get('json'):
        content = result['json'].get('content', [])
        if content:
            print(f"   Forecast data retrieved successfully: {len(str(content))} chars")
        else:
            print(f"   Response: {result['json']}")
    print()

    print("✅ Authentication testing complete!")
    print("🌐 Your authenticated MCP server is running on Azure!")

if __name__ == "__main__":
    main()
