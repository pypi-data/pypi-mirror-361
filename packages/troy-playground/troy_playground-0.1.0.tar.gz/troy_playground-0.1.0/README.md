# Troy Playground

A Python debugging tool that executes functions and extracts their local variables for inspection. Originally designed for analyzing test functions, it allows you to turn any function into a playground where you can access and examine internal variables after execution.

## Installation

```bash
pip install troy-playground
```

## Usage

### Basic Example

```python
from troy_playground import extract_locals, run_function_playground

# Example with a test function
from tests.test_module import TestClass

test_obj = TestClass()
vars_dict = extract_locals(
    test_obj.test_method,
    ['result', 'data', 'processed'],  # variables to extract
    test_obj  # instance for bound methods
)

# Access the extracted variables
print(vars_dict['result'])
print(vars_dict['data'])
```

### Using with Module Path

```python
# Extract variables from a test method
vars_dict = run_function_playground(
    'tests.test_module',
    'TestClass',
    'test_method', 
    ['result', 'response', 'mock_data']
)

# Also works with regular functions
vars_dict = run_function_playground(
    'my_module',
    None,  # No class for module-level functions
    'process_data',
    ['output', 'transformed']
)
```

### Passing Arguments

```python
# You can pass arguments to the function
vars_dict = extract_locals(
    obj.method_with_params,
    ['result'],
    obj,  # instance
    'arg1', 'arg2',  # positional args
    param1='value1',  # keyword args
    param2='value2'
)
```

## API Reference

### `extract_locals(func, var_names, instance=None, *args, **kwargs)`

Execute a function and extract specified local variables.

- `func`: The function to execute
- `var_names`: List of variable names to extract
- `instance`: Optional instance for bound methods
- `*args`, `**kwargs`: Arguments to pass to the function

Returns a dictionary with extracted variables. If an error occurs, the dict will contain an `__error__` key.

### `run_function_playground(module_path, class_name, func_name, var_names, *args, **kwargs)`

Import and run a function by module path.

- `module_path`: Import path to module
- `class_name`: Class name (None for module-level functions)  
- `func_name`: Function/method name
- `var_names`: List of variable names to extract
- `*args`, `**kwargs`: Arguments to pass to the function

## Use Cases

- **Test Debugging**: Extract intermediate values from test functions to understand failures
- **Function Analysis**: Inspect internal state without modifying source code
- **Interactive Development**: Turn any function into a REPL-like playground

## License

MIT