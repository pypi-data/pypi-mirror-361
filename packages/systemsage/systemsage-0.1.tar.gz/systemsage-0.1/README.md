# SystemSage

A powerful cross-platform system management and monitoring tool that provides comprehensive system insights and management capabilities.

## Features

- System resource monitoring (CPU, Memory, Disk)
- Process management
- Network interface monitoring
- System alerts and diagnostics
- Service management
- Docker container management
- Kubernetes cluster monitoring
- Log management
- Security monitoring
- Performance analysis
- System health checks

## Installation

```bash
pip install systemsage
```

For additional cloud features (Docker, Kubernetes, HTTP requests):
```bash
pip install systemsage[cloud]
```

## Quick Start

```python
from SystemSage.server import mcp

# Get system metrics
print(mcp.get_cpu_usage())
print(mcp.get_memory_usage())
print(mcp.get_disk_usage())

# Monitor system resources
print(mcp.monitor_system_resources(duration=10))

# Get system alerts
print(mcp.get_system_alerts())
```

## Command Line Usage

```bash
# Run the MCP server
systemsage

# Or run as a module
python -m SystemSage
```

## Requirements

- Python 3.10 or higher
- psutil>=5.9.0
- fastmcp>=1.0.0
- click>=8.1.0

### Optional Dependencies

- requests>=2.31.0 (for cloud services)
- docker>=6.1.0 (for Docker management)
- kubernetes>=28.1.0 (for Kubernetes monitoring)

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. 