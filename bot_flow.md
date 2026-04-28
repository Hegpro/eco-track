# 📱 Eco-Track Bot: Final Production Menu Catalog

This document provides a comprehensive map of the Eco-Track Telegram bot's menu structure, sub-options, and step-by-step flows.

---

## 🏁 1. MAIN MENU (Home Screen)
Visible after successful registration or typing `/start`.

*   **📊 Report Issue**: Initiates the incident reporting wizard.
*   **✅ Resolve Issue**: Browse and fix community incidents.
*   **🌿 Area Score**: View localized sustainability performance.
*   **👤 My Impact**: Personal stats and rank tracking.
*   **🏆 Leaderboard**: Competitive view of areas and contributors.
*   **⚙️ More**: Advanced options and settings.

---

## 📊 2. REPORT ISSUE (Step-by-Step Flow)

### Step 1 — Select Category
*   `💧 Water`
*   `⚡ Electricity`
*   `🗑 Waste`
*   `❌ Cancel`

### Step 2 — Select Issue Type (Contextual)
*   **Water**: `Leak 💧`, `Overflow 🌊`, `Misuse 🚿`, `Other ❓`.
*   **Electricity**: `Light Left On 💡`, `Illegal Usage ⚡`, `Overuse 🔌`, `Other ❓`.
*   **Waste**: `Garbage Pile 🗑`, `No Segregation ♻️`, `Overflow Bin 🚮`, `Other ❓`.
*   `⬅️ Back` | `❌ Cancel`

### Step 3 — Location Wizard
1.  **Select Method**:
    *   `📍 Enter Pincode`: Manual pincode entry.
    *   `📍 Use Saved Area`: Pulls registered area.
    *   `✏️ Enter Manually`: Quick landmark/landmark entry.
2.  **Pincode Sequence** (if selected):
    *   **Input**: Enter 6-digit Pincode.
    *   **Input**: Enter nearby **Landmark** (e.g. *Near Main Gate*).
    *   **Selection**: Pick **Locality** from list (e.g. *Indiranagar*, *HAL*).
3.  **Final Confirmation**:
    *   `✅ Confirm` | `⬅️ Change` | `❌ Cancel`
    *   `✅ Save for Future` | `❌ Skip`

### Step 4 — Final Submission
*   `✅ Submit` | `⬅️ Back` | `❌ Cancel`

---

## ✅ 3. RESOLVE ISSUE FLOW
1.  **Select Issue**: Browse last 5 open incidents (e.g., *#101 Water Leak - Block A*).
2.  **Confirm**:
    *   `✅ Mark Resolved` | `⬅️ Back` | `❌ Cancel`
3.  **Success Output**: Shows resources saved and community score improvement.

---

## 🌿 4. AREA SCORE SUB-MENU
*   **📊 View Score**: Real-time score (0-100) and issue breakdown.
*   **📈 View Trends**: Visual indicators of performance over time.
*   **❓ How Score Works**: Explanation of point deductions and rewards.
*   `⬅️ Back`

---

## 👤 5. MY IMPACT SUB-MENU
*   **📊 My Stats**: Count of reports, resolutions, and estimated resources saved.
*   **🏅 My Rank**: Your standing in the community leaderboard.
*   **📈 My History**: Quick list of your last 5 submissions.
*   `⬅️ Back`

---

## 🏆 6. LEADERBOARD SUB-MENU
*   **🏘 Top Areas**: Ranking of neighborhood blocks by sustainability score.
*   **👤 Top Contributors**: Hall of fame for most active users/resolvers.
*   **📊 Area Comparison**: Performance side-by-side.
*   `⬅️ Back`

---

## ⚙️ 7. MORE MENU
*   **📢 Daily Updates**: Toggle community nudge notifications.
*   **📴 Offline Sync**: Sync reports queued during connectivity drops.
*   **🌐 Change Language**: Toggle between English and local languages.
*   **🔍 Report Status**: Detailed lookup of any report ID.
*   **❓ Help**: FAQ and support info.
*   `⬅️ Back`

---

## 🔁 8. GLOBAL NAVIGATION
These buttons are standard across all wizards and sub-menus:
*   `⬅️ Back`: Return to the previous screen.
*   `❌ Cancel`: Exit the current process and return to Home.
*   `🏠 Home`: Jump directly to the Main Menu.
