# Google Slides Integration
# This module fetches presentation content from a specific Google Drive folder

from googleapiclient.discovery import build

# Import credentials function from our calendar module (reuse the same auth)
from integrations.google_calendar import get_credentials, is_authenticated

# Your "Viven AI" folder ID from Google Drive
# This scopes the integration to only look at files in this folder
VIVEN_FOLDER_ID = "1aTjCY_oZDNu-lJF4GUYuGT8529rf-O5E"


def list_presentations() -> list[dict]:
    """
    List all Google Slides presentations in the Viven AI folder.

    Returns:
        List of dicts with 'id', 'name' for each presentation

    Example return:
        [
            {"id": "1abc123...", "name": "Viven Pitch Deck"},
            {"id": "2def456...", "name": "Q4 KPIs"},
        ]

    How it works:
        1. Connect to Google Drive API using our saved credentials
        2. Query for files where:
           - Parent folder is VIVEN_FOLDER_ID
           - MIME type is Google Slides presentation
        3. Return list of matching files
    """
    # Check if user is authenticated
    if not is_authenticated():
        print("Not authenticated. Please login first.")
        return []

    # Get saved credentials (same ones used for Calendar)
    credentials = get_credentials()

    # Build Google Drive API service
    # 'drive' = API name, 'v3' = version
    drive_service = build("drive", "v3", credentials=credentials)

    # Query for Google Slides files in our specific folder
    # q = query string using Drive's query syntax
    # - 'parents' contains folder ID = file is in that folder
    # - mimeType = only get Google Slides presentations
    query = f"'{VIVEN_FOLDER_ID}' in parents and mimeType='application/vnd.google-apps.presentation'"

    # Execute the query
    results = drive_service.files().list(
        q=query,                    # Our search query
        fields="files(id, name)",   # Only return these fields (id and name)
        pageSize=100,               # Max results (probably won't have 100 slides)
    ).execute()

    # Extract the files list
    files = results.get("files", [])

    # Format as simple dicts
    presentations = []
    for file in files:
        presentations.append({
            "id": file["id"],
            "name": file["name"],
        })

    return presentations


def get_presentation_content(presentation_id: str) -> dict:
    """
    Extract all text content from a Google Slides presentation.

    Args:
        presentation_id: The ID of the presentation (from list_presentations)

    Returns:
        Dict with:
            - 'title': Presentation title
            - 'slides': List of slide content dicts

    Example return:
        {
            "title": "Viven Pitch Deck",
            "slides": [
                {"slide_number": 1, "title": "Welcome", "body": "Introduction to Viven..."},
                {"slide_number": 2, "title": "Problem", "body": "The market needs..."},
            ]
        }

    How it works:
        1. Connect to Google Slides API
        2. Fetch the presentation data (all slides, all elements)
        3. Parse each slide to extract text from shapes/text boxes
        4. Return structured content
    """
    if not is_authenticated():
        print("Not authenticated. Please login first.")
        return {}

    credentials = get_credentials()

    # Build Google Slides API service
    # 'slides' = API name, 'v1' = version
    slides_service = build("slides", "v1", credentials=credentials)

    # Fetch the entire presentation
    # This returns a complex object with all slides, shapes, text, etc.
    presentation = slides_service.presentations().get(
        presentationId=presentation_id
    ).execute()

    # Get presentation title
    title = presentation.get("title", "Untitled Presentation")

    # Extract content from each slide
    slides_content = []

    # Loop through each slide in the presentation
    for slide_index, slide in enumerate(presentation.get("slides", []), start=1):
        # Each slide has "pageElements" = shapes, text boxes, images, etc.
        page_elements = slide.get("pageElements", [])

        # We'll collect all text from this slide
        slide_title = ""
        slide_body_parts = []

        # Loop through each element on the slide
        for element in page_elements:
            # Check if this element is a shape (text box, title, etc.)
            shape = element.get("shape")
            if not shape:
                continue  # Skip non-shape elements (like images)

            # Get the text content from the shape
            text_content = extract_text_from_shape(shape)

            if not text_content:
                continue  # Skip empty shapes

            # Determine if this is a title or body text
            # Google Slides marks titles with specific placeholder types
            placeholder = shape.get("placeholder", {})
            placeholder_type = placeholder.get("type", "")

            # TITLE, CENTERED_TITLE, SUBTITLE are title-ish
            if placeholder_type in ["TITLE", "CENTERED_TITLE"]:
                slide_title = text_content
            else:
                # Everything else is body content
                slide_body_parts.append(text_content)

        # Combine body parts into one string
        slide_body = "\n".join(slide_body_parts)

        # Add this slide's content to our list
        slides_content.append({
            "slide_number": slide_index,
            "title": slide_title,
            "body": slide_body,
        })

    return {
        "title": title,
        "slides": slides_content,
    }


def extract_text_from_shape(shape: dict) -> str:
    """
    Extract plain text from a Google Slides shape object.

    Args:
        shape: The shape dict from the Slides API

    Returns:
        Plain text string with all text from the shape

    How it works:
        Google Slides stores text in a nested structure:
        shape → text → textElements → textRun → content

        We dig through this structure to get the actual text.
    """
    # Get the text object from the shape
    text = shape.get("text")
    if not text:
        return ""

    # Text is made up of "textElements" (paragraphs, runs, etc.)
    text_elements = text.get("textElements", [])

    # Collect all text content
    text_parts = []

    for element in text_elements:
        # Each element might have a "textRun" with actual content
        text_run = element.get("textRun")
        if text_run:
            content = text_run.get("content", "")
            # Clean up the text (remove extra whitespace)
            content = content.strip()
            if content:
                text_parts.append(content)

    # Join all parts with spaces
    return " ".join(text_parts)


def get_all_slides_content() -> list[dict]:
    """
    Convenience function: Get content from ALL presentations in the Viven folder.

    Returns:
        List of presentation content dicts (same format as get_presentation_content)

    This is what the ingest script will call to get everything at once.
    """
    all_content = []

    # First, list all presentations
    presentations = list_presentations()

    print(f"Found {len(presentations)} presentation(s) in Viven AI folder:")
    for pres in presentations:
        print(f"  - {pres['name']}")

    # Then, get content from each one
    for pres in presentations:
        print(f"\nExtracting content from: {pres['name']}...")
        content = get_presentation_content(pres["id"])
        content["source_name"] = pres["name"]  # Add the file name
        all_content.append(content)

    return all_content
