"""
Phone Link Kiosk Launcher - main entry point.

Flow:
  1. Launch Phone Link (ms-phone: protocol).
  2. Find its window; bring to foreground + topmost.
  3. Watch loop: restore if minimized, relaunch if closed, hold focus.
  4. Periodically OCR the window for the "connected & synced" indicator.
  5. On confirmed sync: release topmost lock, stop, exit cleanly.

Lock policy (per user choice): practical kiosk hold =
  always-on-top + deny minimize + auto-relaunch. No timeout: holds until
  sync is detected.

WINDOWS ONLY. Build into an .exe with PyInstaller (see README.md).
"""

import os
import sys
import time
import logging
import subprocess

import config
import window_utils
import sync_detector


def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.FileHandler(config.LOG_FILE, encoding="utf-8"),
            logging.StreamHandler(sys.stdout),
        ],
    )


def launch_phone_link():
    """Open Phone Link via the ms-phone: protocol."""
    logging.info("Launching Phone Link via %s", config.PHONE_LINK_URI)
    try:
        os.startfile(config.PHONE_LINK_URI)  # noqa: S606 (Windows only)
    except Exception:
        # Fallback: use the shell 'start' command.
        subprocess.run(["cmd", "/c", "start", "", config.PHONE_LINK_URI],
                       shell=False)


def ensure_window():
    """Return a live Phone Link hwnd, launching/relaunching as needed."""
    hwnd = window_utils.find_phone_link_window()
    if hwnd:
        return hwnd

    logging.info("Phone Link window not found. Launching...")
    launch_phone_link()
    hwnd = window_utils.wait_for_window()
    if not hwnd:
        logging.warning("Window did not appear within timeout; will retry.")
    return hwnd


def enforce_kiosk(hwnd):
    """Apply one pass of the kiosk rules to the window."""
    if config.DENY_MINIMIZE and window_utils.is_minimized(hwnd):
        logging.info("Window minimized - restoring.")
        window_utils.restore_window(hwnd)

    if config.KEEP_TOPMOST:
        window_utils.set_topmost(hwnd, True)

    window_utils.force_foreground(hwnd)


def release_lock(hwnd):
    """Undo the topmost pin so the window behaves normally again."""
    try:
        if hwnd and config.KEEP_TOPMOST:
            window_utils.set_topmost(hwnd, False)
    except Exception:
        pass


def show_startup_banner():
    """
    Print the startup message and hold for STARTUP_HOLD_SECONDS before the
    watch loop begins. Shows a live countdown if enabled.

    NOTE: this prints to the console. If you build with --noconsole, the
    text won't be visible (but the hold still happens). To SEE it, build
    without --noconsole or run `python main.py`.
    """
    for line in config.STARTUP_MESSAGE_LINES:
        logging.info(line)

    hold = config.STARTUP_HOLD_SECONDS
    if hold <= 0:
        return

    if config.STARTUP_COUNTDOWN:
        for remaining in range(hold, 0, -1):
            sys.stdout.write("\rContinuing in %2d second(s)... " % remaining)
            sys.stdout.flush()
            time.sleep(1)
        sys.stdout.write("\r" + " " * 40 + "\r")
        sys.stdout.flush()
    else:
        time.sleep(hold)

    logging.info("Startup hold complete - continuing.")


def main():
    setup_logging()
    logging.info("=== Phone Link Kiosk Launcher started ===")

    show_startup_banner()

    hwnd = ensure_window()
    last_ocr = 0.0
    confirm_streak = 0

    while True:
        try:
            # (Re)acquire the window if it vanished (user closed it).
            if not hwnd or not window_utils.find_phone_link_window():
                logging.info("Window gone - relaunching in %.1fs.",
                             config.RELAUNCH_DELAY)
                time.sleep(config.RELAUNCH_DELAY)
                hwnd = ensure_window()
                if not hwnd:
                    continue

            enforce_kiosk(hwnd)

            # Periodic OCR sync check.
            now = time.time()
            if now - last_ocr >= config.OCR_INTERVAL:
                last_ocr = now
                text = sync_detector.capture_window_text(hwnd)
                if sync_detector.is_synced(text):
                    confirm_streak += 1
                    logging.info("Sync indicator detected (%d/%d).",
                                 confirm_streak, config.SYNC_CONFIRM_COUNT)
                    if confirm_streak >= config.SYNC_CONFIRM_COUNT:
                        logging.info("Sync confirmed. Releasing lock + exiting.")
                        release_lock(hwnd)
                        break
                else:
                    if confirm_streak:
                        logging.info("Sync indicator lost - resetting streak.")
                    confirm_streak = 0

            time.sleep(config.LOOP_INTERVAL)

        except KeyboardInterrupt:
            logging.info("Interrupted by user - releasing lock + exiting.")
            release_lock(hwnd)
            break
        except Exception as exc:
            logging.exception("Loop error (continuing): %s", exc)
            time.sleep(config.LOOP_INTERVAL)

    logging.info("=== Phone Link Kiosk Launcher finished ===")


if __name__ == "__main__":
    main()
