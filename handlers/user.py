from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
from db.mongo import db
from utils.constants import (
    START_REG, IDLE, SELECT_RESOURCE, SELECT_ISSUE_TYPE, 
    LOCATION_MENU, ENTER_PINCODE, ENTER_LANDMARK, SELECT_LOCALITY, CONFIRM_LOC_SAVE, MANUAL_LOCATION,
    CONFIRM_REPORT, SELECT_RESOLVE_ISSUE, CONFIRM_RESOLVE, 
    VIEW_SCORE_MENU, VIEW_IMPACT_MENU, VIEW_LEADERBOARD_MENU, VIEW_MORE,
    BTN_REPORT, BTN_RESOLVE, BTN_AREA_SCORE, BTN_MY_IMPACT, BTN_LEADERBOARD, BTN_MORE,
    BTN_CANCEL, BTN_BACK, BTN_YES, BTN_HOME, RESOURCES, ISSUE_TYPES,
    BTN_LOC_PIN, BTN_LOC_SAVED, BTN_LOC_MANUAL,
    BTN_VIEW_SCORE, BTN_VIEW_TRENDS, BTN_HOW_SCORE,
    BTN_MY_STATS, BTN_MY_RANK, BTN_MY_HISTORY,
    BTN_TOP_AREAS, BTN_TOP_CONTRIBS, BTN_AREA_COMPARE,
    BTN_NUDGES, BTN_SYNC, BTN_LANG, BTN_STATUS, BTN_HELP
)
import datetime
from services.impact_service import get_area_impact, get_personal_impact, get_leaderboard, calculate_score

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
        [BTN_REPORT, BTN_RESOLVE],
        [BTN_AREA_SCORE, BTN_MY_IMPACT],
        [BTN_LEADERBOARD, BTN_MORE]
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
        keyboard = [[f"{user['area_name']} ({user.get('pincode', '560038')})"], [BTN_BACK]]
        await update.message.reply_text("Use Saved Area:", reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))
        return SELECT_LOCALITY
    elif choice == BTN_LOC_MANUAL:
        await update.message.reply_text("Enter Block / Lane / Landmark:", reply_markup=ReplyKeyboardMarkup([[BTN_BACK, BTN_CANCEL]], resize_keyboard=True))
        return MANUAL_LOCATION
    return LOCATION_MENU

async def handle_pincode_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    pin = update.message.text
    if pin == BTN_BACK: return await handle_issue_type_selection(update, context)
    if pin == BTN_CANCEL: return await show_main_menu(update, context)
    
    context.user_data["report"]["pincode"] = pin
    await update.message.reply_text(
        "Enter a nearby Landmark (e.g. Near Park, Opp. Gate 1):",
        reply_markup=ReplyKeyboardMarkup([[BTN_BACK, BTN_CANCEL]], resize_keyboard=True)
    )
    return ENTER_LANDMARK

async def handle_landmark_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    landmark = update.message.text
    if landmark == BTN_BACK: 
        await update.message.reply_text("Enter Pincode:", reply_markup=ReplyKeyboardMarkup([[BTN_BACK, BTN_CANCEL]], resize_keyboard=True))
        return ENTER_PINCODE
    if landmark == BTN_CANCEL: return await show_main_menu(update, context)
    
    context.user_data["report"]["landmark"] = landmark
    # Mock localities for demo
    localities = ["Indiranagar", "HAL 2nd Stage", "Domlur", "CV Raman Nagar"]
    keyboard = [[l] for l in localities]
    keyboard.append([BTN_BACK, BTN_CANCEL])
    await update.message.reply_text("Select Locality:", reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))
    return SELECT_LOCALITY

async def handle_locality_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    locality = update.message.text
    if locality == BTN_BACK:
        await update.message.reply_text("Enter Landmark:", reply_markup=ReplyKeyboardMarkup([[BTN_BACK, BTN_CANCEL]], resize_keyboard=True))
        return ENTER_LANDMARK
    if locality == BTN_CANCEL: return await show_main_menu(update, context)
    
    context.user_data["report"]["locality"] = locality
    context.user_data["report"]["location"] = f"{locality}, Near {context.user_data['report']['landmark']}"
    
    keyboard = [["✅ Confirm", "⬅️ Change"], [BTN_CANCEL]]
    await update.message.reply_text(f"Confirm Location: {locality}?", reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))
    return CONFIRM_LOC_SAVE

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
    old_score = calculate_score(user["area_id"])
    
    db.add_report({
        "user_id": update.effective_user.id, "area_id": user["area_id"],
        "topic_id": report_data["res_key"] + "_id", "issue_type": report_data["issue_text"],
        "location": report_data["location"], 
        "pincode": report_data.get("pincode"),
        "landmark": report_data.get("landmark"),
        "locality": report_data.get("locality"),
        "status": "Open", "timestamp": datetime.datetime.now(), "impact_value": impact_l
    })
    db.db.users.update_one({"user_id": user["user_id"]}, {"$inc": {"reports_count": 1}})
    new_score = calculate_score(user["area_id"])
    
    success_msg = f"⚠️ {report_data['issue_text']} Reported\n\n*Impact:*\n~{impact_l}L/day waste\nScore: {old_score} → {new_score}\n\n*Action:* Fix within 24 hrs"
    await update.message.reply_text(success_msg, parse_mode="Markdown")
    return await show_main_menu(update, context)

# --- ✅ RESOLVE ISSUE ---

async def initiate_resolve(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = db.get_user(update.effective_user.id)
    reports = list(db.reports.find({"area_id": user["area_id"], "status": "Open"}).limit(5))
    if not reports: return await show_main_menu(update, context)
    keyboard = [[f"#{r['report_id']} {r['issue_type']} - {r['location']}"] for r in reports]
    keyboard.append([BTN_BACK])
    await update.message.reply_text("Select Issue to Resolve:", reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))
    return SELECT_RESOLVE_ISSUE

async def handle_resolve_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text == BTN_BACK: return await show_main_menu(update, context)
    report_id = text.split(" ")[0][1:]
    report = db.db.reports.find_one({"status": "Open", "report_id": report_id})
    if not report: return SELECT_RESOLVE_ISSUE
    context.user_data["resolve_id"] = report["_id"]
    await update.message.reply_text(f"Confirm Resolution: {text}?", reply_markup=ReplyKeyboardMarkup([["✅ Mark Resolved", BTN_CANCEL], [BTN_BACK]], resize_keyboard=True))
    return CONFIRM_RESOLVE

async def handle_resolve_final(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text == BTN_CANCEL: return await show_main_menu(update, context)
    if update.message.text == BTN_BACK: return await initiate_resolve(update, context)
    
    user_id = update.effective_user.id
    report_id = context.user_data["resolve_id"]
    report = db.db.reports.find_one({"_id": report_id})
    old_score = calculate_score(db.get_user(user_id)["area_id"])
    db.resolve_report(report_id, user_id)
    db.db.users.update_one({"user_id": user_id}, {"$inc": {"resolved_count": 1}})
    new_score = calculate_score(db.get_user(user_id)["area_id"])
    
    impact_text = f"💧 Water Saved: ~{report.get('impact_value', 0)}L/day" if "water" in report["topic_id"] else "🗑 Waste Reduced"
    await update.message.reply_text(f"✔ *Issue Resolved*\n\n{impact_text}\nScore: {old_score} → {new_score}\n\n👏 Good job!", parse_mode="Markdown")
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
        await update.message.reply_text("📈 *Trend Analysis*\n\nYour area score improved by 12% last week!", parse_mode="Markdown")
    elif text == BTN_HOW_SCORE:
        await update.message.reply_text("📖 *How Scoring Works*\n\n- Resolve Issue: +15 points\n- New Report: -10 points\n- Zero leaks for 24h: +20 bonus", parse_mode="Markdown")
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

async def view_leaderboard_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[BTN_TOP_AREAS, BTN_TOP_CONTRIBS], [BTN_AREA_COMPARE], [BTN_BACK]]
    await update.message.reply_text("🏆 *Leaderboard Menu*", reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True), parse_mode="Markdown")
    return VIEW_LEADERBOARD_MENU

async def handle_leaderboard_menu_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text == BTN_BACK: return await show_main_menu(update, context)
    
    if text == BTN_TOP_AREAS:
        await update.message.reply_text(get_leaderboard(), parse_mode="Markdown")
    elif text == BTN_TOP_CONTRIBS:
        await update.message.reply_text("👤 *Top Contributors*\n\n1. John Doe (15 fixed)\n2. Sarah Smith (12 fixed)", parse_mode="Markdown")
    elif text == BTN_AREA_COMPARE:
        await update.message.reply_text("📊 *Area Comparison*\n\nIndiranagar is 15% more efficient than Koramangala this month!", parse_mode="Markdown")
    return VIEW_LEADERBOARD_MENU

async def view_more_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[BTN_NUDGES, BTN_SYNC], [BTN_LANG, BTN_STATUS], [BTN_HELP], [BTN_BACK]]
    await update.message.reply_text("⚙️ *More Options*", reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True), parse_mode="Markdown")
    return VIEW_MORE

async def handle_more_menu_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text == BTN_BACK: return await show_main_menu(update, context)
    
    if text == BTN_NUDGES:
        await update.message.reply_text("📢 *Nudge Notifications: ON*", parse_mode="Markdown")
    elif text == BTN_HELP:
        await update.message.reply_text("❓ *Help Center*\n\nContact support at @EcoTrackSupportBot", parse_mode="Markdown")
    else:
        await update.message.reply_text(f"Selected: {text}")
    return VIEW_MORE

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Cancelled.", reply_markup=ReplyKeyboardRemove())
    return await show_main_menu(update, context)
