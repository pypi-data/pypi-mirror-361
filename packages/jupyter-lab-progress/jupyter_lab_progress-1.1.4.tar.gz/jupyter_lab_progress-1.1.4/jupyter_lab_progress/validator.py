from typing import Any, Callable, Optional, List, Dict, Union
import re
import inspect
from IPython.display import display, HTML
import pandas as pd
import numpy as np

class LabValidator:
    """
    Comprehensive validation class for Jupyter lab exercises.
    Provides a variety of validation methods with visual feedback.
    """
    
    def __init__(self, progress_tracker=None):
        """
        Initialize the validator.
        
        Args:
            progress_tracker: Optional LabProgress instance to auto-update on successful validations
        """
        self.progress_tracker = progress_tracker
        self.last_validation_result = None
    
    def _display_result(self, success: bool, message: str, details: str = ""):
        """Display validation result with color-coded output."""
        if success:
            icon = "✅"
            color = "#4CAF50"
            bg_color = "#e8f5e9"
        else:
            icon = "❌"
            color = "#f44336"
            bg_color = "#ffebee"
        
        html = f"""
        <div style='background-color: {bg_color}; border-left: 4px solid {color}; 
                    padding: 10px; margin: 10px 0; border-radius: 5px;'>
            <span style='font-size: 20px; margin-right: 10px;'>{icon}</span>
            <strong style='color: {color};'>{message}</strong>
            {f"<br><small style='color: #666;'>{details}</small>" if details else ""}
        </div>
        """
        display(HTML(html))
        self.last_validation_result = success
        return success
    
    def validate_variable_exists(self, var_name: str, globals_dict: dict, 
                                expected_type: Optional[type] = None) -> bool:
        """
        Validate that a variable exists in the namespace.
        
        Args:
            var_name: Name of the variable to check
            globals_dict: Usually globals() from the notebook
            expected_type: Optional type to check against
        """
        if var_name not in globals_dict:
            return self._display_result(False, f"Variable '{var_name}' not found", 
                                      "Make sure you've run the cell that creates this variable.")
        
        if expected_type:
            actual_type = type(globals_dict[var_name])
            if not isinstance(globals_dict[var_name], expected_type):
                return self._display_result(False, f"Type mismatch for '{var_name}'", 
                                          f"Expected {expected_type.__name__}, got {actual_type.__name__}")
        
        return self._display_result(True, f"Variable '{var_name}' validated successfully")
    
    def validate_function_exists(self, func_name: str, globals_dict: dict,
                               expected_params: Optional[List[str]] = None) -> bool:
        """
        Validate that a function exists and has expected parameters.
        
        Args:
            func_name: Name of the function
            globals_dict: Usually globals() from the notebook
            expected_params: Optional list of expected parameter names
        """
        if func_name not in globals_dict:
            return self._display_result(False, f"Function '{func_name}' not found",
                                      "Make sure you've defined this function.")
        
        obj = globals_dict[func_name]
        if not callable(obj):
            return self._display_result(False, f"'{func_name}' is not callable",
                                      f"Found {type(obj).__name__} instead of a function.")
        
        if expected_params:
            sig = inspect.signature(obj)
            actual_params = list(sig.parameters.keys())
            missing = set(expected_params) - set(actual_params)
            if missing:
                return self._display_result(False, f"Missing parameters in '{func_name}'",
                                          f"Expected: {expected_params}, Missing: {list(missing)}")
        
        return self._display_result(True, f"Function '{func_name}' validated successfully")
    
    def validate_output(self, actual: Any, expected: Any, 
                       comparison_func: Optional[Callable] = None,
                       tolerance: float = 1e-6) -> bool:
        """
        Validate that output matches expected value.
        
        Args:
            actual: The actual output
            expected: The expected output
            comparison_func: Optional custom comparison function
            tolerance: Tolerance for float comparisons
        """
        if comparison_func:
            match = comparison_func(actual, expected)
        elif isinstance(expected, (int, float)) and isinstance(actual, (int, float)):
            match = abs(actual - expected) < tolerance
        elif isinstance(expected, np.ndarray) and isinstance(actual, np.ndarray):
            match = np.allclose(actual, expected, atol=tolerance)
        else:
            match = actual == expected
        
        if match:
            return self._display_result(True, "Output matches expected value")
        else:
            return self._display_result(False, "Output does not match expected value",
                                      f"Expected: {expected}, Got: {actual}")
    
    def validate_dataframe(self, df: Any, expected_shape: Optional[tuple] = None,
                          expected_columns: Optional[List[str]] = None,
                          expected_dtypes: Optional[Dict[str, type]] = None) -> bool:
        """
        Validate pandas DataFrame properties.
        
        Args:
            df: The dataframe to validate
            expected_shape: Expected (rows, cols) tuple
            expected_columns: Expected column names
            expected_dtypes: Expected column data types
        """
        if not isinstance(df, pd.DataFrame):
            return self._display_result(False, "Not a DataFrame",
                                      f"Got {type(df).__name__} instead")
        
        issues = []
        
        if expected_shape and df.shape != expected_shape:
            issues.append(f"Shape mismatch: expected {expected_shape}, got {df.shape}")
        
        if expected_columns:
            missing_cols = set(expected_columns) - set(df.columns)
            if missing_cols:
                issues.append(f"Missing columns: {missing_cols}")
        
        if expected_dtypes:
            for col, expected_type in expected_dtypes.items():
                if col in df.columns and not df[col].dtype == expected_type:
                    issues.append(f"Column '{col}' has wrong dtype: expected {expected_type}, got {df[col].dtype}")
        
        if issues:
            return self._display_result(False, "DataFrame validation failed", "; ".join(issues))
        
        return self._display_result(True, "DataFrame validated successfully")
    
    def check_embedding_shape(self, embedding: Any, expected_dim: int) -> bool:
        """Check if embedding has correct dimensions."""
        try:
            if hasattr(embedding, '__len__'):
                actual_dim = len(embedding)
            elif hasattr(embedding, 'shape'):
                actual_dim = embedding.shape[-1]
            else:
                return self._display_result(False, "Invalid embedding format",
                                          "Embedding should be a list or array")
            
            if actual_dim != expected_dim:
                return self._display_result(False, f"Embedding dimension mismatch",
                                          f"Expected {expected_dim}, got {actual_dim}")
            
            return self._display_result(True, f"Embedding shape is correct: {actual_dim}")
        except Exception as e:
            return self._display_result(False, "Error checking embedding shape", str(e))
    
    def assert_in_dataframe(self, df: Any, column: str, value: Any) -> bool:
        """Check if a value exists in a dataframe column."""
        if not isinstance(df, pd.DataFrame):
            return self._display_result(False, "Not a DataFrame",
                                      f"Got {type(df).__name__} instead")
        
        if column not in df.columns:
            return self._display_result(False, f"Column '{column}' not found",
                                      f"Available columns: {list(df.columns)}")
        
        if value not in df[column].values:
            return self._display_result(False, f"Value not found in column '{column}'",
                                      f"Looking for: {value}")
        
        return self._display_result(True, f"Found {value} in {column}")
    
    def validate_file_exists(self, filepath: str) -> bool:
        """Validate that a file exists."""
        import os
        if not os.path.exists(filepath):
            return self._display_result(False, f"File not found: {filepath}",
                                      "Make sure the file path is correct")
        
        return self._display_result(True, f"File exists: {filepath}")
    
    def validate_string_pattern(self, text: str, pattern: str, 
                              description: str = "pattern") -> bool:
        """Validate that a string matches a regex pattern."""
        if re.match(pattern, text):
            return self._display_result(True, f"Text matches {description}")
        else:
            return self._display_result(False, f"Text does not match {description}",
                                      f"Pattern: {pattern}")
    
    def validate_range(self, value: Union[int, float], min_val: Optional[float] = None, 
                      max_val: Optional[float] = None) -> bool:
        """Validate that a value is within a specified range."""
        if min_val is not None and value < min_val:
            return self._display_result(False, f"Value {value} is below minimum",
                                      f"Minimum allowed: {min_val}")
        
        if max_val is not None and value > max_val:
            return self._display_result(False, f"Value {value} is above maximum",
                                      f"Maximum allowed: {max_val}")
        
        return self._display_result(True, f"Value {value} is within valid range")
    
    def validate_list_items(self, lst: List[Any], 
                          validator_func: Callable[[Any], bool],
                          description: str = "validation") -> bool:
        """Validate all items in a list using a custom function."""
        if not isinstance(lst, list):
            return self._display_result(False, "Not a list",
                                      f"Got {type(lst).__name__} instead")
        
        invalid_items = []
        for i, item in enumerate(lst):
            try:
                if not validator_func(item):
                    invalid_items.append((i, item))
            except Exception as e:
                invalid_items.append((i, f"Error: {e}"))
        
        if invalid_items:
            details = f"Failed items: {invalid_items[:3]}{'...' if len(invalid_items) > 3 else ''}"
            return self._display_result(False, f"List {description} failed", details)
        
        return self._display_result(True, f"All {len(lst)} items passed {description}")
    
    def validate_custom(self, condition: bool, success_msg: str, 
                       failure_msg: str, details: str = "") -> bool:
        """Generic validation with custom condition and messages."""
        if condition:
            return self._display_result(True, success_msg)
        else:
            return self._display_result(False, failure_msg, details)
    
    def validate_and_mark_complete(self, step_name: str, condition: bool,
                                 success_msg: str = "Step completed!",
                                 failure_msg: str = "Step not yet complete") -> bool:
        """
        Validate a condition and automatically mark progress if validator has progress_tracker.
        
        Args:
            step_name: Name of the step in progress tracker
            condition: Boolean condition to validate
            success_msg: Message to show on success
            failure_msg: Message to show on failure
        """
        result = self.validate_custom(condition, success_msg, failure_msg)
        
        if result and self.progress_tracker:
            self.progress_tracker.mark_done(step_name)
        
        return result
    
    def create_step_validator(self, step_name: str) -> Callable:
        """
        Create a validator function tied to a specific step.
        
        Returns a function that when called with a condition, validates and marks progress.
        """
        def validator(condition: bool, success_msg: str = f"{step_name} completed!",
                     failure_msg: str = f"{step_name} not yet complete"):
            return self.validate_and_mark_complete(step_name, condition, success_msg, failure_msg)
        
        return validator