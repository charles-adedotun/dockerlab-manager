# DockerLab Manager

DockerLab Manager is a Python-based CLI tool designed to simplify the management of Docker services in a homelab environment. It provides an easy-to-use interface for starting, stopping, and monitoring Docker services defined in Docker Compose files.

## Features

- Start and stop individual services
- Start and stop all services simultaneously
- Check the status of services
- Configurable service definitions
- Support for both local and remote Docker Compose files
- Comprehensive test suite including unit and functional tests

## Requirements

- Python 3.10+
- Docker
- Docker Compose

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/charles-adedotun/dockerlab-manager.git
   cd dockerlab-manager
   ```

2. Install the required dependencies:
   ```
   make install
   ```

## Usage

DockerLab Manager uses a `config.json` file to define services. Here's an example structure:

```json
{
  "services": [
    {
      "name": "service1",
      "enabled": true,
      "core": true,
      "compose_file": "./services/service1/docker-compose.yml"
    },
    {
      "name": "service2",
      "enabled": true,
      "compose_file": "https://example.com/service2-compose.yml"
    }
  ]
}
```

### Commands

- Start a service: `make start <service_name>`
- Stop a service: `make stop <service_name>`
- Start all services: `make start-all`
- Stop all services: `make stop-all`
- Check status of services: `make status`

## Development

### Running Tests

To run the test suite:

```
make test
```

For test coverage:

```
make coverage
```

### Code Formatting and Linting

To format the code:

```
make format
```

To run the linter:

```
make lint
```

## CI/CD

This project uses GitHub Actions for continuous integration. The workflow is defined in `.github/workflows/tests.yml` and runs the test suite on every push to the main branch and for pull requests.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

[MIT License](LICENSE)