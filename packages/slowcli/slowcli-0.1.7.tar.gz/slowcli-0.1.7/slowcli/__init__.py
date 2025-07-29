"""
SlowCLI - A deliberately slow CLI application with complex argument structures.

This package demonstrates a realistic slow CLI with heavy imports in the main entry point,
but follows proper Python packaging practices by keeping __init__.py lightweight.
"""

import logging
from pathlib import Path

# Version information
__version__ = "0.1.7"
__author__ = "Your Name"
__email__ = "your.email@example.com"

# Configure basic logging (lightweight)
logger = logging.getLogger(__name__)

# Lazy imports - only import when actually needed
def get_main():
    """Lazy import of main function to avoid heavy imports during package import."""
    from .main import main
    return main

def get_cli():
    """Lazy import of CLI class to avoid heavy imports during package import."""
    from .cli import SlowCLI
    return SlowCLI

def get_utils():
    """Lazy import of utility classes to avoid heavy imports during package import."""
    from .utils import PerformanceTracker, ConfigManager
    return PerformanceTracker, ConfigManager

# Only expose essential items at package level
__all__ = [
    '__version__',
    '__author__',
    '__email__',
    'get_main',
    'get_cli',
    'get_utils',
]

# For backward compatibility, provide main function at package level
def main(*args, **kwargs):
    """Main entry point with lazy loading."""
    main_func = get_main()
    return main_func(*args, **kwargs)
