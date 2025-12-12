# Dockerlab Manager

[![Tests](https://github.com/charles-adedotun/dockerlab-manager/actions/workflows/test.yml/badge.svg)](https://github.com/charles-adedotun/dockerlab-manager/actions/workflows/test.yml)

CLI tool to manage Docker Compose services across your homelab.

## The Problem

You have 15 Docker Compose files scattered across three machines. Some are in `/opt/services`, others in home directories, a few mounted via NFS. When you need to restart a service, you're grepping through bash history to remember where that compose file lives and what you named it.

Want to see which services are running? SSH to each host, cd to each directory, run `docker-compose ps`. Want to update everything? Write a bash script that you'll forget to update when you add the next service.

Dockerlab Manager solves this with a single config file that maps all your services and a CLI that lets you manage everything from one place.

## What It Does

- **Unified Interface**: One command to control all compose services across all hosts
- **Config-Driven**: `config.json` defines where everything lives
- **Remote Support**: Manage services over SSH or locally
- **Smart Discovery**: Auto-detect running services and their health
- **Batch Operations**: Start, stop, restart, or update multiple services at once
- **Status Overview**: See all services and their states in one view
- **Log Aggregation**: Tail logs from any service, local or remote

## Tech Stack

- **Python 3.10+**: Core application
- **Click**: CLI framework
- **Docker SDK**: Python Docker client
- **Paramiko**: SSH for remote operations
- **Rich**: Terminal formatting and output

## Quick Start

### Installation

```bash
# Install from PyPI (when published)
pip install dockerlab-manager

# Or install from source
git clone https://github.com/charles-adedotun/dockerlab-manager.git
cd dockerlab-manager
pip install -e .
```

### Initial Setup

Create `~/.config/dockerlab/config.json`:

```json
{
  "services": [
    {
      "name": "pihole",
      "host": "local",
      "compose_file": "/opt/homelab/services/pihole/docker-compose.yml",
      "description": "Network DNS and ad blocking"
    },
    {
      "name": "wireguard",
      "host": "local",
      "compose_file": "/opt/homelab/services/wireguard/docker-compose.yml",
      "description": "VPN server"
    },
    {
      "name": "monitoring",
      "host": "192.168.1.20",
      "compose_file": "/home/user/monitoring/docker-compose.yml",
      "ssh_user": "admin",
      "ssh_key": "~/.ssh/id_rsa",
      "description": "Prometheus and Grafana"
    }
  ],
  "defaults": {
    "ssh_user": "admin",
    "ssh_key": "~/.ssh/id_rsa",
    "compose_timeout": 300
  }
}
```

### Basic Usage

```bash
# List all configured services
dockerlab list

# Show status of all services
dockerlab status

# Start a service
dockerlab start pihole

# Stop a service
dockerlab stop pihole

# Restart a service
dockerlab restart wireguard

# Update service (pull latest images and recreate)
dockerlab update monitoring

# Tail logs
dockerlab logs pihole --follow

# Batch operations
dockerlab start pihole wireguard monitoring

# Start everything
dockerlab start --all

# Interactive mode
dockerlab interactive
```

## Configuration Reference

### Service Definition

```json
{
  "name": "service-name",           // Unique identifier
  "host": "local",                  // "local" or IP/hostname
  "compose_file": "/path/to/file",  // Absolute path to docker-compose.yml
  "description": "What it does",    // Optional description
  "ssh_user": "user",               // Override default SSH user
  "ssh_key": "~/.ssh/key",          // Override default SSH key
  "ssh_port": 22,                   // Override default SSH port
  "working_dir": "/path",           // Override working directory
  "env_file": "/path/.env",         // Additional environment file
  "depends_on": ["other-service"]   // Service dependencies
}
```

### Global Defaults

```json
{
  "defaults": {
    "ssh_user": "admin",
    "ssh_key": "~/.ssh/id_rsa",
    "ssh_port": 22,
    "compose_timeout": 300,
    "log_lines": 100,
    "parallel_operations": 4
  }
}
```

## Architecture

### Local Operations

```
dockerlab CLI
    ↓
Docker SDK
    ↓
Docker Socket (/var/run/docker.sock)
    ↓
Docker Compose
    ↓
Containers
```

For local services, dockerlab uses the Docker SDK to execute compose commands directly.

### Remote Operations

```
dockerlab CLI
    ↓
Paramiko SSH Client
    ↓
SSH Connection
    ↓
Remote Host Docker Socket
    ↓
Remote Docker Compose
    ↓
Remote Containers
```

For remote services, commands are executed over SSH. The remote host must have docker-compose installed.

### Command Flow

1. **Parse Config**: Load service definitions from `config.json`
2. **Validate**: Check SSH connectivity for remote hosts
3. **Execute**: Run docker-compose commands (up, down, restart, etc.)
4. **Monitor**: Stream output and capture exit codes
5. **Report**: Display results with rich formatting

### Dependency Resolution

If service A depends on service B:

```bash
# Starting A will automatically start B first
dockerlab start A
```

Dependency order is resolved automatically to ensure services start in the correct sequence.

## Advanced Usage

### Environment Variables

Override config values with environment variables:

```bash
export DOCKERLAB_CONFIG=/custom/path/config.json
export DOCKERLAB_SSH_USER=different-user
export DOCKERLAB_LOG_LEVEL=DEBUG

dockerlab status
```

### Filtering

```bash
# Status of services on specific host
dockerlab status --host 192.168.1.20

# Start all services matching pattern
dockerlab start --pattern "monitoring-*"

# Logs from multiple services
dockerlab logs pihole wireguard --tail 50
```

### Health Checks

```bash
# Check if services are healthy
dockerlab health

# Output format:
# ✓ pihole        UP (healthy)
# ✓ wireguard     UP (healthy)
# ✗ monitoring    DOWN (exit code 1)
```

### Batch Updates

```bash
# Update all services (pull images, recreate containers)
dockerlab update --all

# Update only services on local host
dockerlab update --host local

# Dry run to see what would change
dockerlab update --all --dry-run
```

### Export/Import

```bash
# Export current service states
dockerlab export --output snapshot.json

# Restore to previous state
dockerlab import --input snapshot.json
```

## Development

### Setup Development Environment

```bash
git clone https://github.com/charles-adedotun/dockerlab-manager.git
cd dockerlab-manager

# Create virtual environment
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows

# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Type checking
mypy homelab_manager

# Linting
ruff check homelab_manager
black --check homelab_manager
```

### Project Structure

```
dockerlab-manager/
├── homelab_manager/
│   ├── __init__.py
│   ├── cli.py              # Click CLI commands
│   ├── config.py           # Config loading and validation
│   ├── service.py          # Service management logic
│   ├── docker_ops.py       # Docker SDK operations
│   ├── ssh_ops.py          # SSH/remote operations
│   └── utils.py            # Helper functions
├── tests/
│   ├── test_config.py
│   ├── test_service.py
│   └── test_integration.py
├── pyproject.toml          # Package configuration
├── README.md
└── LICENSE
```

### Adding New Commands

Commands are defined in `homelab_manager/cli.py` using Click:

```python
@cli.command()
@click.argument('service_name')
@click.option('--timeout', default=300)
def custom_command(service_name, timeout):
    """Your custom command description."""
    # Implementation
    pass
```

## Troubleshooting

### SSH Connection Fails

```bash
# Test SSH manually
ssh -i ~/.ssh/id_rsa admin@192.168.1.20

# Check SSH key permissions
chmod 600 ~/.ssh/id_rsa

# Add host to known_hosts
ssh-keyscan 192.168.1.20 >> ~/.ssh/known_hosts
```

### Docker Socket Permission Denied

```bash
# Add user to docker group (Linux)
sudo usermod -aG docker $USER
# Log out and back in

# Or run with sudo
sudo dockerlab status
```

### Compose File Not Found

Verify paths in config.json are absolute and correct:

```bash
# On remote host
ssh admin@192.168.1.20 "ls -la /path/to/docker-compose.yml"
```

### Service Won't Start

Check logs for errors:

```bash
dockerlab logs service-name --tail 100

# Or use docker directly
docker-compose -f /path/to/compose.yml logs
```

## Future Roadmap

- **Web UI**: Browser-based dashboard for visual service management
- **Health Checks**: Integrated health monitoring with alerting (Slack, email)
- **Resource Monitoring**: Track CPU, memory, and disk usage per service
- **Template Support**: Service templates for quick deployment of common stacks
- **Backup/Restore**: Automated volume backups with rotation policies
- **Secrets Management**: Integration with Vault or SOPS for sensitive configs
- **Compose v2 Features**: Support for newer Docker Compose features (profiles, etc.)

## Contributing

Contributions welcome. Please open an issue before starting work on major features.

### Development Guidelines

- Use type hints for all functions
- Write tests for new features
- Follow Black code formatting
- Update documentation for user-facing changes
- Keep CLI help text clear and concise

## License

MIT
