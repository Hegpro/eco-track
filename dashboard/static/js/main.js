console.log("Eco-Track Dashboard Initialized");

// Auto-refresh stats every 30 seconds
async function updateStats() {
    try {
        const response = await fetch('/api/stats');
        const data = await response.json();
        console.log("Stats updated:", data);
        // We could update the UI here without refreshing, 
        // but for a simple MVP, page refresh is also an option.
    } catch (error) {
        console.error("Error updating stats:", error);
    }
}

setInterval(updateStats, 30000);
