# Conversation States
(
    START_REG, IDLE, SELECT_RESOURCE, SELECT_ISSUE_TYPE, 
    LOCATION_MENU, ENTER_PINCODE, ENTER_LANDMARK, CONFIRM_LOC_SAVE, MANUAL_LOCATION,
    CONFIRM_REPORT, 
    VIEW_SCORE_MENU, VIEW_IMPACT_MENU, VIEW_MORE,
    SELECT_POST_OFFICE, ENTER_HELP_MSG
) = range(15)

# Main Menu Buttons
BTN_REPORT = "📊 Report Issue"
BTN_AREA_SCORE = "🌿 Area Score"
BTN_MY_IMPACT = "👤 My Impact"
BTN_MORE = "⚙️ More"

# Common Buttons
BTN_CANCEL = "❌ Cancel"
BTN_BACK = "⬅️ Back"
BTN_YES = "✅ Yes"
BTN_HOME = "🏠 Home"

# Location Menu Buttons
BTN_LOC_PIN = "📍 Enter Pincode"
BTN_LOC_SAVED = "📍 Use Saved Area"
BTN_LOC_MANUAL = "✏️ Enter Manually"

# Sub-menu Buttons
BTN_VIEW_SCORE = "📊 View Score"
BTN_VIEW_TRENDS = "📈 View Trends"
BTN_HOW_SCORE = "❓ How Score Works"

BTN_MY_STATS = "📊 My Stats"
BTN_MY_RANK = "🏅 My Rank"
BTN_MY_HISTORY = "📈 My History"

# More Menu Buttons
BTN_LANG = "🌐 Change Language"
BTN_STATUS = "🔍 Report Status"
BTN_HELP = "❓ Help"

# Resources & Issues
RESOURCES = {"water": "💧 Water", "electricity": "⚡ Electricity", "sewage": "🗑 Waste"}
ISSUE_TYPES = {
    "water": ["Leak 💧", "Overflow 🌊", "Misuse 🚿", "Other ❓"],
    "electricity": ["Light Left On 💡", "Illegal Usage ⚡", "Overuse 🔌", "Other ❓"],
    "sewage": ["Garbage Pile 🗑", "No Segregation ♻️", "Overflow Bin 🚮", "Other ❓"]
}
