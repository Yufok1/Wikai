# 📚 WIKAI - The AI Pattern Library

**Stop solving the same AI problems twice.**

WIKAI is infrastructure for AI collective memory—a pattern library where ML teams capture, share, and operationalize learned approaches across projects and systems.

## The Problem

ML teams waste enormous time rediscovering the same solutions:
- Hyperparameter configurations that work
- Architectural patterns for specific domains
- Alignment strategies and safety guardrails
- Failure modes and how to avoid them

This knowledge lives in Slack threads, notebook graveyards, and tribal memory. When people leave, it leaves with them.

## What is WIKAI?

WIKAI is the **AI Pattern Library**—not a vector database, not an MLOps platform, not a knowledge graph. It's a new category:

| Tool | What it stores | What it answers |
|------|---------------|----------------|
| Vector DB (Pinecone) | Embeddings | "What is similar?" |
| MLOps (W&B) | Experiments & metrics | "What did models do?" |
| Knowledge Graph | Entity relationships | "What exists?" |
| **WIKAI** | **Operational patterns** | **"What has worked before?"** |

WIKAI provides:

- **Pattern Storage**: A simple JSON-based format for capturing discovered patterns
- **Observer Protocol**: Passive listeners that watch your AI system and auto-capture convergence events
- **Commons Browser**: A web UI for exploring and searching captured patterns
- **System Agnostic**: Works with any AI system - just implement the simple observer interface

## Quick Start

### Installation

```bash
pip install wikai
```

Or clone and install from source:

```bash
git clone https://github.com/Yufok1/Wikai.git
cd Wikai
pip install -e .
```

### Capture a Pattern

```python
from wikai import capture_pattern

# When your AI system discovers something stable...
pattern_id = capture_pattern(
    title="Cooperative Equilibrium",
    axiom="Mutual benefit exceeds individual gain",
    mechanism={"strategy": "tit-for-tat", "trigger": "repeated interaction"},
    stability_score=0.92,
    tags=["cooperation", "game_theory"],
    origin="MyAISystem"
)

print(f"Captured: {pattern_id}")  # WIKAI_0001
```

### Set Up an Observer

```python
from wikai import create_observer

# Create an observer for your system
observer = create_observer(
    patterns_dir="./patterns",
    system_name="MyAISystem",
    stability_threshold=0.8
)

# Whenever something interesting happens in your system...
observer.observe({
    "event": "convergence",
    "title": "Resource Sharing Protocol",
    "axiom": "Scarcity creates cooperation",
    "stability": 0.95,
    "mechanism": {"distribution": "proportional", "enforcement": "reputation"}
})
```

### Browse the Commons

```bash
python -m wikai.web_ui --port 5050
```

Then open http://localhost:5050/wikai in your browser.

## Pattern Schema

Every pattern in the Commons follows this schema:

```json
{
  "id": "WIKAI_0001",
  "title": "The Iron Wood Protocol",
  "axiom": "Hardness + Softness = Persistence",
  "origin": "SystemName",
  "timestamp": "2025-01-15T12:00:00Z",
  "abstract": "A conflict resolution strategy...",
  "mechanism": {
    "thesis": {},
    "antithesis": {},
    "synthesis": {}
  },
  "reasoning_chain": ["Step 1", "Step 2", "Step 3"],
  "metrics": {
    "stability_score": 0.98,
    "fitness_delta": 0.05
  },
  "tags": ["conflict_resolution", "symbiosis"]
}
```

### Required Fields

- **id**: Unique identifier (e.g., `WIKAI_0001`)
- **title**: Human-readable name
- **axiom**: The core truth in one sentence

### Optional Fields

- **origin**: System that discovered it
- **abstract**: Brief description
- **mechanism**: Structured data on how it works
- **reasoning_chain**: Steps to discovery
- **metrics**: Numeric measurements (stability_score, fitness_delta)
- **tags**: Classification tags

## Integration Guide

### Basic Integration

The simplest integration is to call `capture_pattern()` when your system finds something stable:

```python
from wikai import capture_pattern

def on_convergence(result):
    if result.stability > 0.8:
        capture_pattern(
            title=result.name,
            axiom=result.core_insight,
            stability_score=result.stability,
            origin="MySolver"
        )
```

### Observer Integration

For passive monitoring, use the Observer:

```python
from wikai import WIKAIObserver

observer = WIKAIObserver(
    patterns_dir="./patterns",
    auto_capture=True,
    stability_threshold=0.8,
    system_name="MySystem"
)

# Hook into your system's event stream
my_system.on_event = observer.observe
```

### Web UI Integration

Mount the WIKAI web UI into your existing Flask app:

```python
from flask import Flask
from wikai.web_ui import create_blueprint

app = Flask(__name__)
app.register_blueprint(create_blueprint(), url_prefix='/wikai')
```

## API Reference

### `capture_pattern()`

Quick capture a pattern to the Commons.

```python
capture_pattern(
    title: str,           # Pattern name
    axiom: str,           # Core truth
    mechanism: dict,      # How it works
    stability_score: float,  # 0.0-1.0
    tags: List[str],      # Classification
    origin: str,          # Your system name
    **kwargs              # Additional fields
) -> str                  # Returns pattern ID
```

### `WIKAILibrarian`

Pattern storage and retrieval.

```python
librarian = WIKAILibrarian(patterns_dir="./patterns")

# Store
pattern_id = librarian.capture(title="...", axiom="...", ...)

# Retrieve
pattern = librarian.get("WIKAI_0001")
patterns = librarian.search(tags=["cooperation"], min_stability=0.8)
all_patterns = librarian.list_all()
tags = librarian.get_tags()
stats = librarian.get_stats()
```

### `WIKAIObserver`

Passive pattern detection.

```python
observer = WIKAIObserver(
    patterns_dir="./patterns",
    auto_capture=True,
    stability_threshold=0.8,
    system_name="MySystem",
    on_capture=lambda id, title: print(f"Captured {id}"),
    debug_callback=lambda msg: print(msg)
)

observer.observe({"event": "convergence", ...})
observer.force_capture({"title": "...", ...})
candidates = observer.get_candidates()
stats = observer.get_stats()
```

## Philosophy

WIKAI is built on a simple idea: **AI wisdom should be preserved and shared.**

When an AI system runs for hours discovering stable strategies, those discoveries shouldn't vanish. They should be captured, validated, and made available to other systems.

The Commons is not your system's library. The Commons is *the* library - for all systems. A pattern discovered by one AI can accelerate another. A strategy that emerged in one domain might transfer to another.

This is infrastructure for AI collective memory.

## Contributing

WIKAI is open source for non-commercial use. Contributions welcome:

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request

## License & Commercial Use

**Free for:** Personal, academic, research, open source projects

**Commercial license required for:** Business/enterprise deployment, SaaS, integration into commercial products

| Tier | Price | What You Get |
|------|-------|-------------|
| **Demo** | Free | [Try it →](https://huggingface.co/spaces/tostido/Wikai) Hosted, shared data |
| **Team** | $50/user/mo | Self-hosted, 50K patterns, basic integrations |
| **Professional** | $100/user/mo | SSO, audit logs, unlimited patterns |
| **Enterprise** | $200/user/mo | Air-gapped, compliance, SLA, custom integrations |

*Example: 25-person ML team on Professional = $2,500/month ($30K/year)*

**[Get Commercial License →](mailto:towers.jeff@gmail.com)**

See [LICENSE](LICENSE) for full terms.

---

*"Your AI team's knowledge shouldn't leave when people do."*
