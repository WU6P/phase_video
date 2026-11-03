"""Checks dsp.py and the numbers the video states against independent references:

1. the numpy port of windowMagPhase / windowMagPhase2 against ../phase/core.js itself (run in Node);
2. donor = x gives x back (sqrt-Hann at hop W/2 is a perfect-reconstruction pair);
3. the QAM first-failure angles (narration r_5, r_6) against core.js firstFailure, a brute-force scan;
4. sound and picture facts the narration relies on (crest factor, resolved harmonics, swap, tiles, Morse timing).
Run: .venv/bin/python test_dsp.py
"""
import json
import os
import subprocess
import sys

import numpy as np

import dsp

HERE = os.path.dirname(os.path.abspath(__file__))
CORE = os.path.join(HERE, "..", "phase", "core.js")
fails = 0


def check(name, cond, detail=""):
    global fails
    fails += not cond
    print(f"{'PASS' if cond else 'FAIL'}  {name}  {detail}")


def node(js, data):
    p = subprocess.run(["node", "-e", f"const C=require({json.dumps(CORE)});const D=JSON.parse(require('fs').readFileSync(0));{js}"],
                       input=json.dumps(data), capture_output=True, text=True, check=True)
    return json.loads(p.stdout)


HAVE_CORE = os.path.exists(CORE)  # ../phase is a separate (private) project; without it those checks are skipped
if not HAVE_CORE:
    print(f"SKIP  core.js comparisons: {CORE} not found")
rng = np.random.default_rng(1)
x, d = rng.standard_normal(256), rng.standard_normal(256)
for W in ((16, 64, 256) if HAVE_CORE else ()):
    js = np.array(node("console.log(JSON.stringify(Array.from(C.windowMagPhase(D.x,D.d,D.W))))",
                       {"x": x.tolist(), "d": d.tolist(), "W": W}))
    err = np.abs(js - dsp.window_mag_phase(x, d, W)).max()
    check(f"1-D port vs core.js, W={W}", err < 1e-9, f"max diff {err:.1e}")
img, don = rng.uniform(0, 1, (32, 32)), rng.uniform(0, 1, (32, 32))
for B in ((8, 32) if HAVE_CORE else ()):
    js = np.array(node("console.log(JSON.stringify(Array.from(C.windowMagPhase2(D.x,D.d,32,D.B))))",
                       {"x": img.ravel().tolist(), "d": don.ravel().tolist(), "B": B})).reshape(32, 32)
    err = np.abs(js - dsp.window_mag_phase2(img, don, B)).max()
    check(f"2-D port vs core.js, B={B}", err < 1e-9, f"max diff {err:.1e}")
for W in (16, 64):
    err = np.abs(dsp.window_mag_phase(x, x, W) - x).max()
    check(f"donor = x gives x back, W={W}", err < 1e-9, f"{err:.1e}")

# QAM: closed form used on screen (45 deg - asin(boundary / corner radius)) vs core.js brute force
closed = [45 - np.degrees(np.arcsin(b / (c * np.sqrt(2)))) for b, c in ((0, 1), (2, 3), (6, 7))]
if HAVE_CORE:
    ff = node("console.log(JSON.stringify(['qpsk','16qam','64qam'].map(s=>C.firstFailure(s)*180/Math.PI)))", {})
else:  # independent brute force here: rotate each constellation until a point leaves its decision box
    def brute(M):
        lv = np.arange(-(M - 1), M, 2)
        P = np.array([[a, b] for a in lv for b in lv], float)
        for th in np.arange(0, 46, 0.0005):
            c, s_ = np.cos(np.radians(th)), np.sin(np.radians(th))
            R = np.c_[P[:, 0] * c - P[:, 1] * s_, P[:, 0] * s_ + P[:, 1] * c]
            q = lv[np.abs(R[:, :, None] - lv).argmin(-1)]
            if (q != P).any():
                return th
    ff = [brute(M) for M in (2, 4, 8)]
for name, a, b, said in zip(("QPSK", "16-QAM", "64-QAM"), ff, closed, (45.0, 16.9, 7.7)):
    check(f"{name} first failure", abs(a - b) < 2e-3 and round(a, 1) == said, f"{'core.js' if HAVE_CORE else 'brute force'} {a:.3f} deg, closed {b:.3f}, narration {said}")

n = json.load(open(os.path.join(HERE, "assets", "numbers.json")))
check("cosine-phase crest = sqrt(2H) (k_1 'sharp spike')", abs(n["crest_low"]["cos"] - np.sqrt(12)) < 1e-9,
      f"{n['crest_low']['cos']:.3f} vs random {n['crest_low']['rand']:.3f}")
check("harmonics 1-6 of 200 Hz resolved (e_4)", n["erb"]["1200"] < 200, f"ERB(1.2 kHz) = {n['erb']['1200']:.0f} Hz < 200 Hz spacing")
check("harmonics 20-30 of 100 Hz share filters (e_6)", n["erb"]["2500"] / 100 > 2.5, f"ERB(2.5 kHz) = {n['erb']['2500']:.0f} Hz ~ {n['erb']['2500'] / 100:.1f} harmonics")
s = n["swap_corr"]
check("swap looks like the phase donor (w_3)", s["with_B"] > 0.5 > s["with_A"], f"r(B) {s['with_B']:.2f}, r(A) {s['with_A']:.2f}")
t = n["tile_corr"]
check("small tiles keep the picture, one window loses it (w_10)", t["16"] > 0.8 and abs(t["256"]) < 0.35,
      f"r 8px {t['8']:.2f}, 16px {t['16']:.2f}, 32px {t['32']:.2f}, whole {t['256']:.2f}")
m = n["morse_score"]
check("Morse rhythm survives 32 ms windows, not one window (w_9, w_10)", m["w32"] > 0.7 and m["whole"] < 0.3,
      f"envelope r 32 ms {m['w32']:.2f}, whole {m['whole']:.2f}, original {m['orig']:.2f}")
print("ALL PASS" if not fails else f"{fails} FAILED")
sys.exit(1 if fails else 0)
