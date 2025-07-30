# Telegram Init Data Python

[![PyPI version](https://badge.fury.io/py/telegram-init-data.svg)](https://badge.fury.io/py/telegram-init-data)
[![Python versions](https://img.shields.io/pypi/pyversions/telegram-init-data.svg)](https://pypi.org/project/telegram-init-data)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A Python library for working with Telegram Mini Apps initialization data. This library provides utilities to parse, validate, and sign init data on the server side, similar to the official [@telegram-apps/init-data-node](https://docs.telegram-mini-apps.com/packages/telegram-apps-init-data-node/2-x) package.

## Features

- 🔐 **Validate init data** - Verify signature and expiration of Telegram Mini App init data
- 📝 **Parse init data** - Convert URL-encoded init data to structured Python objects
- ✍️ **Sign init data** - Create signed init data for testing and development
- 🔍 **Type safety** - Full type hints and validation
- 🚀 **FastAPI integration** - Ready-to-use middleware for FastAPI applications
- 🌐 **3rd party validation** - Support for validating data signed by Telegram directly

## Installation

```bash
pip install telegram-init-data
```

For FastAPI integration:
```bash
pip install telegram-init-data[fastapi]
```

## Quick Start

### Basic Validation

```python
from telegram_init_data import validate, parse

# Your bot token from @BotFather
bot_token = "YOUR_BOT_TOKEN"

# Init data string from Telegram Mini App
init_data = "query_id=AAHdF6IQAAAAAN0XohDhrOrc&user=%7B%22id%22%3A279058397%2C%22first_name%22%3A%22Vladislav%22%2C%22last_name%22%3A%22Kibenko%22%2C%22username%22%3A%22vdkfrost%22%2C%22language_code%22%3A%22ru%22%2C%22is_premium%22%3Atrue%7D&auth_date=1662771648&hash=c501b71e775f74ce10e377dea85a7ea24ecd640b223ea86dfe453e0eaed2e2b2"

try:
    # Validate the init data
    validate(init_data, bot_token)
    print("✅ Init data is valid!")
    
    # Parse the init data
    parsed_data = parse(init_data)
    print(f"User: {parsed_data['user']['first_name']}")
    
except Exception as e:
    print(f"❌ Validation failed: {e}")
```

### Using with FastAPI

```python
from fastapi import FastAPI, Depends, HTTPException
from telegram_init_data import validate, parse

app = FastAPI()

def verify_init_data(init_data: str) -> dict:
    """Dependency to verify and parse init data"""
    bot_token = "YOUR_BOT_TOKEN"
    
    try:
        validate(init_data, bot_token)
        return parse(init_data)
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))

@app.post("/user/profile")
async def get_profile(init_data: dict = Depends(verify_init_data)):
    user = init_data.get("user")
    if not user:
        raise HTTPException(status_code=400, detail="User data not found")
    
    return {"user_id": user["id"], "name": user["first_name"]}
```

### Advanced Usage

```python
from telegram_init_data import sign, is_valid
from datetime import datetime

# Create test init data
test_data = {
    "query_id": "test_query_id",
    "user": {
        "id": 123456789,
        "first_name": "John",
        "last_name": "Doe",
        "username": "johndoe",
        "language_code": "en"
    },
    "auth_date": datetime.now()
}

# Sign the data
signed_data = sign(test_data, bot_token, datetime.now())
print(f"Signed data: {signed_data}")

# Check if data is valid (returns boolean)
if is_valid(signed_data, bot_token):
    print("✅ Data is valid")
else:
    print("❌ Data is invalid")
```

## API Reference

### Core Functions

#### `validate(value, token, options=None)`

Validates Telegram Mini App init data.

**Parameters:**
- `value` (str | dict): Init data to validate
- `token` (str): Bot token from @BotFather
- `options` (dict, optional): Validation options
  - `expires_in` (int): Expiration time in seconds (default: 86400)

**Raises:**
- `SignatureMissingError`: When hash parameter is missing
- `AuthDateInvalidError`: When auth_date is invalid or missing
- `ExpiredError`: When init data has expired
- `SignatureInvalidError`: When signature verification fails

#### `is_valid(value, token, options=None)`

Checks if init data is valid without raising exceptions.

**Returns:** `bool` - True if valid, False otherwise

#### `parse(value)`

Parses init data string into structured Python object.

**Parameters:**
- `value` (str | dict): Init data to parse

**Returns:** `InitData` - Parsed init data object

#### `sign(data, token, auth_date, options=None)`

Signs init data for testing/development.

**Parameters:**
- `data` (dict): Data to sign
- `token` (str): Bot token
- `auth_date` (datetime): Authentication date
- `options` (dict, optional): Signing options

**Returns:** `str` - Signed init data as URL-encoded string

### Data Types

#### `InitData`

```python
class InitData(TypedDict):
    query_id: Optional[str]
    user: Optional[User]
    receiver: Optional[User]
    chat: Optional[Chat]
    chat_type: Optional[ChatType]
    chat_instance: Optional[str]
    start_param: Optional[str]
    can_send_after: Optional[int]
    auth_date: int
    hash: str
    signature: Optional[str]
```

#### `User`

```python
class User(TypedDict):
    id: int
    first_name: str
    last_name: Optional[str]
    username: Optional[str]
    language_code: Optional[str]
    is_bot: Optional[bool]
    is_premium: Optional[bool]
    added_to_attachment_menu: Optional[bool]
    allows_write_to_pm: Optional[bool]
    photo_url: Optional[str]
```

#### `Chat`

```python
class Chat(TypedDict):
    id: int
    type: ChatType
    title: Optional[str]
    username: Optional[str]
    photo_url: Optional[str]
```

### Exception Classes

- `TelegramInitDataError`: Base exception class
- `AuthDateInvalidError`: Invalid or missing auth_date
- `SignatureInvalidError`: Invalid signature
- `SignatureMissingError`: Missing signature/hash
- `ExpiredError`: Init data has expired

## Configuration Options

### Validation Options

```python
options = {
    "expires_in": 3600,  # 1 hour expiration instead of default 24 hours
}

validate(init_data, bot_token, options)
```

### Disable Expiration Check

```python
options = {
    "expires_in": 0,  # Disable expiration check
}

validate(init_data, bot_token, options)
```

## Testing

Run tests with pytest:

```bash
# Install development dependencies
pip install -e .[dev]

# Run tests
pytest

# Run with coverage
pytest --cov=telegram_init_data --cov-report=html
```

## Examples

### Complete FastAPI Application

```python
from fastapi import FastAPI, Depends, HTTPException, Header
from telegram_init_data import validate, parse, is_valid

app = FastAPI()

def get_init_data(authorization: str = Header(None)):
    """Extract and validate init data from Authorization header"""
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header missing")
    
    if not authorization.startswith("tma "):
        raise HTTPException(status_code=401, detail="Invalid authorization format")
    
    init_data = authorization[4:]  # Remove "tma " prefix
    bot_token = "YOUR_BOT_TOKEN"
    
    if not is_valid(init_data, bot_token):
        raise HTTPException(status_code=401, detail="Invalid init data")
    
    return parse(init_data)

@app.get("/me")
async def get_current_user(init_data: dict = Depends(get_init_data)):
    """Get current user info"""
    user = init_data.get("user")
    if not user:
        raise HTTPException(status_code=400, detail="User data not found")
    
    return {
        "id": user["id"],
        "name": user.get("first_name", ""),
        "username": user.get("username"),
        "is_premium": user.get("is_premium", False)
    }

@app.post("/settings")
async def update_settings(
    settings: dict,
    init_data: dict = Depends(get_init_data)
):
    """Update user settings"""
    user = init_data.get("user")
    # Save settings for user["id"]
    return {"status": "success"}
```

## Development

### Setup Development Environment

```bash
# Clone the repository
git clone https://github.com/telegram-init-data/telegram-init-data-python.git
cd telegram-init-data-python

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e .[dev]

# Run tests
pytest

# Format code
black telegram_init_data tests
isort telegram_init_data tests

# Type checking
mypy telegram_init_data
```

### Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## License

MIT License. See [LICENSE](LICENSE) for details.

## Related Projects

- [@telegram-apps/init-data-node](https://docs.telegram-mini-apps.com/packages/telegram-apps-init-data-node/2-x) - Official Node.js implementation
- [Telegram Mini Apps Documentation](https://docs.telegram-mini-apps.com/) - Official documentation

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for details about changes in each version.

## Support

If you have questions or need help:

1. Check the [documentation](https://github.com/iCodeCraft/telegram-init-data/blob/main/README.md)
2. Look at the [examples](examples/)
3. Open an [issue](https://github.com/iCodeCraft/telegram-init-data/issues)

---

Developed with ❤️ by Imran Gadzhiev to support Telegram Mini Apps developers.
