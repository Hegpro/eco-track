import logging
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler, ConversationHandler, filters, CallbackQueryHandler
)
import config
from utils.constants import (
    START_REG, IDLE, SELECT_RESOURCE, SELECT_ISSUE_TYPE, 
    LOCATION_MENU, ENTER_PINCODE, ENTER_LANDMARK, CONFIRM_LOC_SAVE, MANUAL_LOCATION,
    CONFIRM_REPORT, 
    VIEW_SCORE_MENU, VIEW_IMPACT_MENU, VIEW_MORE,
    SELECT_POST_OFFICE, ENTER_HELP_MSG,
    BTN_REPORT, BTN_AREA_SCORE, BTN_MY_IMPACT, BTN_MORE,
    BTN_BACK, BTN_HOME
)
from handlers.user import (
    start, handle_area_selection, initiate_report, handle_resource_selection,
    handle_issue_type_selection, handle_location_menu, handle_pincode_input,
    handle_post_office_selection,
    handle_landmark_input, handle_loc_confirmation, 
    handle_manual_location, handle_report_final, 
    view_score_menu, handle_score_menu_click, view_impact_menu, handle_impact_menu_click,
    view_more_menu, handle_more_menu_click, handle_help_message, cancel
)
from handlers.admin import admin_menu
from utils.errors import handle_error

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)

def main():
    application = ApplicationBuilder().token(config.BOT_TOKEN).build()
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            START_REG: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_area_selection)],
            IDLE: [
                MessageHandler(filters.Regex(f"^{BTN_REPORT}$"), initiate_report),
                MessageHandler(filters.Regex(f"^{BTN_AREA_SCORE}$"), view_score_menu),
                MessageHandler(filters.Regex(f"^{BTN_MY_IMPACT}$"), view_impact_menu),
                MessageHandler(filters.Regex(f"^{BTN_MORE}$"), view_more_menu),
                CommandHandler("start", start),
            ],
            SELECT_RESOURCE: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_resource_selection)],
            SELECT_ISSUE_TYPE: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_issue_type_selection)],
            LOCATION_MENU: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_location_menu)],
            ENTER_PINCODE: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_pincode_input)],
            SELECT_POST_OFFICE: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_post_office_selection)],
            ENTER_LANDMARK: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_landmark_input)],
            CONFIRM_LOC_SAVE: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_loc_confirmation)],
            MANUAL_LOCATION: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_manual_location)],
            CONFIRM_REPORT: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_report_final)],
            CONFIRM_REPORT: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_report_final)],
            VIEW_SCORE_MENU: [
                MessageHandler(filters.Regex(f"^{BTN_BACK}$"), start),
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_score_menu_click)
            ],
            VIEW_IMPACT_MENU: [
                MessageHandler(filters.Regex(f"^{BTN_BACK}$"), start),
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_impact_menu_click)
            ],
            VIEW_MORE: [
                MessageHandler(filters.Regex(f"^{BTN_BACK}$"), start),
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_more_menu_click)
            ],
            ENTER_HELP_MSG: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_help_message)],
        },
        fallbacks=[CommandHandler("cancel", cancel), MessageHandler(filters.Regex(f"^{BTN_BACK}$"), start), MessageHandler(filters.Regex(f"^{BTN_HOME}$"), start)],
        allow_reentry=True,
    )
    application.add_handler(conv_handler)
    application.add_handler(CommandHandler("admin", admin_menu))
    application.add_handler(CommandHandler("cancel", cancel))
    
    # Global Error Handler
    application.add_error_handler(handle_error)

    print("Eco-Track Production Bot is starting...")
    application.run_polling()

if __name__ == "__main__": main()
