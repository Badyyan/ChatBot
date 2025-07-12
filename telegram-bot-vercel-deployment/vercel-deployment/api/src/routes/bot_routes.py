from flask import Blueprint, request, jsonify
from src.models.bot import db, Bot, KnowledgeBase, Document, TextChunk, Conversation
from datetime import datetime
import os

bot_bp = Blueprint('bot', __name__)

@bot_bp.route('/bots', methods=['GET'])
def get_bots():
    """Get all bots"""
    try:
        bots = Bot.query.all()
        return jsonify({
            'success': True,
            'data': [bot.to_dict() for bot in bots]
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bot_bp.route('/bots', methods=['POST'])
def create_bot():
    """Create a new bot"""
    try:
        data = request.get_json()
        
        if not data or not data.get('name') or not data.get('token') or not data.get('username'):
            return jsonify({
                'success': False,
                'error': 'Name, token, and username are required'
            }), 400
        
        # Check if username already exists
        existing_bot = Bot.query.filter_by(username=data['username']).first()
        if existing_bot:
            return jsonify({
                'success': False,
                'error': 'Bot username already exists'
            }), 400
        
        bot = Bot(
            name=data['name'],
            username=data['username'],
            description=data.get('description', '')
        )
        bot.encrypt_token(data['token'])
        
        db.session.add(bot)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': bot.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bot_bp.route('/bots/<int:bot_id>', methods=['GET'])
def get_bot(bot_id):
    """Get a specific bot"""
    try:
        bot = Bot.query.get_or_404(bot_id)
        return jsonify({
            'success': True,
            'data': bot.to_dict()
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bot_bp.route('/bots/<int:bot_id>', methods=['PUT'])
def update_bot(bot_id):
    """Update a bot"""
    try:
        bot = Bot.query.get_or_404(bot_id)
        data = request.get_json()
        
        if data.get('name'):
            bot.name = data['name']
        if data.get('description'):
            bot.description = data['description']
        if data.get('token'):
            bot.encrypt_token(data['token'])
        if 'is_active' in data:
            bot.is_active = data['is_active']
        
        bot.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': bot.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bot_bp.route('/bots/<int:bot_id>', methods=['DELETE'])
def delete_bot(bot_id):
    """Delete a bot"""
    try:
        bot = Bot.query.get_or_404(bot_id)
        db.session.delete(bot)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Bot deleted successfully'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bot_bp.route('/bots/<int:bot_id>/knowledge-bases', methods=['GET'])
def get_bot_knowledge_bases(bot_id):
    """Get all knowledge bases for a bot"""
    try:
        bot = Bot.query.get_or_404(bot_id)
        knowledge_bases = KnowledgeBase.query.filter_by(bot_id=bot_id).all()
        
        return jsonify({
            'success': True,
            'data': [kb.to_dict() for kb in knowledge_bases]
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bot_bp.route('/bots/<int:bot_id>/knowledge-bases', methods=['POST'])
def create_knowledge_base(bot_id):
    """Create a new knowledge base for a bot"""
    try:
        bot = Bot.query.get_or_404(bot_id)
        data = request.get_json()
        
        if not data or not data.get('name'):
            return jsonify({
                'success': False,
                'error': 'Name is required'
            }), 400
        
        kb = KnowledgeBase(
            name=data['name'],
            description=data.get('description', ''),
            bot_id=bot_id
        )
        
        db.session.add(kb)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': kb.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bot_bp.route('/knowledge-bases/<int:kb_id>', methods=['DELETE'])
def delete_knowledge_base(kb_id):
    """Delete a knowledge base"""
    try:
        kb = KnowledgeBase.query.get_or_404(kb_id)
        db.session.delete(kb)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Knowledge base deleted successfully'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bot_bp.route('/bots/<int:bot_id>/conversations', methods=['GET'])
def get_bot_conversations(bot_id):
    """Get conversation history for a bot"""
    try:
        bot = Bot.query.get_or_404(bot_id)
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        conversations = Conversation.query.filter_by(bot_id=bot_id)\
            .order_by(Conversation.created_at.desc())\
            .paginate(page=page, per_page=per_page, error_out=False)
        
        return jsonify({
            'success': True,
            'data': [conv.to_dict() for conv in conversations.items],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': conversations.total,
                'pages': conversations.pages
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

