# DDBModel

A Python library for DynamoDB modeling and operations.

## Installation

```bash
pip install ddbmodel
```

## Usage

```python
from ddbmodel.base import DDBModel
from ddbmodel.field import StringField, PasswordField

class User(DDBModel):
    table_name = "users"
    
    username = StringField(hash_key=True)
    password = PasswordField()
    email = StringField()

# Create a user
user = User(username="john", password="secret", email="john@example.com")
user.put_item()

# Get a user
user = User(username="john").get_item()
```

## Features

- Simple DynamoDB modeling
- Field validation
- Password hashing
- Transaction support
- Key management