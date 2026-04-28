from telegram import Update
from telegram.ext import ContextTypes
import config
from services import admin_service
from db.mongo import db

def is_admin(user_id):
    return user_id in config.ADMIN_IDS

async def admin_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("⛔ Access Denied. Admins only.")
        return

    msg = (
        "🛠 *Admin Menu*\n\n"
        "/add\_staff <tg_id> <name> <dept_id>\n"
        "(dept_ids: electrical_id, sewage_id, plumbing_id)"
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

async def handle_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): return
    
    if not context.args:
        await update.message.reply_text("Usage: /broadcast <message>")
        return
        
    message = " ".join(context.args)
    users = admin_service.get_users_in_area() # All users
    
    count = 0
    for user in users:
        try:
            await context.bot.send_message(
                chat_id=user["user_id"], 
                text=f"📢 *GLOBAL ANNOUNCEMENT*\n\n{message}", 
                parse_mode="Markdown"
            )
            count += 1
        except Exception:
            pass
            
    await update.message.reply_text(f"✅ Broadcast sent to {count} users.")

async def handle_add_staff(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): return
    if len(context.args) < 3:
        await update.message.reply_text("Usage: /add_staff <tg_id> <name> <dept_id>")
        return
    
    tg_id = int(context.args[0])
    name = context.args[1]
    dept_id = context.args[2]
    
    db.add_staff({
        "user_id": tg_id,
        "name": name,
        "dept_id": dept_id
    })
    await update.message.reply_text(f"✅ Added {name} as staff for {dept_id}!")
