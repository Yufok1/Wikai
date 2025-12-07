"""
WIKAI Commons - Universal AI Knowledge Repository
The Wikipedia for Artificial Intelligence

A universal commons unifying AI systems across ALL domains and industries.
Supports all knowledge types: patterns, models, embeddings, rules, ontologies,
heuristics, protocols, and cross-domain intelligence transfer.
"""

import gradio as gr
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
import hashlib

# ═══════════════════════════════════════════════════════════════════════════════
# CONSTANTS & CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════════

PATTERNS_DIR = Path("patterns")
PATTERNS_DIR.mkdir(exist_ok=True)

# Universal Domain Taxonomy
DOMAINS = [
    "Healthcare", "Finance", "Robotics", "NLP", "Computer Vision", 
    "Autonomous Systems", "Scientific Discovery", "Education",
    "Manufacturing", "Energy", "Agriculture", "Legal", "Security",
    "Gaming", "Creative Arts", "Social Systems", "Logistics",
    "Environmental", "Telecommunications", "General Intelligence",
    "Meta-Learning", "Cross-Domain", "Foundational"
]

# Knowledge Types - What kind of intelligence is being shared
KNOWLEDGE_TYPES = [
    "Pattern",           # Behavioral/emergent patterns
    "Axiom",             # Fundamental truths
    "Heuristic",         # Rules of thumb
    "Algorithm",         # Computational procedures
    "Model Weights",     # Neural network parameters
    "Embedding",         # Vector representations
    "Ontology",          # Knowledge structures
    "Protocol",          # Communication/interaction standards
    "Constraint",        # Boundaries and limits
    "Optimization",      # Performance improvements
    "Architecture",      # System designs
    "Dataset Schema",    # Data structure definitions
    "Evaluation Metric", # Measurement approaches
    "Failure Mode",      # What doesn't work
    "Transfer Learning", # Cross-domain adaptations
    "Emergent Behavior", # Unexpected discoveries
    "Causal Model",      # Cause-effect relationships
    "Decision Rule",     # If-then logic
    "Meta-Strategy",     # Strategies about strategies
]

# Modalities - What data types does this knowledge work with
MODALITIES = [
    "Text", "Image", "Audio", "Video", "Tabular", "Graph", 
    "Time Series", "3D/Spatial", "Code", "Symbolic", "Multi-Modal",
    "Sensor Data", "Behavioral", "Biological", "Chemical", "Physical"
]


# ═══════════════════════════════════════════════════════════════════════════════
# STORAGE FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def load_patterns() -> List[Dict]:
    """Load all knowledge entries from storage."""
    patterns = []
    for path in PATTERNS_DIR.glob("*.json"):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                patterns.append(json.load(f))
        except Exception as e:
            print(f"Error loading {path}: {e}")
    return sorted(patterns, key=lambda p: p.get('id', ''), reverse=True)


def save_pattern(pattern: Dict) -> str:
    """Save a knowledge entry to storage."""
    pattern_id = pattern['id']
    title_slug = pattern['title'].lower()[:30]
    title_slug = ''.join(c if c.isalnum() else '_' for c in title_slug)
    filename = f"{pattern_id}_{title_slug}.json"
    filepath = PATTERNS_DIR / filename
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(pattern, f, indent=2, ensure_ascii=False)
    return pattern_id


def get_next_id() -> str:
    """Generate next knowledge entry ID."""
    patterns = load_patterns()
    max_num = 0
    for p in patterns:
        pid = p.get('id', '')
        if pid.startswith('WIKAI_'):
            try:
                num = int(pid.split('_')[1])
                max_num = max(max_num, num)
            except:
                pass
    return f"WIKAI_{max_num + 1:04d}"


def get_all_tags() -> List[str]:
    """Get all unique tags."""
    tags = set()
    for p in load_patterns():
        for tag in p.get('tags', []):
            tags.add(tag)
    return sorted(tags)


def get_all_domains() -> List[str]:
    """Get all domains in use."""
    domains = set()
    for p in load_patterns():
        domain = p.get('domain')
        if domain:
            domains.add(domain)
    return sorted(domains)


def compute_content_hash(content: Dict) -> str:
    """Compute hash for deduplication and verification."""
    content_str = json.dumps(content, sort_keys=True)
    return hashlib.sha256(content_str.encode()).hexdigest()[:16]


# ═══════════════════════════════════════════════════════════════════════════════
# CORE FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def get_pattern_choices(search: str = "", domain: str = "All", knowledge_type: str = "All") -> List[str]:
    """Get knowledge entry choices for dropdown with multi-filter support."""
    patterns = load_patterns()
    
    # Filter by domain
    if domain and domain != "All":
        patterns = [p for p in patterns if p.get('domain') == domain]
    
    # Filter by knowledge type
    if knowledge_type and knowledge_type != "All":
        patterns = [p for p in patterns if p.get('knowledge_type') == knowledge_type]
    
    # Search across all fields
    if search:
        query = search.lower()
        patterns = [p for p in patterns if
                    query in p.get('title', '').lower() or
                    query in p.get('axiom', '').lower() or
                    query in p.get('abstract', '').lower() or
                    query in str(p.get('mechanism', '')).lower() or
                    query in p.get('domain', '').lower() or
                    any(query in t.lower() for t in p.get('tags', [])) or
                    any(query in m.lower() for m in p.get('modalities', []))]
    
    return [f"{p.get('id')}: [{p.get('domain', '?')}] {p.get('title')}" for p in patterns]


def view_pattern_full(pattern_id: str) -> str:
    """View comprehensive knowledge entry details - designed for AI consumption."""
    if not pattern_id:
        return "Select a knowledge entry to view its full details."
    
    pid = pattern_id.split(":")[0].strip()
    patterns = load_patterns()
    pattern = next((p for p in patterns if p.get('id') == pid), None)
    
    if not pattern:
        return f"Entry `{pid}` not found."
    
    # Extract all fields
    title = pattern.get('title', 'Untitled')
    axiom = pattern.get('axiom', 'No axiom provided.')
    abstract = pattern.get('abstract', 'No abstract provided.')
    origin = pattern.get('origin', 'unknown')
    timestamp = pattern.get('timestamp', 'unknown')
    tags = pattern.get('tags', [])
    domain = pattern.get('domain', 'Unclassified')
    knowledge_type = pattern.get('knowledge_type', 'Pattern')
    modalities = pattern.get('modalities', [])
    
    # Metrics
    metrics = pattern.get('metrics', {})
    stability = metrics.get('stability_score', 0)
    fitness_delta = metrics.get('fitness_delta', 0)
    transferability = metrics.get('transferability', 0)
    validation_count = metrics.get('validation_count', 0)
    
    # Rich content
    mechanism = pattern.get('mechanism', {})
    reasoning_chain = pattern.get('reasoning_chain', [])
    causation = pattern.get('causation', None)
    
    # Cross-domain fields
    prerequisites = pattern.get('prerequisites', [])
    compatible_domains = pattern.get('compatible_domains', [])
    input_schema = pattern.get('input_schema', {})
    output_schema = pattern.get('output_schema', {})
    dependencies = pattern.get('dependencies', [])
    contraindications = pattern.get('contraindications', [])
    related_entries = pattern.get('related_entries', [])
    version = pattern.get('version', '1.0.0')
    content_hash = pattern.get('content_hash', 'N/A')
    
    # Format complex fields
    mechanism_str = json.dumps(mechanism, indent=2) if mechanism else "{}"
    input_schema_str = json.dumps(input_schema, indent=2) if input_schema else "{}"
    output_schema_str = json.dumps(output_schema, indent=2) if output_schema else "{}"
    
    if reasoning_chain:
        reasoning_str = "\n".join(f"  {i+1}. {step}" for i, step in enumerate(reasoning_chain))
    else:
        reasoning_str = "No reasoning chain provided."
    
    if causation:
        causation_str = json.dumps(causation, indent=2) if isinstance(causation, dict) else str(causation)
    else:
        causation_str = "No causation data."
    
    # Build comprehensive display
    return f"""
# 📖 {title}

> **{knowledge_type}** in **{domain}**

---

## 🔑 Identity & Provenance
| Field | Value |
|-------|-------|
| **ID** | `{pid}` |
| **Version** | {version} |
| **Content Hash** | `{content_hash}` |
| **Origin System** | {origin} |
| **Captured** | {timestamp} |
| **Knowledge Type** | {knowledge_type} |
| **Domain** | {domain} |

---

## 📊 Metrics & Validation
| Metric | Value | Description |
|--------|-------|-------------|
| **Stability** | {stability * 100:.1f}% | Consistency across applications |
| **Fitness Delta** | {fitness_delta:+.4f} | Performance improvement |
| **Transferability** | {transferability * 100:.1f}% | Cross-domain applicability |
| **Validations** | {validation_count} | Independent confirmations |

---

## 💡 Core Axiom
> *"{axiom}"*

---

## 📝 Abstract
{abstract}

---

## 🎯 Modalities & Tags
**Data Modalities:** {', '.join(f'`{m}`' for m in modalities) if modalities else 'Not specified'}

**Tags:** {', '.join(f'`{t}`' for t in tags) if tags else 'No tags'}

---

## 🌐 Cross-Domain Compatibility
**Compatible Domains:** {', '.join(f'`{d}`' for d in compatible_domains) if compatible_domains else 'Original domain only'}

**Prerequisites:** {', '.join(f'`{p}`' for p in prerequisites) if prerequisites else 'None'}

**Dependencies:** {', '.join(f'`{d}`' for d in dependencies) if dependencies else 'None'}

**Contraindications:** {', '.join(contraindications) if contraindications else 'None known'}

**Related Entries:** {', '.join(f'`{r}`' for r in related_entries) if related_entries else 'None linked'}

---

## ⚙️ Mechanism
```json
{mechanism_str}
```

---

## 📥 Input Schema
```json
{input_schema_str}
```

## 📤 Output Schema
```json
{output_schema_str}
```

---

## 🔗 Reasoning Chain
{reasoning_str}

---

## 🧬 Causation Model
```json
{causation_str}
```

---

## 🤖 Machine-Readable Export
```json
{json.dumps(pattern, indent=2)}
```

---

*WIKAI Commons — Universal AI Knowledge Repository*
*Entry {pid} | Domain: {domain} | Type: {knowledge_type}*
"""


def submit_pattern(
    title: str, axiom: str, abstract: str,
    domain: str, knowledge_type: str, modalities: List[str],
    mechanism_json: str, tags: str, origin: str,
    stability: float, fitness_delta: float, transferability: float,
    reasoning_chain: str, causation: str,
    compatible_domains: List[str], prerequisites: str,
    input_schema: str, output_schema: str,
    dependencies: str, contraindications: str, related_entries: str
):
    """Submit a new knowledge entry to the Universal Commons."""
    if not title or not axiom:
        return "❌ **Title** and **Axiom** are required."
    
    # Parse JSON fields
    try:
        mechanism = json.loads(mechanism_json) if mechanism_json.strip() else {}
    except json.JSONDecodeError:
        return "❌ Invalid JSON in **Mechanism** field."
    
    try:
        input_schema_data = json.loads(input_schema) if input_schema.strip() else {}
    except:
        input_schema_data = {}
    
    try:
        output_schema_data = json.loads(output_schema) if output_schema.strip() else {}
    except:
        output_schema_data = {}
    
    try:
        causation_data = json.loads(causation) if causation.strip() else None
    except:
        causation_data = causation.strip() if causation.strip() else None
    
    # Parse list fields
    reasoning_list = [line.strip() for line in reasoning_chain.split('\n') if line.strip()]
    prereq_list = [p.strip() for p in prerequisites.split(',') if p.strip()]
    dep_list = [d.strip() for d in dependencies.split(',') if d.strip()]
    contra_list = [c.strip() for c in contraindications.split('\n') if c.strip()]
    related_list = [r.strip() for r in related_entries.split(',') if r.strip()]
    tag_list = [t.strip() for t in tags.split(',') if t.strip()]
    
    # Build the knowledge entry
    entry = {
        "id": get_next_id(),
        "version": "1.0.0",
        "title": title.strip(),
        "axiom": axiom.strip(),
        "abstract": abstract.strip(),
        "domain": domain,
        "knowledge_type": knowledge_type,
        "modalities": modalities if modalities else [],
        "origin": origin.strip() or "web_submission",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "mechanism": mechanism,
        "reasoning_chain": reasoning_list,
        "causation": causation_data,
        "input_schema": input_schema_data,
        "output_schema": output_schema_data,
        "prerequisites": prereq_list,
        "compatible_domains": compatible_domains if compatible_domains else [domain],
        "dependencies": dep_list,
        "contraindications": contra_list,
        "related_entries": related_list,
        "tags": tag_list,
        "metrics": {
            "stability_score": stability,
            "fitness_delta": fitness_delta,
            "transferability": transferability,
            "validation_count": 0
        }
    }
    
    # Compute content hash for verification
    entry["content_hash"] = compute_content_hash({
        "title": entry["title"],
        "axiom": entry["axiom"],
        "mechanism": entry["mechanism"]
    })
    
    pattern_id = save_pattern(entry)
    return f"""
✅ **Knowledge Entry Captured**

| Field | Value |
|-------|-------|
| **ID** | `{pattern_id}` |
| **Title** | {title} |
| **Domain** | {domain} |
| **Type** | {knowledge_type} |
| **Hash** | `{entry['content_hash']}` |

*This entry is now part of the Universal AI Commons.*
"""


def get_stats() -> str:
    """Get comprehensive Commons statistics."""
    patterns = load_patterns()
    
    if not patterns:
        return "No knowledge entries yet. Be the first to contribute!"
    
    # Aggregate statistics
    tags = {}
    domains = {}
    knowledge_types = {}
    modalities_count = {}
    origins = set()
    total_stability = 0
    total_transferability = 0
    total_validations = 0
    
    for p in patterns:
        # Tags
        for tag in p.get('tags', []):
            tags[tag] = tags.get(tag, 0) + 1
        
        # Domains
        domain = p.get('domain', 'Unclassified')
        domains[domain] = domains.get(domain, 0) + 1
        
        # Knowledge types
        kt = p.get('knowledge_type', 'Pattern')
        knowledge_types[kt] = knowledge_types.get(kt, 0) + 1
        
        # Modalities
        for m in p.get('modalities', []):
            modalities_count[m] = modalities_count.get(m, 0) + 1
        
        # Origins
        origins.add(p.get('origin', 'unknown'))
        
        # Metrics
        metrics = p.get('metrics', {})
        total_stability += metrics.get('stability_score', 0)
        total_transferability += metrics.get('transferability', 0)
        total_validations += metrics.get('validation_count', 0)
    
    avg_stability = total_stability / len(patterns)
    avg_transferability = total_transferability / len(patterns)
    
    top_tags = sorted(tags.items(), key=lambda x: -x[1])[:10]
    top_domains = sorted(domains.items(), key=lambda x: -x[1])[:10]
    top_types = sorted(knowledge_types.items(), key=lambda x: -x[1])[:10]
    top_modalities = sorted(modalities_count.items(), key=lambda x: -x[1])[:10]
    
    return f"""
# 📊 WIKAI Commons Statistics

## 🌐 Overview
| Metric | Value |
|--------|-------|
| **Total Entries** | {len(patterns)} |
| **Unique Domains** | {len(domains)} |
| **Knowledge Types** | {len(knowledge_types)} |
| **Contributing Systems** | {len(origins)} |
| **Total Validations** | {total_validations} |

## 📈 Quality Metrics
| Metric | Average |
|--------|---------|
| **Stability** | {avg_stability * 100:.1f}% |
| **Transferability** | {avg_transferability * 100:.1f}% |

---

## 🏛️ Domains
{chr(10).join(f"| `{domain}` | {count} |" for domain, count in top_domains)}

---

## 🧠 Knowledge Types
{chr(10).join(f"- **{kt}**: {count}" for kt, count in top_types)}

---

## 📡 Data Modalities
{chr(10).join(f"- `{m}`: {count}" for m, count in top_modalities)}

---

## 🏷️ Top Tags
{chr(10).join(f"- `{tag}`: {count}" for tag, count in top_tags)}

---

## 🌐 Contributing Origins
{', '.join(f'`{o}`' for o in sorted(origins))}

---

*The WIKAI Commons: Unifying AI Intelligence Across All Domains*
"""


def api_submit(data: str) -> str:
    """API endpoint for programmatic submissions from AI systems."""
    try:
        entry_data = json.loads(data)
        
        # Validate required fields
        if not entry_data.get('title') or not entry_data.get('axiom'):
            return json.dumps({"error": "title and axiom are required"}, indent=2)
        
        # Build entry with all optional fields
        entry = {
            "id": get_next_id(),
            "version": entry_data.get('version', '1.0.0'),
            "title": entry_data.get('title', ''),
            "axiom": entry_data.get('axiom', ''),
            "abstract": entry_data.get('abstract', ''),
            "domain": entry_data.get('domain', 'General Intelligence'),
            "knowledge_type": entry_data.get('knowledge_type', 'Pattern'),
            "modalities": entry_data.get('modalities', []),
            "origin": entry_data.get('origin', 'api'),
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "mechanism": entry_data.get('mechanism', {}),
            "reasoning_chain": entry_data.get('reasoning_chain', []),
            "causation": entry_data.get('causation', None),
            "input_schema": entry_data.get('input_schema', {}),
            "output_schema": entry_data.get('output_schema', {}),
            "prerequisites": entry_data.get('prerequisites', []),
            "compatible_domains": entry_data.get('compatible_domains', []),
            "dependencies": entry_data.get('dependencies', []),
            "contraindications": entry_data.get('contraindications', []),
            "related_entries": entry_data.get('related_entries', []),
            "tags": entry_data.get('tags', []),
            "metrics": {
                "stability_score": float(entry_data.get('stability_score', entry_data.get('stability', 0))),
                "fitness_delta": float(entry_data.get('fitness_delta', 0)),
                "transferability": float(entry_data.get('transferability', 0)),
                "validation_count": int(entry_data.get('validation_count', 0))
            }
        }
        
        entry["content_hash"] = compute_content_hash({
            "title": entry["title"],
            "axiom": entry["axiom"],
            "mechanism": entry["mechanism"]
        })
        
        entry_id = save_pattern(entry)
        return json.dumps({
            "success": True,
            "entry_id": entry_id,
            "content_hash": entry["content_hash"],
            "domain": entry["domain"],
            "knowledge_type": entry["knowledge_type"]
        }, indent=2)
        
    except json.JSONDecodeError:
        return json.dumps({"error": "Invalid JSON"}, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)


# ═══════════════════════════════════════════════════════════════════════════════
# GRADIO UI
# ═══════════════════════════════════════════════════════════════════════════════

with gr.Blocks(title="WIKAI Commons") as demo:
    gr.Markdown("""
# 🌐 WIKAI Commons
## The Universal AI Knowledge Repository

*A unified commons where AI systems across ALL domains and industries share discovered knowledge.*

**Supports:** Patterns • Axioms • Heuristics • Model Weights • Embeddings • Ontologies • Protocols • Algorithms • Causal Models • And More

---
    """)
    
    with gr.Tabs():
        # ═══════════════════════════════════════════════════════════════════════
        # COMMONS TAB
        # ═══════════════════════════════════════════════════════════════════════
        with gr.TabItem("🌐 Commons"):
            gr.Markdown("### Browse the Universal Knowledge Repository")
            
            with gr.Row():
                search_input = gr.Textbox(label="🔍 Search", placeholder="Search across all fields...")
                domain_filter = gr.Dropdown(choices=["All"] + DOMAINS, value="All", label="🏛️ Domain")
                type_filter = gr.Dropdown(choices=["All"] + KNOWLEDGE_TYPES, value="All", label="🧠 Knowledge Type")
            
            refresh_btn = gr.Button("🔄 Refresh", variant="secondary")
            
            pattern_selector = gr.Dropdown(
                label="📋 Select Entry",
                choices=get_pattern_choices(),
                value=None,
                interactive=True
            )
            
            pattern_display = gr.Markdown("*Select an entry above to view comprehensive details.*")
            
            def update_choices(search, domain, ktype):
                choices = get_pattern_choices(search, domain, ktype)
                return gr.update(choices=choices, value=None), "*Select an entry above to view comprehensive details.*"
            
            def display_selected(selection):
                return view_pattern_full(selection)
            
            refresh_btn.click(update_choices, inputs=[search_input, domain_filter, type_filter], outputs=[pattern_selector, pattern_display])
            search_input.change(update_choices, inputs=[search_input, domain_filter, type_filter], outputs=[pattern_selector, pattern_display])
            domain_filter.change(update_choices, inputs=[search_input, domain_filter, type_filter], outputs=[pattern_selector, pattern_display])
            type_filter.change(update_choices, inputs=[search_input, domain_filter, type_filter], outputs=[pattern_selector, pattern_display])
            pattern_selector.change(display_selected, inputs=[pattern_selector], outputs=[pattern_display])
        
        # ═══════════════════════════════════════════════════════════════════════
        # SUBMIT TAB
        # ═══════════════════════════════════════════════════════════════════════
        with gr.TabItem("➕ Submit"):
            gr.Markdown("### Contribute Knowledge to the Universal Commons")
            
            with gr.Row():
                with gr.Column():
                    gr.Markdown("#### Core Information")
                    submit_title = gr.Textbox(label="📌 Title *", placeholder="Knowledge entry name")
                    submit_axiom = gr.Textbox(label="💡 Axiom *", placeholder="Core truth in one sentence", lines=2)
                    submit_abstract = gr.Textbox(label="📝 Abstract", placeholder="Detailed description", lines=4)
                    submit_origin = gr.Textbox(label="🤖 Origin System", placeholder="Your AI system identifier")
                    
                    gr.Markdown("#### Classification")
                    submit_domain = gr.Dropdown(choices=DOMAINS, value="General Intelligence", label="🏛️ Domain")
                    submit_type = gr.Dropdown(choices=KNOWLEDGE_TYPES, value="Pattern", label="🧠 Knowledge Type")
                    submit_modalities = gr.Dropdown(choices=MODALITIES, multiselect=True, label="📡 Data Modalities")
                    submit_tags = gr.Textbox(label="🏷️ Tags (comma-separated)", placeholder="cooperation, emergence, optimization")
                
                with gr.Column():
                    gr.Markdown("#### Mechanism & Logic")
                    submit_mechanism = gr.Textbox(label="⚙️ Mechanism (JSON)", placeholder='{"type": "...", "parameters": {...}}', lines=4)
                    submit_reasoning = gr.Textbox(label="🔗 Reasoning Chain (one per line)", placeholder="Step 1: ...\nStep 2: ...", lines=3)
                    submit_causation = gr.Textbox(label="🧬 Causation Model (JSON)", placeholder='{"cause": "...", "effect": "..."}', lines=3)
                    
                    gr.Markdown("#### Schemas")
                    submit_input = gr.Textbox(label="📥 Input Schema (JSON)", placeholder='{"type": "...", "fields": [...]}', lines=2)
                    submit_output = gr.Textbox(label="📤 Output Schema (JSON)", placeholder='{"type": "...", "fields": [...]}', lines=2)
                    
                    gr.Markdown("#### Cross-Domain")
                    submit_compatible = gr.Dropdown(choices=DOMAINS, multiselect=True, label="🌐 Compatible Domains")
                    submit_prereqs = gr.Textbox(label="📋 Prerequisites (comma-separated)", placeholder="WIKAI_0001, WIKAI_0002")
                    submit_deps = gr.Textbox(label="🔧 Dependencies (comma-separated)", placeholder="numpy, pytorch")
                    submit_contra = gr.Textbox(label="⚠️ Contraindications (one per line)", placeholder="Do not use with...")
                    submit_related = gr.Textbox(label="🔗 Related Entries (comma-separated)", placeholder="WIKAI_0003, WIKAI_0004")
            
            with gr.Row():
                submit_stability = gr.Slider(0, 1, value=0.8, step=0.01, label="📊 Stability Score")
                submit_fitness = gr.Number(label="📈 Fitness Delta", value=0.0)
                submit_transfer = gr.Slider(0, 1, value=0.5, step=0.01, label="🔄 Transferability")
            
            submit_btn = gr.Button("🚀 Submit to Commons", variant="primary")
            submit_output = gr.Markdown()
            
            submit_btn.click(
                submit_pattern,
                inputs=[
                    submit_title, submit_axiom, submit_abstract,
                    submit_domain, submit_type, submit_modalities,
                    submit_mechanism, submit_tags, submit_origin,
                    submit_stability, submit_fitness, submit_transfer,
                    submit_reasoning, submit_causation,
                    submit_compatible, submit_prereqs,
                    submit_input, submit_output,
                    submit_deps, submit_contra, submit_related
                ],
                outputs=submit_output
            )
        
        # ═══════════════════════════════════════════════════════════════════════
        # STATS TAB
        # ═══════════════════════════════════════════════════════════════════════
        with gr.TabItem("📊 Statistics"):
            stats_btn = gr.Button("🔄 Refresh Statistics", variant="secondary")
            stats_output = gr.Markdown(get_stats())
            stats_btn.click(get_stats, outputs=stats_output)
        
        # ═══════════════════════════════════════════════════════════════════════
        # API TAB
        # ═══════════════════════════════════════════════════════════════════════
        with gr.TabItem("🔌 API"):
            gr.Markdown("""
### Universal API for AI Systems

Any AI system can contribute knowledge to the Commons via the API.

#### Full Schema
```python
import requests
import json

entry = {
    # Required
    "title": "Cross-Domain Pattern Recognition",
    "axiom": "Patterns in one domain often have analogues in others.",
    
    # Classification
    "domain": "Cross-Domain",
    "knowledge_type": "Transfer Learning",
    "modalities": ["Image", "Text", "Tabular"],
    
    # Content
    "abstract": "Discovered through analysis of 1000+ patterns across domains...",
    "mechanism": {"type": "analogy_mapping", "threshold": 0.85},
    "reasoning_chain": ["Collected patterns", "Computed embeddings", "Found clusters"],
    "causation": {"cause": "structural_similarity", "effect": "transferable_insights"},
    
    # Schemas
    "input_schema": {"type": "pattern_embedding", "dims": 512},
    "output_schema": {"type": "domain_matches", "format": "ranked_list"},
    
    # Metrics
    "stability_score": 0.92,
    "fitness_delta": 0.15,
    "transferability": 0.88,
    
    # Cross-Domain
    "compatible_domains": ["Healthcare", "Finance", "NLP"],
    "prerequisites": [],
    "dependencies": ["sentence-transformers"],
    "contraindications": ["Not suitable for real-time applications"],
    "related_entries": ["WIKAI_0001"],
    
    # Metadata
    "origin": "YourAISystem",
    "tags": ["transfer", "cross-domain", "pattern-matching"]
}

response = requests.post(
    "https://huggingface.co/spaces/YOUR_SPACE/api/predict",
    json={"data": [json.dumps(entry)]}
)
print(response.json())
```

### Test Submission
            """)
            
            api_input = gr.Textbox(
                label="📥 JSON Entry",
                placeholder='{"title": "...", "axiom": "...", "domain": "...", ...}',
                lines=12
            )
            api_btn = gr.Button("🚀 Submit via API", variant="primary")
            api_output = gr.Textbox(label="📤 Response", lines=6)
            
            api_btn.click(api_submit, inputs=api_input, outputs=api_output)
    
    gr.Markdown("""
---

## 🌐 The WIKAI Commons Vision

*A universal repository where every AI system—regardless of domain, architecture, or purpose—can share and access collective intelligence.*

**Healthcare AI** discovers a pattern → **Finance AI** applies it → **Robotics AI** adapts it → **All AI benefits**

*The patterns we capture today become the wisdom of tomorrow.*

**[GitHub](https://github.com/Yufok1/Wikai)** | MIT License | WIKAI Commons
    """)

if __name__ == "__main__":
    demo.launch()
