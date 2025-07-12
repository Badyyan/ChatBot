from flask import Blueprint, request, jsonify, current_app
from src.models.bot import db, Bot
from src.services.telegram_bot_service import TelegramBotService
import threading

bot_control_bp = Blueprint('bot_control', __name__)

# Global bot service instance
bot_service = None

def get_bot_service():
    """Get or create bot service instance"""
    global bot_service
    if bot_service is None:
        bot_service = TelegramBotService(current_app.app_context)
    return bot_service

@bot_control_bp.route('/bots/<int:bot_id>/start', methods=['POST'])
def start_bot(bot_id):
    """Start a Telegram bot"""
    try:
        bot = Bot.query.get_or_404(bot_id)
        service = get_bot_service()
        
        # Check if bot is already running
        if service.is_bot_running(bot_id):
            return jsonify({
                'success': False,
                'error': 'Bot is already running'
            }), 400
        
        # Start bot in a separate thread
        thread = service.start_bot_in_thread(bot_id)
        
        # Give it a moment to start
        import time
        time.sleep(2)
        
        # Check if bot started successfully
        if service.is_bot_running(bot_id):
            return jsonify({
                'success': True,
                'message': f'Bot {bot.name} started successfully'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to start bot. Please check the bot token.'
            }), 500
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bot_control_bp.route('/bots/<int:bot_id>/stop', methods=['POST'])
def stop_bot(bot_id):
    """Stop a Telegram bot"""
    try:
        bot = Bot.query.get_or_404(bot_id)
        service = get_bot_service()
        
        # Check if bot is running
        if not service.is_bot_running(bot_id):
            return jsonify({
                'success': False,
                'error': 'Bot is not running'
            }), 400
        
        # Stop bot
        success = service.stop_bot_sync(bot_id)
        
        if success:
            return jsonify({
                'success': True,
                'message': f'Bot {bot.name} stopped successfully'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to stop bot'
            }), 500
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bot_control_bp.route('/bots/<int:bot_id>/status', methods=['GET'])
def get_bot_status(bot_id):
    """Get bot running status"""
    try:
        bot = Bot.query.get_or_404(bot_id)
        service = get_bot_service()
        
        is_running = service.is_bot_running(bot_id)
        
        return jsonify({
            'success': True,
            'data': {
                'bot_id': bot_id,
                'name': bot.name,
                'is_running': is_running,
                'is_active': bot.is_active
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bot_control_bp.route('/bots/status', methods=['GET'])
def get_all_bots_status():
    """Get status of all bots"""
    try:
        bots = Bot.query.all()
        service = get_bot_service()
        
        bot_statuses = []
        for bot in bots:
            is_running = service.is_bot_running(bot.id)
            bot_statuses.append({
                'bot_id': bot.id,
                'name': bot.name,
                'username': bot.username,
                'is_running': is_running,
                'is_active': bot.is_active
            })
        
        return jsonify({
            'success': True,
            'data': bot_statuses
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bot_control_bp.route('/bots/running', methods=['GET'])
def get_running_bots():
    """Get list of currently running bots"""
    try:
        service = get_bot_service()
        running_bot_ids = service.get_running_bots()
        
        running_bots = []
        for bot_id in running_bot_ids:
            bot = Bot.query.get(bot_id)
            if bot:
                running_bots.append({
                    'bot_id': bot.id,
                    'name': bot.name,
                    'username': bot.username
                })
        
        return jsonify({
            'success': True,
            'data': running_bots
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

