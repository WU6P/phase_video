"""Round-trip every narration clip through local speech recognition (oMLX Qwen3-ASR) and compare
with the subtitle text. Catches mispronounced or garbled words without anyone listening.
Writes audio/asr.json; prints cues whose word error rate exceeds the threshold.
"""
import json
import os
import re
import subprocess
import sys

from lang import AUDIO, HERE, LANG
from narration import cues

# an OpenAI-style /v1/audio/transcriptions server (here: oMLX with Qwen3-ASR); key from ASR_KEY or oMLX settings
_S = os.path.expanduser("~/.omlx/settings.json")
KEY = os.environ.get("ASR_KEY") or (json.load(open(_S))["auth"].get("api_key", "") if os.path.exists(_S) else "")
PORT = int(os.environ.get("ASR_PORT", 8001))

# spellings that mean the same thing when spoken
EQUIV = {"kwam": "qam", "quam": "qam", "q.a.m.": "qam", "q a m": "qam", "a.m.": "am", "c.w.": "cw", "c w": "cw",
         "q.p.s.k.": "qpsk", "q p s k": "qpsk", "wi-fi": "wifi", "wi fi": "wifi", "16-qam": "sixteen qam",
         "64-qam": "sixty four qam", "16 qam": "sixteen qam", "64 qam": "sixty four qam", "200": "two hundred",
         "100": "one hundred", "45": "forty five", "16.9": "sixteen point nine", "7.7": "seven point seven",
         "ohm's": "ohms", "90": "ninety", "32": "thirty two", "mhm": ""}

NUMS = {}


def norm_zh(s):
    """Chinese: compare characters. Numbers -> Chinese numerals, drop punctuation/space, Latin letters kept."""
    import cn2an
    s = cn2an.transform(s.replace("°", "度").replace("-", " "), "an2cn").lower()
    for a, b in (("wifi", "wi fi"), ("q a m", "qam"), ("q p s k", "qpsk"), ("c w", "cw")):
        s = s.replace(a, b)
    s = re.sub(r"[a-z]+", lambda m: " " + m.group(0) + " ", s)
    return [t for t in re.split(r"\s+|(?<![a-z])|(?![a-z])", re.sub(r"[^\w ]+", " ", s)) if t.strip()]


def norm(s):
    if LANG == "zh":
        return norm_zh(s)
    s = s.lower()
    for a, b in EQUIV.items():
        s = s.replace(a, b)
    s = re.sub(r"[^a-z0-9 ]+", " ", s.replace("-", " "))
    return [NUMS.get(w, w) for w in s.split()]


def wer(ref, hyp):
    d = list(range(len(hyp) + 1))
    for i, r in enumerate(ref, 1):
        prev, d[0] = d[0], i
        for j, h in enumerate(hyp, 1):
            prev, d[j] = d[j], min(d[j] + 1, d[j - 1] + 1, prev + (r != h))
    return d[-1] / max(1, len(ref))


def transcribe(path):
    out = subprocess.run(["curl", "-s", "-m", "120", "-H", f"Authorization: Bearer {KEY}", "-F", f"file=@{path}",
                          "-F", "model=Qwen3-ASR-1.7B-8bit", "-F", f"language={LANG}",
                          f"http://localhost:{PORT}/v1/audio/transcriptions"], capture_output=True, text=True).stdout
    return json.loads(out)["text"]


def main():
    thresh = float(sys.argv[1]) if len(sys.argv) > 1 else 0.10
    res, bad = {}, 0
    for scene, cid, text, spoken in cues():
        hyp = transcribe(os.path.join(AUDIO, f"{cid}.wav"))
        e = wer(norm(text), norm(hyp))
        res[cid] = {"text": text, "heard": hyp, "wer": round(e, 3)}
        if e > thresh:
            bad += 1
            print(f"[{cid}] WER {e:.2f}\n   script: {text}\n   heard:  {hyp}")
    json.dump(res, open(os.path.join(AUDIO, "asr.json"), "w"), indent=1, ensure_ascii=False)
    ws = [v["wer"] for v in res.values()]
    print(f"{len(ws)} clips, mean {'CER' if LANG == 'zh' else 'WER'} {sum(ws)/len(ws):.3f}, {bad} above {thresh}")


if __name__ == "__main__":
    main()
