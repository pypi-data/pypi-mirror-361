# li-submit

Minimal command-line utility to submit a website to [liveinternet.ru](https://www.liveinternet.ru/add) using a simple HTTP POST request.

## Features

- Requires only website URL and email
- Optional password argument (default is `123123`)
- Simple one-command usage

## Installation

```bash
pip install li-submit
```


## Usage exmaple

```python
from li_submit import register_site

result = register_site(
    url="example.com",
    email="user@example.com",
    anticaptcha_key="your_anticaptcha_key"
)

if result.success:
    print("Registration successful!")
else:
    print(f"Registration failed: {result.message}")
```
