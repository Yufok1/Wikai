"""
🌐 WIKAI Web UI - Commons Browser

A Flask-based web interface for browsing the WIKAI Commons.
This is a standalone web server that can be run to explore
captured patterns and monitor live pattern capture.

Usage:
    from wikai.web_ui import create_app, run_server
    
    app = create_app(patterns_dir="./patterns")
    run_server(app, port=5050)
    
Or from command line:
    python -m wikai.web_ui --port 5050
"""

import os
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional, List

from flask import Flask, Blueprint, render_template_string, jsonify, request

from .librarian import WIKAILibrarian

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════════════════════
# BLUEPRINT CREATION
# ═══════════════════════════════════════════════════════════════════════════════

def create_blueprint(librarian: Optional[WIKAILibrarian] = None) -> Blueprint:
    """
    Create a Flask Blueprint for WIKAI Commons browser.
    
    This can be mounted into an existing Flask app at any prefix.
    
    Args:
        librarian: WIKAILibrarian instance (creates default if not provided)
        
    Returns:
        Flask Blueprint
    """
    bp = Blueprint('wikai', __name__, url_prefix='/wikai')
    
    # Use provided librarian or create default
    _librarian = librarian or WIKAILibrarian()
    
    # Debug message buffer for live feed
    _debug_messages: List[Dict[str, Any]] = []
    _max_debug_messages = 100
    
    def add_debug_message(message: str, level: str = "info"):
        """Add a message to the debug buffer."""
        _debug_messages.append({
            "timestamp": datetime.now().isoformat(),
            "message": message,
            "level": level
        })
        # Keep buffer limited
        while len(_debug_messages) > _max_debug_messages:
            _debug_messages.pop(0)
    
    @bp.route('/')
    def index():
        """Main Commons browser page."""
        return render_template_string(MAIN_TEMPLATE, 
                                      title="WIKAI Commons")
    
    @bp.route('/api/patterns')
    def api_patterns():
        """Get all patterns."""
        patterns = _librarian.list_all()
        return jsonify([p.to_dict() for p in patterns])
    
    @bp.route('/api/patterns/<pattern_id>')
    def api_pattern(pattern_id: str):
        """Get a single pattern by ID."""
        pattern = _librarian.get(pattern_id)
        if pattern:
            return jsonify(pattern.to_dict())
        return jsonify({"error": "Pattern not found"}), 404
    
    @bp.route('/api/search')
    def api_search():
        """Search patterns."""
        query = request.args.get('q', '')
        tags = request.args.get('tags', '').split(',') if request.args.get('tags') else None
        min_stability = float(request.args.get('min_stability', 0))
        
        patterns = _librarian.search(
            query=query if query else None,
            tags=tags,
            min_stability=min_stability
        )
        return jsonify([p.to_dict() for p in patterns])
    
    @bp.route('/api/tags')
    def api_tags():
        """Get all tags with counts."""
        return jsonify(_librarian.get_tags())
    
    @bp.route('/api/stats')
    def api_stats():
        """Get Commons statistics."""
        return jsonify(_librarian.get_stats())
    
    @bp.route('/api/debug')
    def api_debug():
        """Get debug messages for live feed."""
        since = request.args.get('since')
        if since:
            # Filter messages after timestamp
            messages = [m for m in _debug_messages if m["timestamp"] > since]
        else:
            messages = _debug_messages[-20:]  # Last 20 by default
        return jsonify(messages)
    
    @bp.route('/api/debug', methods=['POST'])
    def api_debug_post():
        """Add a debug message."""
        data = request.get_json() or {}
        add_debug_message(
            data.get('message', 'No message'),
            data.get('level', 'info')
        )
        return jsonify({"status": "ok"})
    
    return bp


# ═══════════════════════════════════════════════════════════════════════════════
# STANDALONE APP CREATION
# ═══════════════════════════════════════════════════════════════════════════════

def create_app(patterns_dir: Optional[str] = None) -> Flask:
    """
    Create a standalone Flask app for the Commons browser.
    
    Args:
        patterns_dir: Directory containing patterns
        
    Returns:
        Flask app
    """
    app = Flask(__name__)
    
    librarian = WIKAILibrarian(patterns_dir=patterns_dir) if patterns_dir else None
    bp = create_blueprint(librarian)
    
    app.register_blueprint(bp)
    
    # Redirect root to /wikai
    @app.route('/')
    def root():
        return app.redirect('/wikai')
    
    return app


def run_server(app: Optional[Flask] = None, 
               host: str = "127.0.0.1", 
               port: int = 5050,
               debug: bool = False):
    """
    Run the WIKAI web server.
    
    Args:
        app: Flask app (creates default if not provided)
        host: Host to bind to
        port: Port to listen on
        debug: Enable Flask debug mode
    """
    if app is None:
        app = create_app()
    
    print(f"🌐 WIKAI Commons Browser starting at http://{host}:{port}/wikai")
    app.run(host=host, port=port, debug=debug)


# ═══════════════════════════════════════════════════════════════════════════════
# HTML TEMPLATE
# ═══════════════════════════════════════════════════════════════════════════════

MAIN_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ title }}</title>
    <style>
        :root {
            --bg-primary: #0a0e17;
            --bg-secondary: #111827;
            --bg-tertiary: #1f2937;
            --text-primary: #f3f4f6;
            --text-secondary: #9ca3af;
            --accent: #3b82f6;
            --accent-hover: #60a5fa;
            --success: #10b981;
            --warning: #f59e0b;
            --error: #ef4444;
            --border: #374151;
        }
        
        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }
        
        body {
            font-family: 'Segoe UI', system-ui, sans-serif;
            background: var(--bg-primary);
            color: var(--text-primary);
            min-height: 100vh;
            display: flex;
            flex-direction: column;
        }
        
        /* Header */
        header {
            background: var(--bg-secondary);
            border-bottom: 1px solid var(--border);
            padding: 1rem 2rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .logo {
            font-size: 1.5rem;
            font-weight: 700;
            color: var(--accent);
        }
        
        .logo span {
            color: var(--text-primary);
        }
        
        /* Search */
        .search-container {
            display: flex;
            gap: 1rem;
            align-items: center;
        }
        
        .search-input {
            background: var(--bg-tertiary);
            border: 1px solid var(--border);
            border-radius: 6px;
            padding: 0.5rem 1rem;
            color: var(--text-primary);
            width: 300px;
        }
        
        .search-input:focus {
            outline: none;
            border-color: var(--accent);
        }
        
        /* Main content */
        main {
            flex: 1;
            display: flex;
            flex-direction: column;
            overflow: hidden;
        }
        
        /* Top section (patterns grid) */
        .top-section {
            flex: 1;
            display: grid;
            grid-template-columns: 200px 1fr 350px;
            gap: 1rem;
            padding: 1rem 2rem;
            overflow: hidden;
            min-height: 200px;
        }
        
        /* Horizontal resize handle */
        .h-resize-handle {
            width: 100%;
            height: 8px;
            background: var(--bg-tertiary);
            cursor: ns-resize;
            display: flex;
            justify-content: center;
            align-items: center;
            border-top: 1px solid var(--border);
            border-bottom: 1px solid var(--border);
        }
        
        .h-resize-handle:hover {
            background: var(--accent);
        }
        
        .h-resize-handle::before {
            content: '';
            width: 40px;
            height: 3px;
            background: var(--border);
            border-radius: 2px;
        }
        
        .h-resize-handle:hover::before {
            background: var(--text-primary);
        }
        
        /* Bottom section (live feed) */
        .bottom-section {
            height: 200px;
            min-height: 100px;
            max-height: 50vh;
            padding: 1rem 2rem;
            overflow: hidden;
        }
        
        /* Sidebar */
        .sidebar {
            background: var(--bg-secondary);
            border-radius: 8px;
            padding: 1rem;
            overflow-y: auto;
        }
        
        .sidebar h3 {
            font-size: 0.875rem;
            color: var(--text-secondary);
            margin-bottom: 0.75rem;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }
        
        .tag-list {
            display: flex;
            flex-direction: column;
            gap: 0.25rem;
        }
        
        .tag-item {
            display: flex;
            justify-content: space-between;
            padding: 0.5rem 0.75rem;
            border-radius: 4px;
            cursor: pointer;
            font-size: 0.875rem;
        }
        
        .tag-item:hover {
            background: var(--bg-tertiary);
        }
        
        .tag-item.active {
            background: var(--accent);
        }
        
        .tag-count {
            color: var(--text-secondary);
            font-size: 0.75rem;
        }
        
        /* Patterns grid */
        .patterns-container {
            overflow-y: auto;
        }
        
        .patterns-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
            gap: 1rem;
        }
        
        .pattern-card {
            background: var(--bg-secondary);
            border-radius: 8px;
            padding: 1.25rem;
            cursor: pointer;
            transition: transform 0.2s, box-shadow 0.2s;
            border: 1px solid var(--border);
        }
        
        .pattern-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
            border-color: var(--accent);
        }
        
        .pattern-title {
            font-size: 1rem;
            font-weight: 600;
            margin-bottom: 0.5rem;
            color: var(--text-primary);
        }
        
        .pattern-axiom {
            font-size: 0.875rem;
            color: var(--text-secondary);
            font-style: italic;
            margin-bottom: 0.75rem;
        }
        
        .pattern-meta {
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-size: 0.75rem;
        }
        
        .pattern-id {
            color: var(--accent);
            font-family: monospace;
        }
        
        .pattern-stability {
            display: flex;
            align-items: center;
            gap: 0.25rem;
        }
        
        .stability-bar {
            width: 60px;
            height: 4px;
            background: var(--bg-tertiary);
            border-radius: 2px;
            overflow: hidden;
        }
        
        .stability-fill {
            height: 100%;
            background: var(--success);
            transition: width 0.3s;
        }
        
        /* Detail panel */
        .detail-panel {
            background: var(--bg-secondary);
            border-radius: 8px;
            padding: 1.5rem;
            overflow-y: auto;
        }
        
        .detail-empty {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            height: 100%;
            color: var(--text-secondary);
        }
        
        .detail-title {
            font-size: 1.25rem;
            font-weight: 600;
            margin-bottom: 0.5rem;
        }
        
        .detail-axiom {
            font-size: 1rem;
            font-style: italic;
            color: var(--accent);
            margin-bottom: 1rem;
            padding: 0.75rem;
            background: var(--bg-tertiary);
            border-radius: 4px;
            border-left: 3px solid var(--accent);
        }
        
        .detail-section {
            margin-top: 1.5rem;
        }
        
        .detail-section h4 {
            font-size: 0.75rem;
            color: var(--text-secondary);
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin-bottom: 0.5rem;
        }
        
        .detail-tags {
            display: flex;
            flex-wrap: wrap;
            gap: 0.5rem;
        }
        
        .detail-tag {
            background: var(--bg-tertiary);
            padding: 0.25rem 0.5rem;
            border-radius: 4px;
            font-size: 0.75rem;
        }
        
        .detail-mechanism {
            background: var(--bg-tertiary);
            padding: 1rem;
            border-radius: 4px;
            font-family: monospace;
            font-size: 0.75rem;
            overflow-x: auto;
        }
        
        /* Live feed */
        .live-feed {
            background: var(--bg-secondary);
            border-radius: 8px;
            height: 100%;
            display: flex;
            flex-direction: column;
            overflow: hidden;
        }
        
        .live-feed-header {
            padding: 0.75rem 1rem;
            border-bottom: 1px solid var(--border);
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-shrink: 0;
        }
        
        .live-feed-title {
            font-size: 0.875rem;
            font-weight: 600;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }
        
        .live-indicator {
            width: 8px;
            height: 8px;
            background: var(--success);
            border-radius: 50%;
            animation: pulse 2s infinite;
        }
        
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }
        
        .live-feed-content {
            flex: 1;
            overflow-y: auto;
            padding: 0.5rem;
            font-family: monospace;
            font-size: 0.75rem;
        }
        
        .debug-line {
            padding: 0.25rem 0.5rem;
            border-radius: 2px;
            white-space: pre-wrap;
            word-break: break-all;
        }
        
        .debug-line:hover {
            background: var(--bg-tertiary);
        }
        
        .debug-line.info { color: var(--text-secondary); }
        .debug-line.success { color: var(--success); }
        .debug-line.warning { color: var(--warning); }
        .debug-line.error { color: var(--error); }
        
        /* Stats */
        .stats-bar {
            padding: 0.5rem 2rem;
            background: var(--bg-secondary);
            border-top: 1px solid var(--border);
            display: flex;
            gap: 2rem;
            font-size: 0.75rem;
            color: var(--text-secondary);
        }
        
        .stat-item strong {
            color: var(--text-primary);
        }
        
        /* Empty state */
        .empty-state {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            padding: 3rem;
            color: var(--text-secondary);
        }
        
        .empty-state-icon {
            font-size: 3rem;
            margin-bottom: 1rem;
        }
    </style>
</head>
<body>
    <header>
        <div class="logo">📚 <span>WIKAI</span> Commons</div>
        <div class="search-container">
            <input type="text" class="search-input" id="searchInput" placeholder="Search patterns...">
        </div>
    </header>
    
    <main>
        <div class="top-section" id="topSection">
            <!-- Tags sidebar -->
            <div class="sidebar">
                <h3>Tags</h3>
                <div class="tag-list" id="tagList">
                    <div class="tag-item active" data-tag="">
                        <span>All Patterns</span>
                        <span class="tag-count" id="totalCount">0</span>
                    </div>
                </div>
            </div>
            
            <!-- Patterns grid -->
            <div class="patterns-container">
                <div class="patterns-grid" id="patternsGrid">
                    <div class="empty-state">
                        <div class="empty-state-icon">📚</div>
                        <p>No patterns captured yet</p>
                        <p style="font-size: 0.875rem; margin-top: 0.5rem;">
                            Patterns will appear here as they are discovered
                        </p>
                    </div>
                </div>
            </div>
            
            <!-- Detail panel -->
            <div class="detail-panel" id="detailPanel">
                <div class="detail-empty">
                    <div style="font-size: 2rem; margin-bottom: 0.5rem;">👈</div>
                    <p>Select a pattern to view details</p>
                </div>
            </div>
        </div>
        
        <!-- Horizontal resize handle -->
        <div class="h-resize-handle" id="hResizeHandle"></div>
        
        <!-- Live feed -->
        <div class="bottom-section" id="bottomSection">
            <div class="live-feed">
                <div class="live-feed-header">
                    <div class="live-feed-title">
                        <div class="live-indicator"></div>
                        Live Feed
                    </div>
                </div>
                <div class="live-feed-content" id="liveFeed">
                    <div class="debug-line info">[WIKAI] Ready to capture patterns...</div>
                </div>
            </div>
        </div>
    </main>
    
    <div class="stats-bar">
        <div class="stat-item">Patterns: <strong id="statPatterns">0</strong></div>
        <div class="stat-item">Tags: <strong id="statTags">0</strong></div>
        <div class="stat-item">Avg Stability: <strong id="statStability">0%</strong></div>
    </div>
    
    <script>
        // State
        let patterns = [];
        let tags = {};
        let selectedTag = '';
        let selectedPattern = null;
        let lastDebugTimestamp = '';
        
        // DOM elements
        const searchInput = document.getElementById('searchInput');
        const tagList = document.getElementById('tagList');
        const patternsGrid = document.getElementById('patternsGrid');
        const detailPanel = document.getElementById('detailPanel');
        const liveFeed = document.getElementById('liveFeed');
        const topSection = document.getElementById('topSection');
        const bottomSection = document.getElementById('bottomSection');
        const hResizeHandle = document.getElementById('hResizeHandle');
        
        // Horizontal resize
        let isHResizing = false;
        let startY = 0;
        let startTopHeight = 0;
        let startBottomHeight = 0;
        
        hResizeHandle.addEventListener('mousedown', (e) => {
            isHResizing = true;
            startY = e.clientY;
            startTopHeight = topSection.offsetHeight;
            startBottomHeight = bottomSection.offsetHeight;
            document.body.style.cursor = 'ns-resize';
            document.body.style.userSelect = 'none';
        });
        
        document.addEventListener('mousemove', (e) => {
            if (!isHResizing) return;
            
            const deltaY = e.clientY - startY;
            const newTopHeight = Math.max(200, startTopHeight + deltaY);
            const newBottomHeight = Math.max(100, startBottomHeight - deltaY);
            
            // Use flex-basis for proper flexbox behavior
            topSection.style.flex = `0 0 ${newTopHeight}px`;
            bottomSection.style.height = `${newBottomHeight}px`;
        });
        
        document.addEventListener('mouseup', () => {
            if (isHResizing) {
                isHResizing = false;
                document.body.style.cursor = '';
                document.body.style.userSelect = '';
            }
        });
        
        // API calls
        async function fetchPatterns() {
            try {
                const response = await fetch('/wikai/api/patterns');
                patterns = await response.json();
                renderPatterns();
            } catch (error) {
                console.error('Failed to fetch patterns:', error);
            }
        }
        
        async function fetchTags() {
            try {
                const response = await fetch('/wikai/api/tags');
                tags = await response.json();
                renderTags();
            } catch (error) {
                console.error('Failed to fetch tags:', error);
            }
        }
        
        async function fetchStats() {
            try {
                const response = await fetch('/wikai/api/stats');
                const stats = await response.json();
                document.getElementById('statPatterns').textContent = stats.total_patterns;
                document.getElementById('statTags').textContent = stats.total_tags;
                document.getElementById('statStability').textContent = 
                    (stats.avg_stability * 100).toFixed(0) + '%';
            } catch (error) {
                console.error('Failed to fetch stats:', error);
            }
        }
        
        async function fetchDebug() {
            try {
                const url = lastDebugTimestamp 
                    ? `/wikai/api/debug?since=${encodeURIComponent(lastDebugTimestamp)}`
                    : '/wikai/api/debug';
                const response = await fetch(url);
                const messages = await response.json();
                
                if (messages.length > 0) {
                    messages.forEach(msg => {
                        addDebugLine(msg.message, msg.level);
                    });
                    lastDebugTimestamp = messages[messages.length - 1].timestamp;
                }
            } catch (error) {
                console.error('Failed to fetch debug:', error);
            }
        }
        
        function addDebugLine(message, level = 'info') {
            const line = document.createElement('div');
            line.className = `debug-line ${level}`;
            line.textContent = message;
            liveFeed.appendChild(line);
            liveFeed.scrollTop = liveFeed.scrollHeight;
            
            // Limit lines
            while (liveFeed.children.length > 100) {
                liveFeed.removeChild(liveFeed.firstChild);
            }
        }
        
        // Rendering
        function renderTags() {
            const allItem = tagList.querySelector('[data-tag=""]');
            const totalCount = document.getElementById('totalCount');
            totalCount.textContent = patterns.length;
            
            // Remove existing tags (except "All")
            Array.from(tagList.children).forEach(child => {
                if (child.dataset.tag !== '') {
                    child.remove();
                }
            });
            
            // Add tags
            Object.entries(tags).forEach(([tag, count]) => {
                const item = document.createElement('div');
                item.className = 'tag-item' + (tag === selectedTag ? ' active' : '');
                item.dataset.tag = tag;
                item.innerHTML = `<span>${tag}</span><span class="tag-count">${count}</span>`;
                item.onclick = () => selectTag(tag);
                tagList.appendChild(item);
            });
        }
        
        function selectTag(tag) {
            selectedTag = tag;
            // Update active state
            tagList.querySelectorAll('.tag-item').forEach(item => {
                item.classList.toggle('active', item.dataset.tag === tag);
            });
            renderPatterns();
        }
        
        function renderPatterns() {
            const query = searchInput.value.toLowerCase();
            
            let filtered = patterns;
            
            // Filter by tag
            if (selectedTag) {
                filtered = filtered.filter(p => p.tags && p.tags.includes(selectedTag));
            }
            
            // Filter by search
            if (query) {
                filtered = filtered.filter(p => 
                    p.title.toLowerCase().includes(query) ||
                    p.axiom.toLowerCase().includes(query) ||
                    (p.abstract && p.abstract.toLowerCase().includes(query))
                );
            }
            
            if (filtered.length === 0) {
                patternsGrid.innerHTML = `
                    <div class="empty-state">
                        <div class="empty-state-icon">🔍</div>
                        <p>No patterns found</p>
                    </div>
                `;
                return;
            }
            
            patternsGrid.innerHTML = filtered.map(p => `
                <div class="pattern-card" onclick="selectPattern('${p.id}')">
                    <div class="pattern-title">${escapeHtml(p.title)}</div>
                    <div class="pattern-axiom">"${escapeHtml(p.axiom)}"</div>
                    <div class="pattern-meta">
                        <span class="pattern-id">${p.id}</span>
                        <div class="pattern-stability">
                            <div class="stability-bar">
                                <div class="stability-fill" style="width: ${(p.metrics?.stability_score || 0) * 100}%"></div>
                            </div>
                            <span>${((p.metrics?.stability_score || 0) * 100).toFixed(0)}%</span>
                        </div>
                    </div>
                </div>
            `).join('');
        }
        
        function selectPattern(id) {
            selectedPattern = patterns.find(p => p.id === id);
            if (!selectedPattern) return;
            
            const p = selectedPattern;
            detailPanel.innerHTML = `
                <div class="detail-title">${escapeHtml(p.title)}</div>
                <div class="detail-axiom">"${escapeHtml(p.axiom)}"</div>
                
                ${p.abstract ? `
                <div class="detail-section">
                    <h4>Abstract</h4>
                    <p>${escapeHtml(p.abstract)}</p>
                </div>
                ` : ''}
                
                ${p.tags && p.tags.length ? `
                <div class="detail-section">
                    <h4>Tags</h4>
                    <div class="detail-tags">
                        ${p.tags.map(t => `<span class="detail-tag">${escapeHtml(t)}</span>`).join('')}
                    </div>
                </div>
                ` : ''}
                
                ${p.mechanism && Object.keys(p.mechanism).length ? `
                <div class="detail-section">
                    <h4>Mechanism</h4>
                    <pre class="detail-mechanism">${escapeHtml(JSON.stringify(p.mechanism, null, 2))}</pre>
                </div>
                ` : ''}
                
                <div class="detail-section">
                    <h4>Metrics</h4>
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 0.5rem; font-size: 0.875rem;">
                        <div>Stability: <strong>${((p.metrics?.stability_score || 0) * 100).toFixed(1)}%</strong></div>
                        <div>Fitness Δ: <strong>${(p.metrics?.fitness_delta || 0).toFixed(4)}</strong></div>
                    </div>
                </div>
                
                <div class="detail-section">
                    <h4>Origin</h4>
                    <p>${escapeHtml(p.origin || 'unknown')}</p>
                </div>
            `;
        }
        
        function escapeHtml(str) {
            if (!str) return '';
            const div = document.createElement('div');
            div.textContent = str;
            return div.innerHTML;
        }
        
        // Initialize
        searchInput.addEventListener('input', renderPatterns);
        
        // Initial load
        fetchPatterns();
        fetchTags();
        fetchStats();
        
        // Polling
        setInterval(() => {
            fetchPatterns();
            fetchTags();
            fetchStats();
        }, 5000);
        
        setInterval(fetchDebug, 1000);
    </script>
</body>
</html>
'''


# ═══════════════════════════════════════════════════════════════════════════════
# COMMAND LINE INTERFACE
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='WIKAI Commons Browser')
    parser.add_argument('--host', default='127.0.0.1', help='Host to bind to')
    parser.add_argument('--port', type=int, default=5050, help='Port to listen on')
    parser.add_argument('--patterns', default=None, help='Patterns directory')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    
    args = parser.parse_args()
    
    app = create_app(patterns_dir=args.patterns)
    run_server(app, host=args.host, port=args.port, debug=args.debug)
