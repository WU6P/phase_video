"""Join the rendered scenes into one video with a sample-accurate narration track and subtitles.

Video: the scene MP4s concatenated without re-encoding.
Audio: rebuilt here, not taken from Manim: every cue WAV is placed at
       (start of its scene in the final video) + (cue start logged by the scene), then loudness-matched.
       The same logged times drove the animations, so picture and voice share one clock.
Subtitles: SRT from the same times (long sentences split into readable chunks), muxed as a soft track.

Usage: [VLANG=zh] assemble.py [quality-dir, default 1080p60]   ->  out/phase_explained[_zh].mp4 (+ .srt)
"""
import json
import os
import re
import subprocess
import sys

import numpy as np
import soundfile as sf

from lang import AUDIO, HERE, LANG, MEDIA, NAME, OUT, TIMING
from narration import ORDER

SR = 48000
TARGET_LUFS = -16.0


def probe(path, stream="v:0", entry="stream=duration"):
    out = subprocess.run(["ffprobe", "-v", "error", "-select_streams", stream, "-show_entries", entry,
                          "-of", "csv=p=0", path], capture_output=True, text=True).stdout.strip()
    return out


def video_duration(path):
    n = int(probe(path, entry="stream=nb_frames"))
    num, den = map(int, probe(path, entry="stream=r_frame_rate").split("/"))
    return n * den / num


def load_wav(path):
    x, sr = sf.read(path, dtype="float32")
    if x.ndim > 1:
        x = x.mean(axis=1)
    if sr != SR:  # Kokoro is 24 kHz: exact 2x upsample by linear interpolation is plenty for speech
        t = np.arange(int(len(x) * SR / sr)) * sr / SR
        x = np.interp(t, np.arange(len(x)), x).astype(np.float32)
    return x


def lufs(path):
    err = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", path, "-af", "ebur128", "-f", "null", "-"],
                         capture_output=True, text=True).stderr
    return float(re.findall(r"I:\s+(-?[\d.]+) LUFS", err)[-1])


def srt_time(t):
    ms = int(round(t * 1000))
    return f"{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d},{ms % 1000:03d}"


def chunks(text, limit=None):
    """Split a sentence into subtitle-sized pieces at sentence/clause boundaries."""
    if LANG == "zh":
        limit = limit or 30
        parts, sep = [p for p in re.split(r"(?<=[，。？！：；])", text) if p], ""
    else:
        limit = limit or 84
        parts, sep = re.split(r"(?<=[.?!:;])\s+|(?<=,)\s+", text), " "
    out, cur = [], ""
    for p in parts:
        if cur and len(cur) + len(sep) + len(p) > limit:
            out.append(cur)
            cur = p
        else:
            cur = f"{cur}{sep}{p}".strip()
    if cur:
        out.append(cur)
    return out


def main():
    q = sys.argv[1] if len(sys.argv) > 1 else "1080p60"
    vdir = os.path.join(MEDIA, "videos/scenes", q)
    out_dir = OUT
    os.makedirs(out_dir, exist_ok=True)

    offsets, t = {}, 0.0
    for sc in ORDER:
        offsets[sc] = t
        t += video_duration(os.path.join(vdir, f"{sc}.mp4"))
    total = t

    # narration track
    track = np.zeros(int(round(total * SR)) + SR, dtype=np.float32)
    cues = []
    for sc in ORDER:
        tm = json.load(open(os.path.join(TIMING, f"{sc}.json")))
        for c in tm["cues"]:
            start = offsets[sc] + c["start"]
            x = load_wav(os.path.join(AUDIO, f"{c['cue']}.wav"))
            i = int(round(start * SR))
            track[i:i + len(x)] += x
            cues.append({"cue": c["cue"], "scene": sc, "start": round(start, 4), "end": round(start + c["dur"], 4),
                         "text": c["text"]})
        for s in tm.get("sfx", []):  # demo sounds go into the same track, at the times the scene logged
            x = load_wav(os.path.join(HERE, "assets", f"{s['sfx']}.wav"))
            i = int(round((offsets[sc] + s["start"]) * SR))
            track[i:i + len(x)] += x
    track = track[:int(round(total * SR))]
    raw = os.path.join(out_dir, f"_narration_raw{LANG}.wav")
    sf.write(raw, track, SR, subtype="FLOAT")
    gain = 10 ** ((TARGET_LUFS - lufs(raw)) / 20)
    track = track * gain
    peak = float(np.abs(track).max())
    if peak > 0.89:  # keep true peak under about -1 dBFS
        track *= 0.89 / peak
    wav = os.path.join(out_dir, f"{NAME}.narration.wav")
    sf.write(wav, track, SR, subtype="PCM_16")
    os.remove(raw)

    # subtitles
    lines, k = [], 1
    for c in cues:
        pieces = chunks(c["text"])
        n = sum(len(p) for p in pieces)
        t0 = c["start"]
        for p in pieces:
            t1 = t0 + (c["end"] - c["start"]) * len(p) / n
            lines.append(f"{k}\n{srt_time(t0)} --> {srt_time(t1)}\n{p}\n")
            k += 1
            t0 = t1
    srt = os.path.join(out_dir, f"{NAME}.srt")
    open(srt, "w", encoding="utf-8").write("\n".join(lines))

    # video: lossless concat of the scene files, then mux narration + subtitles
    lst = os.path.join(out_dir, f"_concat{LANG}.txt")
    open(lst, "w").write("".join(f"file '{os.path.join(vdir, sc + '.mp4')}'\n" for sc in ORDER))
    final = os.path.join(out_dir, f"{NAME}.mp4")
    iso = {"en": "eng", "zh": "chi"}[LANG]
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", lst, "-i", wav, "-i", srt,
                    "-map", "0:v:0", "-map", "1:a:0", "-map", "2:s:0", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
                    "-c:s", "mov_text", "-metadata:s:s:0", f"language={iso}", "-metadata:s:a:0", f"language={iso}",
                    "-movflags", "+faststart", "-t", f"{total:.4f}", final], check=True)
    os.remove(lst)
    json.dump({"total": round(total, 4), "offsets": offsets, "cues": cues},
              open(os.path.join(out_dir, f"{NAME}.cues.json"), "w"), indent=1, ensure_ascii=False)
    print(f"{final}\n  {total:.2f} s, {len(cues)} cues, {k - 1} subtitles, gain {20 * np.log10(gain):+.1f} dB")


if __name__ == "__main__":
    main()
