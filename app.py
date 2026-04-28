import logging
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    filters,
)
import config
from utils.constants import START_REG, IDLE, SELECT_TOPIC, ENTER_QUANTITY, BTN_REPORT, BTN_IMPACT
from handlers.user import (
    start,
    handle_area_selection,
    initiate_report,
    handle_topic_selection,
    handle_quantity_input,
    view_impact,
    cancel,
)
from handlers.admin import (
    admin_menu,
    handle_add_area,
    handle_add_topic,
    handle_view_reports,
    handle_send_nudge,
)

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

def main():
    # Create the Application
    application = ApplicationBuilder().token(config.BOT_TOKEN).build()

    # Conversation Handler
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            START_REG: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_area_selection)],
            IDLE: [
                MessageHandler(filters.Regex(f"^{BTN_REPORT}$"), initiate_report),
                MessageHandler(filters.Regex(f"^{BTN_IMPACT}$"), view_impact),
                CommandHandler("start", start), # Allow restarting
            ],
            SELECT_TOPIC: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_topic_selection)],
            ENTER_QUANTITY: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_quantity_input)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
        allow_reentry=True,
    )

    application.add_handler(conv_handler)
    
    # Admin Handlers
    application.add_handler(CommandHandler("admin", admin_menu))
    application.add_handler(CommandHandler("add_area", handle_add_area))
    application.add_handler(CommandHandler("add_topic", handle_add_topic))
    application.add_handler(CommandHandler("view_reports", handle_view_reports))
    application.add_handler(CommandHandler("send_nudge", handle_send_nudge))
    
    # Global cancel command
    application.add_handler(CommandHandler("cancel", cancel))

    # Run the bot
    print("Eco-Track Bot is starting...")
    application.run_polling()

if __name__ == "__main__":
    main()
