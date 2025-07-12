import os
import sys

# Ensure the src directory is in the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from flask import Flask, send_from_directory
from flask_cors import CORS
from models.user import db
# Import all models to ensure they are registered with SQLAlchemy
from models.user import User
from models.bot import Bot, KnowledgeBase, Document, TextChunk, Conversation
from routes.user import user_bp
from routes.bot_routes import bot_bp

app = Flask(__name__, static_folder=os.path.join(current_dir, 'static'))
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'asdf#FGSgvasgf$5$WGT')

# Database configuration for Vercel (use environment variable or SQLite)
database_url = os.environ.get('DATABASE_URL')
if database_url:
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
else:
    # Use SQLite for development/testing
    db_path = os.path.join('/tmp', 'app.db')  # Use /tmp for Vercel
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Enable CORS for all routes
CORS(app, origins="*")

# Initialize database
db.init_app(app)

# Register blueprints
app.register_blueprint(user_bp, url_prefix='/api')
app.register_blueprint(bot_bp, url_prefix='/api')

# Import and register bot control routes
from routes.bot_control import bot_control_bp
app.register_blueprint(bot_control_bp, url_prefix='/api')

# Import and register file routes
from routes.file_routes import file_bp
app.register_blueprint(file_bp, url_prefix='/api')

# Create database tables
with app.app_context():
    db.create_all()

# Serve static files
@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:filename>')
def static_files(filename):
    return send_from_directory(app.static_folder, filename)

# Health check endpoint
@app.route('/health')
def health_check():
    return {'status': 'healthy', 'message': 'Telegram Bot Knowledge Base API is running'}

if __name__ == '__main__':
    # For local development
    app.run(host='0.0.0.0', port=5000, debug=True)

# Export app for Vercel
application = app

