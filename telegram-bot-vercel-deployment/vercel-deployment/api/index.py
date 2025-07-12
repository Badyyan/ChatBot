import os
import sys

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.main import app

# Vercel expects the Flask app to be available as 'app'
# This is the entry point for Vercel deployment
if __name__ == "__main__":
    app.run()

