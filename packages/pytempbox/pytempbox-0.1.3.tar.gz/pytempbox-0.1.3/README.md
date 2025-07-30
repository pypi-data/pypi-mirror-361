# PyTempBox - Python Temporary Email Service

[![PyPI version](https://img.shields.io/pypi/v/pytempbox.svg)](https://pypi.org/project/pytempbox/)
[![Python versions](https://img.shields.io/pypi/pyversions/pytempbox.svg)](https://pypi.org/project/pytempbox/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

PyTempBox is a lightweight Python library for generating and managing temporary email addresses. Perfect for testing, automation, and protecting your privacy when interacting with online services.

## ✨ Features

With this service, you can instantly create temporary email addresses 🚀. Once the email address is generated, you can fetch incoming messages in real-time 📩. The service is designed to be lightweight ⚡, requiring minimal dependencies. Additionally, the API follows best practices in Python programming, making it user-friendly 🐍. Security is a top priority, as all connections are made through secure HTTPS 🔒. You can also retrieve the full content of each message received 📝.

## 📦 Installation

To install the package, simply run the following command in your terminal:

```bash
pip install pytempbox
```

Please note that this package requires Python version 3.9 or higher to work properly.

## 🚀 Quick Start

```python
from pytempbox import PyTempBox

client = PyTempBox()
email = client.generate_email()
print(f"Temporary email: {email}")

messages = client.get_messages(email)
if messages:
    print(f"Received {len(messages)} message(s)")
    print(f"Latest: {messages[0]['subject']}")
else:
    print("No messages yet")
```

## 📚 Documentation

### Core Methods

The package offers several useful functions to manage temporary emails. First, you can use `generate_email(min_length=10, max_length=15)` to create a new temporary email address with a specified minimum and maximum length 🆕✉️. To retrieve messages sent to that email, you can call `get_messages(email, timeout=300, interval=10)`, which checks for incoming messages within a set timeout and interval ⏳📥. If you want to see the full content of a specific message, you can use `get_message_content(email, message_id)` to get all the details of that message 📜. Lastly, the function `get_available_domains()` will list all the email domains you can use for generating temporary addresses 🌐.

### Advanced Usage

```python
email = client.generate_email(min_length=8, max_length=12)

message = client.get_message_content(
    email="your_temp@example.com",
    message_id="12345"
)
```

## 📜 License

This package is distributed under the MIT License, which means you can use, modify, and distribute it freely. For more details about the license, please refer to the [LICENSE](LICENSE) file. 📄✨