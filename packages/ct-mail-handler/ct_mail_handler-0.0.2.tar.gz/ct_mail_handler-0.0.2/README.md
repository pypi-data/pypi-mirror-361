# CredentiMail Logging System

This project provides a custom logging handler for Python applications that sends log messages via HTTP POST to a remote mail server. It includes structured data models for email and attachment handling using Python dataclasses.

## 📆 Features

* Custom logging handler: `CredentiMailHandler`
* Data models for email and attachments: `MailDetail`, `Attachment`
* Sends logs to a mail server over HTTP
* Flask-compatible
* Includes test command via Flask CLI
* Installable as a Python package

---

## 🚀 Installation

Install the package via pip:

```bash
pip install ct-mail-handler
```


## 📅 Packaging and Uploading to PyPI

To build and upload the package to [PyPI](https://pypi.org/):

### 1. Install required tools

```bash
pip install build twine
```

### 2. Build the package

```bash
python -m build
```

This creates `dist/` containing `.tar.gz` and `.whl` files.

### 3. Upload to PyPI

```bash
python -m twine upload dist/*
```

You'll be prompted for your PyPI credentials.

For test uploads, use:

```bash
python -m twine upload --repository-url https://test.pypi.org/legacy/ dist/*
```

---


## 🚧 Testing Requirements

The dependencies listed in `requirements.txt` are used only for **testing purposes** (e.g., Flask CLI and testing libraries). They are not needed when installing this package for runtime use.

Install testing dependencies:

```bash
pip install -r requirements.txt
```

---

## 🌐 Usage

### 1. Add the Logging Handler

```python
from credenti_mail_handler import CredentiMailHandler
import logging

handler = CredentiMailHandler(
    fromaddr="logger@example.com",
    toaddrs=["admin@example.com"],
    subject="Application Error",
    mail_server_url="http://localhost:5000/send-mail"
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)
logger.addHandler(handler)

logger.error("This is a test error log.")
```

### 2. Email Data Models

#### `MailDetail`

* `from_address: str`
* `to_address: List[str]`
* `subject: str`
* `body: str`
* `attachments: Optional[List[Attachment]]`

#### `Attachment`

* `file_content_b64: str`
* `file_name: Optional[str>`
* `file_type: Optional[str>`
* `disposition: Literal['attachment', 'inline']`

Add attachments using:

```python
mail_detail.add_attachment(
    file_content_b64="base64content...",
    file_name="report.pdf",
    file_type="application/pdf"
)
```

---

## 🔧 Internal Methods

### `CredentiMailHandler.emit()`

Formats and sends a log record as an email via `send_email()`.

### `prepare_email()`

Returns a `MailDetail` object from parameters.

### `send_email()`

Uses `requests.post()` to send the `MailDetail` as JSON to the mail server.

---

## 🔮 Testing

To run tests using Flask CLI:

### `manage.py`

Ensure you have a `manage.py` file that defines the `test` command, e.g.:

```python
import click
from flask import Flask

app = Flask(__name__)

@app.cli.command("test")
def test():
    import unittest
    tests = unittest.TestLoader().discover("tests")
    unittest.TextTestRunner().run(tests)
```

### Run tests:

```bash
flask --app manage.py test
```

---

## 📅 Folder Structure

```
.
├── README.md
├── app.py
├── ct_mail_handler/
│   ├── __init__.py
│   ├── credenti_mail_handler.py
│   └── models.py
├── manage.py
├── requirements.txt
├── setup.py
├── tests/
    └── test_handler.py
```

---