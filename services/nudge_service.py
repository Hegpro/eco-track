from db.mongo import db
from services.impact_service import calculate_score
import asyncio
from telegram import Bot
import config

async def send_daily_nudges(bot: Bot):
    areas = list(db.areas.find())
    for area in areas:
        area_id = area["area_id"]
        score = calculate_score(area_id)
        
        # Determine status and message
        status_msg = ""
        if score < 75:
            status_msg = (
                f"📢 *Daily Community Update*\n\n"
                f"🏘 Area: {area['area_name']}\n"
                f"⭐ Current Score: {score}/100 (⚠️ Needs Improvement)\n\n"
                "Action needed: Several open issues are affecting our community score. "
                "Check the app to help resolve them!"
            )
        else:
            status_msg = (
                f"📢 *Daily Community Update*\n\n"
                f"🏘 Area: {area['area_name']}\n"
                f"⭐ Current Score: {score}/100 (✅ Doing Great!)\n\n"
                "Thank you for keeping our neighborhood sustainable!"
            )
            
        # Send to all users in this area
        users = list(db.users.find({"area_id": area_id}))
        for user in users:
            try:
                await bot.send_message(
                    chat_id=user["user_id"],
                    text=status_msg,
                    parse_mode="Markdown"
                )
            except Exception:
                pass

if __name__ == "__main__":
    # For testing independently
    import sys
    from telegram.ext import ApplicationBuilder
    
    async def test():
        app = ApplicationBuilder().token(config.BOT_TOKEN).build()
        await send_daily_nudges(app.bot)
        
    asyncio.run(test())
