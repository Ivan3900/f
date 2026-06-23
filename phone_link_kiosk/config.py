"""
Configuration for Phone Link Kiosk Launcher.
Edit these values to tune behaviour for your specific PC / Phone Link version.
"""

# ---------------------------------------------------------------------------
# Startup banner (shown right after the .exe is launched)
# ---------------------------------------------------------------------------

# Lines printed/logged on startup before the watch loop begins.
STARTUP_MESSAGE_LINES = [
    "Phone Link Kiosk Launcher",
    "Starting up - please wait...",
    "Phone Link will be locked to the foreground until it is synced.",
]

# How long (seconds) to display the banner before continuing. Set to 0 to skip.
STARTUP_HOLD_SECONDS = 30

# Print a live 'continuing in N...' countdown during the hold.
STARTUP_COUNTDOWN = True

# ---------------------------------------------------------------------------
# Launch settings
# ---------------------------------------------------------------------------

# Primary way to open Phone Link. The ms-phone: protocol is the most reliable.
PHONE_LINK_URI = "ms-phone:"

# Fallback executable name (used to detect/relaunch the underlying process).
# On modern Windows the Phone Link UI host is PhoneExperienceHost.exe.
PHONE_LINK_PROCESS = "PhoneExperienceHost.exe"

# Substrings used to identify the Phone Link top-level window by its title.
# Matching is case-insensitive and matches if ANY of these appears in the title.
WINDOW_TITLE_KEYWORDS = ["phone link", "your phone", "phone experience"]

# How long (seconds) to wait for the window to appear after launching.
WINDOW_WAIT_TIMEOUT = 25

# ---------------------------------------------------------------------------
# Kiosk / foreground loop settings
# ---------------------------------------------------------------------------

# How often (seconds) the main watch loop runs.
LOOP_INTERVAL = 0.5

# If the window disappears (user closed it), wait this long before relaunch.
RELAUNCH_DELAY = 2.0

# Keep the window always-on-top (HWND_TOPMOST).
KEEP_TOPMOST = True

# Restore the window if the user minimizes it.
DENY_MINIMIZE = True

# ---------------------------------------------------------------------------
# OCR sync-detection settings
# ---------------------------------------------------------------------------

# Run OCR every N seconds (independent of LOOP_INTERVAL, to save CPU).
OCR_INTERVAL = 2.0

# Path to the Tesseract executable. Default is the standard install location.
# If Tesseract is on your PATH you can leave this as None.
TESSERACT_CMD = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# The launcher unlocks/exits as soon as ANY of these phrases is found in the
# Phone Link window text (case-insensitive). Tune to match your UI wording.
SYNC_SUCCESS_KEYWORDS = [
    "connected",
    "synced",
    "all synced",
    "up to date",
]

# Phrases that, if present, mean we are NOT yet synced. These VETO a success
# match on the same OCR pass (e.g. "Not connected", "Connecting...").
SYNC_NEGATIVE_KEYWORDS = [
    "not connected",
    "connecting",
    "disconnected",
    "reconnecting",
    "sign in",
    "set up",
]

# Require the success keyword to be seen on this many consecutive OCR passes
# before unlocking (reduces false positives from transient text).
SYNC_CONFIRM_COUNT = 2

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

LOG_FILE = "phone_link_kiosk.log"
