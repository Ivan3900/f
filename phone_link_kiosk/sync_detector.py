"""
OCR-based "connected & synced" detector for the Phone Link window.

Captures the window region as an image, runs Tesseract OCR over it, and
decides whether Phone Link is in the synced state based on the keyword
lists in config.py.

WINDOWS ONLY (depends on the captured screen and Tesseract install).
"""

import pytesseract
from PIL import ImageGrab

import config
import window_utils


# Point pytesseract at the Tesseract executable if a path is configured.
if config.TESSERACT_CMD:
    pytesseract.pytesseract.tesseract_cmd = config.TESSERACT_CMD


def capture_window_text(hwnd: int) -> str:
    """
    Screenshot the Phone Link window and OCR it to plain text.

    Note: the window must be in the foreground / not occluded for an
    accurate capture, which the kiosk loop already guarantees.
    """
    left, top, right, bottom = window_utils.get_window_rect(hwnd)
    # Guard against zero-size / off-screen rects.
    if right <= left or bottom <= top:
        return ""

    image = ImageGrab.grab(bbox=(left, top, right, bottom))
    try:
        text = pytesseract.image_to_string(image)
    except Exception as exc:  # Tesseract missing / misconfigured
        raise RuntimeError(
            "Tesseract OCR failed. Check that Tesseract is installed and "
            "config.TESSERACT_CMD points to tesseract.exe. Original: %s" % exc
        )
    return text.lower()


def is_synced(text: str) -> bool:
    """
    Decide sync state from OCR text.

    A negative keyword (e.g. 'connecting', 'not connected') vetoes the pass.
    Otherwise any success keyword counts as synced.
    """
    if not text:
        return False

    for neg in config.SYNC_NEGATIVE_KEYWORDS:
        if neg in text:
            return False

    return any(pos in text for pos in config.SYNC_SUCCESS_KEYWORDS)
