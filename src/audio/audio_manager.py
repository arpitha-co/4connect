# connect4_vision_robot/audio_manager.py
import threading
import os
import time

# Try pygame for music/sfx
try:
    import pygame
    _HAS_PYGAME = True
except Exception:
    pygame = None
    _HAS_PYGAME = False

# Try pyttsx3 for TTS (offline)
try:
    import pyttsx3
    _HAS_TTS = True
except Exception:
    pyttsx3 = None
    _HAS_TTS = False

ASSETS_DIR = os.path.join(os.path.dirname(__file__), '..', 'assets', 'sounds')
ASSETS_DIR = os.path.normpath(ASSETS_DIR)

_music_channel = None
_tts_engine = None
_music_playing = False
_lock = threading.Lock()

def init(audio_enable=True):
    global _tts_engine
    if _HAS_PYGAME and audio_enable:
        pygame.mixer.init()
    if _HAS_TTS:
        try:
            _tts_engine = pyttsx3.init()
            # optional: set voice rate/volume
            _tts_engine.setProperty('rate', 160)
        except Exception:
            _tts_engine = None

def _full_path(fn):
    if os.path.isabs(fn):
        return fn
    return os.path.join(ASSETS_DIR, fn)

def play_music(filename, loop=True, volume=0.6):
    """Play background music in non-blocking mode."""
    global _music_playing
    if not _HAS_PYGAME:
        return
    path = _full_path(filename)
    if not os.path.exists(path):
        return
    def _play():
        global _music_playing
        try:
            pygame.mixer.music.load(path)
            pygame.mixer.music.set_volume(volume)
            pygame.mixer.music.play(-1 if loop else 0)
            _music_playing = True
        except Exception:
            _music_playing = False
    threading.Thread(target=_play, daemon=True).start()

def stop_music():
    if not _HAS_PYGAME:
        return
    try:
        pygame.mixer.music.stop()
    except Exception:
        pass

def play_sound(filename, volume=1.0):
    """Play a short effect (non-blocking)."""
    if not _HAS_PYGAME:
        return
    path = _full_path(filename)
    if not os.path.exists(path):
        return
    def _play():
        try:
            s = pygame.mixer.Sound(path)
            s.set_volume(volume)
            s.play()
        except Exception:
            pass
    threading.Thread(target=_play, daemon=True).start()

def say(text, block=False):
    """Speak a line of text. Non-blocking by default."""
    if not _HAS_TTS:
        return
    def _speak():
        try:
            _tts_engine.say(text)
            _tts_engine.runAndWait()
        except Exception:
            pass
    t = threading.Thread(target=_speak, daemon=True)
    t.start()
    if block:
        t.join()