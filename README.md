<div align="center">

```
██████╗  █████╗  ██████╗███████╗██████╗     ████████╗███████╗███████╗████████╗
██╔══██╗██╔══██╗██╔════╝██╔════╝██╔══██╗    ╚══██╔══╝██╔════╝██╔════╝╚══██╔══╝
██████╔╝███████║██║     █████╗  ██████╔╝       ██║   █████╗  ███████╗   ██║   
██╔═══╝ ██╔══██║██║     ██╔══╝  ██╔══██╗       ██║   ██╔══╝  ╚════██║   ██║   
██║     ██║  ██║╚██████╗███████╗██║  ██║       ██║   ███████╗███████║   ██║   
╚═╝     ╚═╝  ╚═╝ ╚═════╝╚══════╝╚═╝  ╚═╝       ╚═╝   ╚══════╝╚══════╝   ╚═╝   
```

# 🏃 FitnessGram Pacer Test Prank

**A harmless Windows prank that plays the FitnessGram Pacer Test audio,<br>
locks the victim's screen, and ends in a real kernel BSOD.**

[![License: CC BY-NC-SA 4.0](https://img.shields.io/badge/License-CC%20BY--NC--SA%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by-nc-sa/4.0/)
[![Platform](https://img.shields.io/badge/Platform-Windows%20Only-blue?logo=windows)](https://www.microsoft.com/windows)
[![Python](https://img.shields.io/badge/Python-3.8%2B-yellow?logo=python)](https://python.org)
[![Made With](https://img.shields.io/badge/Made%20With-Chaos-red)](.)

> ⚠️ **For educational and prank purposes only. Always use on machines you own or have explicit permission to mess with.**

</div>

---

## 📋 Table of Contents

- [What It Does](#-what-it-does)
- [The Full Timeline](#-the-full-timeline)
- [GDI Escalation Ladder](#-gdi-escalation-ladder)
- [System Lockdown](#-system-lockdown)
- [Requirements](#-requirements)
- [Setup & Usage](#-setup--usage)
- [Compiling to EXE](#-compiling-to-exe)
- [Is It Safe?](#-is-it-safe)
- [License](#-license)

---

## 🎯 What It Does

The moment the victim runs it:

- 🔇 **Silently plays the Pacer Test MP3** for 45 seconds — no window, nothing visible
- 🪟 **A window appears** mid-audio with a single white button: `Click me!`
- 🖱️ **Mouse starts jiggling** at click 2, getting more violent with each click
- 💀 **Real GDI effects** erupt at click 7, escalating through 12 intensity levels
- 📢 **Accelerating error popups** fire if they ignore the button — faster and faster
- 💥 **Real kernel BSOD** triggers after 20 ignored warnings — or instantly on Ctrl+Alt+Del
- 🔒 **No exit** — Task Manager is killed on sight, all keyboard escape routes are blocked

---

## ⏱ The Full Timeline

```
t=0s    ┌─────────────────────────────────────────────────────────────────┐
        │  MP3 STARTS PLAYING                                             │
        │  "The FitnessGram Pacer Test is a multistage aerobic           │
        │   capacity test that progressively gets more difficult..."      │
        │                                                                 │
t=45s   ├─────────────────────────────────────────────────────────────────┤
        │  ┌──────────────────────┐                                       │
        │  │   Totally Normal     │  ← Window appears                    │
        │  │  ┌────────────────┐  │                                       │
        │  │  │   Click me!    │  │  ← White button                      │
        │  │  └────────────────┘  │                                       │
        │  └──────────────────────┘                                       │
        │  Audio continues playing...                                     │
        │                                                                 │
+2clk   │  Mouse starts jiggling                                         │
+7clk   │  GDI effects begin (light static)                              │
+9clk   │  Wobble joins                                                   │
+13clk  │  Tunnel effect                                                  │
+25clk  │  Full screen invert                                             │
+32clk  │  ALL EFFECTS — 8ms between frames                              │
        │                                                                 │
        │  ┌─────────────────────────────────────────────────────────┐   │
        │  │  ERROR: Why aren't you clicking me? (Warning 1/20)      │   │
        │  └─────────────────────────────────────────────────────────┘   │
        │     ↑ Fires every 4s, accelerates 0.3s per ignored popup      │
        │       until firing every 0.5s                                  │
        │                                                                 │
20wrn   ├─────────────────────────────────────────────────────────────────┤
        │                                                                 │
        │   ██████╗ ███████╗ ██████╗ ██████╗                             │
        │   ██╔══██╗██╔════╝██╔═══██╗██╔══██╗                            │
        │   ██████╔╝███████╗██║   ██║██║  ██║                            │
        │   ██╔══██╗╚════██║██║   ██║██║  ██║                            │
        │   ██████╔╝███████║╚██████╔╝██████╔╝                            │
        │   ╚═════╝ ╚══════╝ ╚═════╝ ╚═════╝                            │
        │                                                                 │
        │           PACER_TEST_FAILURE                                   │
        └─────────────────────────────────────────────────────────────────┘
```

---

## 📈 GDI Escalation Ladder

GDI effects are **real Win32 GDI operations** drawn directly on the Windows desktop device context using `BitBlt`, `StretchBlt`, and memory DCs — not overlays, not transparency tricks. Actual screen pixels.

| Clicks | Level | Effects Active | Frame Delay |
|:------:|:-----:|----------------|:-----------:|
| 0–6    | —     | *(nothing, clean screen)* | — |
| 7      | 0     | 🔲 Static noise | 200ms |
| 9      | 1     | 🔲 Static + 〰️ Wobble | 140ms |
| 11     | 2     | 〰️〰️ Heavy wobble | 100ms |
| 13     | 3     | 〰️ Still just wobble | 90ms |
| 15     | 4     | 〰️ 🔄 Rotation chunks (no tunnel yet) | 80ms |
| 17     | 5     | 〰️ 🔄 🪞 Kaleidoscope joins | 70ms |
| 19     | 6     | 🔄 🪞 Chunks heavy | 55ms |
| 20     | 7     | 🔄 🪞 🌀 **Tunnel starts** | 45ms |
| 22     | 8     | 🌀 🪞 🌊 Swirl joins | 38ms |
| 24     | 9     | 🌊 🌀 ↕️ Vertical flip strips | 30ms |
| 26     | 10    | 🌊 ⚡ 🌀 ↕️ Invert joins | 22ms |
| 28     | 11    | ⚡ 🌊 🌀 🔄 Near full chaos | 15ms |
| 33+    | 12    | **💀 ALL 7 EFFECTS** | **8ms** |

### The 8 GDI Effects

| Effect | Technique |
|--------|-----------|
| **Static Noise** | Random solid-colour `FillRect` blocks splattered across the screen |
| **Sine Wobble** | Screen captured to mem DC; each 5px horizontal strip `BitBlt`'d back with sine offset |
| **Zoom Tunnel** | Screen captured then `StretchBlt`'d into 4–7 shrinking centered layers |
| **Rotation Chunks** | Screen tiled into chunks; each `StretchBlt`'d with negative dimensions for 90° flips |
| **Screen Swirl** | Concentric rings each `BitBlt`'d with a radial angle offset — screen spirals inward |
| **Vertical Flip Strips** | Alternating strips `StretchBlt`'d with `-height` to flip upside-down |
| **Kaleidoscope** | Half or quarter of screen mirrored onto the other half via negative-dimension `StretchBlt` |
| **Full Invert** | `BitBlt` with `SRCINVERT` raster op — every pixel on screen flips to its complement |

---

## 🔒 System Lockdown

The moment the exe launches, the following escape routes are sealed:

```
╔════════════════════════════════════════════════════════╗
║  BLOCKED                          METHOD               ║
╠════════════════════════════════════════════════════════╣
║  ✗  Window close (X button)       WM_DELETE_WINDOW     ║
║  ✗  Alt+F4                        WH_KEYBOARD_LL hook  ║
║  ✗  Win key                       WH_KEYBOARD_LL hook  ║
║  ✗  Ctrl+Shift+Esc                WH_KEYBOARD_LL hook  ║
║  ✗  Alt+Tab                       WH_KEYBOARD_LL hook  ║
║  ✗  Ctrl+C / Ctrl+Q / Escape      tkinter bind         ║
║  ✗  Title bar close button        Win32 WS_SYSMENU     ║
║  ✗  Task Manager                  psutil kill loop      ║
║  ✗  Process Explorer              psutil kill loop      ║
║  ✗  Process Hacker                psutil kill loop      ║
║  ✗  cmd.exe / powershell.exe      psutil kill loop      ║
║  ✗  regedit.exe                   psutil kill loop      ║
║  ✗  Ctrl+Alt+Del                  → instant BSOD 💀    ║
╚════════════════════════════════════════════════════════╝

  ✓  Only escape: Task Manager via Ctrl+Alt+Del
     (which triggers the BSOD anyway lmao)
```

### Audio Lockdown
The MP3 watchdog checks every **100ms** — if anything pauses, stops, or mutes the audio, it immediately reloads and replays at full volume. `set_volume(1.0)` is forced every tick.

---

## 📦 Requirements

```bash
pip install pygame pyautogui psutil
```

| Package | Purpose |
|---------|---------|
| `pygame` | MP3 playback + audio watchdog |
| `pyautogui` | Mouse jiggle |
| `psutil` | Kill Task Manager / blocked processes |

> All GDI effects use pure `ctypes` Win32 — no extra packages needed.

---

## 🚀 Setup & Usage

### Running from source

```
📁 your_folder\
   pacer_prank.py
   pacer_test.mp3      ← MP3 File
```

```bash
# Auto-detects any .mp3 in the same folder
python pacer_prank.py

# Or specify the path explicitly
python pacer_prank.py "C:\path\to\pacer.mp3"
```

### Folder structure for compiling

```
📁 your_folder\
   pacer_prank.py
   compile.bat
   pacer_test.mp3      ← MP3 gets bundled INTO the exe automatically
```

---

## 🔨 Compiling to EXE

Drop `compile.bat` in the same folder as `pacer_prank.py` and your `.mp3`, then double-click it.

```
compile.bat
   │
   ├── Installs: pyinstaller, pygame, pyautogui, psutil
   ├── Detects your .mp3 automatically
   ├── Bundles it inside the exe with --add-data
   └── Output: dist\pacer_prank.exe
```

The resulting exe is **fully self-contained**. No Python, no MP3, no dependencies needed on the target machine.

**Optional PyInstaller flags you can add:**
```bash
--icon=chrome.ico          # disguise it as Chrome or something innocent
--uac-admin                # request admin on launch (helps BSOD succeed first try)
--name "ChromeUpdate"      # rename the exe to something unsuspicious
```

---

## 💥 The BSOD

When the victim ignores 20 warnings **or** presses Ctrl+Alt+Del, a **real kernel BSOD** is triggered via `NtRaiseHardError` — the same undocumented NT API Windows itself uses for fatal system errors.

```python
# Sets argtypes explicitly (the key to making it work without admin)
ntdll.RtlAdjustPrivilege(19, 1, 0, byref(prev))      # grant SeShutdownPrivilege
ntdll.NtRaiseHardError(0xC000007B, 0, 0, 0, 6, ...)  # ResponseOption 6 = crash
```

**Three-layer fallback:**
1. Process token privilege escalation → `NtRaiseHardError`
2. Thread token escalation → `NtRaiseHardError`  
3. Nuclear: kill `csrss.exe` (always BSODs Windows instantly)

**100% non-destructive.** Windows writes a minidump to `C:\Windows\Minidump\`, runs a quick chkdsk on reboot if needed, and comes back perfectly fine. No data loss. No OS damage.

---

## ✅ Is It Safe?

| Thing | Safe? |
|-------|:-----:|
| Deletes files | ✅ Never |
| Modifies registry | ✅ Never |
| Installs anything | ✅ Never |
| Network activity | ✅ None |
| Permanent system changes | ✅ None |
| Data corruption | ✅ No |
| Recovers after BSOD | ✅ Yes, fully |
| Scary as hell | 💀 Absolutely |

> The BSOD is a clean kernel crash — Windows is designed to survive it. The machine reboots and comes back like nothing happened (except maybe a slightly scared victim).

---

## 📁 File Structure

```
📦 pacer-test-prank
 ┣ 📜 pacer_prank.py     ← main prank script
 ┣ 📜 compile.bat        ← one-click EXE compiler
 ┣ 📜 README.md          ← you are here
 ┗ 🎵 pacer_test.mp3     ← MP3 File
```

---

## ⚖️ License

<div align="center">

This project is licensed under the **Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International** license.

[![CC BY-NC-SA 4.0](https://licensebuttons.net/l/by-nc-sa/4.0/88x31.png)](https://creativecommons.org/licenses/by-nc-sa/4.0/)

**You are free to:**
- ✅ Share — copy and redistribute in any medium or format
- ✅ Adapt — remix, transform, and build upon the material

**Under the following terms:**
- 📛 **Attribution** — You must give appropriate credit
- 🚫 **NonCommercial** — You may not use this for commercial purposes
- 🔄 **ShareAlike** — Derivatives must use the same license

[View full license →](https://creativecommons.org/licenses/by-nc-sa/4.0/)

</div>

---

<div align="center">

```
The 20 meter pacer test will begin in 30 seconds.
Line up at the start. The running speed starts slowly,
but gets faster each minute after you hear this signal.

[beep]

A single lap should be completed each time you hear this sound.

[ding]

Remember to run in a straight line, and run as long as possible.
The second time you fail to complete a lap before the sound, your test is over.

The test will begin on the word start. On your mark, get ready, start.
```

*made with 💀 and an unhealthy knowledge of Win32 GDI*

</div>
