# Status Endpoint - Returns current availability/mood
# This powers the "Current State" panel in the UI

from fastapi import APIRouter
from engines.mood_engine import MoodEngine

router = APIRouter(prefix="/api")

# Initialize mood engine once
mood_engine = MoodEngine()


@router.get("/status")
def get_status():
    """
    Get current professional status based on calendar.

    Returns:
        {
            "availability": "open" | "focused" | "busy" | "winding_down",
            "energy_estimate": "high" | "medium" | "low",
            "best_contact_method": "async" | "quick_sync" | "deep_discussion",
            "suggested_wait_time": "now" | "30min" | "end_of_day" | "tomorrow",
            "context_summary": "Human readable explanation",
            "meeting_count": 3,
            "in_meeting": false,
            "events": [...]
        }
    """
    return mood_engine.get_status()
