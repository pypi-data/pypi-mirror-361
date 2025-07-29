"""
Jupyter Lab Utils - A comprehensive toolkit for creating interactive lab exercises.

Provides progress tracking, validation methods, and display utilities for 
creating interactive lab exercises in Jupyter notebooks.
"""

from ._version import (
    __version__,
    __version_info__,
    __title__,
    __description__,
    __author__,
    __author_email__,
    __license__,
    __url__,
)

from .progress import LabProgress
from .validator import LabValidator
from .display import (
    show_info,
    show_warning,
    show_error,
    show_success,
    show_code,
    show_hint,
    show_progress_bar,
    show_json,
    show_table,
    show_checklist,
    show_tabs,
    clear
)

__all__ = [
    # Version info
    "__version__",
    "__version_info__",
    "__title__",
    "__description__",
    "__author__",
    "__author_email__",
    "__license__",
    "__url__",
    
    # Progress tracking
    "LabProgress",
    
    # Validation
    "LabValidator",
    
    # Display functions
    "show_info",
    "show_warning",
    "show_error",
    "show_success",
    "show_code",
    "show_hint",
    "show_progress_bar",
    "show_json",
    "show_table",
    "show_checklist",
    "show_tabs",
    "clear"
]