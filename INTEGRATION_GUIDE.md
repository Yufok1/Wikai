# WIKAI Integration Guide

This guide shows how to integrate WIKAI into your AI system.

## Overview

WIKAI provides three levels of integration:

1. **Simple Capture** - Just call `capture_pattern()` when you have something
2. **Observer Pattern** - Hook an Observer into your event stream
3. **Full Integration** - Mount the web UI and use the API

## Level 1: Simple Capture

The easiest integration. When your system finds something stable, capture it:

```python
from wikai import capture_pattern

def my_solver(problem):
    solution = find_solution(problem)
    
    if solution.is_stable:
        capture_pattern(
            title=solution.name,
            axiom=solution.core_insight,
            stability_score=solution.stability,
            origin="MySolver"
        )
    
    return solution
```

That's it. Patterns are saved to `./patterns/` as JSON files.

## Level 2: Observer Pattern

For passive monitoring, create an Observer that watches your system:

```python
from wikai import create_observer

# Create observer
observer = create_observer(
    patterns_dir="./patterns",
    system_name="MySystem",
    stability_threshold=0.8
)

# Hook into your event stream
class MyAISystem:
    def __init__(self):
        self.observer = observer
    
    def emit_event(self, event_type, data):
        # Your normal event handling...
        process_event(event_type, data)
        
        # Let WIKAI observe
        self.observer.observe({
            "event": event_type,
            **data
        })
```

The Observer will automatically capture patterns that:
- Look like convergence events
- Meet the stability threshold
- Haven't been captured before

## Level 3: Full Integration

For the complete experience, mount the web UI:

```python
from flask import Flask
from wikai.web_ui import create_blueprint

app = Flask(__name__)
app.register_blueprint(create_blueprint(), url_prefix='/wikai')

# Now /wikai shows the Commons browser
```

## Event Format

The Observer looks for these fields in events:

| Field | Type | Description |
|-------|------|-------------|
| `event` | string | Event type (convergence, stable, lock, etc.) |
| `title` | string | Pattern name |
| `axiom` | string | Core truth |
| `stability` | float | Stability score (0-1) |
| `fitness` | float | Fitness value |
| `fitness_delta` | float | Fitness improvement |
| `mechanism` | dict | How it works |
| `tags` | list | Classification tags |

Alternative stability sources (Observer checks these in order):
- `stability` 
- `stability_score`
- `metrics.stability`
- `health_score`
- `coherence`
- `1 - loss`

## API Reference

### Capturing

```python
from wikai import capture_pattern, WIKAILibrarian

# Quick capture
pattern_id = capture_pattern(
    title="...",
    axiom="...",
    stability_score=0.9,
    ...
)

# With librarian
librarian = WIKAILibrarian(patterns_dir="./patterns")
pattern_id = librarian.capture(
    title="...",
    axiom="...",
    metrics={"stability_score": 0.9},
    ...
)
```

### Querying

```python
librarian = WIKAILibrarian()

# Get one
pattern = librarian.get("WIKAI_0001")

# Search
patterns = librarian.search(
    query="cooperation",
    tags=["game_theory"],
    min_stability=0.8
)

# List all
all_patterns = librarian.list_all()
```

### Observer

```python
from wikai import WIKAIObserver

observer = WIKAIObserver(
    patterns_dir="./patterns",
    auto_capture=True,
    stability_threshold=0.8,
    system_name="MySystem",
    on_capture=lambda id, title: print(f"Captured {id}"),
    debug_callback=lambda msg: print(msg)
)

# Observe events
observer.observe({"event": "convergence", ...})

# Force capture
observer.force_capture({"title": "...", ...})

# Get stats
observer.get_stats()
observer.get_candidates()
```

## Pattern Schema

```json
{
  "id": "WIKAI_0001",
  "title": "Pattern Name",
  "axiom": "Core truth in one sentence",
  "origin": "SystemName",
  "timestamp": "2025-01-15T12:00:00Z",
  "abstract": "Brief description",
  "mechanism": {},
  "reasoning_chain": [],
  "metrics": {
    "stability_score": 0.95,
    "fitness_delta": 0.1
  },
  "tags": ["tag1", "tag2"]
}
```

## Best Practices

1. **Be selective** - Only capture truly stable patterns
2. **Good axioms** - The axiom should be a complete thought in one sentence
3. **Rich mechanism** - Include enough detail to recreate the pattern
4. **Meaningful tags** - Use consistent tags across your system
5. **Track origin** - Always set the origin to your system name

## File Structure

After integration, your patterns directory will look like:

```
patterns/
├── WIKAI_0001_cooperative_equilibrium.json
├── WIKAI_0002_resource_allocation.json
└── WIKAI_0003_hierarchical_delegation.json
```

These files can be:
- Version controlled
- Shared across systems
- Manually edited
- Backed up
