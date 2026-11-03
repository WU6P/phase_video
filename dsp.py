"""Signals and pictures for the video -> assets/ (WAV sound effects, PNG pictures and spectrograms, numbers.json).

The windowed "keep the magnitude, take the phase from a donor" operation is a port of windowMagPhase /
windowMagPhase2 in ../phase/core.js (periodic sqrt-Hann windows, hop W/2, circular signal, one untapered window
when W >= length). test_dsp.py checks the port against core.js itself.
"""
import json
import os

import numpy as np
import soundfile as sf
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "assets")
FS = 48000
RMS = 0.07  # sound effects are matched to roughly the loudness of the voice clips


# ------------------------------------------------------------------------------------------------ core
def sqrt_hann(W):
    return np.sin(np.pi * np.arange(W) / W)


def mag_of_phase_of(A, B):
    return np.abs(A) * np.exp(1j * np.angle(B))


def window_mag_phase(x, donor, W):
    """1-D: magnitude of x, phase of donor, in each window of length W (hop W/2, circular)."""
    N = len(x)
    if W >= N:
        return np.real(np.fft.ifft(mag_of_phase_of(np.fft.fft(x), np.fft.fft(donor))))
    w = sqrt_hann(W)
    out = np.zeros(N)
    for s in range(0, N, W // 2):
        idx = (s + np.arange(W)) % N
        y = np.real(np.fft.ifft(mag_of_phase_of(np.fft.fft(x[idx] * w), np.fft.fft(donor[idx] * w))))
        np.add.at(out, idx, y * w)
    return out


def window_mag_phase2(img, donor, B):
    """2-D: the same on an S x S image with B x B windows."""
    S = img.shape[0]
    if B >= S:
        return np.real(np.fft.ifft2(mag_of_phase_of(np.fft.fft2(img), np.fft.fft2(donor))))
    w = sqrt_hann(B)
    ww = np.outer(w, w)
    out = np.zeros_like(img, dtype=float)
    for sy in range(0, S, B // 2):
        iy = (sy + np.arange(B)) % S
        for sx in range(0, S, B // 2):
            ix = (sx + np.arange(B)) % S
            blk = np.ix_(iy, ix)
            y = np.real(np.fft.ifft2(mag_of_phase_of(np.fft.fft2(img[blk] * ww), np.fft.fft2(donor[blk] * ww))))
            out[blk] += y * ww
    return out


def corr(a, b):
    a, b = a.ravel() - a.mean(), b.ravel() - b.mean()
    return float(a @ b / np.sqrt((a @ a) * (b @ b)))


# ---------------------------------------------------------------------------------------------- sounds
def fade(x, ms=15):
    n = int(FS * ms / 1000)
    r = 0.5 - 0.5 * np.cos(np.pi * np.arange(n) / n)
    x = x.copy()
    x[:n] *= r
    x[-n:] *= r[::-1]
    return x


def norm(x):
    return x * RMS / np.sqrt(np.mean(x ** 2))


def harmonic_complex(f0, ns, phases, dur):
    t = np.arange(int(FS * dur)) / FS
    return sum(np.cos(2 * np.pi * n * f0 * t + p) for n, p in zip(ns, phases))


MORSE = {"C": "-.-.", "Q": "--.-", " ": " "}


def morse(text, wpm=25, f=600.0, pad=0.25):
    dit = 1.2 / wpm
    env = [np.zeros(int(pad * FS))]
    rise = int(0.005 * FS)
    ramp = 0.5 - 0.5 * np.cos(np.pi * np.arange(rise) / rise)
    for ci, ch in enumerate(text):
        if ch == " ":
            env.append(np.zeros(int(4 * dit * FS)))  # 3 already added after the previous letter -> 7
            continue
        for k, sym in enumerate(MORSE[ch]):
            on = np.ones(int((3 if sym == "-" else 1) * dit * FS))
            on[:rise] = ramp
            on[-rise:] = ramp[::-1]
            env.append(on)
            env.append(np.zeros(int(dit * FS)))
        env.append(np.zeros(int(2 * dit * FS)))
    env.append(np.zeros(int(pad * FS)))
    e = np.concatenate(env)
    return e * np.sin(2 * np.pi * f * np.arange(len(e)) / FS), e


def spectrogram(x, W=1024, hop=256, fmax=1400, height=220):
    """Magnitude STFT in dB as an RGB image (time left to right, frequency upwards), 3b1b-ish colour ramp."""
    w = np.hanning(W)
    frames = [np.abs(np.fft.rfft(x[s:s + W] * w)) for s in range(0, len(x) - W, hop)]
    S = np.array(frames).T[: int(fmax * W / FS)]
    db = 20 * np.log10(S / S.max() + 1e-6)
    v = np.clip((db + 60) / 60, 0, 1)[::-1]
    lut = np.array([[0, 0, 0], [20, 40, 80], [40, 110, 160], [88, 196, 221], [255, 255, 160]], float)
    pos = np.linspace(0, 1, len(lut))
    rgb = np.stack([np.interp(v, pos, lut[:, c]) for c in range(3)], -1).astype(np.uint8)
    im = Image.fromarray(rgb).resize((rgb.shape[1] * 3, height), Image.BILINEAR)
    return im


# --------------------------------------------------------------------------------------------- pictures
S = 256


def picture_a():
    """A face."""
    im = Image.new("L", (S, S), 0)
    d = ImageDraw.Draw(im)
    d.ellipse((38, 38, 218, 218), outline=255, width=12)
    d.ellipse((88, 92, 112, 122), fill=255)
    d.ellipse((144, 92, 168, 122), fill=255)
    d.arc((80, 100, 176, 180), 20, 160, fill=255, width=12)
    return np.asarray(im, float) / 255


def picture_b():
    """A sailing boat under a sun."""
    im = Image.new("L", (S, S), 0)
    d = ImageDraw.Draw(im)
    d.polygon([(124, 36), (124, 170), (54, 170)], fill=255)          # main sail
    d.polygon([(134, 64), (134, 170), (196, 170)], fill=170)         # jib
    d.polygon([(40, 182), (216, 182), (190, 212), (66, 212)], fill=220)  # hull
    d.ellipse((182, 22, 230, 70), outline=255, width=8)              # sun
    for k in range(4):
        y = 228 + 0 * k
        d.arc((14 + 58 * k, 218, 72 + 58 * k, 246), 200, 340, fill=200, width=5)
    return np.asarray(im, float) / 255


def to_png(a, path, lo=None, hi=None):
    lo = a.min() if lo is None else lo
    hi = a.max() if hi is None else hi
    g = np.clip((a - lo) / (hi - lo), 0, 1)
    Image.fromarray((g * 255).astype(np.uint8)).save(path)


def main():
    os.makedirs(OUT, exist_ok=True)
    rng = np.random.default_rng(7)
    nums = {}

    def wav(name, x):
        x = fade(norm(x))
        sf.write(os.path.join(OUT, f"{name}.wav"), x.astype(np.float32), FS, subtype="PCM_16")
        nums.setdefault("sfx", {})[name] = round(len(x) / FS, 3)

    # Ohm's law pair: harmonics 1-6 of 200 Hz (all resolved: harmonic spacing 200 Hz > ERB(1.2 kHz) = 154 Hz)
    ns = list(range(1, 7))
    rph = rng.uniform(0, 2 * np.pi, len(ns))
    wav("low_cos", harmonic_complex(200, ns, [0] * 6, 1.6))
    wav("low_rand", harmonic_complex(200, ns, rph, 1.6))
    nums["low_rand_phases"] = [float(p) for p in rph]
    one = lambda ph: harmonic_complex(200, ns, ph, 1 / 200)
    nums["crest_low"] = {k: float(np.abs(v).max() / np.sqrt(np.mean(v ** 2))) for k, v in
                         (("cos", one([0] * 6)), ("rand", one(rph)))}
    # unresolved: harmonics 20-30 of 100 Hz (ERB at 2.5 kHz is about 295 Hz -> about three harmonics per filter)
    nh = list(range(20, 31))
    wav("high_cos", harmonic_complex(100, nh, [0] * len(nh), 1.6))
    wav("high_rand", harmonic_complex(100, nh, rng.uniform(0, 2 * np.pi, len(nh)), 1.6))
    erb = lambda f: 24.7 * (4.37 * f / 1000 + 1)
    nums["erb"] = {"1200": erb(1200), "2500": erb(2500)}

    # Morse "CQ CQ" at 25 wpm, 600 Hz; window scrambles with a white-noise phase donor
    x, env = morse("CQ CQ")
    donor = rng.standard_normal(len(x))
    W = int(0.032 * FS)
    x32 = window_mag_phase(x, donor, W)
    xall = window_mag_phase(x, donor, len(x))
    wav("morse", x)
    wav("morse_w32", x32)
    wav("morse_whole", xall)
    # timing score: correlation of the smoothed energy envelope with the keying envelope
    def envscore(y):
        k = np.ones(int(0.01 * FS)) / int(0.01 * FS)
        return corr(np.convolve(y ** 2, k, "same"), env)
    nums["morse_score"] = {"w32": envscore(x32), "whole": envscore(xall), "orig": envscore(x)}
    for name, y in (("morse", x), ("morse_w32", x32), ("morse_whole", xall)):
        spectrogram(y).save(os.path.join(OUT, f"spec_{name}.png"))
    nums["morse_len"] = len(x) / FS
    W32 = int(0.032 * FS)
    nums["morse_win_on"] = [round(float(env[i:i + W32].mean()), 3) for i in range(0, len(env) - W32 + 1, W32)]

    # pictures: Fourier swap and tile scrambles (noise donor >= 0, as in the phase page)
    A, B = picture_a(), picture_b()
    hyb = window_mag_phase2(A, B, S)  # magnitudes of A, phases of B
    to_png(A, os.path.join(OUT, "pic_a.png"))
    to_png(B, os.path.join(OUT, "pic_b.png"))
    to_png(hyb, os.path.join(OUT, "pic_magA_phB.png"), *np.percentile(hyb, [1, 99.5]))
    nums["swap_corr"] = {"with_A": corr(hyb, A), "with_B": corr(hyb, B)}
    pd = rng.uniform(0, 1, (S, S))
    nums["tile_corr"] = {}
    for b in (8, 16, 32, S):
        y = window_mag_phase2(B, pd, b)
        to_png(y, os.path.join(OUT, f"pic_b_tile{b}.png"), *np.percentile(y, [1, 99.5]))
        nums["tile_corr"][b] = corr(y, B)
    json.dump(nums, open(os.path.join(OUT, "numbers.json"), "w"), indent=1)
    print(json.dumps(nums, indent=1))


if __name__ == "__main__":
    main()
