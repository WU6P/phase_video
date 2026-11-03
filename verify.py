"""Independent checks on the finished video (does not trust the code that built it).

1. container: video, audio and subtitle streams present; audio and video lengths agree to within one frame.
2. scenes: each scene file's frame count matches the length its timing log reports.
3. sync, final file: decode the final MP4's audio, find where speech starts (energy onsets after >=0.3 s
   silence), and require a speech onset within 60 ms of every cue start.
4. sync, Manim's own audio: the same onset test on each scene file's Manim-muxed audio, which proves the
   logged cue times are where Manim actually placed the sound next to the frames it drew.
5. subtitles: every SRT cue is inside the video and they never overlap.
6. voice clips: each narration file is found by cross-correlation in Manim's scene audio and in the final file
   (match r > 0.9, constant offset), so a scene that played the wrong clip fails even if speech starts on time.
   Demo sounds: located by cross-correlation in the final file and in Manim's scene audio; they must agree.
7. end card: the QR code in the last seconds of the final file decodes to the repository URL.
"""
import json
import os
import re
import subprocess
import sys

import numpy as np

from lang import AUDIO, HERE, LANG, MEDIA, NAME, OUT, REPO, TIMING
from narration import ORDER

SR = 16000
LEAD = 0.04   # tts.py keeps 40 ms of lead-in before the first word of every clip
TOL = 0.035   # allowed deviation from that lead-in: about two frames at 60 fps


def pcm(path):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-map", "0:a:0", "-ac", "1", "-ar", str(SR),
                          "-f", "s16le", "-"], capture_output=True).stdout
    return np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768


def onsets(x, thresh_db=-40, min_sil=0.3):
    hop = int(0.01 * SR)
    n = len(x) // hop
    e = np.sqrt((x[:n * hop].reshape(n, hop) ** 2).mean(axis=1) + 1e-12)
    db = 20 * np.log10(e)
    loud = db > thresh_db + db.max()
    res, quiet = [], int(min_sil / 0.01)
    run = quiet
    for i, l in enumerate(loud):
        if l:
            if run >= quiet:
                res.append(i * 0.01)
            run = 0
        else:
            run += 1
    return np.array(res)


def match(starts, ons):
    """Signed (detected speech onset - cue start - LEAD) for each cue, using the nearest onset."""
    errs = []
    for s in starts:
        if not len(ons):
            errs.append(99.0)
            continue
        o = ons[np.argmin(np.abs(ons - s - LEAD))]
        errs.append(float(o - s - LEAD))
    return np.array(errs)


def summary(e):
    return (f"offset vs expected: median {np.median(e) * 1000:+.0f} ms, range {e.min() * 1000:+.0f}..{e.max() * 1000:+.0f} ms")


def probe_json(path):
    return json.loads(subprocess.run(["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", path],
                                     capture_output=True, text=True).stdout)


def main():
    q = sys.argv[1] if len(sys.argv) > 1 else "1080p60"
    final = os.path.join(OUT, f"{NAME}.mp4")
    meta = json.load(open(os.path.join(OUT, f"{NAME}.cues.json")))
    ok = True

    def report(name, cond, detail):
        nonlocal ok
        ok &= bool(cond)
        print(f"{'PASS' if cond else 'FAIL'}  {name}: {detail}")

    p = probe_json(final)
    kinds = sorted(s["codec_type"] for s in p["streams"])
    v = next(s for s in p["streams"] if s["codec_type"] == "video")
    a = next(s for s in p["streams"] if s["codec_type"] == "audio")
    num, den = map(int, v["r_frame_rate"].split("/"))
    vd, ad = float(v["duration"]), float(a["duration"])
    report("streams", kinds == ["audio", "subtitle", "video"], f"{kinds}, {v['width']}x{v['height']} @ {num / den:g} fps")
    report("A/V length", abs(vd - ad) <= den / num + 0.03, f"video {vd:.3f} s, audio {ad:.3f} s")

    bad = []
    for sc in ORDER:
        f = os.path.join(MEDIA, "videos/scenes", q, f"{sc}.mp4")
        frames = int(subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                                     "stream=nb_frames", "-of", "csv=p=0", f], capture_output=True, text=True).stdout)
        logged = json.load(open(os.path.join(TIMING, f"{sc}.json")))["duration"]
        if abs(frames * den / num - logged) > 1.5 * den / num:
            bad.append((sc, frames * den / num, logged))
    report("scene lengths", not bad, "frame counts match timing logs" if not bad else str(bad))

    starts = np.array([c["start"] for c in meta["cues"]])
    errs = match(starts, onsets(pcm(final)))
    worst = int(np.abs(errs).argmax())
    report("sync (final MP4)", np.abs(errs).max() <= TOL,
           f"{len(starts)} cues, {summary(errs)}, worst {meta['cues'][worst]['cue']}")

    allerr, who = [], []
    for sc in ORDER:
        f = os.path.join(MEDIA, "videos/scenes", q, f"{sc}.mp4")
        tm = json.load(open(os.path.join(TIMING, f"{sc}.json")))
        e = match(np.array([c["start"] for c in tm["cues"]]), onsets(pcm(f)))
        allerr += list(e)
        who += [c["cue"] for c in tm["cues"]]
    allerr = np.array(allerr)
    report("sync (Manim's own scene audio)", np.abs(allerr).max() <= TOL,
           f"{summary(allerr)}, worst {who[int(np.abs(allerr).argmax())]}")

    # 6. demo sounds: find each one by cross-correlation (search +-0.4 s) in the final MP4 AND in the scene file's own
    #    Manim-muxed audio (Manim placed it beside the frames it drew, independently of assemble.py), and require the
    #    two positions to agree; also check the level against the voice in the final mix.
    import soundfile as sf
    SR = 48000  # full rate: at 16 kHz a sub-sample offset alone costs up to ~0.2 in r for 3 kHz content

    def dec(path):
        return np.frombuffer(subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-map", "0:a:0", "-ac", "1", "-ar",
                                             str(SR), "-f", "s16le", "-"], capture_output=True).stdout,
                             dtype=np.int16).astype(np.float32) / 32768

    def find(x, ref, t_guess, span=0.4):
        i0, pad = int(t_guess * SR), int(span * SR)
        seg = x[max(0, i0 - pad):i0 + len(ref) + pad]
        cc = np.correlate(seg, ref, "valid")
        k = int(np.argmax(cc))
        r = float(cc[k] / np.sqrt((ref @ ref) * (seg[k:k + len(ref)] ** 2).sum()))
        return (max(0, i0 - pad) + k) / SR, r

    x = dec(final)
    rows, lv, calib, vmatch = [], [], [], []
    for sc in ORDER:
        tm = json.load(open(os.path.join(TIMING, f"{sc}.json")))
        xs = dec(os.path.join(MEDIA, "videos/scenes", q, f"{sc}.mp4"))
        for c in tm["cues"]:  # every voice clip must really be in Manim's audio (content, not only an onset there)
            ref, sr = sf.read(os.path.join(AUDIO, f"{c['cue']}.wav"), dtype="float32")
            ref = np.interp(np.arange(int(len(ref) * SR / sr)) * sr / SR, np.arange(len(ref)), ref).astype(np.float32)
            tf, rf = find(x, ref, meta["offsets"][sc] + c["start"])
            ts, rs = find(xs, ref, c["start"])
            vmatch.append((c["cue"], min(rf, rs), ts - c["start"]))
            if tm.get("sfx"):  # calibration for the demo sounds: the same measurement on this scene's voice clips
                calib.append((tf - meta["offsets"][sc]) - ts)
        for e in tm.get("sfx", []):
            ref, _ = sf.read(os.path.join(HERE, "assets", f"{e['sfx']}.wav"), dtype="float32")
            tf, rf = find(x, ref, meta["offsets"][sc] + e["start"])
            ts, rs = find(xs, ref, e["start"])
            rows.append((e["sfx"], (tf - meta["offsets"][sc]) - ts, min(rf, rs)))
            lv.append(20 * np.log10(np.sqrt(np.mean(x[int(tf * SR):int(tf * SR) + len(ref)] ** 2))))
    vr = [20 * np.log10(np.sqrt(np.mean(x[int(c["start"] * SR):int(c["end"] * SR)] ** 2))) for c in meta["cues"]]
    wv = min(vmatch, key=lambda m: m[1])
    sp = np.array([m[2] for m in vmatch])
    report("voice clips in Manim's scene audio and the final file", wv[1] > 0.9 and np.ptp(sp) < 0.01,
           f"{len(vmatch)} clips, min match r {wv[1]:.3f} ({wv[0]}), Manim offset {sp.min() * 1000:+.1f}..{sp.max() * 1000:+.1f} ms")
    c0 = float(np.median(calib))  # Manim's muxed audio runs a constant ~20 ms late (AAC priming); the voice measures it
    print(f"      voice calibration {c0 * 1000:+.1f} ms (spread {np.ptp(calib) * 1000:.1f} ms over {len(calib)} clips); "
          + ", ".join(f"{n} {(d - c0) * 1000:+.1f} ms r {r:.3f}" for n, d, r in rows))
    worst = max(abs(r[1] - c0) for r in rows)
    report("demo sounds: final vs Manim's scene audio", worst <= 0.010 and min(r[2] for r in rows) > 0.95,
           f"{len(rows)} sounds, worst {worst * 1000:.1f} ms after calibration, min match r {min(r[2] for r in rows):.3f}")
    rel = np.array(lv) - np.median(vr)
    report("demo sound level", np.abs(rel).max() <= 6, f"vs voice: {rel.min():+.1f} .. {rel.max():+.1f} dB")

    # 7. end card: decode the QR code from frames of the final MP4 (last 5 s) with OpenCV; it must give the repo URL
    import cv2
    got = []
    for back in (1.5, 3.0, 4.5):
        png = os.path.join(OUT, "_qr.png")
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{vd - back:.2f}", "-i", final, "-frames:v", "1", png], check=True)
        got.append(cv2.QRCodeDetector().detectAndDecode(cv2.imread(png))[0])
        os.remove(png)
    report("end card QR code", all(g == REPO for g in got), f"decoded {got[0]!r} in {sum(g == REPO for g in got)}/3 frames")

    srt = open(os.path.join(OUT, f"{NAME}.srt"), encoding="utf-8").read()
    ts = re.findall(r"(\d\d):(\d\d):(\d\d),(\d{3}) --> (\d\d):(\d\d):(\d\d),(\d{3})", srt)
    spans = [(int(h) * 3600 + int(m) * 60 + int(s) + int(ms) / 1000, int(h2) * 3600 + int(m2) * 60 + int(s2) + int(ms2) / 1000)
             for h, m, s, ms, h2, m2, s2, ms2 in ts]
    overl = sum(1 for (a0, a1), (b0, b1) in zip(spans, spans[1:]) if b0 < a1 - 0.002)
    report("subtitles", overl == 0 and spans[-1][1] <= vd + 0.01, f"{len(spans)} cues, {overl} overlaps, last ends {spans[-1][1]:.2f} s")
    print("ALL CHECKS PASS" if ok else "SOME CHECKS FAILED")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
