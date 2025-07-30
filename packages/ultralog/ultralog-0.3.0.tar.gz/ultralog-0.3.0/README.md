# UltraLog - High-performance Logging System

UltraLog is a high-performance logging system that supports both local file logging and remote API logging.

## Key Features

- **Thread-Safe**: Supports concurrent writes from multiple threads/clients with segmented locks
- **Flexible Configuration**: Extensive logging parameters via CLI or code
- **Automatic Rotation**: File rotation with size limits and backup counts
- **Formatted Output**: Consistent log formatting with timestamps
- **Lifecycle Management**: Proper resource cleanup on shutdown
- **Large Message Handling**: Optimized for messages up to 10KB with chunking
- **Memory Efficient**: Pre-allocated buffers and memory monitoring
- **Priority Queueing**: Smart prioritization of small messages

## Performance

UltraLog is designed for high performance logging with minimal overhead. Below are benchmark results from testing 100,000 log messages:

### Single Thread Performance (INFO level)

| Message Size | Throughput (logs/sec) | Memory Usage |
|--------------|-----------------------|--------------|
| Small (50B)  | 425,000 (+33%)        | 1.5MB (-25%) |
| Medium (500B)| 410,000 (+36%)        | 5.2MB (-31%) |
| Large (5KB)  | 250,000 (+33%)        | 45MB (-26%)  |
| Very Large (10KB) | 180,000        | 80MB         |

### Multi-Thread Performance (10 threads)

| Logger       | Throughput (logs/sec) | Memory Usage |
|--------------|-----------------------|--------------|
| UltraLog     | 450,000 (+41%)        | 0.7MB (-28%) |
| Standard logging | 50,087            | 0.00MB       |
| Loguru       | 46,630               | 0.00MB       |

### Key Performance Advantages

1. **Extreme Throughput**: 9x faster than standard logging (450k logs/sec)
2. **Efficient Memory**: 25-30% lower memory usage
3. **Large Message Support**: Optimized handling of messages up to 10KB
4. **Smart Batching**: Dynamic batch sizes based on message size
5. **Priority Handling**: Small messages get processed faster
6. **Memory Monitoring**: Real-time memory usage tracking

## Installation

```bash
git clone https://github.com/birchkwok/ultralog.git
cd ultralog
pip install -e .
```

## Basic Usage

### Local Mode (Default)

```python
from ultralog import UltraLog

# Basic initialization
logger = UltraLog(name="MyApp")

# Logging examples
logger.debug("Debug message")
logger.info("Application started")
logger.warning("Low disk space")
logger.error("Failed to connect")
logger.critical("System crash")

# Explicit cleanup (optional)
logger.close()
```

### Remote Mode

```python
from ultralog import UltraLog

# Remote configuration
logger = UltraLog(
    name="MyApp",
    server_url="http://your-server-ip:8000",
    auth_token="your_secret_token"
)

# Same logging interface
logger.info("Remote log message")
```

## Log Formatting

UltraLog provides flexible log formatting similar to Python's built-in logging module.

### Default Format
The default format follows loguru-style:
`%(asctime)s | %(levelname)-8s | %(module)s:%(func)s:%(line)s - %(message)s`

Example output:
`2025-04-19 07:50:22.139 | INFO     | __main__:<module>:1 - Application started`

### Format Placeholders
| Placeholder | Description |
|-------------|-------------|
| %(asctime)s | Timestamp (YYYY-MM-DD HH:MM:SS.microseconds) |
| %(levelname)s | Log level (DEBUG, INFO, WARNING, etc.) |
| %(module)s | Module name where log was called |
| %(func)s | Function name where log was called |
| %(line)s | Line number where log was called |
| %(message)s | The log message |

### Custom Formats
You can customize the format by passing a `fmt` parameter to the LogFormatter:

```python
from ultralog import UltraLog

# Custom format logger
logger = UltraLog(
    name="MyApp",
    fmt="[%(levelname)s] %(name)s - %(asctime)s - %(message)s"
)
```

### Available Placeholders

| Placeholder | Description |
|-------------|-------------|
| %(asctime)s | Timestamp (YYYY-MM-DD HH:MM:SS.microseconds) |
| %(levelname)s | Log level (DEBUG, INFO, WARNING, etc.) |
| %(name)s | Logger name |
| %(message)s | The log message |

### Dynamic Format Changes

You can change the log format dynamically after initialization:

```python
logger = UltraLog(name="MyApp")

# Initial format
logger.info("First message")  # Uses default format

# Change format
logger.set_format("%(levelname)s - %(message)s")
logger.info("Second message")  # Uses new simple format

# Change to detailed format
logger.set_format("[%(asctime)s] %(levelname)-8s %(name)s: %(message)s")
logger.info("Third message")  # Uses detailed format
```

### Format Examples

1. Simple format:
   ```python
   fmt="%(levelname)s: %(message)s"
   ```
   Output: `INFO: Application started`

2. Detailed format:
   ```python
   fmt="[%(asctime)s] [%(levelname)-8s] %(name)-15s: %(message)s"
   ```
   Output: `[2025-04-18 21:17:16.205283] [INFO    ] MyApp          : Application started`

3. JSON format:
   ```python
   fmt='{"time": "%(asctime)s", "level": "%(levelname)s", "logger": "%(name)s", "msg": "%(message)s"}'
   ```
   Output: `{"time": "2025-04-18 21:17:16.205283", "level": "INFO", "logger": "MyApp", "msg": "Application started"}`

## Server Configuration

Run the server with custom parameters:

```bash
python -m ultralog.server \
  --log-dir /var/log/myapp \
  --log-file app.log \
  --log-level DEBUG \
  --max-file-size 10485760 \
  --backup-count 5 \
  --console-output \
  --auth-token your_secure_token
```

## Advanced Configuration

### UltraLog Initialization Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| name | str | "UltraLogger" | Logger name prefix |
| fp | str | None | Local log file path |
| level | str | "INFO" | Minimum log level |
| truncate_file | bool | False | Truncate existing log file |
| with_time | bool | True | Include timestamps |
| max_file_size | int | 10MB | Max file size before rotation |
| backup_count | int | 5 | Number of backup files |
| console_output | bool | False | Print to console |
| force_sync | bool | False | Force synchronous writes |
| enable_rotation | bool | True | Enable log rotation |
| file_buffer_size | int | 256KB | File write buffer size |
| batch_size | int | None | Remote batch size |
| flush_interval | float | None | Remote flush interval |
| server_url | str | None | Remote server URL |
| auth_token | str | None | Remote auth token |

## Development

### Running Tests

```bash
pytest tests/
```

### Building Package

```bash
python -m build
```

## API Documentation

Interactive API docs available at:
`http://localhost:8000/docs` when server is running

## Best Practices

1. For production:
   - Use proper log rotation settings
   - Set appropriate log levels
   - Use secure authentication tokens
   - Monitor log file sizes

2. For remote logging:
   - Implement retry logic in your application
   - Consider batch sizes for high throughput
   - Monitor network connectivity

3. General:
   - Use meaningful logger names
   - Include context in log messages
   - Regularly review log retention policy
