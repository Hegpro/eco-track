from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
from db.mongo import db
import datetime
import requests
import logging
from services.impact_service import (
    get_area_impact, get_area_trends, get_personal_impact, get_leaderboard, calculate_score
)
from utils.constants import (
    START_REG, IDLE, SELECT_RESOURCE, SELECT_ISSUE_TYPE, 
    LOCATION_MENU, ENTER_PINCODE, ENTER_LANDMARK, CONFIRM_LOC_SAVE, MANUAL_LOCATION,
    CONFIRM_REPORT, 
    VIEW_SCORE_MENU, VIEW_IMPACT_MENU, VIEW_MORE,
    SELECT_POST_OFFICE, ENTER_HELP_MSG,
    BTN_REPORT, BTN_AREA_SCORE, BTN_MY_IMPACT, BTN_MORE,
    BTN_CANCEL, BTN_BACK, BTN_YES, BTN_HOME, RESOURCES, ISSUE_TYPES,
    BTN_LOC_PIN, BTN_LOC_SAVED, BTN_LOC_MANUAL,
    BTN_VIEW_SCORE, BTN_VIEW_TRENDS, BTN_HOW_SCORE,
    BTN_MY_STATS, BTN_MY_RANK, BTN_MY_HISTORY,
    BTN_LANG, BTN_STATUS, BTN_HELP
)

logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user = db.get_user(user_id)
    if not user:
        areas = db.get_areas()
        keyboard = [[area["area_name"]] for area in areas]
        await update.message.reply_text(
            "📍 *Eco-Track neighborhood App*\n\nPlease select your area:",
            reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True),
            parse_mode="Markdown"
        )
        return START_REG
    return await show_main_menu(update, context)


async def handle_area_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    area = db.db.areas.find_one({"area_name": {"$regex": text, "$options": "i"}})
    if not area: return START_REG
    db.add_user({
        "user_id": update.effective_user.id, "name": update.effective_user.full_name,
        "area_id": area["area_id"], "area_name": area["area_name"], "pincode": area.get("pincode", "560038"),
        "registered_at": datetime.datetime.now(), "reports_count": 0, "resolved_count": 0
    })
    return await show_main_menu(update, context)

async def show_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [BTN_REPORT],
        [BTN_AREA_SCORE, BTN_MY_IMPACT],
        [BTN_MORE]
    ]
    await update.message.reply_text("🌿 *Main Menu*", reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True), parse_mode="Markdown")
    return IDLE

# --- 📊 REPORT ISSUE FLOW ---

async def initiate_report(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[r] for r in RESOURCES.values()]
    keyboard.append([BTN_CANCEL])
    await update.message.reply_text("Step 1/4: Select Category", reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))
    return SELECT_RESOURCE

async def handle_resource_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    res_text = update.message.text
    if res_text == BTN_CANCEL: return await show_main_menu(update, context)
    res_key = next((k for k, v in RESOURCES.items() if v == res_text), None)
    if not res_key: return SELECT_RESOURCE
    context.user_data["report"] = {"res_key": res_key, "res_text": res_text}
    keyboard = [[i] for i in ISSUE_TYPES[res_key]]
    keyboard.append([BTN_BACK, BTN_CANCEL])
    await update.message.reply_text(f"Selected: {res_text}\n\nStep 2/4: Select Issue Type", reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))
    return SELECT_ISSUE_TYPE

async def handle_issue_type_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    issue_text = update.message.text
    if issue_text == BTN_CANCEL: return await show_main_menu(update, context)
    if issue_text == BTN_BACK: return await initiate_report(update, context)
    context.user_data["report"]["issue_text"] = issue_text
    
    keyboard = [
        [BTN_LOC_PIN, BTN_LOC_SAVED],
        [BTN_LOC_MANUAL],
        [BTN_BACK, BTN_CANCEL]
    ]
    await update.message.reply_text("Step 3/4: Location Menu", reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))
    return LOCATION_MENU

# --- 📍 LOCATION SYSTEM ---

async def handle_location_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    choice = update.message.text
    if choice == BTN_BACK: 
        res_key = context.user_data["report"]["res_key"]
        keyboard = [[i] for i in ISSUE_TYPES[res_key]]
        keyboard.append([BTN_BACK, BTN_CANCEL])
        await update.message.reply_text("Step 2/4: Select Issue Type", reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))
        return SELECT_ISSUE_TYPE
    if choice == BTN_CANCEL: return await show_main_menu(update, context)
    
    if choice == BTN_LOC_PIN:
        await update.message.reply_text("Enter Pincode:", reply_markup=ReplyKeyboardMarkup([[BTN_BACK, BTN_CANCEL]], resize_keyboard=True))
        return ENTER_PINCODE
    elif choice == BTN_LOC_SAVED:
        user = db.get_user(update.effective_user.id)
        context.user_data["report"]["locality"] = user["area_name"]
        context.user_data["report"]["pincode"] = user.get("pincode", "560038")
        await update.message.reply_text(f"Using Saved Area: {user['area_name']}\n\nEnter a nearby Landmark:", reply_markup=ReplyKeyboardMarkup([[BTN_BACK, BTN_CANCEL]], resize_keyboard=True))
        return ENTER_LANDMARK
    elif choice == BTN_LOC_MANUAL:
        await update.message.reply_text("Enter Block / Lane / Landmark:", reply_markup=ReplyKeyboardMarkup([[BTN_BACK, BTN_CANCEL]], resize_keyboard=True))
        return MANUAL_LOCATION
    return LOCATION_MENU

async def handle_pincode_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    pin = update.message.text
    if pin == BTN_BACK: return await handle_issue_type_selection(update, context)
    if pin == BTN_CANCEL: return await show_main_menu(update, context)
    
    # Validate pincode via API
    try:
        logger.info(f"Validating pincode: {pin}")
        headers = {'User-Agent': 'EcoTrack-Bot/1.0'}
        response = requests.get(f"https://api.postalpincode.in/pincode/{pin}", timeout=10, headers=headers)
        data = response.json()
        logger.info(f"API Response for {pin}: {data}")
        
        if data[0]["Status"] != "Success":
            logger.warning(f"Invalid pincode entered: {pin}. API returned Status: {data[0].get('Status')}")
            await update.message.reply_text(f"❌ Invalid Pincode: {pin}. Please try again.")
            return ENTER_PINCODE
        
        post_offices = data[0]["PostOffice"]
        context.user_data["post_offices"] = [po["Name"] for po in post_offices]
        context.user_data["report"]["pincode"] = pin
        
        keyboard = [[po] for po in context.user_data["post_offices"]]
        keyboard.append([BTN_BACK, BTN_CANCEL])
        await update.message.reply_text(
            f"✅ Pincode {pin} validated!\n\nPlease select your Area/Post Office:",
            reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        )
        return SELECT_POST_OFFICE
    except requests.exceptions.Timeout:
        logger.error(f"Pincode validation timed out for {pin}")
        await update.message.reply_text("⏳ The verification service is slow. Please try again in a moment.")
        return ENTER_PINCODE
    except requests.exceptions.ConnectionError as e:
        logger.error(f"Pincode validation connection error for {pin}: {str(e)}")
        await update.message.reply_text("🔌 Service connectivity issue. Retrying may help.")
        return ENTER_PINCODE
    except Exception as e:
        logger.error(f"Pincode validation failed for {pin}: {str(e)}", exc_info=True)
        await update.message.reply_text("⚠️ Unexpected error during validation. Please try again.")
        return ENTER_PINCODE

async def handle_post_office_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    po_name = update.message.text
    if po_name == BTN_BACK: 
        await update.message.reply_text("Enter Pincode:", reply_markup=ReplyKeyboardMarkup([[BTN_BACK, BTN_CANCEL]], resize_keyboard=True))
        return ENTER_PINCODE
    if po_name == BTN_CANCEL: return await show_main_menu(update, context)
    
    if po_name not in context.user_data.get("post_offices", []):
        return SELECT_POST_OFFICE
    
    context.user_data["report"]["locality"] = po_name
    await update.message.reply_text(
        "Enter a nearby Landmark (e.g. Near Park, Opp. Gate 1):",
        reply_markup=ReplyKeyboardMarkup([[BTN_BACK, BTN_CANCEL]], resize_keyboard=True)
    )
    return ENTER_LANDMARK

async def handle_landmark_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    landmark = update.message.text
    if landmark == BTN_BACK: 
        if context.user_data.get("post_offices"):
            keyboard = [[po] for po in context.user_data["post_offices"]]
            keyboard.append([BTN_BACK, BTN_CANCEL])
            await update.message.reply_text("Select Locality:", reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))
            return SELECT_POST_OFFICE
        await update.message.reply_text("Enter Pincode:", reply_markup=ReplyKeyboardMarkup([[BTN_BACK, BTN_CANCEL]], resize_keyboard=True))
        return ENTER_PINCODE
    if landmark == BTN_CANCEL: return await show_main_menu(update, context)
    
    context.user_data["report"]["landmark"] = landmark
    locality = context.user_data["report"].get("locality")
    
    if locality:
        # If locality was already picked (from API or Saved Area), skip mock selection
        context.user_data["report"]["location"] = f"{locality}, Near {landmark}"
        keyboard = [["✅ Confirm", "⬅️ Change"], [BTN_CANCEL]]
        await update.message.reply_text(f"Confirm Location: {locality}?", reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))
        return CONFIRM_LOC_SAVE
    
    # Fallback for manual or legacy flows (can be removed if strictly API-only)
    await update.message.reply_text("Locality not found. Please re-enter pincode or manual location.", reply_markup=ReplyKeyboardMarkup([[BTN_BACK, BTN_CANCEL]], resize_keyboard=True))
    return LOCATION_MENU

async def handle_loc_confirmation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text == "⬅️ Change": 
        await update.message.reply_text("Enter Pincode:", reply_markup=ReplyKeyboardMarkup([[BTN_BACK, BTN_CANCEL]], resize_keyboard=True))
        return ENTER_PINCODE
    if text == BTN_CANCEL: return await show_main_menu(update, context)
    
    keyboard = [["✅ Save for Future", "❌ Skip"]]
    await update.message.reply_text("Save location for future use?", reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))
    return CONFIRM_REPORT

async def handle_manual_location(update: Update, context: ContextTypes.DEFAULT_TYPE):
    loc = update.message.text
    if loc == BTN_BACK: return await handle_issue_type_selection(update, context)
    if loc == BTN_CANCEL: return await show_main_menu(update, context)
    context.user_data["report"]["location"] = loc
    return await handle_report_confirmation_step(update, context)

async def handle_report_confirmation_step(update: Update, context: ContextTypes.DEFAULT_TYPE):
    report = context.user_data["report"]
    confirm_msg = f"Step 4/4: Confirmation\n\n📍 {report['location']}\n{report['res_text'].split(' ')[0]} {report['issue_text']}\n\nSubmit?"
    keyboard = [["✅ Submit", BTN_CANCEL], [BTN_BACK]]
    await update.message.reply_text(confirm_msg, reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))
    return CONFIRM_REPORT

async def handle_report_final(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text == BTN_CANCEL: return await show_main_menu(update, context)
    if text == BTN_BACK: return await handle_issue_type_selection(update, context)
    
    user = db.get_user(update.effective_user.id)
    report_data = context.user_data["report"]
    impact_l = 200 if report_data["res_key"] == "water" else 0
    locality = report_data.get("locality")
    area_id = locality if locality else user["area_id"]
    area_name = locality if locality else user["area_name"]
    
    # Ensure the area exists in the areas collection for the dashboard
    db.update_area_score(area_id, 0, area_name=area_name) # This will upsert if not exists with score 100
    
    old_score = calculate_score(area_id)
    
    # Use the new increment logic
    report_data.update({
        "user_id": update.effective_user.id, 
        "area_id": area_id,
        "area_name": area_name,
        "topic_id": report_data["res_key"] + "_id", 
        "issue_type": report_data["issue_text"],
        "status": "Open", 
        "timestamp": datetime.datetime.now(), 
        "impact_value": impact_l
    })
    
    res = db.add_or_increment_report(report_data)
    
    # Check if it was an increment or a new insert
    is_increment = hasattr(res, 'modified_count') and res.modified_count > 0
    
    db.db.users.update_one({"user_id": user["user_id"]}, {"$inc": {"reports_count": 1}})
    new_score = calculate_score(area_id)
    
    if is_increment:
        success_msg = f"♻️ Issue Frequency Increased!\n\nThis issue has been reported multiple times at this location.\nScore: {old_score} → {new_score}"
    else:
        success_msg = f"⚠️ {report_data['issue_text']} Reported\n\n*Impact:*\n~{impact_l}L/day waste\nScore: {old_score} → {new_score}\n\n*Action:* Fix within 24 hrs"
    
    await update.message.reply_text(success_msg, parse_mode="Markdown")
    return await show_main_menu(update, context)


# --- 🌿 SUB-MENUS ---

async def view_score_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[BTN_VIEW_SCORE, BTN_VIEW_TRENDS], [BTN_HOW_SCORE], [BTN_BACK]]
    await update.message.reply_text("🌿 *Area Score Menu*", reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True), parse_mode="Markdown")
    return VIEW_SCORE_MENU

async def handle_score_menu_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text == BTN_BACK: return await show_main_menu(update, context)
    user = db.get_user(update.effective_user.id)
    
    if text == BTN_VIEW_SCORE:
        await update.message.reply_text(get_area_impact(user["area_id"]), parse_mode="Markdown")
    elif text == BTN_VIEW_TRENDS:
        await update.message.reply_text(get_area_trends(user["area_id"]), parse_mode="Markdown")
    elif text == BTN_HOW_SCORE:
        msg = (
            "📖 *How Score is Calculated*\n\n"
            "Every area starts with a base score of *100* points. Points are deducted for every open issue:\n\n"
            "💧 *Water Issue:* -10 pts\n"
            "⚡ *Electricity Issue:* -12 pts\n"
            "🗑 *Waste Issue:* -5 pts\n\n"
            "Points are restored as soon as the issue is marked as *Resolved* by the department or community volunteers."
        )
        await update.message.reply_text(msg, parse_mode="Markdown")
    return VIEW_SCORE_MENU

async def view_impact_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[BTN_MY_STATS, BTN_MY_RANK], [BTN_MY_HISTORY], [BTN_BACK]]
    await update.message.reply_text("👤 *My Impact Menu*", reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True), parse_mode="Markdown")
    return VIEW_IMPACT_MENU

async def handle_impact_menu_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text == BTN_BACK: return await show_main_menu(update, context)
    user_id = update.effective_user.id
    
    if text == BTN_MY_STATS:
        await update.message.reply_text(get_personal_impact(user_id), parse_mode="Markdown")
    elif text == BTN_MY_RANK:
        await update.message.reply_text("🏅 *Community Rank*\n\nYou are currently **#3** in your neighborhood!", parse_mode="Markdown")
    elif text == BTN_MY_HISTORY:
        reports = list(db.reports.find({"user_id": user_id}).sort("timestamp", -1).limit(5))
        msg = "📈 *Your Recent Activity*\n\n" + "\n".join([f"- {r['issue_type']} ({r['status']})" for r in reports])
        await update.message.reply_text(msg, parse_mode="Markdown")
    return VIEW_IMPACT_MENU



async def view_more_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[BTN_STATUS, BTN_LANG], [BTN_HELP], [BTN_BACK]]
    await update.message.reply_text("⚙️ *More Options*", reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True), parse_mode="Markdown")
    return VIEW_MORE

async def handle_more_menu_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text == BTN_BACK: return await show_main_menu(update, context)
    
    if text == BTN_STATUS:
        user_id = update.effective_user.id
        # Fetch last 10 reports from this user
        reports = list(db.db.reports.find({"user_id": user_id}).sort("timestamp", -1).limit(10))
        
        if not reports:
            await update.message.reply_text("🔍 You haven't reported any issues yet.", parse_mode="Markdown")
        else:
            msg = "🔍 *Your Recent Reports*\n\n"
            for r in reports:
                status_emoji = "⏳" if r["status"] == "Open" else "✅"
                date_str = r["timestamp"].strftime("%d %b")
                msg += f"{status_emoji} *{r['issue_type']}*\n   Status: {r['status']} | Date: {date_str}\n   ID: `{r.get('report_id', 'N/A')}`\n\n"
            await update.message.reply_text(msg, parse_mode="Markdown")
            
    elif text == BTN_HELP:
        await update.message.reply_text(
            "❓ *Help & Feedback*\n\nPlease type your message below. Our team will review it and get back to you.",
            reply_markup=ReplyKeyboardMarkup([[BTN_BACK]], resize_keyboard=True),
            parse_mode="Markdown"
        )
        return ENTER_HELP_MSG
    elif text == BTN_LANG:
        await update.message.reply_text("🌐 *Language Settings*\n\nEnglish is currently selected.", parse_mode="Markdown")
    else:
        await update.message.reply_text(f"Selected: {text}")
    return VIEW_MORE

async def handle_help_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text == BTN_BACK: return await view_more_menu(update, context)
    
    user = db.get_user(update.effective_user.id)
    request_data = {
        "user_id": user["user_id"],
        "name": user["name"],
        "area_name": user["area_name"],
        "message": text,
        "timestamp": datetime.datetime.now(),
        "status": "Pending"
    }
    
    db.add_support_request(request_data)
    
    await update.message.reply_text(
        "✅ *Message Sent!*\n\nThank you for your feedback. We will look into it.",
        parse_mode="Markdown"
    )
    return await show_main_menu(update, context)

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Cancelled.", reply_markup=ReplyKeyboardRemove())
    return await show_main_menu(update, context)
