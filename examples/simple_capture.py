"""
Simple Pattern Capture Example

This example shows the simplest way to capture a pattern to WIKAI.
"""

from wikai import capture_pattern

# When your AI system discovers something stable, capture it
pattern_id = capture_pattern(
    title="Cooperative Equilibrium",
    axiom="Mutual benefit exceeds individual gain when interactions repeat",
    mechanism={
        "strategy": "tit-for-tat",
        "trigger": "repeated interaction",
        "stability_condition": "probability of future interaction > cost/benefit ratio"
    },
    stability_score=0.92,
    tags=["cooperation", "game_theory", "equilibrium"],
    origin="example_script",
    abstract="In repeated games, cooperative strategies outperform purely selfish ones when agents expect to interact again. The shadow of the future enables trust."
)

print(f"✅ Captured pattern: {pattern_id}")


# You can also use the librarian directly for more control
from wikai import WIKAILibrarian

librarian = WIKAILibrarian(patterns_dir="./patterns")

# Search for patterns
cooperative = librarian.search(tags=["cooperation"])
print(f"\n📚 Found {len(cooperative)} cooperative patterns")

# Get all tags
tags = librarian.get_tags()
print(f"\n🏷️ Tags in Commons: {list(tags.keys())}")

# Get stats
stats = librarian.get_stats()
print(f"\n📊 Commons Stats: {stats}")
