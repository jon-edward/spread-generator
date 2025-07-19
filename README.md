# spread-generator

> [!WARNING]
> This is not recommended for use in production, and is designed
> for entertainment purposes only.

A hack for unpacking from potentially infinite generators in Python through AST manipulation.

## Usage

```python
@spread_generator
def gen():
    while True:
        yield 1

(a, b, c), rest = gen()
print(a, b, c) # 1 1 1
```

Where the remaining generator is returned as `rest`.

See [tests.py](tests.py) for more examples.

## What to use instead?

A more robust approach is to use `itertools.islice` to limit the number of elements of the generator to be returned. For example:

```python
from itertools import islice

def gen():
    while True:
        yield 1

a, b, c = islice(gen(), 3)
```
