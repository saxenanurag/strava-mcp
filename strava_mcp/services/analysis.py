from typing import Any
import pydantic_monty


def analyze_data(code: str, data: Any) -> Any:
    """
    Executes Python code safely using Monty, passing 'data' as a variable.

    Args:
        code: The Python code snippet to execute.
        data: The data structure (dict, list, etc.) to inject as the 'data' variable.
    """

    # Always inject data as 'data' variable
    inputs = {"data": data}
    input_names = ["data"]

    try:
        # Initialize Monty with the code and expected input variables
        # Using strict limits by default for safety
        m = pydantic_monty.Monty(code, inputs=input_names)

        # Execute the code
        result = m.run(inputs=inputs)
        return result

    except Exception as e:
        # Raise a clear error message that the MCP client can display
        raise RuntimeError(f"Analysis failed: {str(e)}") from e
