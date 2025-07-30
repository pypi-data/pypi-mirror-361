# ConfigBee Server Side SDK for Python

ConfigBee Server SDK is a Python client library for integrating your application with ConfigBee, a feature flags and configuration management service. This library allows you to dynamically manage feature flags and configuration settings in your application.

## Features

- 🚀 **Real-time Updates**: Automatic configuration updates with live streaming
- 🔧 **Multiple Data Types**: Support for boolean flags, text, numbers, and JSON configurations
- 🎯 **Hyper Availability**: Intelligent fallback across multiple cloud endpoints
- 🔄 **Async/Await Support**: Full async support with thread-safe synchronous methods
- 📦 **Lightweight**: Minimal dependencies with efficient caching
- 🛡️ **Error Handling**: Robust error handling and automatic retries

## Installation

```bash
pip install configbee-server-sdk
```

## Quick Start

### Basic Usage

```python
import configbee

# Initialize client
client = configbee.get_client(
    account_id="your_account_id",
    project_id="your_project_id", 
    environment_id="your_environment_id"
)

# Wait for initial load
client.wait_to_load()

# Get feature flags
is_feature_enabled = client.get_flag("new_feature")
if is_feature_enabled:
    print("New feature is enabled!")

# Get other configuration types
api_endpoint = client.get_text("api_endpoint")
max_retries = client.get_number("max_retries")
config_data = client.get_json("app_config")
```

### Async Usage

```python
import asyncio
import configbee

async def main():
    client = configbee.get_client(
        account_id="your_account_id",
        project_id="your_project_id",
        environment_id="your_environment_id"
    )
    
    # Wait for initial load (async)
    await client.await_to_load()
    
    # Use configurations
    feature_enabled = client.get_flag("beta_feature")
    print(f"Beta feature enabled: {feature_enabled}")

asyncio.run(main())
```

## API Reference

### Client Initialization

#### `configbee.get_client(account_id, project_id, environment_id, logger=None)`

Creates or returns an existing ConfigBee client instance.

**Parameters:**
- `account_id` (str): Your ConfigBee account ID
- `project_id` (str): Your ConfigBee project ID  
- `environment_id` (str): Your ConfigBee environment ID
- `logger` (logging.Logger, optional): Custom logger instance

**Returns:** `ConfigbeeClient` instance

### Configuration Retrieval Methods

#### `get_flag(key)` → `Optional[bool]`
Retrieves a boolean feature flag value.

```python
enabled = client.get_flag("feature_toggle")
```

#### `get_text(key)` → `Optional[str]`
Retrieves a text configuration value.

```python
api_url = client.get_text("api_endpoint")
```

#### `get_number(key)` → `Optional[float]`
Retrieves a numeric configuration value.

```python
timeout = client.get_number("request_timeout")
```

#### `get_json(key)` → `Optional[object]`
Retrieves a JSON configuration value.

```python
config = client.get_json("app_settings")
```

### Bulk Retrieval Methods

#### `get_all_flags()` → `Optional[Dict[str, bool]]`
Retrieves all feature flags.

```python
all_flags = client.get_all_flags()
# Returns: {"feature_a": True, "feature_b": False, ...}
```

#### `get_all_texts()` → `Optional[Dict[str, str]]`
Retrieves all text configurations.

#### `get_all_numbers()` → `Optional[Dict[str, float]]`
Retrieves all numeric configurations.

#### `get_all_jsons()` → `Optional[Dict[str, object]]`
Retrieves all JSON configurations.

### Loading and Status Methods

#### `wait_to_load(timeout=40)`
Blocks until the client is loaded or timeout occurs.

**Parameters:**
- `timeout` (int): Maximum seconds to wait (default: 40)

**Raises:** `Exception` if loading fails or times out

#### `await_to_load(timeout=40)`
Async version of `wait_to_load()`.

#### `status` → `ConfigbeeStatus`
Returns the current client status:
- `INITIALIZING`: Client is loading initial configuration
- `ACTIVE`: Client is ready and receiving updates
- `DEACTIVE`: Client is inactive
- `ERROR`: Client encountered an error

## Error Handling

The SDK includes comprehensive error handling:

```python
import configbee
import logging

# Set up logging to see error details
logging.basicConfig(level=logging.INFO)

try:
    client = configbee.get_client("account", "project", "environment")
    client.wait_to_load(timeout=30)
    
    # Safe configuration access
    feature_enabled = client.get_flag("my_feature")
    if feature_enabled is None:
        print("Feature flag not found or client not ready")
    
except Exception as e:
    print(f"ConfigBee initialization failed: {e}")
```

## Configuration Types

ConfigBee supports four configuration types:

| Type | Method | Python Type | Use Case |
|------|--------|-------------|----------|
| FLAG | `get_flag()` | `bool` | Feature toggles, A/B testing |
| TEXT | `get_text()` | `str` | API endpoints, messages |
| NUMBER | `get_number()` | `float` | Timeouts, limits, percentages |
| JSON | `get_json()` | `object` | Complex configurations |

## Advanced Usage

### Custom Logging

```python
import logging
import configbee

# Create custom logger
logger = logging.getLogger("my_app.configbee")
logger.setLevel(logging.DEBUG)

client = configbee.get_client(
    account_id="account_id",
    project_id="project_id", 
    environment_id="env_id",
    logger=logger
)
```

### Multiple Environments

```python
import configbee

# Development environment
dev_client = configbee.get_client("account", "project", "dev")

# Production environment  
prod_client = configbee.get_client("account", "project", "prod")

# Clients are automatically cached and reused
```

### FastAPI Integration

ConfigBee works seamlessly with FastAPI applications. Here's how to integrate it:

```python
from fastapi import FastAPI, HTTPException
from contextlib import asynccontextmanager
import configbee

# Global client instance
cb_client = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global cb_client
    # Initialize ConfigBee client on startup
    cb_client = configbee.get_client(
        account_id="your_account_id",
        project_id="your_project_id",
        environment_id="your_environment_id"
    )
    
    # Wait for initial configuration load
    await cb_client.await_to_load()
    print("ConfigBee client initialized")
    
    yield
    
    # Cleanup on shutdown (if needed)
    print("Shutting down ConfigBee client")

app = FastAPI(lifespan=lifespan)

@app.get("/")
async def read_root():
    # Use feature flags in your endpoints
    if cb_client.get_flag("maintenance_mode"):
        raise HTTPException(status_code=503, detail="Service under maintenance")
    
    return {"message": "Hello World"}

@app.get("/config")
async def get_config():
    # Return current configuration
    return {
        "api_version": cb_client.get_text("api_version"),
        "max_requests": cb_client.get_number("max_requests"),
        "features": cb_client.get_all_flags()
    }

@app.get("/users/{user_id}")
async def get_user(user_id: int):
    # Use configuration for business logic
    max_user_limit = cb_client.get_number("max_user_limit")
    if user_id > max_user_limit:
        raise HTTPException(status_code=400, detail="User ID exceeds limit")
    
    # Check if new user features are enabled
    enhanced_profile = cb_client.get_flag("enhanced_user_profile")
    
    return {
        "user_id": user_id,
        "enhanced_profile": enhanced_profile
    }
```

#### Dependency Injection Pattern

For better organization, you can use FastAPI's dependency injection:

```python
from fastapi import FastAPI, Depends, HTTPException
import configbee

cb_client = None

async def get_configbee_client():
    global cb_client
    if cb_client is None:
        raise HTTPException(status_code=500, detail="ConfigBee client not initialized")
    return cb_client

@app.get("/feature-status")
async def feature_status(client: configbee.ConfigbeeClient = Depends(get_configbee_client)):
    return {
        "beta_features": client.get_flag("beta_features"),
        "new_ui": client.get_flag("new_ui_enabled")
    }
```

### Real-time Updates

ConfigBee automatically receives real-time updates with live streaming. No additional code is required - your configuration values will be updated automatically.

```python
import time
import configbee

client = configbee.get_client("account", "project", "env")
client.wait_to_load()

# This will automatically reflect updates made in ConfigBee dashboard
while True:
    current_limit = client.get_number("rate_limit")
    print(f"Current rate limit: {current_limit}")
    time.sleep(5)
```

## Resources
- [NOTICE](https://github.com/configbee/cb-server-sdk-python/blob/main/NOTICE)
- [LICENSE](https://github.com/configbee/cb-server-sdk-python/blob/main/LICENSE)

## Contributing

[Add contribution guidelines here]
