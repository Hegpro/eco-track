import logging

logger = logging.getLogger(__name__)

class EcoTrackError(Exception):
    """Base exception for Eco-Track"""
    def __init__(self, message="An internal error occurred"):
        self.message = message
        super().__init__(self.message)

class DatabaseError(EcoTrackError):
    """Raised when database operations fail"""
    pass

class NetworkError(EcoTrackError):
    """Raised when external API calls fail"""
    pass

class ValidationError(EcoTrackError):
    """Raised when user input is invalid"""
    pass

def handle_error(update, context):
    """Global error handler for the Telegram bot"""
    logger.error(msg="Exception while handling an update:", exc_info=context.error)
    
    # User-friendly message
    error_msg = "⚠️ *Something went wrong internally.*\n\nPlease try again in a moment or use /start to reset."
    
    if update and update.effective_message:
        update.effective_message.reply_text(error_msg, parse_mode="Markdown")
