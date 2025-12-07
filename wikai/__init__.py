"""
📚 WIKAI - Wisdom Keeper for Artificial Intelligence

The universal pattern library for AI systems.

WIKAI captures, stores, and shares the wisdom that emerges when AI systems
discover stable truths. It's infrastructure - not a system, but a library
for all systems.

Usage:
    from wikai import capture_pattern, create_observer, WIKAILibrarian
    
    # Capture a pattern
    pattern_id = capture_pattern(
        title="Cooperative Equilibrium",
        axiom="Mutual benefit exceeds individual gain",
        stability_score=0.92,
        tags=["cooperation"],
        origin="MySystem"
    )
    
    # Create an observer
    observer = create_observer(
        patterns_dir="./patterns",
        system_name="MySystem"
    )
"""

__version__ = "0.1.0"
__author__ = "WIKAI Contributors"

# Core imports
from .librarian import WIKAILibrarian, WIKAIPattern, capture_pattern, get_librarian
from .observer import WIKAIObserver, create_observer, get_observer
from .schema import validate_pattern, get_schema, PATTERN_SCHEMA, SUGGESTED_TAGS

__all__ = [
    # Classes
    "WIKAILibrarian",
    "WIKAIPattern", 
    "WIKAIObserver",
    # Convenience functions
    "capture_pattern",
    "create_observer",
    "get_librarian",
    "get_observer",
    # Schema
    "validate_pattern",
    "get_schema",
    "PATTERN_SCHEMA",
    "SUGGESTED_TAGS",
]
