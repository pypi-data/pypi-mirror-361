# Multipyline

Multipyline is a Python library for formatting multiline strings, especially useful for maintaining proper indentation in complex string compositions.

## Installation

```bash
pip install multipyline
```

## Usage

### Using `multipyline`

`multipyline_inner` is used inside `multipyline` f-strings to format inner multiline content, applying a specified prefix to each line.

```python
from multipyline import multipyline, multipyline_inner

inner_text = '''
    Inner line 1
        Offset inner line 2
    Inner line 3
'''

result = multipyline(f'''
    Outer line 1:
        {multipyline_inner(inner_text, " " * 8)}

        > Outer line 2:
        >
        {multipyline_inner(inner_text, " " * 8 + "> ")}
''')

print(result)
```

The output will be:

```
Outer line 1:
    Inner line 1
        Offset inner line 2
    Inner line 3

    > Outer line 2:
    >
    > Inner line 1
    >     Offset inner line 2
    > Inner line 3
```

### Using `multipyline_format`

`multipyline_format` formats a multiline string with placeholders (`{}`) which are themselves multiline strings, handling proper indentation for each.

```python
from multipyline import multipyline_format

func_impl = '''
    # Inner part
    if (x > 0):
        print('Another line')
'''

result = multipyline_format(
    '''
    def fun(x: int):
        print('Outer part')
        {}
    ''',
    func_impl,
)

print(result)
```

The output will be:

```
def fun(x: int):
    print('Outer part')
    # Inner part
    if (x > 0):
        print('Another line')
```
