# Choke

Rate limiting library.

## Usage

```python
from choke import choke

@choke("mykey", 3, 3)
async def my_function():
    return "success"
```