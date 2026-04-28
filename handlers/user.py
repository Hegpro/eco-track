from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ContextTypes, ConversationHandler
from db.mongo import db
from utils.constants import (
    START_REG, IDLE, SELECT_TOPIC, ENTER_QUANTITY, 
    BTN_REPORT, BTN_IMPACT, BTN_CANCEL, MODE_TELEGRAM
)
import datetime
from services.impact_service import get_area_impact

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user = db.get_user(user_id)
    
    if not user:
        # New user registration
        areas = db.get_areas()
        if not areas:
            await update.message.reply_text("Welcome to Eco-Track! No areas are currently available. Please contact an admin.")
            return ConversationHandler.END
            
        keyboard = [[area["area_name"]] for area in areas]
        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
        await update.message.reply_text(
            f"Welcome {update.effective_user.first_name}! I am Eco-Track Bot.\n"
            "To get started, please select your Area:",
            reply_markup=reply_markup
        )
        return START_REG
    else:
        # Existing user
        return await show_main_menu(update, context)

async def handle_area_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    selected_area_name = update.message.text
    area = db.db.areas.find_one({"area_name": selected_area_name})
    
    if not area:
        await update.message.reply_text("Invalid area. Please select from the list.")
        return START_REG
        
    user_data = {
        "user_id": update.effective_user.id,
        "name": update.effective_user.full_name,
        "area_id": area["area_id"],
        "area_name": area["area_name"],
        "pincode": area.get("pincode"),
        "registered_at": datetime.datetime.now()
    }
    db.add_user(user_data)
    await update.message.reply_text(f"Successfully registered for {selected_area_name}!")
    return await show_main_menu(update, context)

async def show_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[BTN_REPORT, BTN_IMPACT]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text(
        "Main Menu:",
        reply_markup=reply_markup
    )
    return IDLE

async def initiate_report(update: Update, context: ContextTypes.DEFAULT_TYPE):
    topics = db.get_active_topics()
    if not topics:
        await update.message.reply_text("No active topics found. Please try again later.")
        return IDLE
        
    keyboard = [[topic["name"]] for topic in topics]
    keyboard.append([BTN_CANCEL])
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    await update.message.reply_text("What would you like to report?", reply_markup=reply_markup)
    return SELECT_TOPIC

async def handle_topic_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    topic_name = update.message.text
    if topic_name == BTN_CANCEL:
        return await show_main_menu(update, context)
        
    topic = db.db.topics.find_one({"name": topic_name})
    if not topic:
        await update.message.reply_text("Invalid topic. Please select from the list.")
        return SELECT_TOPIC
        
    context.user_data["reporting_topic"] = {
        "topic_id": topic["topic_id"],
        "name": topic["name"],
        "unit": topic["unit"]
    }
    
    await update.message.reply_text(f"Please enter the quantity ({topic['unit']}):", reply_markup=ReplyKeyboardMarkup([[BTN_CANCEL]], resize_keyboard=True))
    return ENTER_QUANTITY

async def handle_quantity_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    quantity_text = update.message.text
    if quantity_text == BTN_CANCEL:
        return await show_main_menu(update, context)
        
    try:
        quantity = float(quantity_text)
    except ValueError:
        await update.message.reply_text("Please enter a valid number.")
        return ENTER_QUANTITY
        
    user_id = update.effective_user.id
    user = db.get_user(user_id)
    topic_data = context.user_data.get("reporting_topic")
    
    report_data = {
        "user_id": user_id,
        "area_id": user["area_id"],
        "topic_id": topic_data["topic_id"],
        "quantity": quantity,
        "timestamp": datetime.datetime.now(),
        "input_mode": MODE_TELEGRAM
    }
    
    db.add_report(report_data)
    await update.message.reply_text(f"✅ Successfully reported {quantity} {topic_data['unit']} for {topic_data['name']}!")
    
    # Clear temp state
    context.user_data.pop("reporting_topic", None)
    
    return await show_main_menu(update, context)

async def view_impact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user = db.get_user(user_id)
    
    if not user:
        await update.message.reply_text("Please register first using /start")
        return ConversationHandler.END
        
    impact_summary = get_area_impact(user["area_id"])
    await update.message.reply_text(impact_summary, parse_mode="Markdown")
    return IDLE

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Action cancelled.", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END
