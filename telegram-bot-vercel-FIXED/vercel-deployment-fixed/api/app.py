import os
import sys

# Add current directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)
sys.path.insert(0, os.path.join(current_dir, 'src'))

from flask import Flask, send_from_directory, jsonify
from flask_cors import CORS

# Create Flask app
app = Flask(__name__, static_folder=os.path.join(current_dir, 'src', 'static'))
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'asdf#FGSgvasgf$5$WGT')

# Database configuration for Vercel
database_url = os.environ.get('DATABASE_URL')
if database_url:
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
else:
    # Use SQLite for development/testing
    db_path = os.path.join('/tmp', 'app.db')
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Enable CORS for all routes
CORS(app, origins="*")

# Basic routes for testing
@app.route('/')
def index():
    try:
        return send_from_directory(app.static_folder, 'index.html')
    except:
        return jsonify({
            'message': 'Telegram Bot Knowledge Base API',
            'status': 'running',
            'version': '1.0.0'
        })

@app.route('/health')
def health_check():
    return jsonify({
        'status': 'healthy', 
        'message': 'Telegram Bot Knowledge Base API is running'
    })

@app.route('/api/test')
def api_test():
    return jsonify({
        'message': 'API is working',
        'status': 'success'
    })

# Try to import and register the full application
try:
    from src.models.user import db
    from src.models.user import User
    from src.models.bot import Bot, KnowledgeBase, Document, TextChunk, Conversation
    from src.routes.user import user_bp
    from src.routes.bot_routes import bot_bp
    from src.routes.bot_control import bot_control_bp
    from src.routes.file_routes import file_bp
    
    # Initialize database
    db.init_app(app)
    
    # Register blueprints
    app.register_blueprint(user_bp, url_prefix='/api')
    app.register_blueprint(bot_bp, url_prefix='/api')
    app.register_blueprint(bot_control_bp, url_prefix='/api')
    app.register_blueprint(file_bp, url_prefix='/api')
    
    # Create database tables
    with app.app_context():
        db.create_all()
        
except Exception as e:
    print(f"Warning: Could not load full application: {e}")
    # Continue with basic app

if __name__ == '__main__':
    app.run(debug=True)

