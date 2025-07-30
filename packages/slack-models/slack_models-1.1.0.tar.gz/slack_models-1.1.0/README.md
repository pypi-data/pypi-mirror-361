# slack-models

[![PyPI version](https://badge.fury.io/py/slack-models.svg)](https://badge.fury.io/py/slack-models)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-BSD--3--Clause-blue.svg)](LICENSE)
[![Documentation](https://img.shields.io/badge/docs-latest-brightgreen.svg)](https://gmr.github.io/slack-models/)

**Comprehensive Pydantic models for working with the Slack API**

slack-models provides type-safe, validated data structures for Slack API integration, making it easier to build robust Slack applications with proper error handling and IDE support.

## 🚀 Features

- **Complete Coverage**: Models for all major Slack events, objects, webhook payloads, and Block Kit elements
- **Type Safety**: Full type annotations with Python 3.12+ modern type hints
- **Validation**: Automatic data validation using Pydantic 2.x
- **IDE Support**: Excellent autocomplete and type checking
- **Event Parsing**: Convenient utilities for parsing webhook payloads
- **Standards Compliant**: Strict adherence to official Slack API specifications

## 📦 Installation

```bash
pip install slack-models
```

**Requirements:**
- Python 3.12+
- pydantic >=2.11.3,<3

## 🔧 Quick Start

### Basic Usage

```python
from slack_models import parse_event, SlackEventCallback, MessageEvent

# Parse a webhook payload
webhook_data = {
    "type": "event_callback",
    "event": {
        "type": "message",
        "channel": "C1234567890",
        "user": "U1234567890",
        "text": "Hello, world!",
        "ts": "1234567890.123456"
    },
    "team_id": "T1234567890",
    "api_app_id": "A1234567890"
}

# Parse and validate
event = parse_event(webhook_data)
if isinstance(event, SlackEventCallback):
    if isinstance(event.event, MessageEvent):
        print(f"Message: {event.event.text}")
        print(f"Channel: {event.event.channel}")
        print(f"User: {event.event.user}")
```

### Event Handling

```python
from slack_models import (
    parse_event, SlackEventCallback, MessageEvent,
    ReactionAddedEvent, ChannelCreatedEvent
)

def handle_slack_event(payload: dict):
    """Handle incoming Slack events with type safety."""
    event = parse_event(payload)

    if isinstance(event, SlackEventCallback):
        if isinstance(event.event, MessageEvent):
            print(f"New message: {event.event.text}")
        elif isinstance(event.event, ReactionAddedEvent):
            print(f"Reaction added: {event.event.reaction}")
        elif isinstance(event.event, ChannelCreatedEvent):
            print(f"Channel created: {event.event.channel.name}")
```

### Working with Models

```python
from slack_models import User, Channel, MessageEvent

# Create and validate user data
user = User(
    id="U1234567890",
    name="john.doe",
    real_name="John Doe",
    profile={
        "email": "john.doe@example.com",
        "display_name": "John",
        "first_name": "John",
        "last_name": "Doe"
    }
)

# Access user information with full type safety
print(f"User: {user.name} ({user.real_name})")
print(f"Email: {user.profile.email}")
```

## 📚 Documentation

- **[Documentation](https://gmr.github.io/slack-models/)**: Comprehensive guides and API reference
- **[Quick Start](https://gmr.github.io/slack-models/quickstart/)**: Get up and running quickly
- **[API Reference](https://gmr.github.io/slack-models/api/models/)**: Detailed model documentation
- **[Examples](https://gmr.github.io/slack-models/examples/basic/)**: Practical usage examples

## 🎯 Supported Events

slack-models supports all major Slack event types:

### Message Events
- `MessageEvent`: Standard messages, bot messages, threaded messages
- `AppMentionEvent`: App mentions in channels
- `MessageEdited`: Message edit events

### Reaction Events
- `ReactionAddedEvent`: Reaction additions
- `ReactionRemovedEvent`: Reaction removals

### Channel Events
- `ChannelCreatedEvent`: New channel creation
- `ChannelDeletedEvent`: Channel deletion
- `ChannelRenameEvent`: Channel name changes

### Team Events
- `TeamJoinEvent`: New team member joins

### File Events
- `FileCreatedEvent`: File uploads
- `FileDeletedEvent`: File deletions

### Block Kit Models
- **Blocks**: `SectionBlock`, `DividerBlock`, `ImageBlock`, `ActionsBlock`, `ContextBlock`, `InputBlock`, `HeaderBlock`, `VideoBlock`, `RichTextBlock`, `FileBlock`
- **Elements**: `ButtonElement`, `StaticSelectElement`, `CheckboxesElement`, `DatePickerElement`, `PlainTextInputElement`, and more
- **Composition Objects**: `TextObject`, `ConfirmationDialog`, `Option`, `OptionGroup`

### Webhook Types
- `SlackEventCallback`: Standard event callbacks
- `SlackUrlVerification`: URL verification challenges
- `SlackAppRateLimited`: Rate limiting notifications

### Error Handling

```python
from pydantic import ValidationError
from slack_models import parse_event

try:
    event = parse_event(webhook_data)
    # Process event
except ValidationError as e:
    print(f"Invalid payload: {e}")
    # Handle validation errors
except Exception as e:
    print(f"Processing error: {e}")
    # Handle other errors
```

## 🧪 Development

### Setup

```bash
# Clone the repository
git clone https://github.com/gmr/slack-models.git
cd slack-models

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -e '.[dev]'

# Install pre-commit hooks
pre-commit install
```

### Testing

```bash
# Run tests
pytest

# Run tests with coverage
pytest --cov=slack_models --cov-report=html

# Run linting
ruff check .

# Run type checking
mypy src/slack_models
```

### Documentation

```bash
# Build documentation
mkdocs build

# Serve documentation locally
mkdocs serve
```

## 🤝 Contributing

Contributions are welcome! Please see our [Contributing Guide](https://gmr.github.io/slack-models/development/contributing/) for details.

### Development Workflow

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run the test suite and linting
6. Submit a pull request

## 📄 License

This project is licensed under the BSD-3-Clause License. See the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built for Slack bot projects at AWeber
- Powered by [Pydantic](https://pydantic.dev/) for data validation
- Inspired by the [Slack API](https://api.slack.com/) documentation

## 📞 Support

- **Documentation**: [https://gmr.github.io/slack-models/](https://gmr.github.io/slack-models/)
- **Issues**: [https://github.com/gmr/slack-models/issues](https://github.com/gmr/slack-models/issues)
- **Source Code**: [https://github.com/gmr/slack-models](https://github.com/gmr/slack-models)

---

Made with ❤️ by [Gavin M. Roy](https://github.com/gmr) at [AWeber](https://aweber.com)
