import re

def parse_function_call(text):
    """
    Parse function call with intermediate complexity (arrays and optional parameters)
    
    Args:
        text (str): Text that may contain a function call
        
    Returns:
        tuple: (function_name, parameters) or (None, None) if no function call found
    """
    # TODO: Define regex pattern to match CALL_FUNCTION format
    
    # TODO: Search for the pattern in the text
    
    # TODO: If no match found, return None, None
    
    # TODO: Extract function name from the match
    
    # TODO: Extract parameters string from the match
    
    # TODO: Parse parameters string into a dictionary
    # Handle simple arrays: ["item1", "item2"]
    # Handle optional parameters with defaults
    
    # TODO: Return function_name and parameters dictionary
    
    pass

def parse_array_parameter(param_str):
    """
    Parse an array parameter like ["Tokyo", "Seoul"]
    
    Args:
        param_str (str): Array parameter string
        
    Returns:
        list: Parsed array
    """
    # TODO: Check if parameter looks like an array
    
    # TODO: Remove brackets and quotes
    
    # TODO: Split by comma and clean up items
    
    # TODO: Return as list
    
    pass