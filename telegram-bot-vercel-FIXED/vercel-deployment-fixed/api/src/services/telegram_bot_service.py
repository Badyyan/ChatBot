import asyncio
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from src.models.bot import db, Bot, Conversation, TextChunk, Document, KnowledgeBase
from src.services.knowledge_base_service import KnowledgeBaseService
import threading
import time

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class TelegramBotService:
    def __init__(self, app_context):
        self.app_context = app_context
        self.running_bots = {}
        self.kb_service = KnowledgeBaseService()
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE, bot_id: int):
        """Handle /start command"""
        with self.app_context():
            bot = Bot.query.get(bot_id)
            if not bot:
                return
            
            welcome_message = f"""
🤖 Welcome to {bot.name}!

I'm an AI assistant with access to a knowledge base. You can ask me questions and I'll try to help you based on the information I have.

Commands:
/start - Show this welcome message
/help - Get help information

Just send me a message with your question!
            """
            
            await update.message.reply_text(welcome_message)
            
            # Log conversation
            conversation = Conversation(
                telegram_user_id=str(update.effective_user.id),
                telegram_username=update.effective_user.username,
                message="/start",
                response=welcome_message,
                bot_id=bot_id
            )
            db.session.add(conversation)
            db.session.commit()
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE, bot_id: int):
        """Handle /help command"""
        with self.app_context():
            bot = Bot.query.get(bot_id)
            if not bot:
                return
            
            help_message = f"""
🆘 Help for {bot.name}

I can help you find information from my knowledge base. Here's how to use me:

1. **Ask Questions**: Simply type your question and I'll search for relevant information
2. **Be Specific**: The more specific your question, the better I can help
3. **Try Different Phrasings**: If you don't get the answer you're looking for, try rephrasing your question

Commands:
/start - Welcome message
/help - This help message

Example questions:
- "What is...?"
- "How do I...?"
- "Tell me about..."
            """
            
            await update.message.reply_text(help_message)
            
            # Log conversation
            conversation = Conversation(
                telegram_user_id=str(update.effective_user.id),
                telegram_username=update.effective_user.username,
                message="/help",
                response=help_message,
                bot_id=bot_id
            )
            db.session.add(conversation)
            db.session.commit()
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE, bot_id: int):
        """Handle regular text messages"""
        with self.app_context():
            bot = Bot.query.get(bot_id)
            if not bot:
                return
            
            user_message = update.message.text
            user_id = str(update.effective_user.id)
            username = update.effective_user.username
            
            # Search knowledge base
            try:
                response = self.kb_service.search_knowledge_base(bot_id, user_message)
                
                if not response:
                    response = """
I'm sorry, I couldn't find relevant information in my knowledge base to answer your question. 

You can try:
- Rephrasing your question
- Being more specific
- Asking about a different topic

If you think this information should be available, please contact the administrator to update the knowledge base.
                    """
                
                await update.message.reply_text(response)
                
                # Log conversation
                conversation = Conversation(
                    telegram_user_id=user_id,
                    telegram_username=username,
                    message=user_message,
                    response=response,
                    bot_id=bot_id
                )
                db.session.add(conversation)
                db.session.commit()
                
            except Exception as e:
                logger.error(f"Error processing message: {e}")
                error_response = "I'm sorry, I encountered an error while processing your request. Please try again later."
                await update.message.reply_text(error_response)
                
                # Log error conversation
                conversation = Conversation(
                    telegram_user_id=user_id,
                    telegram_username=username,
                    message=user_message,
                    response=f"Error: {str(e)}",
                    bot_id=bot_id
                )
                db.session.add(conversation)
                db.session.commit()
    
    def create_bot_handlers(self, bot_id: int):
        """Create handlers for a specific bot"""
        async def start_wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
            await self.start_command(update, context, bot_id)
        
        async def help_wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
            await self.help_command(update, context, bot_id)
        
        async def message_wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
            await self.handle_message(update, context, bot_id)
        
        return start_wrapper, help_wrapper, message_wrapper
    
    async def start_bot(self, bot_id: int):
        """Start a specific bot"""
        with self.app_context():
            bot = Bot.query.get(bot_id)
            if not bot:
                logger.error(f"Bot with ID {bot_id} not found")
                return False
            
            try:
                token = bot.decrypt_token()
                application = Application.builder().token(token).build()
                
                # Create handlers
                start_handler, help_handler, message_handler = self.create_bot_handlers(bot_id)
                
                # Add handlers
                application.add_handler(CommandHandler("start", start_handler))
                application.add_handler(CommandHandler("help", help_handler))
                application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))
                
                # Start the bot
                await application.initialize()
                await application.start()
                await application.updater.start_polling()
                
                # Store the application
                self.running_bots[bot_id] = application
                
                # Update bot status
                bot.is_active = True
                db.session.commit()
                
                logger.info(f"Bot {bot.name} (ID: {bot_id}) started successfully")
                return True
                
            except Exception as e:
                logger.error(f"Error starting bot {bot_id}: {e}")
                return False
    
    async def stop_bot(self, bot_id: int):
        """Stop a specific bot"""
        if bot_id in self.running_bots:
            try:
                application = self.running_bots[bot_id]
                await application.updater.stop()
                await application.stop()
                await application.shutdown()
                
                del self.running_bots[bot_id]
                
                # Update bot status
                with self.app_context():
                    bot = Bot.query.get(bot_id)
                    if bot:
                        bot.is_active = False
                        db.session.commit()
                
                logger.info(f"Bot {bot_id} stopped successfully")
                return True
                
            except Exception as e:
                logger.error(f"Error stopping bot {bot_id}: {e}")
                return False
        
        return False
    
    def start_bot_sync(self, bot_id: int):
        """Synchronous wrapper for starting a bot"""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(self.start_bot(bot_id))
        finally:
            loop.close()
    
    def stop_bot_sync(self, bot_id: int):
        """Synchronous wrapper for stopping a bot"""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(self.stop_bot(bot_id))
        finally:
            loop.close()
    
    def start_bot_in_thread(self, bot_id: int):
        """Start a bot in a separate thread"""
        def run_bot():
            self.start_bot_sync(bot_id)
        
        thread = threading.Thread(target=run_bot, daemon=True)
        thread.start()
        return thread
    
    def get_running_bots(self):
        """Get list of currently running bot IDs"""
        return list(self.running_bots.keys())
    
    def is_bot_running(self, bot_id: int):
        """Check if a bot is currently running"""
        return bot_id in self.running_bots

