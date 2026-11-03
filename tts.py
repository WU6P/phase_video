"""Synthesize one WAV per narration cue (Kokoro, local) -> audio[_zh]/<cue>.wav + durations.json.

English: Kokoro v1.0, voice af_heart, espeak phonemes.
Chinese (VLANG=zh): Kokoro v1.1-zh, voice zf_001, misaki ZHG2P(version 1.1) phonemes. English words inside the
Chinese text go to espeak; all-capital acronyms (QAM, QPSK, CW) are spelled letter by letter.

Clips are cached by a hash of (model, voice, speed, spoken text), so editing one line re-synthesizes only that line.
Leading/trailing silence is trimmed so the scene code alone decides the pauses.
"""
import hashlib
import json
import os

import numpy as np
import soundfile as sf
from kokoro_onnx import Kokoro

from lang import AUDIO, HERE, LANG
from narration import cues

MODEL = {"en": ("kokoro-v1.0.onnx", "voices-v1.0.bin", None, "af_heart"),
         "zh": ("kokoro-v1.1-zh.onnx", "voices-v1.1-zh.bin", "config-v1.1-zh.json", "zf_001")}[LANG]
VOICE, SPEED = MODEL[3], 1.0

# letter names in IPA (espeak reads a lone "A" as the article "a", so spell acronyms ourselves)
LETTER = {"A": "ˈeɪ", "C": "sˈiː", "K": "kˈeɪ", "M": "ˈɛm", "P": "pˈiː", "Q": "kjˈuː", "S": "ˈɛs", "W": "dˈʌbəljˌuː"}


def trim(x, sr, thresh=0.01, pad=0.04):
    idx = np.where(np.abs(x) > thresh)[0]
    if len(idx) == 0:
        return x
    a = max(0, idx[0] - int(pad * sr))
    b = min(len(x), idx[-1] + int(pad * sr))
    return x[a:b]


def make_speaker():
    m = lambda f: os.path.join(HERE, "models", f) if f else None
    k = Kokoro(m(MODEL[0]), m(MODEL[1]), vocab_config=m(MODEL[2]))
    if LANG == "en":
        return lambda text: k.create(text, voice=VOICE, speed=SPEED, lang="en-us")
    from misaki import zh

    def en(s):
        words = s.split()
        if all(w.isupper() and w.isalpha() for w in words):
            return " ".join(LETTER[c] for w in words for c in w)
        return k.tokenizer.phonemize(s, "en-us")
    g2p = zh.ZHG2P(version="1.1", en_callable=en)

    def say(text):
        ph, _ = g2p(text)
        assert "❓" not in ph, (text, ph)
        return k.create(ph, voice=VOICE, speed=SPEED, is_phonemes=True)
    return say


def main():
    os.makedirs(AUDIO, exist_ok=True)
    meta_p = os.path.join(AUDIO, "durations.json")
    meta = json.load(open(meta_p)) if os.path.exists(meta_p) else {}
    say = None
    for scene, cid, text, spoken in cues():
        key = f"{VOICE}|{SPEED}|{spoken}" if LANG == "en" else f"{MODEL[0]}|{VOICE}|{SPEED}|{spoken}"
        h = hashlib.sha256(key.encode()).hexdigest()[:16]
        wav = os.path.join(AUDIO, f"{cid}.wav")
        if meta.get(cid, {}).get("hash") == h and os.path.exists(wav):
            continue
        say = say or make_speaker()
        samples, sr = say(spoken)
        samples = trim(np.asarray(samples, dtype=np.float32), sr)
        sf.write(wav, samples, sr, subtype="PCM_16")
        meta[cid] = {"scene": scene, "hash": h, "duration": round(len(samples) / sr, 4), "text": text}
        print(f"{cid:8s} {meta[cid]['duration']:6.2f}s  {text[:70]}")
    live = {c[1] for c in cues()}
    meta = {c: v for c, v in meta.items() if c in live}
    json.dump(meta, open(meta_p, "w"), indent=1, ensure_ascii=False)
    print(f"total narration {sum(v['duration'] for v in meta.values()):.1f}s over {len(meta)} cues")


if __name__ == "__main__":
    main()
