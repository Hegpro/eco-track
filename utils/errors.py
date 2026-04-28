import logging
from telegram.error import Conflict

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

async def handle_error(update, context):
    """Global error handler for the Telegram bot"""
    # Silently ignore Conflict errors - they mean another instance is running
    if isinstance(context.error, Conflict):
        logger.warning("Conflict error detected: Another bot instance is likely running. Shutting down this instance.")
        # We don't exit(1) here as it might be a temporary network issue, 
        # but the Conflict error is handled by the framework.
        return

    logger.error(msg="Exception while handling an update:", exc_info=context.error)
    
    # User-friendly message
    error_msg = "⚠️ *Something went wrong internally.*\n\nPlease try again in a moment or use /start to reset."
    
    try:
        if update and update.effective_message:
            await update.effective_message.reply_text(error_msg, parse_mode="Markdown")
    except Exception as e:
        logger.error(f"Failed to send error message to user: {e}")
