# OAuth Routes for Google Authentication
# Handles the login flow for Google Calendar access

from fastapi import APIRouter
from fastapi.responses import RedirectResponse
from integrations.google_calendar import (
    get_authorization_url,
    exchange_code_for_tokens,
    is_authenticated
)

router = APIRouter(prefix="/auth")


@router.get("/login")
def login():
    """
    Start the Google OAuth flow.

    When user visits /auth/login:
    1. We generate a Google authorization URL
    2. We redirect them to Google's login page
    3. User logs in and grants permission
    4. Google redirects back to /auth/callback
    """
    auth_url = get_authorization_url()
    # RedirectResponse sends the browser to Google's login page
    return RedirectResponse(url=auth_url)


@router.get("/callback")
def callback(code: str):
    """
    Handle the OAuth callback from Google.

    After user grants permission, Google redirects here with:
    /auth/callback?code=ABC123XYZ

    Args:
        code: Authorization code from Google (FastAPI extracts this from URL)

    We then:
    1. Exchange the code for access/refresh tokens
    2. Save tokens to token.json
    3. Redirect to frontend (or show success message)
    """
    # Exchange the code for tokens
    tokens = exchange_code_for_tokens(code)

    # For now, just return success message
    # In production, you'd redirect to the frontend
    return {
        "status": "success",
        "message": "Google Calendar connected! You can close this window.",
        "authenticated": True
    }


@router.get("/status")
def auth_status():
    """
    Check if Google Calendar is connected.

    Returns:
        {"authenticated": true/false}
    """
    return {"authenticated": is_authenticated()}
