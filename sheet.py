"""Contact sheet per scene: one frame near the end of each narration cue, captioned with the cue id,
so the layout can be reviewed without watching. Usage: sheet.py <quality-dir e.g. 480p15|1080p60> Scene..."""
import json
import os
import subprocess
import sys

from PIL import Image, ImageDraw

from lang import HERE, MEDIA, SUF, TIMING


def main():
    q, scenes = sys.argv[1], sys.argv[2:]
    os.makedirs(os.path.join(HERE, "sheets"), exist_ok=True)
    for sc in scenes:
        tm = json.load(open(os.path.join(TIMING, f"{sc}.json")))
        mp4 = os.path.join(MEDIA, "videos/scenes", q, f"{sc}.mp4")
        tiles = []
        for c in tm["cues"]:
            t = c["start"] + c["dur"] + 0.3
            png = os.path.join(HERE, "sheets", f"_{c['cue']}.png")
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{t:.2f}", "-i", mp4, "-frames:v", "1",
                            "-vf", "scale=640:-1", png], check=True)
            im = Image.open(png).convert("RGB")
            ImageDraw.Draw(im).text((8, 6), c["cue"], fill=(255, 80, 80))
            tiles.append(im)
            os.remove(png)
        w, h = tiles[0].size
        cols = 2
        rows = (len(tiles) + cols - 1) // cols
        sheet = Image.new("RGB", (cols * w + (cols - 1) * 6, rows * h + (rows - 1) * 6), (60, 60, 60))
        for i, im in enumerate(tiles):
            sheet.paste(im, ((i % cols) * (w + 6), (i // cols) * (h + 6)))
        out = os.path.join(HERE, "sheets", f"{sc}{SUF}.png")
        sheet.save(out)
        print(out)


if __name__ == "__main__":
    main()
