# Mood Engine analyzes calendar to determine availability + become "mood-aware"

from datetime import datetime
import pytz
from integrations.google_calendar import get_todays_events, is_authenticated

#Default timezone
USER_TIMEZONE = pytz.timezone("America/Los_Angeles")

class MoodEngine:
    """
    Analyzes calendar events to determine professional state.

    Outputs:
        - availability: "busy" | "focused" | "open" | "winding_down"
        - energy_estimate: "high" | "medium" | "low"
        - best_contact_method: "async" | "quick_sync" | "deep_discussion"
        - suggested_wait_time: "now" | "30min" | "end_of_day" | "tomorrow"
        - context_summary: Human-readable explanation
    """

    def get_status(self) -> dict:
        """
        Get current availability status based on calendar.

        Returns:
            dict with availability, energy, best_contact, wait_time, summary
        """
        #Calendar auth check
        if not is_authenticated():
            return {
                "availability": "unknown",
                "energy_estimate": "unknown",
                "best_contact_method": "async",
                "suggested_wait_time": "unknown",
                "context_summary": "Calendar not connected. Connect Google Calendar for availability info.",
                "meeting_count": 0,
                "in_meeting": False,
            }

        #Get today's events
        events = get_todays_events()

        #Analyze calendar
        analysis = self._analyze_calendar(events)

        return analysis

    def _analyze_calendar(self, events: list[dict]) -> dict:
        """
        Analyze calendar events to determine state.

        Logic:
        - 0-2 meetings: Light day → Open
        - 3-4 meetings: Moderate day → Focused
        - 5+ meetings: Heavy day → Busy
        - Currently in meeting: Busy
        - Time of day affects energy estimate
        """

        meeting_count = len(events)
        current_hour = datetime.now(USER_TIMEZONE).hour  # Use user's timezone

        #Check if in meeting
        in_meeting = any(event.get("is_now", False) for event in events)

        #Count remaining meetings 
        meetings_remaining = sum(1 for event in events if not event.get("is_past", False))

        #Availability logic
        if in_meeting:
            availability = "busy"
            best_contact = "async"
            wait_time = "30min"
            summary = "Currently in a meeting. Best to send an async message."
        elif meeting_count == 0:
            availability = "open"
            best_contact = "deep_discussion"
            wait_time = "now"
            summary = "Calendar is clear today. Great time for a longer conversation."
        elif meeting_count <= 2:
            availability = "open"
            best_contact = "quick_sync"
            wait_time = "now"
            summary = f"Light day with {meeting_count} meeting(s). Good time to connect."
        elif meeting_count <= 4:
            availability = "focused"
            best_contact = "quick_sync"
            wait_time = "30min"
            summary = f"Moderate day with {meeting_count} meetings. Quick sync is fine."
        else:
            availability = "busy"
            best_contact = "async"
            wait_time = "end_of_day"
            summary = f"Heavy day with {meeting_count} meetings. Async communication preferred."

        # Determine energy based on time of day
        if 9 <= current_hour < 12:
            energy = "high"
            summary += " Morning energy is typically high."
        elif 12 <= current_hour < 14:
            energy = "medium"
            summary += " Post-lunch energy dip."
        elif 14 <= current_hour < 16:
            energy = "medium"
            summary += " Afternoon work mode."
        elif current_hour >= 16:
            availability = "winding_down"
            energy = "low"
            summary = "End of workday. Best to reach out tomorrow morning."
        else:
            energy = "medium"

        return {
            "availability": availability,
            "energy_estimate": energy,
            "best_contact_method": best_contact,
            "suggested_wait_time": wait_time,
            "context_summary": summary,
            "meeting_count": meeting_count,
            "meetings_remaining": meetings_remaining,
            "in_meeting": in_meeting,
            "events": events,
        }
