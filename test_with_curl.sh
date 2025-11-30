#!/bin/bash
# Simple MCP server verification
# 
# The MCP server uses stdio (not HTTP), so we test the underlying tools instead.
# For actual MCP testing, use Claude Desktop or an MCP client.

echo "🚀 GIS MCP Server Verification"
echo "================================"
echo ""
echo "Testing underlying GIS tools..."
echo ""

python test_mcp_server.py

echo ""
echo "✅ GIS tools verified!"
echo ""
echo "To test the actual MCP server:"
echo "  1. Add to Claude Desktop config:"
echo "     ~/.claude_config/claude_desktop_config.json"
echo ""
echo '     {
       "mcpServers": {
         "gis": {
           "command": "python",
           "args": ["'$(pwd)'/main.py"]
         }
       }
     }'
echo ""
echo "  2. Restart Claude Desktop"
echo ""
echo "  3. Ask Claude: 'What is the distance from NYC to LA?'"
echo ""
echo "Or use the NLP interface directly:"
echo "  python demo_nlp.py"
