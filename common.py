"""Shared look and the audio-sync mechanism for every scene.

Sync rule: `with self.cue("b_5") as d:` adds that cue's narration clip at the current scene time and
then guarantees the block lasts at least d + GAP seconds (it waits out any remainder). Animations inside
the block are timed against d. So each sentence starts exactly when its visuals start, by construction,
and timing/<Scene>.json records every cue's start for the subtitles and the sync check.
"""
import json
import os
import re
from contextlib import contextmanager

import manimpango
from manim import *

from lang import AUDIO, HERE, LANG, REPO, TIMING

for _f in ("cmunrm", "cmunbx", "cmunti", "cmuntt"):
    manimpango.register_font(os.path.join(HERE, "fonts", f"{_f}.otf"))

DUR = json.load(open(os.path.join(AUDIO, "durations.json")))
NUM = json.load(open(os.path.join(HERE, "assets", "numbers.json")))
SFX = NUM["sfx"]
GAP = 0.45  # breath between sentences

SERIF = "CMU Serif" if LANG == "en" else "Songti SC"  # zh: a font list falls back to a heavy sans; Songti has serif Latin too
MONO = "Menlo"
# 3Blue1Brown palette
BLUE3 = "#58C4DD"
YEL = "#FFFF00"
GOLD3 = "#F0AC5F"
GRN = "#83C167"
RED3 = "#FC6255"
TEAL3 = "#5CD0B3"
PURP = "#9A72AC"
GREY3 = "#888888"
DARK = "#1C1C1C"


if LANG == "zh":
    from zh_text import KEEP, ZH


def tr(s):
    """On-screen text in the build language. zh: every string with English words must have a translation
    (or be listed in KEEP), so no English label can slip through untranslated."""
    if LANG == "en" or s in KEEP:
        return s
    if s in ZH:
        return ZH[s]
    if re.search(r"[a-z]{3,}", s):
        raise KeyError(f"zh_text.py has no translation for {s!r}")
    return s


def T(s, size=40, color=WHITE, **kw):
    return Text(tr(s), font=SERIF, font_size=size, color=color, **kw)


def rt(x, lo=0.4):
    """A run time computed from a cue length, never below lo (the Chinese clips have other lengths)."""
    return max(lo, x)


def qr_code(data, size=3.6, dark=BLACK, light=WHITE):
    """QR code drawn as Manim rectangles (one per run of dark modules), with its 4-module quiet zone."""
    import segno
    rows = [list(r) for r in segno.make(data, error="m").matrix_iter(border=4)]
    n = len(rows)
    u = size / n
    g = VGroup(Square(size, stroke_width=0, fill_color=light, fill_opacity=1))
    for y, r in enumerate(rows):
        x = 0
        while x < n:
            if r[x]:
                x1 = x
                while x1 < n and r[x1]:
                    x1 += 1
                g.add(Rectangle(width=(x1 - x) * u + 0.008, height=u + 0.008, stroke_width=0, fill_color=dark,
                                fill_opacity=1).move_to([-size / 2 + (x + x1) / 2 * u, size / 2 - (y + 0.5) * u, 0]))
                x = x1
            else:
                x += 1
    return g


def M(s, size=24, color=WHITE, **kw):
    return Text(s, font=MONO, font_size=size, color=color, **kw)


def code_block(lines, size=20, color=WHITE, t2c=None, pad=0.25, line_gap=0.12):
    rows = VGroup(*[M(l.lstrip() if l.strip() else ".", size, color, t2c=t2c or {}) for l in lines])
    rows.arrange(DOWN, aligned_edge=LEFT, buff=line_gap)
    cw = M("0" * 40, size).width / 40  # monospace advance: restore the leading spaces Text drops
    for r, l in zip(rows, lines):
        if not l.strip():
            r.set_opacity(0)
        r.shift(RIGHT * cw * (len(l) - len(l.lstrip())))
    box = SurroundingRectangle(rows, buff=pad, corner_radius=0.12, stroke_color=GREY3, stroke_width=1.5,
                               fill_color=DARK, fill_opacity=1).set_z_index(-0.5)  # always behind its text
    g = VGroup(box, rows)
    g.rows = rows
    g.box = box
    return g


def check_mark(color=GRN, scale=1.0):
    m = VMobject(stroke_color=color, stroke_width=7 * scale)
    m.set_points_as_corners([LEFT * 0.18, DOWN * 0.16 + LEFT * 0.03, UP * 0.2 + RIGHT * 0.22])
    return m.scale(scale)


def cross_mark(color=RED3, scale=1.0):
    a = Line(UL * 0.16, DR * 0.16, stroke_color=color, stroke_width=7 * scale)
    b = Line(UR * 0.16, DL * 0.16, stroke_color=color, stroke_width=7 * scale)
    return VGroup(a, b).scale(scale)


def labeled_box(label, w=2.4, h=1.0, color=BLUE3, size=26, mono=False, fill=0.12, opaque=False):
    r = RoundedRectangle(width=w, height=h, corner_radius=0.12, stroke_color=color, stroke_width=3,
                         fill_color=interpolate_color(BLACK, ManimColor(color), fill) if opaque else color,
                         fill_opacity=1 if opaque else fill)
    t = (M if mono else T)(label, size, WHITE)
    if t.width > w * 0.9:
        t.scale_to_fit_width(w * 0.9)
    t.move_to(r).set_z_index(1)  # label stays above its box even after the box is re-added by .animate
    g = VGroup(r, t)
    g.rect, g.label = r, t
    return g


def envelope(w=2.2, h=1.4, color=GOLD3):
    body = Rectangle(width=w, height=h, stroke_color=color, stroke_width=3, fill_color="#2a2216", fill_opacity=1)
    tl, tr = body.get_corner(UL), body.get_corner(UR)
    flap = Polygon(tl, tr, body.get_center() + DOWN * 0.1, stroke_color=color, stroke_width=3,
                   fill_color="#3a2e1c", fill_opacity=1)
    seal = Dot(body.get_center() + DOWN * 0.1, radius=0.17, color=RED3)
    g = VGroup(body, flap, seal)
    g.body, g.flap, g.seal = body, flap, seal
    return g


def chip(label, sub, color=BLUE3, size=1.6):
    sq = Square(side_length=size, stroke_color=color, stroke_width=3, fill_color=color, fill_opacity=0.12)
    pins = VGroup()
    for i in range(5):
        off = (i - 2) * size / 6
        for side, d in ((LEFT, RIGHT), (RIGHT, LEFT)):
            p = sq.get_edge_center(side) + UP * off
            pins.add(Line(p, p + side * 0.22, stroke_color=color, stroke_width=3))
        for side in (UP, DOWN):
            p = sq.get_edge_center(side) + RIGHT * off
            pins.add(Line(p, p + side * 0.22, stroke_color=color, stroke_width=3))
    name = T(label, 30)
    if name.width > size * 0.82:
        name.scale_to_fit_width(size * 0.82)
    name.move_to(sq).shift(UP * 0.18)
    s = T(sub, 20, GREY_B).next_to(name, DOWN, buff=0.12)
    g = VGroup(sq, pins, name, s)
    g.body = sq
    return g


def score_badge(p, t, size=56):
    col = GRN if p == t else YEL
    s = T(f"{p} / {t}", size, col)
    return s


class VScene(Scene):
    def setup(self):
        self.cue_log = []
        self.sfx_log = []
        self.overruns = []

    def sfx(self, name):
        """Play assets/<name>.wav from now; logged so assemble.py mixes it into the rebuilt track. Returns its length."""
        d = SFX[name]
        self.add_sound(os.path.join(HERE, "assets", f"{name}.wav"))
        self.sfx_log.append({"sfx": name, "start": round(self.renderer.time, 4), "dur": d})
        return d

    @contextmanager
    def cue(self, cid, gap=GAP):
        info = DUR[cid]
        d = info["duration"]
        t0 = self.renderer.time
        self.add_sound(os.path.join(AUDIO, f"{cid}.wav"))
        self.cue_log.append({"cue": cid, "start": round(t0, 4), "dur": d, "text": info["text"]})
        yield d
        el = self.renderer.time - t0
        if el < d + gap:
            self.wait(d + gap - el)
        elif el > d + gap + 0.05:
            self.overruns.append({"cue": cid, "visual": round(el, 2), "audio": d})

    def chapter(self, letter, name, color=BLUE3, puzzle=None):
        """3b1b-style chapter card: title in the middle, then it settles into the top-left corner.
        puzzle=(n, question): the Intro puzzle this chapter answers, shown under the title first."""
        circ = Circle(radius=0.55, stroke_color=color, stroke_width=4, fill_color=color, fill_opacity=0.15)
        let = T(letter, 54, color).move_to(circ)
        nm = T(name, 54)
        g = VGroup(VGroup(circ, let), nm).arrange(RIGHT, buff=0.45)
        qt = None
        if puzzle:
            qt = VGroup(T(tr("Puzzle {}").format(puzzle[0]), 30, YEL), T(puzzle[1], 30, GREY_A)).arrange(RIGHT, buff=0.3)
            if qt.width > 13:
                qt.scale_to_fit_width(13)
            VGroup(g, qt).arrange(DOWN, buff=0.6)
        self.play(DrawBorderThenFill(circ), Write(let), Write(nm), run_time=1.0)
        if qt:
            self.play(FadeIn(qt, shift=UP * 0.15), run_time=0.5)
            self.wait(2.2)
            self.play(FadeOut(qt), g.animate.scale(0.5).to_corner(UL, buff=0.4), run_time=0.7)
        else:
            self.play(g.animate.scale(0.5).to_corner(UL, buff=0.4), run_time=0.7)
        self.chap = g
        return g

    def clear_stage(self, run_time=0.5, full=False):
        """Fade out everything; the chapter badge stays unless full=True."""
        keep = None if full else getattr(self, "chap", None)
        objs = [m for m in self.mobjects if m is not keep]
        if objs:
            self.play(FadeOut(Group(*objs)), run_time=run_time)

    def tear_down(self):
        os.makedirs(TIMING, exist_ok=True)
        json.dump({"scene": type(self).__name__, "duration": round(self.renderer.time, 4),
                   "cues": self.cue_log, "sfx": self.sfx_log, "overruns": self.overruns},
                  open(os.path.join(TIMING, f"{type(self).__name__}.json"), "w"), indent=1, ensure_ascii=False)
