from telegram import Update
from telegram.ext import ContextTypes
import config
from services import admin_service

def is_admin(user_id):
    return user_id in config.ADMIN_IDS

async def admin_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("⛔ Access Denied. Admins only.")
        return

    msg = (
        "🛠 *Admin Menu*\n\n"
        "/add\_area <name> <pincode>\n"
        "/add\_topic <name> <unit>\n"
        "/view\_reports\n"
        "/send\_nudge <topic_id> <message>"
    )
    await update.message.reply_text(msg, parse_mode="Markdown")

async def handle_add_area(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): return
    
    if len(context.args) < 2:
        await update.message.reply_text("Usage: /add_area <name> <pincode>")
        return
        
    pincode = context.args[-1]
    name = " ".join(context.args[:-1])
    
    admin_service.add_area(name, pincode)
    await update.message.reply_text(f"✅ Area '{name}' added successfully!")

async def handle_add_topic(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): return
    
    if len(context.args) < 2:
        await update.message.reply_text("Usage: /add_topic <name> <unit>")
        return
        
    unit = context.args[-1]
    name = " ".join(context.args[:-1])
    
    admin_service.add_topic(name, unit)
    await update.message.reply_text(f"✅ Topic '{name}' added successfully!")

async def handle_view_reports(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): return
    
    reports = admin_service.get_all_reports(10)
    if not reports:
        await update.message.reply_text("No reports found.")
        return
        
    msg = "📋 *Recent Reports*\n\n"
    for r in reports:
        msg += f"👤 User: {r['user_id']}\n📍 Area: {r['area_id']}\n🔹 {r['topic_id']}: {r['quantity']}\n⏰ {r['timestamp'].strftime('%H:%M')}\n---\n"
        
    await update.message.reply_text(msg, parse_mode="Markdown")

async def handle_send_nudge(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): return
    
    if len(context.args) < 2:
        await update.message.reply_text("Usage: /send_nudge <topic_id> <message>")
        return
        
    topic_id = context.args[0]
    message = " ".join(context.args[1:])
    
    users = admin_service.get_users_in_area() # For now, nudge all
    count = 0
    for user in users:
        try:
            await context.bot.send_message(chat_id=user["user_id"], text=f"🔔 *NUDGE:* {message}", parse_mode="Markdown")
            count += 1
        except Exception:
            pass
            
    await update.message.reply_text(f"✅ Nudge sent to {count} users.")
