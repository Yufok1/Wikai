"""
Observer Integration Example

This example shows how to set up a WIKAI Observer to passively
capture patterns from your AI system.
"""

import time
import random
from wikai import create_observer, WIKAIObserver


def on_pattern_captured(pattern_id: str, title: str):
    """Called when the observer captures a pattern."""
    print(f"📚 CAPTURED: {pattern_id} - {title}")


def debug_output(message: str):
    """Called for debug messages from the observer."""
    print(f"[WIKAI] {message}")


# Create an observer
observer = create_observer(
    patterns_dir="./patterns",
    system_name="ExampleSystem",
    stability_threshold=0.8,  # Only capture patterns with stability >= 0.8
    on_capture=on_pattern_captured,
    debug_callback=debug_output
)

print("🔭 WIKAI Observer created")
print("   - Watching for convergence events")
print("   - Stability threshold: 0.8")
print()


# Simulate events from your AI system
# In a real system, you'd hook observer.observe() into your event stream

def simulate_ai_system():
    """Simulate an AI system generating events."""
    
    events = [
        {
            "event": "processing",
            "message": "Exploring solution space...",
            "stability": 0.3
        },
        {
            "event": "candidate_found",
            "title": "Local Optimum A",
            "stability": 0.5
        },
        {
            "event": "convergence_detected",
            "title": "Pareto Frontier Strategy",
            "axiom": "Multi-objective optimization requires trading off between goals",
            "stability": 0.75,
            "mechanism": {"type": "pareto", "objectives": 3}
        },
        {
            "event": "stable_convergence",
            "title": "Resource Allocation Principle",
            "axiom": "Allocate resources proportional to demonstrated need",
            "stability": 0.92,
            "fitness_delta": 0.08,
            "mechanism": {
                "strategy": "proportional",
                "feedback_loop": True,
                "adaptation_rate": 0.1
            },
            "tags": ["allocation", "adaptation"]
        },
        {
            "event": "exploration",
            "message": "Continuing search...",
            "stability": 0.4
        },
        {
            "event": "convergence_locked",
            "title": "Hierarchical Delegation",
            "axiom": "Complex problems decompose into independent subproblems",
            "stability": 0.88,
            "fitness_delta": 0.12,
            "mechanism": {
                "decomposition": "recursive",
                "independence_check": True
            },
            "tags": ["hierarchy", "decomposition", "scaling"]
        }
    ]
    
    for event in events:
        print(f"\n>>> Simulated event: {event.get('event', 'unknown')}")
        observer.observe(event)
        time.sleep(0.5)
    
    print("\n" + "="*50)
    print("Simulation complete")
    print(f"Observer stats: {observer.get_stats()}")
    print(f"Candidates pending: {observer.get_candidates()}")


if __name__ == "__main__":
    simulate_ai_system()
