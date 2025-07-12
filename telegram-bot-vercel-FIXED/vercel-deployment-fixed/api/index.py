import os
import sys

# Add the src directory to the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, 'src')
sys.path.insert(0, src_dir)

# Import the Flask app
from main import app

# This is the entry point for Vercel
def handler(request):
    return app(request.environ, lambda status, headers: None)

# For Vercel, we need to export the app
application = app

# Also make it available as 'app' for compatibility
if __name__ == "__main__":
    app.run(debug=True)

