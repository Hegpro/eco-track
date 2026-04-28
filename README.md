# 🌿 Eco-Track: Resource Management Bot & Dashboard

Eco-Track is a comprehensive solution designed for hackathons to monitor and manage resource usage (Water, Electricity, Waste) within communities. It combines a user-friendly Telegram Bot for reporting with a premium web-based Admin Dashboard for real-time analysis.

## 🚀 Features

### 📱 Telegram Bot
- **Seamless Registration**: Context-aware area selection.
- **Reporting Interface**: Easy-to-use menus for reporting daily resource usage.
- **Impact Insights**: Instantly view aggregated data for your area with health indicators.
- **Admin Commands**: In-bot tools for managing areas and topics.

### 📊 Admin Dashboard
- **Real-time Monitoring**: Stunning dark-mode interface showing live system stats.
- **Activity Feed**: Detailed view of all incoming reports across different areas.
- **Scalable Architecture**: Built with FastAPI and MongoDB for high concurrency.

## 🛠 Tech Stack
- **Backend**: Python 3.12, FastAPI
- **Interface**: `python-telegram-bot` (v20+)
- **Database**: MongoDB (Local/Atlas)
- **Frontend**: Vanilla CSS3, Semantic HTML5, JavaScript (ES6)

## 🏁 Getting Started

### Prerequisites
- Python 3.12+
- MongoDB installed locally (default: `localhost:27017`)

### Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/such3/team-lifo.git
   cd eco-track
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Configure environment:
   ```bash
   cp .env.example .env
   # Edit .env with your BOT_TOKEN
   ```

### Running the Project
Launch both the bot and dashboard simultaneously:
```bash
python run.py
```
- Dashboard: [http://localhost:8000](http://localhost:8000)
- Bot: Open your bot on Telegram and send `/start`.

## 📂 Project Structure
- `/handlers`: Telegram bot event handlers.
- `/services`: Business logic for impact calculation and admin tasks.
- `/db`: MongoDB connection and schema management.
- `/dashboard`: FastAPI web server and frontend assets.
- `seed.py`: Utility to initialize database with areas and topics.

## 🤝 Contributing
1. Create a feature branch (`git checkout -b feature/amazing-feature`).
2. Commit your changes (`git commit -m 'Add amazing feature'`).
3. Push to the branch (`git push origin feature/amazing-feature`).
4. Open a Pull Request.

---
Built by **Team LIFO** for the Srishti Hackathon.
