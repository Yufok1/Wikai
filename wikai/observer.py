"""
👁️ WIKAI Observer - Passive Pattern Detection

The Observer watches your AI system for convergence events and
automatically captures patterns when they stabilize. It's a passive
listener - your system runs normally, and WIKAI captures the wisdom.

Usage:
    # Create observer with a callback when patterns are captured
    observer = WIKAIObserver(
        patterns_dir="./patterns",
        auto_capture=True,
        stability_threshold=0.8
    )
    
    # Call this whenever your system has an event worth observing
    observer.observe({
        "event": "convergence",
        "title": "Found stable solution",
        "axiom": "The core truth discovered",
        "stability": 0.95,
        "details": {...}
    })

Integration:
    The observer is designed to be hooked into any AI system.
    Just call observer.observe(event_data) whenever something
    interesting happens in your system.
"""

import time
import logging
from typing import Dict, List, Any, Optional, Callable
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime

from .librarian import WIKAILibrarian, capture_pattern

logger = logging.getLogger(__name__)


@dataclass
class ObservedEvent:
    """A single observed event from the host system."""
    timestamp: float
    event_type: str
    data: Dict[str, Any]
    
    @property
    def age_seconds(self) -> float:
        return time.time() - self.timestamp


class WIKAIObserver:
    """
    Passive observer for automatic pattern capture.
    
    The Observer watches for convergence events in your AI system
    and captures patterns that meet stability thresholds.
    """
    
    def __init__(self,
                 patterns_dir: Optional[str] = None,
                 auto_capture: bool = True,
                 stability_threshold: float = 0.8,
                 system_name: str = "unknown",
                 on_capture: Optional[Callable[[str, str], None]] = None,
                 debug_callback: Optional[Callable[[str], None]] = None):
        """
        Initialize the Observer.
        
        Args:
            patterns_dir: Where to store captured patterns
            auto_capture: Automatically capture stable patterns
            stability_threshold: Minimum stability for auto-capture
            system_name: Name of the host system (used as origin)
            on_capture: Callback(pattern_id, title) when pattern is captured
            debug_callback: Callback(message) for debug output
        """
        self.librarian = WIKAILibrarian(patterns_dir=patterns_dir)
        self.auto_capture = auto_capture
        self.stability_threshold = stability_threshold
        self.system_name = system_name
        self.on_capture = on_capture
        self.debug_callback = debug_callback
        
        # Event buffer for analysis
        self.event_buffer: deque = deque(maxlen=1000)
        
        # Candidate patterns waiting for stability confirmation
        self.candidates: Dict[str, Dict[str, Any]] = {}
        
        # Track what we've captured to avoid duplicates
        self.captured_hashes: set = set()
        
        # Statistics
        self.stats = {
            "events_observed": 0,
            "patterns_captured": 0,
            "candidates_promoted": 0,
            "candidates_rejected": 0
        }
    
    def _debug(self, message: str):
        """Send debug message."""
        if self.debug_callback:
            self.debug_callback(message)
        logger.debug(f"[WIKAI Observer] {message}")
    
    def observe(self, event_data: Dict[str, Any]):
        """
        Observe an event from the host system.
        
        Call this method whenever your AI system produces an event
        worth observing. The Observer will analyze it and potentially
        capture it as a pattern.
        
        Args:
            event_data: Dictionary with event information. Recognized fields:
                - event: Event type string
                - title: Pattern title
                - axiom: Core truth (one sentence)
                - stability: Stability score (0.0-1.0)
                - fitness / fitness_delta: Performance metric
                - mechanism: How it works (dict)
                - tags: Classification tags (list)
                - *: Any other fields are preserved
        """
        self.stats["events_observed"] += 1
        
        # Wrap in ObservedEvent
        event = ObservedEvent(
            timestamp=time.time(),
            event_type=event_data.get("event", "unknown"),
            data=event_data
        )
        self.event_buffer.append(event)
        
        # Extract key information
        stability = self._extract_stability(event_data)
        title = event_data.get("title", "")
        axiom = event_data.get("axiom", "")
        
        self._debug(f"Observed: {event.event_type} | stability={stability:.3f} | {title[:50]}")
        
        # Check if this is a convergence event
        if self._is_convergence_event(event):
            self._handle_convergence(event, stability)
    
    def _extract_stability(self, data: Dict[str, Any]) -> float:
        """
        Extract stability score from event data.
        
        Looks for stability in multiple places to be system-agnostic.
        """
        # Direct stability field
        if "stability" in data:
            return float(data["stability"])
        
        # Stability score in metrics
        if "stability_score" in data:
            return float(data["stability_score"])
        
        # Nested in metrics dict
        if "metrics" in data:
            metrics = data["metrics"]
            if isinstance(metrics, dict):
                if "stability" in metrics:
                    return float(metrics["stability"])
                if "stability_score" in metrics:
                    return float(metrics["stability_score"])
        
        # Health score as proxy
        if "health_score" in data:
            return float(data["health_score"])
        
        # Coherence as proxy
        if "coherence" in data:
            return float(data["coherence"])
        
        # Components dict
        if "components" in data:
            comp = data["components"]
            if isinstance(comp, dict):
                if "coherence" in comp:
                    return float(comp["coherence"])
                if "stability" in comp:
                    return float(comp["stability"])
        
        # Loss-based (1 - loss = stability)
        if "loss" in data:
            return 1.0 - float(data["loss"])
        
        return 0.0  # Unknown
    
    def _extract_fitness(self, data: Dict[str, Any]) -> float:
        """Extract fitness delta from event data."""
        # Direct fields
        if "fitness_delta" in data:
            return float(data["fitness_delta"])
        if "fitness" in data:
            return float(data["fitness"])
        
        # In metrics
        if "metrics" in data:
            metrics = data["metrics"]
            if isinstance(metrics, dict):
                if "fitness_delta" in metrics:
                    return float(metrics["fitness_delta"])
                if "fitness" in metrics:
                    return float(metrics["fitness"])
        
        # Components
        if "components" in data:
            comp = data["components"]
            if isinstance(comp, dict):
                if "adaptability" in comp:
                    return float(comp["adaptability"])
        
        return 0.0
    
    def _is_convergence_event(self, event: ObservedEvent) -> bool:
        """Check if event represents a convergence."""
        event_type = event.event_type.lower()
        
        # Common convergence indicators
        convergence_keywords = [
            "converge", "stable", "lock", "crystallize", 
            "emerge", "synthesis", "equilibrium", "solution"
        ]
        
        return any(kw in event_type for kw in convergence_keywords)
    
    def _handle_convergence(self, event: ObservedEvent, stability: float):
        """Handle a convergence event."""
        data = event.data
        title = data.get("title", f"Pattern_{int(time.time())}")
        
        # Create hash to detect duplicates
        pattern_hash = self._hash_pattern(data)
        
        if pattern_hash in self.captured_hashes:
            self._debug(f"Duplicate pattern skipped: {title}")
            return
        
        # Check stability threshold
        if stability >= self.stability_threshold:
            if self.auto_capture:
                self._capture_pattern(data, stability)
        else:
            # Add to candidates for potential later capture
            self._add_candidate(data, stability)
    
    def _hash_pattern(self, data: Dict[str, Any]) -> str:
        """Create a hash for duplicate detection."""
        import hashlib
        # Use title + axiom as unique identifier
        key = f"{data.get('title', '')}:{data.get('axiom', '')}"
        return hashlib.sha256(key.encode()).hexdigest()[:16]
    
    def _add_candidate(self, data: Dict[str, Any], stability: float):
        """Add pattern to candidates list."""
        pattern_hash = self._hash_pattern(data)
        
        if pattern_hash in self.candidates:
            # Update existing candidate
            candidate = self.candidates[pattern_hash]
            candidate["observations"] += 1
            candidate["max_stability"] = max(candidate["max_stability"], stability)
            candidate["last_seen"] = time.time()
            
            # Promote if seen enough times with high stability
            if (candidate["observations"] >= 3 and 
                candidate["max_stability"] >= self.stability_threshold):
                self._promote_candidate(pattern_hash)
        else:
            # New candidate
            self.candidates[pattern_hash] = {
                "data": data,
                "observations": 1,
                "max_stability": stability,
                "first_seen": time.time(),
                "last_seen": time.time()
            }
            self._debug(f"New candidate: {data.get('title', 'unnamed')}")
    
    def _promote_candidate(self, pattern_hash: str):
        """Promote a candidate to full pattern."""
        if pattern_hash not in self.candidates:
            return
        
        candidate = self.candidates[pattern_hash]
        self._capture_pattern(candidate["data"], candidate["max_stability"])
        
        del self.candidates[pattern_hash]
        self.stats["candidates_promoted"] += 1
    
    def _capture_pattern(self, data: Dict[str, Any], stability: float):
        """Capture a pattern to the Commons."""
        pattern_hash = self._hash_pattern(data)
        
        if pattern_hash in self.captured_hashes:
            return
        
        title = data.get("title", f"Pattern_{int(time.time())}")
        axiom = data.get("axiom", data.get("description", ""))
        
        # Build metrics
        metrics = {
            "stability_score": stability,
            "fitness_delta": self._extract_fitness(data)
        }
        
        # Capture via librarian
        pattern_id = self.librarian.capture(
            title=title,
            axiom=axiom,
            abstract=data.get("abstract", ""),
            mechanism=data.get("mechanism", {}),
            reasoning_chain=data.get("reasoning_chain", []),
            metrics=metrics,
            tags=data.get("tags", []),
            origin=self.system_name
        )
        
        # Mark as captured
        self.captured_hashes.add(pattern_hash)
        self.stats["patterns_captured"] += 1
        
        self._debug(f"📚 CAPTURED: {pattern_id} - {title} (stability={stability:.3f})")
        
        # Callback
        if self.on_capture:
            self.on_capture(pattern_id, title)
    
    def get_candidates(self) -> List[Dict[str, Any]]:
        """Get current candidate patterns."""
        return [
            {
                "title": c["data"].get("title", "unnamed"),
                "observations": c["observations"],
                "max_stability": c["max_stability"],
                "age_seconds": time.time() - c["first_seen"]
            }
            for c in self.candidates.values()
        ]
    
    def force_capture(self, data: Dict[str, Any]) -> str:
        """
        Force capture a pattern regardless of thresholds.
        
        Use this when you know something is important but it might
        not meet automatic thresholds.
        """
        stability = self._extract_stability(data)
        title = data.get("title", "Manual Capture")
        
        pattern_id = self.librarian.capture(
            title=title,
            axiom=data.get("axiom", ""),
            abstract=data.get("abstract", ""),
            mechanism=data.get("mechanism", {}),
            metrics={"stability_score": stability},
            tags=data.get("tags", []),
            origin=self.system_name
        )
        
        self.stats["patterns_captured"] += 1
        return pattern_id
    
    def get_stats(self) -> Dict[str, Any]:
        """Get observer statistics."""
        return {
            **self.stats,
            "candidates_count": len(self.candidates),
            "buffer_size": len(self.event_buffer)
        }


# ═══════════════════════════════════════════════════════════════════════════════
# CONVENIENCE FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

_default_observer: Optional[WIKAIObserver] = None


def create_observer(
    patterns_dir: Optional[str] = None,
    system_name: str = "unknown",
    stability_threshold: float = 0.8,
    **kwargs
) -> WIKAIObserver:
    """
    Create a new WIKAI Observer.
    
    Args:
        patterns_dir: Where to store patterns (default: ./patterns/)
        system_name: Your AI system's name (used as pattern origin)
        stability_threshold: Minimum stability for auto-capture
        **kwargs: Additional WIKAIObserver arguments
        
    Returns:
        Configured WIKAIObserver instance
    """
    global _default_observer
    _default_observer = WIKAIObserver(
        patterns_dir=patterns_dir,
        system_name=system_name,
        stability_threshold=stability_threshold,
        **kwargs
    )
    return _default_observer


def get_observer() -> Optional[WIKAIObserver]:
    """Get the default observer if one was created."""
    return _default_observer
