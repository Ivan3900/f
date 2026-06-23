"""
Win32 helpers for finding, focusing, restoring and capturing the
Microsoft Phone Link window.

WINDOWS ONLY. These imports (win32gui etc.) will not work on Linux/macOS.
"""

import time
import ctypes
from ctypes import wintypes

import win32con
import win32gui
import win32process
import psutil

import config

# ctypes handles for a couple of calls not exposed cleanly by pywin32.
user32 = ctypes.windll.user32


def _title_matches(title: str) -> bool:
    title_l = title.lower()
    return any(kw in title_l for kw in config.WINDOW_TITLE_KEYWORDS)


def _process_matches(hwnd: int) -> bool:
    """Return True if the window belongs to the Phone Link process."""
    try:
        _, pid = win32process.GetWindowThreadProcessId(hwnd)
        proc = psutil.Process(pid)
        return proc.name().lower() == config.PHONE_LINK_PROCESS.lower()
    except Exception:
        return False


def find_phone_link_window():
    """
    Locate the top-level Phone Link window handle.

    Strategy: enumerate visible top-level windows; accept a window if either
    its title matches our keywords OR it belongs to PhoneExperienceHost.exe
    and has a non-empty title. Returns hwnd (int) or None.
    """
    matches = []

    def _enum(hwnd, _):
        if not win32gui.IsWindowVisible(hwnd):
            return True
        title = win32gui.GetWindowText(hwnd)
        if not title:
            return True
        if _title_matches(title) or _process_matches(hwnd):
            matches.append(hwnd)
        return True

    win32gui.EnumWindows(_enum, None)

    # Prefer a window whose title actually matches the keywords.
    for hwnd in matches:
        if _title_matches(win32gui.GetWindowText(hwnd)):
            return hwnd
    return matches[0] if matches else None


def wait_for_window(timeout=None):
    """Poll until the Phone Link window exists or timeout elapses."""
    timeout = config.WINDOW_WAIT_TIMEOUT if timeout is None else timeout
    deadline = time.time() + timeout
    while time.time() < deadline:
        hwnd = find_phone_link_window()
        if hwnd:
            return hwnd
        time.sleep(0.5)
    return None


def is_minimized(hwnd: int) -> bool:
    return bool(win32gui.IsIconic(hwnd))


def restore_window(hwnd: int):
    """Un-minimize / restore the window to its normal state."""
    win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)


def force_foreground(hwnd: int):
    """
    Bring a window to the foreground reliably.

    Windows blocks SetForegroundWindow from background processes, so we
    temporarily attach our input thread to the target's thread, which lets
    the call succeed.
    """
    try:
        if win32gui.IsIconic(hwnd):
            win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)

        fg_window = user32.GetForegroundWindow()
        target_thread = user32.GetWindowThreadProcessId(hwnd, None)
        current_thread = ctypes.windll.kernel32.GetCurrentThreadId()
        fg_thread = user32.GetWindowThreadProcessId(fg_window, None)

        user32.AttachThreadInput(current_thread, fg_thread, True)
        user32.AttachThreadInput(target_thread, fg_thread, True)

        win32gui.SetForegroundWindow(hwnd)
        win32gui.BringWindowToTop(hwnd)

        user32.AttachThreadInput(current_thread, fg_thread, False)
        user32.AttachThreadInput(target_thread, fg_thread, False)
    except Exception:
        # Best-effort; a single failed focus attempt is non-fatal.
        try:
            win32gui.SetForegroundWindow(hwnd)
        except Exception:
            pass


def set_topmost(hwnd: int, topmost=True):
    """Pin (or unpin) the window above all others."""
    flag = win32con.HWND_TOPMOST if topmost else win32con.HWND_NOTOPMOST
    win32gui.SetWindowPos(
        hwnd, flag, 0, 0, 0, 0,
        win32con.SWP_NOMOVE | win32con.SWP_NOSIZE | win32con.SWP_NOACTIVATE,
    )


def get_window_rect(hwnd: int):
    """Return (left, top, right, bottom) screen coordinates."""
    return win32gui.GetWindowRect(hwnd)
