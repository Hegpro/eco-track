import re

KEYWORDS = {
    "water_id": ["water", "leak", "tap", "overflow", "pipe", "tank", "💧"],
    "electricity_id": ["electricity", "light", "power", "fan", "switch", "meter", "⚡"],
    "waste_id": ["waste", "garbage", "trash", "dustbin", "litter", "dump", "🗑"]
}

ISSUE_MAP = {
    "leak": "Leak",
    "overflow": "Overflow",
    "misuse": "Misuse",
    "light": "Misuse",
    "garbage": "Other",
    "trash": "Other"
}

def classify_text(text):
    text = text.lower()
    
    detected_topic = None
    for topic_id, words in KEYWORDS.items():
        if any(word in text for word in words):
            detected_topic = topic_id
            break
            
    detected_issue = "Other"
    for word, issue_type in ISSUE_MAP.items():
        if word in text:
            detected_issue = issue_type
            break
            
    # Quantity detection
    qty = "Unknown"
    qty_match = re.search(r"(\d+)\s*(taps|leaks|lights|fans|bags)", text)
    if qty_match:
        qty = f"{qty_match.group(1)} {qty_match.group(2)}"
        
    # Urgency detection
    urgency = "Normal"
    if any(word in text for word in ["urgent", "emergency", "immediately", "asap", "flowing"]):
        urgency = "High"
            
    return detected_topic, detected_issue, qty, urgency

def extract_location(text):
    # Basic regex for Block/Lane/Area
    match = re.search(r"(block [a-z0-9]|lane [a-z0-9]|area [a-z0-9]|gate|temple|park)", text.lower())
    if match:
        return match.group(0).upper()
    return "Unknown Location"
