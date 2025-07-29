# blender-remote

🎯 **Automate Blender workflows with external Python control, background operation, and LLM integration**

blender-remote enables comprehensive Blender automation through multiple interfaces: auto-start service for external Python control, background mode operation for headless workflows, MCP server for LLM integration, and direct Python APIs. Perfect for CI/CD pipelines, render farms, and AI-assisted 3D workflows.

## ✨ Core Features

### 1. **🔧 Auto-Start Service for Blender Automation**
Enable headless Blender automation via external Python control:

```bash
# Set auto-start and launch Blender
export BLD_REMOTE_MCP_START_NOW=1
blender &

# External Python script controls Blender
python automation_script.py  # Connects to port 6688, executes Blender operations
```

**Perfect for**: CI/CD pipelines, batch processing, render farms, automated asset generation

### 2. **🖥️ Background Mode Operation** 
Run Blender completely headless with `blender --background`:

```python
# start_blender_bg.py - Script to enable service in background mode
import bpy
import bld_remote
bld_remote.start_mcp_service()  # Starts service on port 6688
```

```bash
# Launch headless Blender with service
blender --background --python start_blender_bg.py &

# External control works identically
python your_automation.py  # Same API, no GUI required
```

**Perfect for**: Headless servers, Docker containers, cloud rendering, automated workflows

### 3. **🤖 MCP Server for LLM Integration**
Standard Model Context Protocol server for AI assistant control:

```bash
uvx blender-remote  # Starts MCP server for Claude, VSCode, Cursor, etc.
```

**Compatible with**: VSCode Claude, Claude Desktop, Cursor, and other MCP-compatible LLM IDEs

### 4. **🐍 Python Control Classes**
Direct Python API for programmatic Blender control *(coming soon)*

**Enables**: Native Python integration, custom automation tools, scripted workflows

## 🚀 Quick Start

### For Automation Users

**Auto-Start Service Pattern:**
```bash
# 1. Install addon (see details below) and set auto-start
export BLD_REMOTE_MCP_START_NOW=1
blender &

# 2. External Python automation via socket connection
python -c "
import socket, json
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(('127.0.0.1', 6688))
cmd = {'type': 'execute_code', 'params': {'code': 'bpy.ops.mesh.primitive_cube_add()'}}
sock.send(json.dumps(cmd).encode())
response = sock.recv(4096).decode()
print('Blender automated:', response)
sock.close()
"
```

**Background Mode Pattern:**
```bash
# 1. Create service startup script
echo 'import bld_remote; bld_remote.start_mcp_service()' > start_bg_service.py

# 2. Launch headless Blender with service
blender --background --python start_bg_service.py &

# 3. Same automation API works without GUI
python your_automation_script.py
```

### For LLM Users

### 1. Install Blender Add-on

#### Create the Add-on Zip File

```bash
# Navigate to the blender_addon directory from project root
cd blender-remote/  # Your cloned repository
cd blender_addon/
zip -r bld_remote_mcp.zip bld_remote_mcp/
```

**Note**: The `bld_remote_mcp.zip` file is not included in the repository and must be created by users from the `blender_addon/bld_remote_mcp/` directory.

#### Install via Blender GUI (Recommended)

1. **Open Blender**
2. Go to `Edit > Preferences` from the top menu bar
3. In the Preferences window, select the `Add-ons` tab
4. Click the `Install...` button (opens Blender's file browser)
5. Navigate to your `blender_addon/` directory and select `bld_remote_mcp.zip`
6. Click `Install Add-on`
7. **Search for "BLD Remote MCP" and enable it by ticking the checkbox**

#### Alternative: Manual Installation

```bash
# Copy directly to Blender addons directory
mkdir -p ~/.config/blender/4.4/scripts/addons/
cp -r bld_remote_mcp/ ~/.config/blender/4.4/scripts/addons/
```

#### Verify Installation

**Important**: This add-on has no visible GUI panel. Verify installation via system console:

**Windows**: `Window > Toggle System Console`  
**macOS/Linux**: Start Blender from terminal

**Look for these log messages when enabling the add-on:**
```
=== BLD REMOTE MCP ADDON REGISTRATION STARTING ===
🚀 DEV-TEST-UPDATE: BLD Remote MCP v1.0.2 Loading!
...
✅ BLD Remote MCP addon registered successfully
=== BLD REMOTE MCP ADDON REGISTRATION COMPLETED ===
```

**If auto-start is enabled, you'll also see:**
```
✅ Starting server on port 6688
✅ BLD Remote server STARTED successfully on port 6688
Server is now listening for connections on 127.0.0.1:6688
```

### 2. Start Blender with Auto-Service

```bash
# Set environment variables and start Blender
export BLD_REMOTE_MCP_PORT=6688
export BLD_REMOTE_MCP_START_NOW=1
blender &  # or "blender --background" for headless mode
```

### 3. Configure Your LLM IDE

**VSCode (with Claude/Cursor extensions):**
```json
{
  "mcp": {
    "servers": {
      "blender-remote": {
        "type": "stdio",
        "command": "uvx",
        "args": ["blender-remote"]
      }
    }
  }
}
```

**Claude Desktop:**
```json
{
  "mcpServers": {
    "blender-remote": {
      "command": "uvx",
      "args": ["blender-remote"]
    }
  }
}
```

### 4. Start Creating with AI! 🎉

Your LLM can now:
- **Inspect scenes**: "What objects are in the current Blender scene?"
- **Execute code**: "Create a blue metallic cube at position (2, 0, 0)"
- **Take screenshots**: "Show me the current viewport"
- **Automate workflows**: "Create a donut tutorial scene with lighting"

## 🏗️ Architecture

**Multi-Interface Design for Different Automation Needs:**

```
External Python Scripts ←────┐
                            │
LLM IDE (VSCode/Claude) ←────┼─→ JSON-TCP (port 6688) ←─ BLD_Remote_MCP (Blender addon)
                            │                                      ↓
blender-remote (uvx MCP) ←───┘                               Blender Python API
                                                                   ↓
Python Control Classes* ←─────────────────────────────→ Blender (GUI or --background)
```

**Three Control Pathways:**
1. **Direct Socket Connection**: External Python → JSON-TCP → Blender
2. **MCP Protocol**: LLM IDE → uvx blender-remote → JSON-TCP → Blender  
3. **Python Classes**: Python → Direct API → Blender *(coming soon)*

## 📋 Available MCP Tools

| Tool | Description | Example Use |
|------|-------------|-------------|
| `get_scene_info()` | List all objects, materials, and scene properties | Scene analysis |
| `get_object_info(name)` | Get detailed object properties | Object inspection |
| `execute_blender_code(code)` | Run Python code in Blender context | Any Blender operation |
| `get_viewport_screenshot()` | Capture viewport as base64 image | Visual feedback |
| `check_connection_status()` | Verify service health | Debugging |

## 🔧 Advanced Usage

### Automation Integration

**CI/CD Pipeline Example:**
```yaml
# .github/workflows/blender-automation.yml
- name: Setup Blender Automation
  run: |
    export BLD_REMOTE_MCP_START_NOW=1
    blender --background --python setup_service.py &
    sleep 10  # Wait for service startup
    python batch_render_pipeline.py
```

**Docker Container:**
```dockerfile
FROM blender:4.4.3
COPY blender_addon/bld_remote_mcp/ /opt/blender/scripts/addons/
ENV BLD_REMOTE_MCP_START_NOW=1
CMD ["blender", "--background", "--python", "/app/automation.py"]
```

### Development Installation

```bash
# Clone and install from source
git clone https://github.com/igamenovoer/blender-remote.git
cd blender-remote
pixi install  # or pip install -e .
```

### CLI Tools (for testing)

```bash
# Check connection to BLD_Remote_MCP service
blender-remote status

# Execute Blender Python code
blender-remote exec "bpy.ops.mesh.primitive_cube_add()"

# Get scene information
blender-remote scene

# Capture viewport screenshot
blender-remote screenshot
```

### Python API (for custom scripts)

```python
# Direct connection to BLD_Remote_MCP service
import socket
import json

# Connect to service
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(('127.0.0.1', 6688))

# Send command
command = {"type": "execute_code", "params": {"code": "bpy.ops.mesh.primitive_cube_add()"}}
sock.sendall(json.dumps(command).encode('utf-8'))

# Get response
response = json.loads(sock.recv(4096).decode('utf-8'))
print(response)
sock.close()
```

## 🧪 Testing & Development

This project uses [pixi](https://pixi.sh) for environment management:

```bash
# Install pixi (if not already installed)
curl -fsSL https://pixi.sh/install.sh | bash

# Create development environment
pixi install

# Run comprehensive test suite
pixi run python tests/run_dual_service_tests.py

# Quick smoke test
pixi run python tests/smoke_test.py

# Test MCP server functionality
pixi run python tests/mcp-server/test_fastmcp_server.py
```

## 📁 Project Structure

```
blender-remote/
├── blender_addon/              # Blender add-ons
│   └── bld_remote_mcp/        # BLD_Remote_MCP service (port 6688)
├── src/blender_remote/         # Python package (src layout)
│   ├── mcp_server.py          # FastMCP server implementation
│   └── cli.py                 # CLI tools
├── tests/                      # Comprehensive test suite
│   ├── mcp-server/            # MCP server functionality tests
│   ├── integration/           # Service comparison tests
│   └── others/                # Development scripts
├── docs/                      # Documentation
├── examples/                  # Usage examples
└── context/                   # AI assistant resources
```

## 🔧 Automation Capabilities

### Background Mode Support

**Key Advantage**: Full automation support in both GUI and headless environments:

- **GUI Mode**: Complete functionality including viewport screenshots
- **Background Mode**: Code execution, scene manipulation, rendering (no screenshots)
- **Automatic Detection**: Service gracefully handles mode-specific limitations

**Automation Patterns:**

```bash
# Interactive development with screenshots
export BLD_REMOTE_MCP_START_NOW=1
blender &  # GUI mode with auto-start service

# Production automation (CI/CD, render farms)
blender --background --python start_service.py &  # Headless with service
```

### External Control Examples

**Batch Asset Generation:**
```python
# automation_example.py
import socket, json, time

def send_blender_command(cmd_type, params={}):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(('127.0.0.1', 6688))
    command = {"type": cmd_type, "params": params}
    sock.send(json.dumps(command).encode())
    response = json.loads(sock.recv(4096).decode())
    sock.close()
    return response

# Automated workflow
send_blender_command("execute_code", {"code": "bpy.ops.object.select_all(action='DELETE')"})
send_blender_command("execute_code", {"code": "bpy.ops.mesh.primitive_cube_add(location=(0,0,0))"})
send_blender_command("execute_code", {"code": "bpy.context.object.name = 'AutoCube'"})
print("✅ Automated asset creation complete")
```

## 🔧 Troubleshooting

### Common Issues

**"Connection refused" error:**
- Ensure Blender is running with BLD_Remote_MCP addon enabled
- **Verify addon installation**: Check system console for registration messages:
  ```
  ✅ BLD Remote MCP addon registered successfully
  ✅ BLD Remote server STARTED successfully on port 6688
  ```
- Check service is listening: `netstat -tlnp | grep 6688`
- Try restarting Blender with environment variables set

**Add-on not working:**
- **Critical**: Check system console (Windows: `Window > Toggle System Console`, macOS/Linux: start from terminal)
- Look for registration messages when enabling the add-on
- If no messages appear, the add-on failed to load - check console for errors

**"No module named 'fastmcp'" error:**
- Install with uvx: `uvx blender-remote` (handles dependencies automatically)
- For development: `pixi run pip install fastmcp>=2.0.0`

**Screenshots not working:**
- Only available in GUI mode (`blender`, not `blender --background`)
- Service will return clear error message in background mode

### Debug Mode

```bash
# Test MCP server directly
pixi run python -m blender_remote.mcp_server

# Test with FastMCP inspector
pixi run fastmcp dev src/blender_remote/mcp_server.py
```

## 🤝 Contributing

Contributions are welcome! Please see our comprehensive test suite and development workflow:

1. **Fork the repository** and create a feature branch
2. **Run tests**: `pixi run python tests/run_dual_service_tests.py`
3. **Add tests** for new functionality
4. **Submit pull request** with clear description

## 📄 License

[MIT License](LICENSE)

## 🙏 Credits

This project was inspired by [ahujasid/blender-mcp](https://github.com/ahujasid/blender-mcp), which demonstrated the potential for integrating Blender with the Model Context Protocol. We extend our gratitude to the original developers for pioneering this concept.

blender-remote builds upon this foundation with enhanced features including background mode support, thread-safe operations, comprehensive testing, and production-ready deployment capabilities.

## 🔗 Links

- **📚 Documentation**: [https://igamenovoer.github.io/blender-remote/](https://igamenovoer.github.io/blender-remote/)
- **🐛 Issue Tracker**: [Report bugs and request features](https://github.com/igamenovoer/blender-remote/issues)
- **💬 Discussions**: [Community support](https://github.com/igamenovoer/blender-remote/discussions)
- **🎥 Examples**: [Usage examples and workflows](https://github.com/igamenovoer/blender-remote/tree/main/examples)

---

**🎯 Ready to enhance your Blender workflow with AI? Start with `uvx blender-remote` today!**