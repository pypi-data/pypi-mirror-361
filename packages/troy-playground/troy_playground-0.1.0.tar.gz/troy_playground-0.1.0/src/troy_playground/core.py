import inspect
from typing import Dict, Any, List, Callable, Optional
import sys
import traceback


def extract_locals(func: Callable, var_names: List[str], 
                  instance: Optional[object] = None,
                  *args, **kwargs) -> Dict[str, Any]:
    """
    Execute a function and extract specified variables from its local scope.
    
    Args:
        func: The function to execute
        var_names: List of variable names to extract from the function's local scope
        instance: Optional instance for bound methods (if func needs self)
        *args: Additional positional arguments to pass to the function
        **kwargs: Additional keyword arguments to pass to the function
    
    Returns:
        Dictionary containing the requested variables and their values
        
    Example:
        >>> # For a regular function
        >>> vars_dict = extract_locals(some_function, ['result', 'data'])
        >>> 
        >>> # For a method that needs self
        >>> obj = MyClass()
        >>> vars_dict = extract_locals(
        ...     obj.some_method,
        ...     ['result', 'data'],
        ...     obj,  # pass instance
        ...     param1="value"
        ... )
    """
    # Store original trace function
    original_trace = sys.gettrace()
    
    # Dictionary to store captured variables
    captured_vars = {}
    
    # Create a trace function to capture local variables
    def trace_func(frame, event, arg):
        if event == 'line':
            # Update captured vars with current locals
            for var_name in var_names:
                if var_name in frame.f_locals:
                    captured_vars[var_name] = frame.f_locals[var_name]
        return trace_func
    
    try:
        # Set the trace function
        sys.settrace(trace_func)
        
        # Execute the function with provided arguments
        if instance is not None:
            # Call with instance if provided
            func(*args, **kwargs)
        else:
            # Call without instance
            func(*args, **kwargs)
    
    except Exception as e:
        # Add error info to captured vars
        captured_vars['__error__'] = {
            'type': type(e).__name__,
            'message': str(e),
            'traceback': traceback.format_exc()
        }
    
    finally:
        # Restore original trace function
        sys.settrace(original_trace)
    
    return captured_vars


def run_function_playground(module_path: str, class_name: Optional[str], 
                           func_name: str, var_names: List[str],
                           *args, **kwargs) -> Dict[str, Any]:
    """
    Higher-level function to run any function/method and extract variables by path.
    
    Args:
        module_path: Import path to module (e.g., 'mypackage.mymodule')
        class_name: Name of the class (None for module-level functions)
        func_name: Name of the function/method
        var_names: List of variable names to extract
        *args: Additional positional arguments to pass to the function
        **kwargs: Additional keyword arguments to pass to the function
        
    Returns:
        Dictionary containing the requested variables
        
    Example:
        >>> # For a class method
        >>> vars_dict = run_function_playground(
        ...     'test.features.test_runpy_basemodel_docs',
        ...     'TestRunpyBaseModelDocs', 
        ...     'test_basemodel_parameter_documentation',
        ...     ['specific_result', 'runner', 'cli']
        ... )
        >>> 
        >>> # For a module-level function
        >>> vars_dict = run_function_playground(
        ...     'mymodule',
        ...     None,
        ...     'process_data',
        ...     ['result', 'processed']
        ... )
    """
    # Import the module
    module = __import__(module_path, fromlist=[class_name] if class_name else [])
    
    if class_name:
        # Get the class and create instance
        cls = getattr(module, class_name)
        instance = cls()
        
        # Get the method
        func = getattr(instance, func_name)
        
        # Extract variables with instance
        return extract_locals(func, var_names, instance, *args, **kwargs)
    else:
        # Get module-level function
        func = getattr(module, func_name)
        
        # Extract variables without instance
        return extract_locals(func, var_names, None, *args, **kwargs)


# Example usage:
if __name__ == "__main__":
    # Example 1: Direct usage with a class instance
    from test.features.test_runpy_basemodel_docs import TestRunpyBaseModelDocs
    
    test_obj = TestRunpyBaseModelDocs()
    vars_dict = extract_locals(
        test_obj.test_basemodel_parameter_documentation,
        ['specific_result', 'runner', 'cli', 'UserInput', 'UserOutput', 'create_user', 'update_user'],
        test_obj  # pass instance since it's a bound method
    )
    
    print("Extracted variables:")
    for name, value in vars_dict.items():
        if name == '__error__':
            print(f"\nError occurred: {value['type']}: {value['message']}")
        else:
            print(f"\n{name}: {type(value).__name__}")
            if hasattr(value, 'output'):
                print(f"  Output preview: {value.output[:100]}...")
    
    # Example 2: Using the higher-level function
    print("\n" + "="*50 + "\n")
    
    vars_dict2 = run_function_playground(
        'test.features.test_runpy_basemodel_docs',
        'TestRunpyBaseModelDocs',
        'test_basemodel_parameter_documentation',
        ['specific_result', 'general_result', 'cli']
    )
    
    print("Variables from playground function:")
    for name, value in vars_dict2.items():
        if name == '__error__':
            print(f"\nError occurred: {value['type']}: {value['message']}")
        else:
            print(f"{name}: {type(value).__name__}")