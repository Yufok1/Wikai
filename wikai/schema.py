"""
📋 WIKAI Schema - Pattern Validation

Defines the schema for WIKAI patterns and provides validation utilities.
Patterns must conform to this schema to be stored in the Commons.
"""

from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass
import json

# ═══════════════════════════════════════════════════════════════════════════════
# SCHEMA DEFINITION
# ═══════════════════════════════════════════════════════════════════════════════

PATTERN_SCHEMA = {
    "type": "object",
    "required": ["id", "title", "axiom"],
    "properties": {
        "id": {
            "type": "string",
            "description": "Unique identifier (e.g., WIKAI_0001)",
            "pattern": "^WIKAI_[0-9]{4,}$"
        },
        "title": {
            "type": "string",
            "description": "Human-readable pattern name",
            "minLength": 1,
            "maxLength": 200
        },
        "axiom": {
            "type": "string",
            "description": "Core truth in one sentence",
            "maxLength": 500
        },
        "origin": {
            "type": "string",
            "description": "System that discovered the pattern",
            "default": "unknown"
        },
        "timestamp": {
            "type": "string",
            "description": "ISO 8601 timestamp",
            "format": "date-time"
        },
        "abstract": {
            "type": "string",
            "description": "Brief description of the pattern",
            "maxLength": 2000
        },
        "mechanism": {
            "type": "object",
            "description": "Structured data describing how the pattern works",
            "additionalProperties": True
        },
        "reasoning_chain": {
            "type": "array",
            "description": "Steps that led to the discovery",
            "items": {"type": "string"}
        },
        "metrics": {
            "type": "object",
            "description": "Numeric measurements",
            "properties": {
                "stability_score": {
                    "type": "number",
                    "minimum": 0,
                    "maximum": 1,
                    "description": "How stable the pattern is (0-1)"
                },
                "fitness_delta": {
                    "type": "number",
                    "description": "Performance improvement from this pattern"
                }
            }
        },
        "tags": {
            "type": "array",
            "description": "Classification tags",
            "items": {"type": "string"}
        },
        "data": {
            "type": "object",
            "description": "Additional raw data",
            "additionalProperties": True
        }
    }
}


# ═══════════════════════════════════════════════════════════════════════════════
# VALIDATION
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class ValidationResult:
    """Result of pattern validation."""
    valid: bool
    errors: List[str]
    warnings: List[str]


def validate_pattern(data: Dict[str, Any]) -> ValidationResult:
    """
    Validate a pattern against the schema.
    
    Args:
        data: Pattern data dictionary
        
    Returns:
        ValidationResult with valid flag and any errors/warnings
    """
    errors = []
    warnings = []
    
    # Required fields
    if not data.get("id"):
        errors.append("Missing required field: id")
    if not data.get("title"):
        errors.append("Missing required field: title")
    if not data.get("axiom"):
        errors.append("Missing required field: axiom")
    
    # ID format
    pattern_id = data.get("id", "")
    if pattern_id and not pattern_id.startswith("WIKAI_"):
        warnings.append(f"ID '{pattern_id}' should start with 'WIKAI_'")
    
    # Title length
    title = data.get("title", "")
    if len(title) > 200:
        errors.append(f"Title too long ({len(title)} chars, max 200)")
    
    # Axiom length
    axiom = data.get("axiom", "")
    if len(axiom) > 500:
        warnings.append(f"Axiom is long ({len(axiom)} chars, recommended max 500)")
    
    # Metrics validation
    metrics = data.get("metrics", {})
    if isinstance(metrics, dict):
        stability = metrics.get("stability_score")
        if stability is not None:
            if not isinstance(stability, (int, float)):
                errors.append("stability_score must be a number")
            elif not (0 <= stability <= 1):
                warnings.append(f"stability_score {stability} is outside normal range [0, 1]")
    
    # Tags validation
    tags = data.get("tags", [])
    if not isinstance(tags, list):
        errors.append("tags must be a list")
    elif not all(isinstance(t, str) for t in tags):
        errors.append("All tags must be strings")
    
    return ValidationResult(
        valid=len(errors) == 0,
        errors=errors,
        warnings=warnings
    )


def validate_pattern_strict(data: Dict[str, Any]) -> bool:
    """
    Strictly validate a pattern (must pass all checks).
    
    Args:
        data: Pattern data dictionary
        
    Returns:
        True if valid, raises ValueError if not
    """
    result = validate_pattern(data)
    if not result.valid:
        raise ValueError(f"Pattern validation failed: {'; '.join(result.errors)}")
    return True


# ═══════════════════════════════════════════════════════════════════════════════
# SCHEMA UTILITIES
# ═══════════════════════════════════════════════════════════════════════════════

def get_schema() -> Dict[str, Any]:
    """Get the JSON schema for patterns."""
    return PATTERN_SCHEMA.copy()


def get_schema_json() -> str:
    """Get the JSON schema as a JSON string."""
    return json.dumps(PATTERN_SCHEMA, indent=2)


def create_empty_pattern(pattern_id: str = "WIKAI_0000") -> Dict[str, Any]:
    """
    Create an empty pattern template.
    
    Args:
        pattern_id: ID for the new pattern
        
    Returns:
        Empty pattern dictionary with all fields
    """
    return {
        "id": pattern_id,
        "title": "",
        "axiom": "",
        "origin": "unknown",
        "timestamp": "",
        "abstract": "",
        "mechanism": {},
        "reasoning_chain": [],
        "metrics": {
            "stability_score": 0.0,
            "fitness_delta": 0.0
        },
        "tags": [],
        "data": {}
    }


# ═══════════════════════════════════════════════════════════════════════════════
# COMMON TAGS
# ═══════════════════════════════════════════════════════════════════════════════

# Suggested tags for pattern classification
SUGGESTED_TAGS = [
    # Domains
    "optimization",
    "learning",
    "reasoning",
    "planning",
    "perception",
    
    # Mechanisms
    "cooperation",
    "competition",
    "emergence",
    "convergence",
    "adaptation",
    
    # Properties
    "stable",
    "recursive",
    "compositional",
    "hierarchical",
    
    # Origins
    "discovered",
    "engineered",
    "emergent",
    "imported"
]


def suggest_tags(title: str, axiom: str, abstract: str = "") -> List[str]:
    """
    Suggest tags based on pattern content.
    
    Args:
        title: Pattern title
        axiom: Pattern axiom
        abstract: Pattern abstract
        
    Returns:
        List of suggested tags
    """
    text = f"{title} {axiom} {abstract}".lower()
    
    suggestions = []
    
    # Simple keyword matching
    keyword_tags = {
        "cooperation": ["cooperat", "mutual", "together", "share"],
        "competition": ["compet", "rival", "contest", "versus"],
        "optimization": ["optim", "improve", "enhance", "better"],
        "learning": ["learn", "train", "adapt", "improve"],
        "emergence": ["emerg", "arise", "spontan", "self-organ"],
        "convergence": ["converg", "stabil", "lock", "settle"],
        "stable": ["stable", "persist", "endur", "robust"],
        "recursive": ["recurs", "self-refer", "fractal", "nested"],
    }
    
    for tag, keywords in keyword_tags.items():
        if any(kw in text for kw in keywords):
            suggestions.append(tag)
    
    return suggestions
