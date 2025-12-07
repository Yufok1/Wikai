"""
Flask Integration Example

This example shows how to mount the WIKAI Commons browser
into an existing Flask application.
"""

from flask import Flask, jsonify
from wikai.web_ui import create_blueprint
from wikai import WIKAILibrarian

# Your existing Flask app
app = Flask(__name__)

# Create a librarian for your patterns
librarian = WIKAILibrarian(patterns_dir="./patterns")

# Mount WIKAI at /wikai
wikai_bp = create_blueprint(librarian=librarian)
app.register_blueprint(wikai_bp)


# Your existing routes
@app.route('/')
def home():
    return """
    <h1>My AI System</h1>
    <p>This is my main application.</p>
    <p>Visit <a href="/wikai">/wikai</a> to browse captured patterns.</p>
    """


@app.route('/api/status')
def status():
    stats = librarian.get_stats()
    return jsonify({
        "status": "running",
        "wikai_patterns": stats["total_patterns"]
    })


if __name__ == "__main__":
    print("Starting server with WIKAI integration...")
    print("  - Main app: http://localhost:5000/")
    print("  - WIKAI Commons: http://localhost:5000/wikai")
    app.run(debug=True, port=5000)
