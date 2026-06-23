# Phone Link Kiosk Launcher

A small **Windows desktop utility** that, when double-clicked:

1. Launches Microsoft **Phone Link**
2. Forces its window to stay **focused and always-on-top**
3. Holds a **practical kiosk lock** — restores it if minimized, relaunches it if closed
4. Periodically reads the window with **OCR** and, once it sees the **"connected & synced"** text, releases the lock and exits cleanly

> Configured per your choices: practical kiosk lock · OCR detection · **no timeout** (holds until sync is detected).

---

## ⚠️ This is native Windows software

It uses Win32 APIs (`pywin32`) and screen capture, so it **only runs on Windows** and **must be built on a Windows PC**. It cannot be compiled in a Linux/cloud environment.

---

## Prerequisites (on your Windows PC)

1. **Python 3.9+** — https://www.python.org/downloads/ (tick *"Add Python to PATH"* during install)
2. **Tesseract OCR** — https://github.com/UB-Mannheim/tesseract/wiki
   - Install to the default path `C:\Program Files\Tesseract-OCR\`
   - If you install elsewhere, update `TESSERACT_CMD` in `config.py`

---

## Build the .exe (one command)

Open **Command Prompt**, `cd` into this folder, and run:

```bat
build.bat
```

When it finishes, your executable is at:

```
dist\PhoneLinkKiosk.exe
```

Double-click that `.exe` to use it.

> Tip: the build uses `--noconsole` (no window). While **testing**, remove `--noconsole` from `build.bat`, or just run `python main.py` to watch the live log.

---

## Run from source (for testing, no build needed)

```bat
pip install -r requirements.txt
python main.py
```

A log is also written to `phone_link_kiosk.log`.

---

## Tuning detection (`config.py`)

The most important settings:

| Setting | What it does |
|---|---|
| `SYNC_SUCCESS_KEYWORDS` | Text that means "synced" (e.g. `connected`, `synced`, `up to date`). **Match these to your exact Phone Link wording.** |
| `SYNC_NEGATIVE_KEYWORDS` | Text that vetoes success (e.g. `connecting`, `not connected`). |
| `SYNC_CONFIRM_COUNT` | How many consecutive OCR passes must see "synced" before unlocking (reduces false positives). |
| `WINDOW_TITLE_KEYWORDS` | How the Phone Link window is identified by title. |
| `TESSERACT_CMD` | Full path to `tesseract.exe`. |
| `KEEP_TOPMOST` / `DENY_MINIMIZE` | Toggle the kiosk behaviours. |
| `OCR_INTERVAL` | Seconds between OCR checks. |

**How to find the right keywords:** open Phone Link, connect your phone, and note the exact words shown when it's fully synced (e.g. *"Connected"*, *"All synced"*, your device name). Put those in `SYNC_SUCCESS_KEYWORDS`. No code changes or rebuild are needed if you edit `config.py` and run from source; if running the built `.exe`, edit `config.py` then rerun `build.bat`.

---

## How to stop it manually

- It exits automatically once sync is detected.
- If running from source, press **Ctrl+C** in the console — it releases the always-on-top lock and exits.
- The kiosk lock is **practical, not un-killable**: it does not block Task Manager or Alt+F4-then-relaunch loops aggressively. (You chose this option for stability.)

---

## File overview

| File | Purpose |
|---|---|
| `main.py` | Entry point + watch loop |
| `window_utils.py` | Find / focus / restore / capture the Phone Link window (Win32) |
| `sync_detector.py` | Screenshot + OCR + synced-state decision |
| `config.py` | All tunable settings |
| `build.bat` | Installs deps and builds the single-file `.exe` |
| `requirements.txt` | Python dependencies |

---

## Notes & limitations

- **OCR accuracy** depends on the window being visible and unobstructed (the kiosk loop keeps it foreground/topmost, which helps).
- Phone Link UI wording can change between versions — if detection stops working, update `SYNC_SUCCESS_KEYWORDS`.
- If `os.startfile("ms-phone:")` doesn't open Phone Link on your machine, ensure Phone Link is installed from the Microsoft Store.
