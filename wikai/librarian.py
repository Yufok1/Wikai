"""
📚 WIKAI Librarian - Pattern Storage and Retrieval

The Librarian manages the Commons: a collection of validated patterns
discovered by AI systems. Each pattern represents a stable truth -
something that emerged through convergence and proved itself useful.

Usage:
    librarian = WIKAILibrarian()
    
    # Capture a pattern
    pattern_id = librarian.capture(
        title="The Iron Wood Protocol",
        axiom="Hardness + Softness = Persistence",
        abstract="Conflict resolution through role transformation",
        mechanism={"thesis": {...}, "antithesis": {...}, "synthesis": {...}},
        reasoning_chain=["Step 1", "Step 2", "Step 3"],
        metrics={"stability_score": 0.98},
        tags=["conflict_resolution", "symbiosis"]
    )
    
    # Query patterns
    patterns = librarian.search(tags=["conflict_resolution"])
    pattern = librarian.get("WIKAI_0001")
"""

import json
import hashlib
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Union
import logging

logger = logging.getLogger(__name__)


@dataclass
class WIKAIPattern:
    """
    A captured pattern from the Commons.
    
    Each pattern represents a stable truth discovered by an AI system.
    The schema is designed to be system-agnostic - any AI can contribute.
    """
    id: str
    title: str
    axiom: str  # The core truth in one sentence
    
    # Origin information
    origin: str = "unknown"  # System that discovered it
    timestamp: str = ""
    
    # Content
    abstract: str = ""  # Brief description
    mechanism: Dict[str, Any] = field(default_factory=dict)  # How it works
    reasoning_chain: List[str] = field(default_factory=list)  # Steps to discovery
    
    # Metrics
    metrics: Dict[str, float] = field(default_factory=dict)
    
    # Classification
    tags: List[str] = field(default_factory=list)
    
    # Raw data storage
    data: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def stability_score(self) -> float:
        """Get stability score from metrics."""
        return self.metrics.get("stability_score", 0.0)
    
    @property
    def fitness_delta(self) -> float:
        """Get fitness delta from metrics."""
        return self.metrics.get("fitness_delta", 0.0)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to JSON-serializable dictionary."""
        return {
            "id": self.id,
            "title": self.title,
            "axiom": self.axiom,
            "origin": self.origin,
            "timestamp": self.timestamp,
            "abstract": self.abstract,
            "mechanism": self.mechanism,
            "reasoning_chain": self.reasoning_chain,
            "metrics": self.metrics,
            "tags": self.tags,
            "data": self.data
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "WIKAIPattern":
        """Create pattern from dictionary."""
        return cls(
            id=data.get("id", ""),
            title=data.get("title", "Untitled"),
            axiom=data.get("axiom", ""),
            origin=data.get("origin", "unknown"),
            timestamp=data.get("timestamp", ""),
            abstract=data.get("abstract", ""),
            mechanism=data.get("mechanism", {}),
            reasoning_chain=data.get("reasoning_chain", []),
            metrics=data.get("metrics", {}),
            tags=data.get("tags", []),
            data=data
        )


class WIKAILibrarian:
    """
    The Librarian of the Commons.
    
    Manages pattern storage, retrieval, and search. Patterns are stored
    as JSON files in a directory structure that can be version-controlled
    and shared across systems.
    """
    
    def __init__(self, 
                 patterns_dir: Optional[Union[str, Path]] = None,
                 auto_create: bool = True):
        """
        Initialize the Librarian.
        
        Args:
            patterns_dir: Directory to store patterns. Defaults to ./patterns/
            auto_create: Create directory if it doesn't exist
        """
        if patterns_dir is None:
            patterns_dir = Path(__file__).parent.parent / "patterns"
        
        self.patterns_dir = Path(patterns_dir)
        
        if auto_create and not self.patterns_dir.exists():
            self.patterns_dir.mkdir(parents=True, exist_ok=True)
            logger.info(f"[WIKAI] Created patterns directory: {self.patterns_dir}")
        
        # Cache loaded patterns
        self._cache: Dict[str, WIKAIPattern] = {}
        self._next_id: int = 1
        
        # Load existing patterns
        self._scan_patterns()
    
    def _scan_patterns(self):
        """Scan patterns directory and update cache."""
        if not self.patterns_dir.exists():
            return
        
        max_id = 0
        for path in self.patterns_dir.glob("*.json"):
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                pattern = WIKAIPattern.from_dict(data)
                self._cache[pattern.id] = pattern
                
                # Track highest ID for auto-increment
                if pattern.id.startswith("WIKAI_"):
                    try:
                        num = int(pattern.id.split("_")[1])
                        max_id = max(max_id, num)
                    except (IndexError, ValueError):
                        pass
            except Exception as e:
                logger.warning(f"[WIKAI] Failed to load pattern {path}: {e}")
        
        self._next_id = max_id + 1
        logger.info(f"[WIKAI] Loaded {len(self._cache)} patterns from Commons")
    
    def _generate_id(self) -> str:
        """Generate next pattern ID."""
        pattern_id = f"WIKAI_{self._next_id:04d}"
        self._next_id += 1
        return pattern_id
    
    def capture(self,
                title: str,
                axiom: str,
                abstract: str = "",
                mechanism: Optional[Dict[str, Any]] = None,
                reasoning_chain: Optional[List[str]] = None,
                metrics: Optional[Dict[str, float]] = None,
                tags: Optional[List[str]] = None,
                origin: str = "unknown",
                pattern_id: Optional[str] = None) -> str:
        """
        Capture a new pattern to the Commons.
        
        Args:
            title: Pattern title
            axiom: Core truth in one sentence
            abstract: Brief description
            mechanism: How it works (structured data)
            reasoning_chain: Steps to discovery
            metrics: Numeric measurements (stability_score, fitness_delta, etc.)
            tags: Classification tags
            origin: System that discovered it
            pattern_id: Optional specific ID (auto-generated if not provided)
            
        Returns:
            Pattern ID
        """
        if pattern_id is None:
            pattern_id = self._generate_id()
        
        pattern = WIKAIPattern(
            id=pattern_id,
            title=title,
            axiom=axiom,
            origin=origin,
            timestamp=datetime.utcnow().isoformat() + "Z",
            abstract=abstract,
            mechanism=mechanism or {},
            reasoning_chain=reasoning_chain or [],
            metrics=metrics or {},
            tags=tags or []
        )
        
        # Save to file
        filename = f"{pattern_id}_{self._slugify(title)}.json"
        filepath = self.patterns_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(pattern.to_dict(), f, indent=2, ensure_ascii=False)
        
        # Update cache
        self._cache[pattern_id] = pattern
        
        logger.info(f"[WIKAI] 📚 Captured: {pattern_id} - {title}")
        return pattern_id
    
    def _slugify(self, text: str) -> str:
        """Convert text to filename-safe slug."""
        import re
        text = text.lower()
        text = re.sub(r'[^a-z0-9]+', '_', text)
        text = text.strip('_')
        return text[:50]  # Limit length
    
    def get(self, pattern_id: str) -> Optional[WIKAIPattern]:
        """Get a pattern by ID."""
        return self._cache.get(pattern_id)
    
    def list_all(self) -> List[WIKAIPattern]:
        """List all patterns in the Commons."""
        return list(self._cache.values())
    
    def search(self,
               query: Optional[str] = None,
               tags: Optional[List[str]] = None,
               min_stability: float = 0.0,
               limit: int = 100) -> List[WIKAIPattern]:
        """
        Search patterns in the Commons.
        
        Args:
            query: Text search in title, axiom, abstract
            tags: Filter by tags (any match)
            min_stability: Minimum stability score
            limit: Maximum results
            
        Returns:
            List of matching patterns
        """
        results = []
        
        for pattern in self._cache.values():
            # Tag filter
            if tags:
                if not any(t in pattern.tags for t in tags):
                    continue
            
            # Stability filter
            if pattern.stability_score < min_stability:
                continue
            
            # Text search
            if query:
                query_lower = query.lower()
                searchable = f"{pattern.title} {pattern.axiom} {pattern.abstract}".lower()
                if query_lower not in searchable:
                    continue
            
            results.append(pattern)
            
            if len(results) >= limit:
                break
        
        return results
    
    def get_tags(self) -> Dict[str, int]:
        """Get all tags with counts."""
        tag_counts: Dict[str, int] = {}
        for pattern in self._cache.values():
            for tag in pattern.tags:
                tag_counts[tag] = tag_counts.get(tag, 0) + 1
        return dict(sorted(tag_counts.items(), key=lambda x: -x[1]))
    
    def get_stats(self) -> Dict[str, Any]:
        """Get Commons statistics."""
        patterns = list(self._cache.values())
        return {
            "total_patterns": len(patterns),
            "total_tags": len(self.get_tags()),
            "avg_stability": sum(p.stability_score for p in patterns) / len(patterns) if patterns else 0,
            "origins": list(set(p.origin for p in patterns))
        }


# ═══════════════════════════════════════════════════════════════════════════════
# CONVENIENCE FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

_default_librarian: Optional[WIKAILibrarian] = None


def get_librarian(patterns_dir: Optional[str] = None) -> WIKAILibrarian:
    """Get or create the default librarian."""
    global _default_librarian
    if _default_librarian is None:
        _default_librarian = WIKAILibrarian(patterns_dir=patterns_dir)
    return _default_librarian


def capture_pattern(
    title: str,
    axiom: str,
    mechanism: Optional[Dict[str, Any]] = None,
    stability_score: float = 0.0,
    tags: Optional[List[str]] = None,
    origin: str = "unknown",
    **kwargs
) -> str:
    """
    Quick capture a pattern to the Commons.
    
    This is the simplest API for any system to contribute a pattern.
    
    Args:
        title: What to call this pattern
        axiom: The core truth in one sentence
        mechanism: How it works (optional structured data)
        stability_score: How stable is this pattern (0.0-1.0)
        tags: Classification tags
        origin: Your system's name
        **kwargs: Additional fields (abstract, reasoning_chain, etc.)
        
    Returns:
        Pattern ID (e.g., "WIKAI_0042")
        
    Example:
        pattern_id = capture_pattern(
            title="Cooperative Equilibrium",
            axiom="Mutual benefit exceeds individual gain",
            mechanism={"strategy": "tit-for-tat"},
            stability_score=0.92,
            tags=["cooperation", "game_theory"],
            origin="MyAISystem"
        )
    """
    librarian = get_librarian()
    
    metrics = kwargs.pop("metrics", {})
    metrics["stability_score"] = stability_score
    
    return librarian.capture(
        title=title,
        axiom=axiom,
        mechanism=mechanism or {},
        metrics=metrics,
        tags=tags or [],
        origin=origin,
        **kwargs
    )
