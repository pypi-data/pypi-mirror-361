# Platon-Daytona SDK for Python

[![PyPI version](https://badge.fury.io/py/platon-daytona.svg)](https://badge.fury.io/py/platon-daytona)
[![Python Support](https://img.shields.io/pypi/pyversions/platon-daytona.svg)](https://pypi.org/project/platon-daytona/)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

A Python SDK for interacting with the Daytona API, providing a simple interface for Daytona Sandbox management, Git operations, file system operations, and language server protocol support.

**This is a fork of the original Daytona SDK, enhanced and maintained by Platon.AI.**

## Key Features

- **Sandbox Management**: Create, manage and remove sandboxes
- **Git Operations**: Clone repositories, manage branches, and more
- **File System Operations**: Upload, download, search and manipulate files
- **Language Server Protocol**: Interact with language servers for code intelligence
- **Process Management**: Execute code and commands in sandboxes
- **Async Support**: Full async/await support for modern Python applications

## Installation

You can install the package using pip:

```bash
pip install platon-daytona
```

## Quick Start

Here's a simple example of using the SDK:

```python
from daytona import Daytona

# Initialize using environment variables
daytona = Daytona()

# Create a sandbox
sandbox = daytona.create()

# Run code in the sandbox
response = sandbox.process.code_run('print("Hello World!")')
print(response.result)

# Clean up when done
daytona.delete(sandbox)
```

## Configuration

The SDK can be configured using environment variables or by passing a configuration object:

```python
from daytona import Daytona, DaytonaConfig

# Initialize with configuration
config = DaytonaConfig(
    api_key="your-api-key",
    api_url="your-api-url",
    target="us"
)
daytona = Daytona(config)
```

Or using environment variables:

- `DAYTONA_API_KEY`: Your Daytona API key
- `DAYTONA_API_URL`: The Daytona API URL
- `DAYTONA_TARGET`: Your target environment

You can also customize sandbox creation:

```python
sandbox = daytona.create(CreateSandboxFromSnapshotParams(
    language="python",
    env_vars={"PYTHON_ENV": "development"},
    auto_stop_interval=60,  # Auto-stop after 1 hour of inactivity
    auto_archive_interval=60  # Auto-archive after a Sandbox has been stopped for 1 hour
))
```

## Examples

### Execute Commands

```python
# Execute a shell command
response = sandbox.process.exec('echo "Hello, World!"')
print(response.result)

# Run Python code
response = sandbox.process.code_run('''
x = 10
y = 20
print(f"Sum: {x + y}")
''')
print(response.result)
```

### File Operations

```python
# Upload a file
sandbox.fs.upload_file(b'Hello, World!', 'path/to/file.txt')

# Download a file
content = sandbox.fs.download_file('path/to/file.txt')

# Search for files
matches = sandbox.fs.find_files(root_dir, 'search_pattern')
```

### Git Operations

```python
# Clone a repository
sandbox.git.clone('https://github.com/example/repo', 'path/to/clone')

# List branches
branches = sandbox.git.branches('path/to/repo')

# Add files
sandbox.git.add('path/to/repo', ['file1.txt', 'file2.txt'])
```

### Language Server Protocol

```python
# Create and start a language server
lsp = sandbox.create_lsp_server('typescript', 'path/to/project')
lsp.start()

# Notify the lsp for the file
lsp.did_open('path/to/file.ts')

# Get document symbols
symbols = lsp.document_symbols('path/to/file.ts')

# Get completions
completions = lsp.completions('path/to/file.ts', {"line": 10, "character": 15})
```

### Async Support

```python
import asyncio
from daytona import AsyncDaytona

async def main():
    daytona = AsyncDaytona()
    sandbox = await daytona.create()
    
    response = await sandbox.process.code_run('print("Async Hello!")')
    print(response.result)
    
    await daytona.delete(sandbox)

asyncio.run(main())
```

## What's Different in This Fork

This fork includes several enhancements over the original Daytona SDK:

- Enhanced error handling and debugging capabilities
- Additional utility functions for common operations
- Improved documentation and examples
- Better type hints and IDE support
- Regular updates and maintenance by Platon.AI team

## API Compatibility

This package maintains 100% API compatibility with the original Daytona SDK. You can use it as a drop-in replacement:

```python
# Import works exactly the same as original
from daytona import Daytona, DaytonaConfig, AsyncDaytona
```

## Requirements

- Python 3.8 or higher
- Valid Daytona API credentials

## Contributing

We welcome contributions! This project is based on the original Daytona SDK and follows the same contribution guidelines.

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

## Support

- **Issues**: [GitHub Issues](https://github.com/galaxyeye/daytona/issues)
- **Documentation**: [Project Documentation](https://galaxyeye.github.io/daytona)
- **Email**: ivincent.zhang@gmail.com

## Acknowledgments

This project is based on the excellent work by Daytona Platforms Inc. We thank the original team for creating such a powerful SDK.

---

**Note**: This is an independent fork maintained by Platon.AI. For the original Daytona SDK, please visit the official Daytona repository.
