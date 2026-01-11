"""
Triage logic for determining severity levels and emergency detection
"""

SEVERITY_LEVELS = {
    "Critical": (9, 10),  # Immediate ER
    "High": (7, 8),       # Urgent care within 1 hour
    "Medium": (4, 6),     # Appointment within 24 hours
    "Low": (1, 3)         # Self-care guidance
}

EMERGENCY_KEYWORDS = [
    "chest pain", "difficulty breathing", "can't breathe", "choking",
    "severe pain", "unconscious", "severe bleeding", "heart attack",
    "stroke", "seizure", "severe allergic reaction", "overdose"
]


def get_severity_level(severity_score: float) -> str:
    """Convert severity score to level"""
    for level, (min_score, max_score) in SEVERITY_LEVELS.items():
        if min_score <= severity_score <= max_score:
            return level
    return "Medium"


def is_emergency(text: str, severity_score: float) -> bool:
    """Check if the case is an emergency"""
    text_lower = text.lower()
    
    # Check for emergency keywords
    for keyword in EMERGENCY_KEYWORDS:
        if keyword in text_lower:
            return True
    
    # Check severity score
    if severity_score >= 9:
        return True
    
    return False


def get_care_recommendation(severity_level: str) -> str:
    """Get care recommendation based on severity level"""
    recommendations = {
        "Critical": "Please go to the emergency room immediately or call 911.",
        "High": "Please visit urgent care within the next hour.",
        "Medium": "Schedule an appointment within 24 hours.",
        "Low": "You can manage this at home with self-care. Monitor your symptoms."
    }
    return recommendations.get(severity_level, recommendations["Medium"])

