"""Which language this run builds, and where its files go. Set VLANG=zh for the Chinese version (default en).

Everything that depends on the narration (audio clips, timing logs, Manim output, final video) gets its own
directory or name per language, so the two versions never overwrite each other. Pictures, sounds and
numbers in assets/ are shared.
"""
import os

HERE = os.path.dirname(os.path.abspath(__file__))
LANG = os.environ.get("VLANG", "en")
assert LANG in ("en", "zh"), f"VLANG must be en or zh, not {LANG!r}"
SUF = "" if LANG == "en" else "_zh"

AUDIO = os.path.join(HERE, "audio" + SUF)          # narration clips + durations.json
TIMING = os.path.join(HERE, "timing" + SUF)        # per-scene cue/sfx logs written by the scenes
MEDIA = os.path.join(HERE, "media" + SUF)          # Manim output
OUT = os.path.join(HERE, "out")
NAME = "phase_explained" + SUF                     # out/<NAME>.mp4, .srt

REPO = "https://github.com/WU6P/phase_video"       # shown as text and QR code on the end card
