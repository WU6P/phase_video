"""What notices a phase shift? One Scene per chapter, narrated (narration.py), with demo sounds (dsp.py).

Pictures, spectrograms and sounds come from assets/ (dsp.py); the QAM angles are computed here from the
constellation geometry and checked against ../phase/core.js by test_dsp.py.

Render:  .venv/bin/manim -qh --disable_caching scenes.py <Scene>
"""
import os

import numpy as np

from common import *

A = lambda n: os.path.join(HERE, "assets", n)
TAU_ = 2 * np.pi


def rule_card(n, text, color=YEL, size=34):
    head = T(tr("Rule {}").format(n), size, color)
    body = T(text, size)
    g = VGroup(head, body).arrange(RIGHT, buff=0.35).set_z_index(1)
    box = SurroundingRectangle(g, buff=0.25, corner_radius=0.15, stroke_color=color, stroke_width=2.5,
                               fill_color=DARK, fill_opacity=1).set_z_index(0.5)
    return VGroup(box, g).to_edge(DOWN, buff=0.35)


def speaker(color=WHITE, s=0.5):
    body = Polygon([-0.5, 0.2, 0], [-0.2, 0.2, 0], [0.15, 0.5, 0], [0.15, -0.5, 0], [-0.2, -0.2, 0], [-0.5, -0.2, 0],
                   stroke_color=color, stroke_width=3, fill_color=color, fill_opacity=0.25)
    waves = VGroup(*[Arc(radius=r, start_angle=-0.7, angle=1.4, stroke_color=color, stroke_width=3).shift(RIGHT * 0.1)
                     for r in (0.35, 0.6, 0.85)])
    return VGroup(body, waves).scale(s)


def flat_axes(xr, yr, w, h, color=GREY3):
    return Axes(x_range=xr, y_range=yr, x_length=w, y_length=h,
                axis_config={"color": color, "include_tip": False, "include_ticks": False, "stroke_width": 2})


def harmonic_sum(ns, phases, amps=None):
    amps = amps or [1.0] * len(ns)
    return lambda x: sum(a * np.cos(TAU_ * n * x + p) for n, a, p in zip(ns, amps, phases))


# ----------------------------------------------------------------------------------------------- Intro
PUZZLES = ["Can anyone measure the phase of a single wave?",
           "No camera sees the phase of light. So how do two beams make fringes?",
           "Scramble the phases of a sound: does it sound different?",
           "Why do phases carry a picture, but hardly matter for sound?",
           "Why does 64-QAM fail under 8°, while AM radio never notices?"]
CREDIT = "by Nianfeng Li & Claude Code"
DATE = "November 2026"


def puzzle_rows(texts, size=30):
    rows = VGroup(*[VGroup(T(f"{i + 1}", size + 2, YEL), T(q, size)).arrange(RIGHT, buff=0.35) for i, q in enumerate(texts)])
    rows.arrange(DOWN, buff=0.42, aligned_edge=LEFT)
    if rows.width > 13:
        rows.scale_to_fit_width(13)
    return rows


class Intro(VScene):
    def cover(self):
        """Title card, fully drawn from the first frame (so it is also the thumbnail)."""
        title = T("What notices a phase shift?", 64)
        sub = T("five rules, five puzzles", 32, GREY_B)
        ax = flat_axes([0, 2, 1], [-1.2, 1.2, 1], 6.0, 1.3)
        w1 = ax.plot(lambda x: np.cos(TAU_ * x), x_range=[0, 2, 0.01], color=GREY3, stroke_width=3)
        w2 = ax.plot(lambda x: np.cos(TAU_ * (x - 0.22)), x_range=[0, 2, 0.01], color=BLUE3, stroke_width=5)
        who = T(CREDIT, 34, BLUE3)
        when = T(DATE, 28, GREY_B)
        card = VGroup(title, sub, VGroup(w1, w2), who, when).arrange(DOWN, buff=0.45)
        card[3].shift(DOWN * 0.2)
        card[4].next_to(card[3], DOWN, buff=0.25)
        card.move_to(ORIGIN)
        self.add(card)
        self.wait(4.0)
        self.play(FadeOut(card), run_time=0.8)

    def construct(self):
        self.cover()
        ax = flat_axes([0, 3, 1], [-1.3, 1.3, 1], 10, 2.8).shift(UP * 0.4)
        phi = ValueTracker(0)
        ref = ax.plot(lambda x: np.cos(TAU_ * x), x_range=[0, 3, 0.01], color=GREY3, stroke_width=3)
        wave = always_redraw(lambda: ax.plot(lambda x: np.cos(TAU_ * (x - phi.get_value())), x_range=[0, 3, 0.01],
                                             color=BLUE3, stroke_width=5))
        with self.cue("i_1") as d:
            self.play(Create(ax), Create(wave), run_time=1.5)
            self.add(ref)
            self.play(phi.animate.set_value(0.22), run_time=1.8)
            p0, p1 = ax.c2p(1, 1.15), ax.c2p(1.22, 1.15)
            br = DoubleArrow(p0, p1, buff=0, stroke_width=3, color=YEL, tip_length=0.15)
            lab = T("φ", 40, YEL, slant=ITALIC).next_to(br, UP, buff=0.1)
            self.play(GrowFromCenter(br), Write(lab), run_time=0.8)
        top = VGroup(ax, ref, wave, br, lab)
        with self.cue("i_2"):
            q = T("Who can tell?", 60, YEL).to_edge(DOWN, buff=1.2)
            self.play(Write(q), run_time=1.0)
        with self.cue("i_3") as d:
            self.play(FadeOut(q), top.animate.scale(0.5).to_edge(UP, buff=0.3), run_time=0.8)
            hl = T("does not notice", 36, GRN).move_to(LEFT * 3.4 + UP * 1.1)
            hr = T("notices", 36, RED3).move_to(RIGHT * 3.4 + UP * 1.1)
            line = Line(UP * 1.5, DOWN * 3.2, stroke_color=GREY3, stroke_width=2)
            self.play(FadeIn(hl), FadeIn(hr), Create(line), run_time=0.6)
            items = ["your ear (mostly)", "your eye", "an AM radio", "a Morse (CW) receiver"]
            col = VGroup(*[T(s, 32) for s in items]).arrange(DOWN, buff=0.32).next_to(hl, DOWN, buff=0.45)
            for i, it in enumerate(col):
                self.play(FadeIn(it, shift=RIGHT * 0.2), run_time=0.5)
                self.wait([0.3, 0.6, 0.9, 0.2][i])
        with self.cue("i_4") as d:
            qam = T("a QAM modem (Wi-Fi)", 32).next_to(hr, DOWN, buff=0.45)
            few = T("off by a few degrees → errors", 26, GREY_B).next_to(qam, DOWN, buff=0.3)
            self.play(FadeIn(qam, shift=LEFT * 0.2), run_time=0.6)
            self.wait(1.5)
            self.play(FadeIn(few), run_time=0.6)
        with self.cue("i_q0") as d:
            self.clear_stage(run_time=0.6)
            head = T("Five puzzles", 52, YEL).to_edge(UP, buff=0.7)
            self.play(Write(head), run_time=0.9)
        rows = puzzle_rows(PUZZLES).next_to(head, DOWN, buff=0.7)
        for i, r in enumerate(rows):
            with self.cue(f"i_q{i + 1}") as d:
                self.play(FadeIn(r, shift=RIGHT * 0.2), run_time=0.6)
        with self.cue("i_5") as d:
            self.play(rows.animate.set_opacity(0.3), run_time=0.6)
            self.clear_stage(run_time=0.6)
            title = T("What notices a phase shift?", 60)
            self.play(Write(title), run_time=1.3)
            dots = VGroup(*[VGroup(Circle(0.32, stroke_color=YEL, stroke_width=3), T(str(i + 1), 30, YEL))
                            for i in range(5)]).arrange(RIGHT, buff=0.5).next_to(title, DOWN, buff=0.8)
            for c in dots:
                c[1].move_to(c[0])
            five = T("five rules", 30, GREY_B).next_to(dots, DOWN, buff=0.3)
            self.play(LaggedStart(*[GrowFromCenter(c) for c in dots], lag_ratio=0.2), FadeIn(five), run_time=1.4)
        self.clear_stage(run_time=0.6, full=True)


# ---------------------------------------------------------------------------------------------- Phasor
class Phasor(VScene):
    def construct(self):
        self.chapter("1", "Only differences count", puzzle=(1, PUZZLES[0]))
        C, R = LEFT * 4.4 + DOWN * 0.4, 1.45
        W = 2 * PI / 2.0                       # one turn every 2 s of tracker time
        x0, L, lam = -2.3, 8.6, 3.2            # wave starts at x0, spans L, wavelength lam
        t = ValueTracker(0)
        ph0 = 50 * DEGREES
        ang = lambda off=0: W * t.get_value() + ph0 + off
        tip = lambda off=0: C + R * np.array([np.cos(ang(off)), np.sin(ang(off)), 0])
        circ = Circle(R, stroke_color=GREY3, stroke_width=2).move_to(C)
        hax = Line(C + LEFT * (R + 0.3), C + RIGHT * (R + 0.3), stroke_color=GREY3, stroke_width=1.5)
        base = Line([x0, C[1], 0], [x0 + L, C[1], 0], stroke_color=GREY3, stroke_width=1.5)

        def wave(off=0, color=BLUE3):
            return ParametricFunction(lambda s: np.array([x0 + s, C[1] + R * np.sin(ang(off) - TAU_ * s / lam), 0]),
                                      t_range=[0, L, 0.02], color=color, stroke_width=4)

        arrow = always_redraw(lambda: Arrow(C, tip(), buff=0, color=BLUE3, stroke_width=6, max_tip_length_to_length_ratio=0.15))
        shadow = always_redraw(lambda: DashedLine(tip(), [x0, tip()[1], 0], stroke_color=GREY_B, stroke_width=2))
        w1 = always_redraw(lambda: wave())
        dot = always_redraw(lambda: Dot([x0, tip()[1], 0], radius=0.07, color=YEL))
        with self.cue("p_1") as d:
            self.play(Create(circ), Create(hax), Create(base), GrowArrow(arrow), run_time=1.0)
            self.add(shadow, w1, dot)
            self.play(t.animate.set_value(4.0), run_time=rt(d - 1.0), rate_func=linear)  # two full turns: back to ph0
        with self.cue("p_2") as d:
            t.set_value(0)
            arc = always_redraw(lambda: Arc(radius=0.55, start_angle=0, angle=ang(), arc_center=C, color=YEL, stroke_width=4))
            lab = always_redraw(lambda: T("φ", 38, YEL, slant=ITALIC).move_to(
                C + 0.85 * np.array([np.cos(ang() / 2), np.sin(ang() / 2), 0])))
            clock = T("clock starts: t = 0", 28, GREY_B).next_to(circ, UP, buff=0.35)
            self.play(Create(arc), Write(lab), FadeIn(clock), run_time=1.0)
        with self.cue("p_3") as d:
            clock2 = T("start it later", 28, YEL).move_to(clock)
            self.play(FadeOut(clock, shift=UP * 0.2), FadeIn(clock2, shift=UP * 0.2), run_time=0.6)
            self.play(t.animate.set_value(0.4), run_time=2.0)
            same = T("the wave itself: unchanged", 28, GREY_B).move_to([x0 + L / 2, C[1] + R + 0.9, 0])
            self.play(FadeIn(same), run_time=0.8)
        with self.cue("p_4") as d:
            off = -75 * DEGREES
            arrow2 = always_redraw(lambda: Arrow(C, tip(off), buff=0, color=GOLD3, stroke_width=6,
                                                 max_tip_length_to_length_ratio=0.15))
            w2 = always_redraw(lambda: wave(off, GOLD3))
            darc = always_redraw(lambda: Arc(radius=0.75, start_angle=ang(off), angle=-off, arc_center=C, color=WHITE,
                                             stroke_width=4))
            dlab = always_redraw(lambda: T("Δφ", 34, WHITE, slant=ITALIC).move_to(
                C + 1.15 * np.array([np.cos(ang(off / 2)), np.sin(ang(off / 2)), 0])))
            self.play(FadeOut(arc), FadeOut(lab), FadeOut(clock2), FadeOut(same), run_time=0.5)
            self.play(GrowArrow(arrow2), Create(w2), run_time=0.8)
            self.add(darc, dlab)
            note = T("Δφ stays the same while both spin: that you can measure", 28, YEL).to_edge(UP, buff=1.1)
            self.play(FadeIn(note), t.animate.set_value(0.4 + rt(d - 1.6) / 2), run_time=rt(d - 1.3), rate_func=linear)
        with self.cue("p_5") as d:
            card = rule_card(1, "Only phase differences are measurable.")
            self.play(FadeIn(card, shift=UP * 0.3), t.animate.set_value(t.get_value() + d / 2), run_time=d, rate_func=linear)
        self.clear_stage(run_time=0.6, full=True)


# ----------------------------------------------------------------------------------------------- Light
class Light(VScene):
    def construct(self):
        self.chapter("2", "Square law", puzzle=(2, PUZZLES[1]))
        C, R = LEFT * 3.6 + DOWN * 0.3, 1.5
        t = ValueTracker(0)
        tip = lambda: C + R * np.array([np.cos(t.get_value()), np.sin(t.get_value()), 0])
        circ = Circle(R, stroke_color=GREY3, stroke_width=2).move_to(C)
        arrow = always_redraw(lambda: Arrow(C, tip(), buff=0, color=BLUE3, stroke_width=6, max_tip_length_to_length_ratio=0.15))
        freq = T("about 5 × 10¹⁴ turns per second", 28, GREY_B).next_to(circ, UP, buff=0.4)
        det = labeled_box("detector", 2.6, 1.0, GOLD3, 30).move_to(RIGHT * 3.2 + UP * 1.0)
        meter_bg = Rectangle(width=2.6, height=0.35, stroke_color=GREY3, stroke_width=2).next_to(det, DOWN, buff=0.4)
        meter = Rectangle(width=2.6 * 0.8, height=0.35, stroke_width=0, fill_color=YEL, fill_opacity=0.9)
        meter.align_to(meter_bg, LEFT).align_to(meter_bg, DOWN)
        mlab = T("energy = |E|²  (steady)", 28).next_to(meter_bg, DOWN, buff=0.25)
        beam = Arrow(circ.get_right() + RIGHT * 0.2, det.get_left() + LEFT * 0.1, buff=0.1, color=GREY_B, stroke_width=3)
        with self.cue("l_1") as d:
            self.play(Create(circ), GrowArrow(arrow), run_time=0.8)
            self.play(t.animate.set_value(TAU_ * 2), FadeIn(freq), run_time=2.0, rate_func=linear)
            self.play(GrowArrow(beam), FadeIn(det), run_time=0.8)
            self.play(t.animate.set_value(TAU_ * 6), FadeIn(meter_bg), GrowFromEdge(meter, LEFT), Write(mlab),
                      run_time=rt(d - 3.6), rate_func=linear)
        with self.cue("l_2") as d:
            def sq():
                v = tip() - C
                p = np.array([-v[1], v[0], 0])
                return Polygon(C, C + v, C + v + p, C + p, stroke_color=YEL, stroke_width=2, fill_color=YEL,
                               fill_opacity=0.25)
            square = always_redraw(sq)
            alab = T("area = length²: the same at every angle", 28, YEL).next_to(circ, DOWN, buff=1.6).shift(RIGHT * 0.5)
            self.add(square)
            self.play(FadeIn(alab), t.animate.set_value(TAU_ * 7.5), run_time=d * 0.45, rate_func=linear)
            card = rule_card(2, "Square-law detectors are blind to phase.")
            self.play(FadeOut(alab), FadeIn(card, shift=UP * 0.3), t.animate.set_value(TAU_ * 9), run_time=rt(d * 0.55 - 0.2),
                      rate_func=linear)
        self.clear_stage(run_time=0.6)

        # two beams: arrows add first
        O = LEFT * 4.8 + DOWN * 0.3
        dphi = ValueTracker(0.0)
        base = ValueTracker(0.3)
        ra, rb = 1.4, 1.4
        a_tip = lambda: O + ra * np.array([np.cos(base.get_value()), np.sin(base.get_value()), 0])
        b_tip = lambda: a_tip() + rb * np.array([np.cos(base.get_value() + dphi.get_value()),
                                                np.sin(base.get_value() + dphi.get_value()), 0])
        aa = always_redraw(lambda: Arrow(O, a_tip(), buff=0, color=BLUE3, stroke_width=6, max_tip_length_to_length_ratio=0.15))
        bb = always_redraw(lambda: Arrow(a_tip(), b_tip(), buff=0, color=GOLD3, stroke_width=6, max_tip_length_to_length_ratio=0.15))
        ss = always_redraw(lambda: Arrow(O, b_tip(), buff=0, color=WHITE, stroke_width=4, max_tip_length_to_length_ratio=0.1)
                           if np.linalg.norm(b_tip() - O) > 0.05 else VectorizedPoint(O))
        la = T("beam A", 26, BLUE3).move_to(O + DOWN * 0.6 + RIGHT * 0.4)
        lb = T("beam B", 26, GOLD3).move_to(O + DOWN * 1.0 + RIGHT * 0.4)
        bar_bg = Rectangle(width=0.6, height=3.6, stroke_color=GREY3, stroke_width=2).move_to(RIGHT * 4.6 + DOWN * 0.3)
        bar = always_redraw(lambda: Rectangle(width=0.6, height=max(0.001, 3.6 * (2 + 2 * np.cos(dphi.get_value())) / 4),
                                              stroke_width=0, fill_color=YEL, fill_opacity=0.9).move_to(bar_bg.get_bottom(), aligned_edge=DOWN))
        blab = T("|A + B|²", 30).next_to(bar_bg, UP, buff=0.25)
        form = T("|A + B|² = |A|² + |B|² + 2|A||B| cos Δφ", 32).to_edge(UP, buff=1.1)
        dval = always_redraw(lambda: T(f"Δφ = {np.degrees(dphi.get_value()):.0f}°", 30, YEL).next_to(bar_bg, LEFT, buff=0.6))
        with self.cue("l_3") as d:
            self.play(GrowArrow(aa), FadeIn(la), run_time=0.7)
            self.play(GrowArrow(bb), FadeIn(lb), run_time=0.7)
            self.add(ss)
            self.play(FadeIn(bar_bg), FadeIn(bar), Write(blab), FadeIn(dval), run_time=0.8)
            self.play(Write(form), run_time=1.6)
            self.play(dphi.animate.set_value(0.6), run_time=1.0)
        with self.cue("l_4") as d:
            self.play(dphi.animate.set_value(0.0), run_time=0.8)
            inph = T("in phase: bright", 28, GRN).next_to(form, DOWN, buff=0.35)
            self.play(FadeIn(inph), run_time=0.5)
            self.wait(0.6)
            self.play(dphi.animate.set_value(PI), run_time=1.8)
            out = T("half a cycle apart: dark", 28, RED3).move_to(inph)
            self.play(FadeOut(inph), FadeIn(out), run_time=0.5)
        self.clear_stage(run_time=0.5)

        # fringes on a screen
        gA, gB = ValueTracker(0.0), ValueTracker(0.0)
        n, Wd, H = 140, 11.0, 1.6
        xs = np.linspace(-Wd / 2, Wd / 2, n)

        def fringes():
            g = VGroup()
            for x in xs:
                i = 0.5 + 0.5 * np.cos(TAU_ * x / 2.2 + gB.get_value() - gA.get_value())
                g.add(Rectangle(width=Wd / n + 0.01, height=H, stroke_width=0, fill_color=YEL, fill_opacity=0.05 + 0.9 * i)
                      .move_to([x, 1.5, 0]))
            return g
        fr = always_redraw(fringes)
        frame = Rectangle(width=Wd, height=H, stroke_color=GREY3, stroke_width=2).move_to(UP * 1.5)
        scr = T("screen", 26, GREY_B).next_to(frame, UP, buff=0.15)

        def dial(tr, pos, color, name):
            c = Circle(0.6, stroke_color=GREY3, stroke_width=2).move_to(pos)
            a = always_redraw(lambda: Arrow(pos, pos + 0.6 * np.array([np.cos(tr.get_value()), np.sin(tr.get_value()), 0]),
                                            buff=0, color=color, stroke_width=5, max_tip_length_to_length_ratio=0.25))
            return VGroup(c, a, T(name, 24, color).next_to(c, DOWN, buff=0.15))
        dA = dial(gA, LEFT * 1.6 + DOWN * 0.8, BLUE3, "phase of A")
        dB = dial(gB, RIGHT * 1.6 + DOWN * 0.8, GOLD3, "phase of B")
        with self.cue("l_5") as d:
            self.play(FadeIn(frame), FadeIn(scr), FadeIn(fr), FadeIn(dA), FadeIn(dB), run_time=1.0)
            both = T("shift both: the fringes stay", 28, GRN).to_edge(DOWN, buff=0.5)
            self.play(FadeIn(both), run_time=0.4)
            self.play(gA.animate.set_value(TAU_), gB.animate.set_value(TAU_), run_time=2.6, rate_func=smooth)
            one = T("shift one: they move", 28, RED3).to_edge(DOWN, buff=0.5)
            self.play(FadeOut(both), FadeIn(one), run_time=0.4)
            self.play(gB.animate.set_value(TAU_ * 2), run_time=2.6, rate_func=smooth)
            r1 = T("(rule 1 again)", 28, YEL).next_to(one, RIGHT, buff=0.3)
            self.play(FadeIn(r1), run_time=0.4)
        self.clear_stage(run_time=0.6, full=True)


# ----------------------------------------------------------------------------------------------- Kinds
class Kinds(VScene):
    def construct(self):
        self.chapter("3", "Delay or shape?")
        ns = list(range(1, 7))
        tau, c = ValueTracker(0.0), ValueTracker(0.0)
        phases = lambda: [-TAU_ * n * tau.get_value() + c.get_value() for n in ns]
        top = flat_axes([-0.35, 1.85, 1], [-3.5, 6.5, 1], 11.5, 2.6).move_to(UP * 1.6)
        wave = always_redraw(lambda: top.plot(lambda x: harmonic_sum(ns, phases())(x), x_range=[-0.35, 1.85, 0.004],
                                              color=BLUE3, stroke_width=4))
        wl = T("the sum of six harmonics", 26, GREY_B).next_to(top, UP, buff=0.05).align_to(top, RIGHT)
        # magnitude bars (left) and phase plot (right)
        mag = flat_axes([0, 7, 1], [0, 1.3, 1], 4.0, 2.0).move_to(LEFT * 4.0 + DOWN * 2.6)
        bars = VGroup(*[Rectangle(width=0.35, height=mag.c2p(0, 1)[1] - mag.c2p(0, 0)[1], stroke_width=0,
                                  fill_color=TEAL3, fill_opacity=0.9).move_to(mag.c2p(n, 0.5)) for n in ns])
        ml = T("magnitude", 26, TEAL3).next_to(mag, UP, buff=0.1)
        pax = flat_axes([0, 7, 1], [-8, 2.2, 1], 5.0, 2.4).move_to(RIGHT * 3.6 + DOWN * 2.45)
        pdots = always_redraw(lambda: VGroup(*[Dot(pax.c2p(n, p), radius=0.09, color=YEL) for n, p in zip(ns, phases())]))
        pl = T("phase of each harmonic", 26, YEL).next_to(pax, UP, buff=0.1)
        fl = T("frequency →", 22, GREY_B).next_to(pax, DOWN, buff=0.1).align_to(pax, RIGHT)
        with self.cue("k_1") as d:
            self.play(Create(mag), LaggedStart(*[GrowFromEdge(b, DOWN) for b in bars], lag_ratio=0.15), FadeIn(ml), run_time=1.6)
            self.play(Create(pax), FadeIn(pdots), FadeIn(pl), FadeIn(fl), run_time=1.2)
            self.play(Create(top), Create(wave), FadeIn(wl), run_time=2.0)
        with self.cue("k_2") as d:
            line = always_redraw(lambda: Line(pax.c2p(0, c.get_value()), pax.c2p(6.6, -TAU_ * 6.6 * tau.get_value() + c.get_value()),
                                              stroke_color=GREY_B, stroke_width=2))
            self.add(line)
            self.play(tau.animate.set_value(0.2), run_time=d * 0.55)
            lab = VGroup(T("a straight line", 24, GREY_B), T("through zero", 24, GREY_B)).arrange(DOWN, buff=0.08, aligned_edge=LEFT)
            lab.move_to(pax.c2p(0.3, -6.6), aligned_edge=LEFT)
            self.play(FadeIn(lab), run_time=0.6)
        with self.cue("k_3") as d:
            m0 = DashedLine(top.c2p(0, -3.5), top.c2p(0, 6.5), stroke_color=GREY3, stroke_width=2)
            m1 = Arrow(top.c2p(0, 5.8), top.c2p(0.2, 5.8), buff=0, color=YEL, stroke_width=4, max_tip_length_to_length_ratio=0.3)
            dl = T("delay", 26, YEL).next_to(m1, RIGHT, buff=0.15)
            self.play(Create(m0), GrowArrow(m1), FadeIn(dl), run_time=1.2)
        with self.cue("k_4") as d:
            card = rule_card(3, "Phase linear in frequency is only a delay.", size=30).move_to(DOWN * 0.2)
            self.play(FadeIn(card, shift=UP * 0.3), run_time=1.0)
        with self.cue("k_5") as d:
            self.play(FadeOut(card), FadeOut(lab), FadeOut(m0), FadeOut(m1), FadeOut(dl), 
                      tau.animate.set_value(0), run_time=1.4)
            self.wait(1.2)
            self.play(c.animate.set_value(PI / 2), run_time=2.4)
            n90 = T("+90° on every harmonic:", 24, GREY_B).move_to(pax.c2p(0.4, -2.6), aligned_edge=LEFT)
            n91 = T("not a line through zero", 24, GREY_B).next_to(n90, DOWN, buff=0.1, aligned_edge=LEFT)
            n90 = VGroup(n90, n91)
            self.play(FadeIn(n90), run_time=0.6)
        with self.cue("k_6") as d:
            self.play(Indicate(bars, color=WHITE, scale_factor=1.08), run_time=1.4)
            same = T("magnitudes: unchanged in every case", 24, TEAL3).move_to(ml)
            self.play(FadeOut(ml), FadeIn(same), run_time=0.6)
            self.wait(1.5)
            q = T("What notices the shape?", 34, YEL).move_to(DOWN * 0.35)
            self.play(Write(q), run_time=1.2)
        self.clear_stage(run_time=0.6, full=True)


# ------------------------------------------------------------------------------------------------- Ear
def erb(f):
    return 24.7 * (4.37 * f / 1000 + 1)


class Ear(VScene):
    def listen(self, name, target):
        """Play a demo sound with a pulsing speaker next to `target`; then leave silence before the next cue."""
        sp = speaker(YEL, 0.7).next_to(target, LEFT, buff=0.35)
        self.add(sp)
        dur = self.sfx(name)
        self.play(Indicate(sp, color=YEL, scale_factor=1.2), run_time=dur, rate_func=there_and_back_with_pause)
        self.remove(sp)
        self.wait(0.6)

    def construct(self):
        self.chapter("4", "Separate bands", puzzle=(3, PUZZLES[2]))
        ns = list(range(1, 7))
        rph = NUM["low_rand_phases"]
        ax = flat_axes([0, 15, 5], [-6.5, 6.5, 1], 8.0, 3.0).move_to(UP * 1.0 + RIGHT * 0.8)
        f_cos = harmonic_sum(ns, [0] * 6)
        f_rnd = harmonic_sum(ns, rph)
        wcos = ax.plot(lambda ms: f_cos(ms / 5), x_range=[0, 15, 0.02], color=BLUE3, stroke_width=4)
        wrnd = ax.plot(lambda ms: f_rnd(ms / 5), x_range=[0, 15, 0.02], color=GOLD3, stroke_width=4)
        tl = T("15 ms", 22, GREY_B).next_to(ax, DOWN, buff=0.1).align_to(ax, RIGHT)
        mag = flat_axes([0, 7, 1], [0, 1.3, 1], 3.6, 1.6).move_to(DOWN * 2.2 + RIGHT * 0.8)
        bars = VGroup(*[Rectangle(width=0.3, height=mag.c2p(0, 1)[1] - mag.c2p(0, 0)[1], stroke_width=0, fill_color=TEAL3,
                                  fill_opacity=0.9).move_to(mag.c2p(n, 0.5)) for n in ns])
        ml = T("200, 400 … 1200 Hz, equal strength", 22, TEAL3).next_to(mag, DOWN, buff=0.15)
        nm = T("cosine phase", 30, BLUE3).next_to(ax, UP, buff=0.2)
        with self.cue("e_1") as d:
            self.play(Create(ax), Create(wcos), FadeIn(nm), FadeIn(tl), run_time=1.6)
            self.play(Create(mag), LaggedStart(*[GrowFromEdge(b, DOWN) for b in bars], lag_ratio=0.1), FadeIn(ml), run_time=1.4)
        self.listen("low_cos", ax)
        with self.cue("e_2") as d:
            nm2 = T("random phases", 30, GOLD3).next_to(ax, UP, buff=0.2)
            self.play(Transform(wcos, wrnd), FadeOut(nm), FadeIn(nm2), run_time=1.6)
            self.play(Indicate(bars, color=WHITE, scale_factor=1.05), run_time=1.2)
        self.listen("low_rand", ax)
        with self.cue("e_3") as d:
            same = T("≈ the same sound", 40, YEL).move_to(ax.get_center())
            self.play(wcos.animate.set_opacity(0.25), FadeIn(same, scale=1.2), run_time=0.8)
            self.wait(1.4)
            ohm = T("Ohm's acoustic law: the ear hears the magnitude spectrum", 30).move_to(nm2)
            self.play(FadeOut(nm2), Write(ohm), run_time=1.6)
        self.clear_stage(run_time=0.5)

        # the cochlea as a filter bank on a linear frequency axis 0..3.2 kHz
        fx = flat_axes([0, 3200, 400], [0, 1.15, 1], 12.4, 2.4).move_to(DOWN * 0.6)
        flab = T("frequency  0 … 3.2 kHz", 24, GREY_B).next_to(fx, DOWN, buff=0.15).align_to(fx, LEFT)

        def bump(fc, color=TEAL3, op=0.18):
            s = erb(fc) / np.sqrt(TAU_)
            return fx.plot(lambda f: np.exp(-0.5 * ((f - fc) / s) ** 2), x_range=[max(0, fc - 4 * s), fc + 4 * s, 2],
                           color=color, stroke_width=3).set_fill(color, op)

        def hline(f, color=YEL, h=1.0):
            return Line(fx.c2p(f, 0), fx.c2p(f, h), stroke_color=color, stroke_width=4)
        low = VGroup(*[hline(200 * n) for n in ns])
        fb = VGroup(*[bump(200 * n) for n in ns])
        meters = VGroup()
        for n in ns:
            p = fx.c2p(200 * n, 1.35)
            meters.add(VGroup(Rectangle(width=0.18, height=0.9, stroke_color=GREY3, stroke_width=1.5).move_to(p + UP * 0.45),
                              Rectangle(width=0.18, height=0.7, stroke_width=0, fill_color=YEL, fill_opacity=0.9)
                              .move_to(p + UP * 0.35)))
        el = T("each filter reports its energy", 26, YEL).next_to(meters, UP, buff=0.25).align_to(fx, LEFT)
        coch = T("cochlea = a bank of filters", 30).to_edge(UP, buff=1.0)
        with self.cue("e_4") as d:
            self.play(Create(fx), FadeIn(flab), FadeIn(coch), run_time=1.2)
            self.play(LaggedStart(*[Create(l) for l in low], lag_ratio=0.1), run_time=1.0)
            self.play(LaggedStart(*[FadeIn(b) for b in fb], lag_ratio=0.15), run_time=1.8)
            self.wait(1.0)
            self.play(LaggedStart(*[FadeIn(m, shift=UP * 0.1) for m in meters], lag_ratio=0.1), FadeIn(el), run_time=1.4)
        with self.cue("e_5") as d:
            gap = DoubleArrow(fx.c2p(400, 1.12), fx.c2p(600, 1.12), buff=0.05, color=RED3, stroke_width=3, tip_length=0.15)
            nm = T("never meet", 26, RED3).next_to(gap, UP, buff=0.12)
            self.play(FadeOut(meters), FadeOut(el), run_time=0.6)
            self.wait(0.9)
            self.play(GrowFromCenter(gap), FadeIn(nm), run_time=0.8)
            self.wait(1.5)
            card = rule_card(4, "Components in different bands cannot interfere.", size=30)
            self.play(FadeIn(card, shift=UP * 0.3), run_time=0.8)
        with self.cue("e_6") as d:
            self.play(FadeOut(card), FadeOut(gap), FadeOut(nm), run_time=0.6)
            hi = VGroup(*[hline(100 * n, GOLD3, 0.8) for n in range(20, 31)])
            hb = VGroup(*[bump(fc, PURP, 0.12) for fc in (2100, 2500, 2900)])
            self.play(LaggedStart(*[Create(l) for l in hi], lag_ratio=0.08), run_time=1.4)
            wl = T("wider filters up here", 24, PURP).next_to(fx.c2p(2500, 1.0), UP, buff=0.2)
            self.play(LaggedStart(*[FadeIn(b) for b in hb], lag_ratio=0.2), FadeIn(wl), run_time=1.6)
            box = SurroundingRectangle(VGroup(hi[4], hi[6]), buff=0.12, color=YEL, stroke_width=3)
            three = T("three harmonics in one filter", 24, YEL).next_to(box, DOWN, buff=0.15)
            self.wait(1.0)
            self.play(Create(box), FadeIn(three), run_time=0.8)
        self.clear_stage(run_time=0.5)

        nh = list(range(20, 31))
        bx = flat_axes([0, 30, 10], [-12, 12, 1], 9.0, 3.2).move_to(UP * 0.3 + RIGHT * 0.6)
        hcos = bx.plot(lambda ms: harmonic_sum(nh, [0] * 11)(ms / 10), x_range=[0, 30, 0.01], color=BLUE3, stroke_width=2.5)
        rng = np.random.default_rng(3)
        hph = rng.uniform(0, TAU_, 11)
        hrnd = bx.plot(lambda ms: harmonic_sum(nh, list(hph))(ms / 10), x_range=[0, 30, 0.01], color=GOLD3, stroke_width=2.5)
        btl = T("30 ms", 22, GREY_B).next_to(bx, DOWN, buff=0.1).align_to(bx, RIGHT)
        with self.cue("e_7") as d:
            hd = T("harmonics 20–30 of 100 Hz", 32).to_edge(UP, buff=0.9)
            nm = T("cosine phase", 30, BLUE3).next_to(bx, DOWN, buff=0.35)
            self.play(FadeIn(hd), Create(bx), Create(hcos), FadeIn(nm), FadeIn(btl), run_time=2.0)
        self.listen("high_cos", bx)
        with self.cue("e_8") as d:
            nm2 = T("random phases", 30, GOLD3).move_to(nm)
            self.play(Transform(hcos, hrnd), FadeOut(nm), FadeIn(nm2), run_time=1.2)
        self.listen("high_rand", bx)
        with self.cue("e_9") as d:
            bz = T("cosine phase: a buzz, 100 times a second", 28, YEL).to_edge(DOWN, buff=0.6)
            hc2 = bx.plot(lambda ms: harmonic_sum(nh, [0] * 11)(ms / 10), x_range=[0, 30, 0.01], color=BLUE3, stroke_width=2.5)
            self.play(Transform(hcos, hc2), FadeOut(nm2), FadeIn(bz), run_time=0.8)
            self.wait(1.6)
            ex = T("inside one filter, phase becomes a waveform the ear can follow", 26, GREY_B).next_to(bz, UP, buff=0.2)
            self.play(FadeIn(ex), run_time=0.6)
        self.clear_stage(run_time=0.6, full=True)


# ---------------------------------------------------------------------------------------------- Window
class Window(VScene):
    def construct(self):
        self.chapter("?", "The window", puzzle=(4, PUZZLES[3]))
        with self.cue("w_1") as d:
            q = T("Pictures seem to say the opposite.", 40)
            self.play(Write(q), run_time=1.2)
        S = 2.5
        pa = ImageMobject(A("pic_a.png")).set(height=S).move_to(LEFT * 4.9 + UP * 1.35)
        pb = ImageMobject(A("pic_b.png")).set(height=S).move_to(LEFT * 4.9 + DOWN * 1.95)
        fa = SurroundingRectangle(pa, buff=0, color=BLUE3, stroke_width=2)
        fb = SurroundingRectangle(pb, buff=0, color=GOLD3, stroke_width=2)
        la = T("picture 1", 26, BLUE3).next_to(pa, DOWN, buff=0.12)
        lb = T("picture 2", 26, GOLD3).next_to(pb, DOWN, buff=0.12)
        mix = labeled_box("2-D Fourier:\nmix", 2.4, 1.3, WHITE, 26).move_to(LEFT * 0.6)
        a1 = Arrow(pa.get_right(), mix.get_left() + UP * 0.25, buff=0.15, color=BLUE3, stroke_width=4)
        a2 = Arrow(pb.get_right(), mix.get_left() + DOWN * 0.25, buff=0.15, color=GOLD3, stroke_width=4)
        t1 = T("magnitudes", 24, BLUE3).move_to(a1.get_center() + UP * 0.45 + RIGHT * 0.35)
        t2 = T("phases", 24, GOLD3).move_to(a2.get_center() + DOWN * 0.45 + RIGHT * 0.35)
        hyb = ImageMobject(A("pic_magA_phB.png")).set(height=3.2).move_to(RIGHT * 4.3)
        fh = SurroundingRectangle(hyb, buff=0, color=WHITE, stroke_width=2)
        a3 = Arrow(mix.get_right(), hyb.get_left(), buff=0.15, color=WHITE, stroke_width=4)
        with self.cue("w_2") as d:
            self.play(FadeOut(q), run_time=0.4)
            self.play(FadeIn(pa), Create(fa), FadeIn(la), FadeIn(pb), Create(fb), FadeIn(lb), run_time=1.2)
            self.wait(1.4)
            self.play(FadeIn(mix), run_time=0.5)
            self.play(GrowArrow(a1), FadeIn(t1), run_time=0.8)
            self.play(GrowArrow(a2), FadeIn(t2), run_time=0.8)
        with self.cue("w_3") as d:
            self.play(GrowArrow(a3), FadeIn(hyb), Create(fh), run_time=1.2)
            r = NUM["swap_corr"]
            lk = T("looks like picture 2", 28, GOLD3).next_to(hyb, DOWN, buff=0.2)
            cc = T(tr("correlation: {:.2f} with 2, {:.2f} with 1").format(r['with_B'], r['with_A']), 20, GREY_B).next_to(lk, DOWN, buff=0.12)
            self.play(FadeIn(lk), FadeIn(cc), run_time=0.6)
        self.clear_stage(run_time=0.5)

        with self.cue("w_4") as d:
            q1 = T("Is phase important?", 44)
            q2 = T("Both. It depends on the window.", 44, YEL).next_to(q1, DOWN, buff=0.5)
            self.play(Write(q1), run_time=1.0)
            self.wait(1.0)
            self.play(FadeIn(q2, shift=UP * 0.2), run_time=0.8)
        # one window: a blip moving inside it; magnitudes fixed, phases turn
        p = ValueTracker(0.3)
        win = Rectangle(width=6.0, height=1.6, stroke_color=WHITE, stroke_width=3).move_to(UP * 1.6)
        wl = T("one window", 24, GREY_B).next_to(win, LEFT, buff=0.25)
        blip = always_redraw(lambda: ParametricFunction(
            lambda s: np.array([win.get_left()[0] + 6 * s, win.get_y() - 0.5 + 1.1 * np.exp(-((s - p.get_value()) / 0.03) ** 2), 0]),
            t_range=[0, 1, 0.002], color=BLUE3, stroke_width=4))
        ks = list(range(1, 7))
        mags = VGroup()
        dials = VGroup()
        for i, k in enumerate(ks):
            x = -4.5 + i * 1.8
            h = 1.3 * np.exp(-((k / 9) ** 2))
            mags.add(Rectangle(width=0.35, height=h, stroke_width=0, fill_color=TEAL3, fill_opacity=0.9)
                     .move_to([x - 0.45, -1.2 + h / 2, 0]))

            def mk(k=k, x=x):
                ctr = np.array([x + 0.35, -0.55, 0])
                a = -TAU_ * k * p.get_value()
                return VGroup(Circle(0.38, stroke_color=GREY3, stroke_width=2).move_to(ctr),
                              Arrow(ctr, ctr + 0.38 * np.array([np.cos(a), np.sin(a), 0]), buff=0, color=YEL,
                                    stroke_width=4, max_tip_length_to_length_ratio=0.3))
            dials.add(always_redraw(mk))
        what = T("magnitudes: what is there", 26, TEAL3).move_to(DOWN * 2.2 + LEFT * 3.2)
        where = T("phases: where it is", 26, YEL).move_to(DOWN * 2.2 + RIGHT * 3.2)
        with self.cue("w_5") as d:
            self.play(VGroup(q1, q2).animate.scale(0.6).to_edge(UP, buff=0.25), run_time=0.6)
            self.play(Create(win), FadeIn(wl), Create(blip), run_time=0.8)
            self.play(LaggedStart(*[GrowFromEdge(m, DOWN) for m in mags], lag_ratio=0.1), FadeIn(what), run_time=1.4)
            self.play(FadeIn(dials), FadeIn(where), run_time=0.8)
            self.play(p.animate.set_value(0.7), run_time=rt(d - 3.2), rate_func=there_and_back)
        self.clear_stage(run_time=0.5)

        with self.cue("w_6") as d:
            pic = ImageMobject(A("pic_b.png")).set(height=4.0).shift(LEFT * 2.5)
            big = SurroundingRectangle(pic, buff=0.12, color=WHITE, stroke_width=5)
            lab = VGroup(T("one giant window:", 30), T("every edge, every position", 30, YEL),
                         T("lives in the phases", 30, YEL)).arrange(DOWN, buff=0.2, aligned_edge=LEFT).next_to(big, RIGHT, buff=0.7)
            self.play(FadeIn(pic), run_time=0.8)
            self.play(Create(big), FadeIn(lab[0]), run_time=1.0)
            self.play(FadeIn(lab[1:]), run_time=1.0)
        self.clear_stage(run_time=0.5)

        # the ear: many short windows along a Morse envelope
        sh = 12.0
        ys = (1.95, -0.25, -2.45)
        spec = ImageMobject(A("spec_morse.png")).stretch_to_fit_width(sh).stretch_to_fit_height(1.4).move_to(UP * ys[0])
        sl = T("Morse code, CQ CQ (spectrogram)", 22, GREY_B).next_to(spec, UP, buff=0.1).align_to(spec, LEFT)
        with self.cue("w_7") as d:
            ear = T("the ear: short windows, about 2 to 30 ms", 30).to_edge(UP, buff=0.3).shift(RIGHT * 1.6)
            self.play(FadeIn(ear), FadeIn(spec), FadeIn(sl), run_time=1.0)
            on = NUM["morse_win_on"]               # keyed fraction of each 32 ms window (dsp.py)
            n = len(on)
            wpx = sh / n
            ticks = VGroup(*[Line(UP * 0.7, DOWN * 0.7, stroke_color=WHITE, stroke_width=0.6, stroke_opacity=0.45)
                             .move_to(spec.get_left() + RIGHT * wpx * i).set_y(spec.get_y()) for i in range(n + 1)])
            lit = VGroup(*[Rectangle(width=wpx, height=0.25, stroke_width=0, fill_color=YEL, fill_opacity=0.9)
                           .move_to(spec.get_left() + RIGHT * wpx * (i + 0.5)).set_y(spec.get_bottom()[1] - 0.18)
                           for i in range(n) if on[i] > 0.25])
            self.play(Create(ticks), run_time=1.4)
            self.play(LaggedStart(*[FadeIn(r) for r in lit], lag_ratio=0.02), run_time=1.6)
            wh = T("when = which window lights up", 28, YEL).next_to(spec, DOWN, buff=0.45)
            self.wait(0.5)
            self.play(FadeIn(wh), run_time=0.6)

        def play_spec(name, img_obj):
            line = Line(img_obj.get_corner(UL), img_obj.get_corner(DL), stroke_color=WHITE, stroke_width=3)
            self.add(line)
            dur = self.sfx(name)
            self.play(line.animate.move_to(img_obj.get_right()), run_time=dur, rate_func=linear)
            self.remove(line)
            self.wait(0.6)
        s32 = ImageMobject(A("spec_morse_w32.png")).stretch_to_fit_width(sh).stretch_to_fit_height(1.4).move_to(UP * ys[1])
        l32 = T("keep the magnitudes, noise phases, 32 ms windows", 22, GREY_B).next_to(s32, UP, buff=0.1).align_to(s32, LEFT)
        with self.cue("w_8") as d:
            self.play(FadeOut(ticks), FadeOut(lit), FadeOut(wh), run_time=0.5)
            self.play(FadeIn(s32), FadeIn(l32), run_time=1.0)
        play_spec("morse_w32", s32)
        sall = ImageMobject(A("spec_morse_whole.png")).stretch_to_fit_width(sh).stretch_to_fit_height(1.4).move_to(UP * ys[2])
        lall = T("the same, with one window the whole message long", 22, GREY_B).next_to(sall, UP, buff=0.1).align_to(sall, LEFT)
        sc = NUM["morse_score"]
        with self.cue("w_9") as d:
            ok = T(tr("rhythm kept (envelope r = {:.2f})").format(sc['w32']), 22, GRN).next_to(s32, DOWN, buff=0.08).align_to(s32, RIGHT)
            self.play(FadeIn(ok), run_time=0.5)
            self.wait(1.0)
            self.play(FadeIn(sall), FadeIn(lall), run_time=1.0)
        play_spec("morse_whole", sall)
        with self.cue("w_10") as d:
            gone = T(tr("timing gone (r = {:.2f})").format(sc['whole']), 22, RED3).next_to(sall, DOWN, buff=0.08).align_to(sall, RIGHT)
            self.play(FadeIn(gone), run_time=0.5)
            self.wait(1.4)
            self.clear_stage(run_time=0.6)
            tc = NUM["tile_corr"]
            imgs = Group()
            for b, lab, col in ((16, "16-pixel windows", GRN), (256, "one window", RED3)):
                im = ImageMobject(A(f"pic_b_tile{b}.png")).set(height=3.6)
                fr = SurroundingRectangle(im, buff=0, color=col, stroke_width=2)
                tt = T(lab, 28, col).next_to(im, UP, buff=0.15)
                rr = T(tr("r = {:.2f} with the picture").format(tc[str(b)]), 22, GREY_B).next_to(im, DOWN, buff=0.15)
                imgs.add(Group(im, fr, tt, rr))
            imgs.arrange(RIGHT, buff=1.4).shift(DOWN * 0.2)
            hd = T("picture 2: keep magnitudes, noise phases", 30).to_edge(UP, buff=0.4)
            self.play(FadeIn(hd), FadeIn(imgs[0]), run_time=1.0)
            self.wait(2.0)
            self.play(FadeIn(imgs[1]), run_time=1.0)
        with self.cue("w_11") as d:
            self.clear_stage(run_time=0.5)
            m = VGroup(T("Sound vs pictures:", 40), T("not the senses, the window.", 40, YEL)).arrange(DOWN, buff=0.35)
            self.play(Write(m), run_time=1.6)
        self.clear_stage(run_time=0.6, full=True)


# ----------------------------------------------------------------------------------------------- Radio
def qam_points(M):
    """Square M-QAM levels (odd integers); QPSK = M 2."""
    lv = np.arange(-(M - 1), M, 2)
    return np.array([[a, b] for a in lv for b in lv], float)


def first_fail(M):
    """Rotation at which the corner point (M-1, M-1) reaches the nearest decision boundary (M-2): 45 deg - asin(.)."""
    return 45 - np.degrees(np.arcsin((M - 2) / ((M - 1) * np.sqrt(2))))


class Radio(VScene):
    def panel(self, M, center, size, name):
        pts = qam_points(M)
        sc = size / 2 / M
        th = ValueTracker(0.0)
        sq = Square(size, stroke_color=GREY3, stroke_width=2).move_to(center)
        grid = VGroup()
        for b in range(-(M - 2), M - 1, 2):
            grid.add(Line(center + np.array([b * sc, -size / 2, 0]), center + np.array([b * sc, size / 2, 0]),
                          stroke_color=GREY3 if b else WHITE, stroke_width=1.5 if b else 2.5))
            grid.add(Line(center + np.array([-size / 2, b * sc, 0]), center + np.array([size / 2, b * sc, 0]),
                          stroke_color=GREY3 if b else WHITE, stroke_width=1.5 if b else 2.5))
        lv = np.arange(-(M - 1), M, 2)
        ff = first_fail(M)

        def dots():
            a = np.radians(th.get_value())
            c, s = np.cos(a), np.sin(a)
            g = VGroup()
            for x, y in pts:
                rx, ry = x * c - y * s, x * s + y * c
                ok = lv[np.argmin(abs(lv - rx))] == x and lv[np.argmin(abs(lv - ry))] == y
                g.add(Dot(center + np.array([rx * sc, ry * sc, 0]), radius=0.11 if M <= 4 else 0.07,
                          color=YEL if ok else RED3))
            return g
        d = always_redraw(dots)
        lab = T(name, 30).next_to(sq, UP, buff=0.2)
        tv = always_redraw(lambda: T(f"θ = {th.get_value():.1f}°", 26, GREY_B).next_to(sq, DOWN, buff=0.2))
        g = VGroup(sq, grid, d, lab, tv)
        g.th, g.ff, g.sq, g.dots = th, ff, sq, d
        return g

    def construct(self):
        self.chapter("5", "Radio", puzzle=(5, PUZZLES[4]))
        ax = flat_axes([0, 4, 1], [-1.8, 1.8, 1], 8.6, 3.2).move_to(RIGHT * 1.6 + UP * 0.2)
        th = ValueTracker(0.0)
        env = lambda x: 1 + 0.6 * np.cos(TAU_ * x / 2)
        car = always_redraw(lambda: ax.plot(lambda x: env(x) * np.cos(TAU_ * 7 * x + th.get_value()), x_range=[0, 4, 0.002],
                                            color=BLUE3, stroke_width=2.5))
        e1 = ax.plot(env, x_range=[0, 4, 0.01], color=YEL, stroke_width=4)
        e2 = ax.plot(lambda x: -env(x), x_range=[0, 4, 0.01], color=YEL, stroke_width=4)
        C, t = LEFT * 5.0 + UP * 0.2, ValueTracker(0)
        circ = Circle(1.6, stroke_color=GREY3, stroke_width=2).move_to(C)
        ph = always_redraw(lambda: Arrow(C, C + env(t.get_value()) * np.array([np.cos(9 * t.get_value()), np.sin(9 * t.get_value()), 0]),
                                         buff=0, color=BLUE3, stroke_width=6, max_tip_length_to_length_ratio=0.15))
        with self.cue("r_1") as d:
            self.play(Create(ax), Create(car), run_time=1.4)
            self.play(Create(e1), Create(e2), run_time=1.2)
            el = T("envelope = length of the arrow", 28, YEL).next_to(ax, UP, buff=0.3)
            self.play(Create(circ), GrowArrow(ph), FadeIn(el), run_time=1.0)
            self.play(t.animate.set_value(4), run_time=rt(d - 3.6), rate_func=linear)
        with self.cue("r_2") as d:
            tl = always_redraw(lambda: T(tr("receiver phase error θ = {:.0f}°").format(np.degrees(th.get_value()) % 360), 28)
                               .next_to(ax, DOWN, buff=0.35))
            self.add(tl)
            self.play(th.animate.set_value(np.radians(300)), t.animate.set_value(8), run_time=d * 0.6, rate_func=linear)
            ok = T("AM and CW: the envelope does not move", 28, GRN).next_to(tl, DOWN, buff=0.2)
            self.play(FadeIn(ok), run_time=0.6)
        self.clear_stage(run_time=0.5)

        q = self.panel(2, LEFT * 4.6 + DOWN * 0.3, 3.4, "QPSK")
        q16 = self.panel(4, DOWN * 0.3, 3.4, "16-QAM")
        q64 = self.panel(8, RIGHT * 4.6 + DOWN * 0.3, 3.4, "64-QAM")
        with self.cue("r_3") as d:
            hd = T("the data is in the angle", 32).to_edge(UP, buff=0.4)
            self.play(FadeIn(hd), run_time=0.6)
            self.play(FadeIn(q), run_time=1.0)
            self.wait(2.0)
            self.play(FadeIn(q16), run_time=1.0)
        with self.cue("r_4") as d:
            hint = T("decision = the box it lands in", 26, GREY_B).next_to(hd, DOWN, buff=0.2)
            self.play(FadeIn(hint), run_time=0.6)
            self.wait(1.8)
            self.play(q.th.animate.set_value(10), q16.th.animate.set_value(10), run_time=1.6)
            self.play(q.th.animate.set_value(0), q16.th.animate.set_value(0), run_time=1.0)
        with self.cue("r_5") as d:
            self.play(q.th.animate.set_value(q.ff + 0.5), run_time=rt(d - 1.0))
            f1 = T(tr("first error at {:.0f}°").format(q.ff), 26, RED3).next_to(q.sq, DOWN, buff=0.65)
            self.play(FadeIn(f1), run_time=0.5)
        with self.cue("r_6") as d:
            self.play(q16.th.animate.set_value(q16.ff + 0.1), run_time=2.6)
            f2 = T(tr("first error at {:.1f}°").format(q16.ff), 26, RED3).next_to(q16.sq, DOWN, buff=0.65)
            self.play(FadeIn(f2), FadeIn(q64), run_time=0.8)
            self.play(q64.th.animate.set_value(q64.ff + 0.1), run_time=2.0)
            f3 = T(tr("first error at {:.1f}°").format(q64.ff), 26, RED3).next_to(q64.sq, DOWN, buff=0.65)
            self.play(FadeIn(f3), run_time=0.5)
        with self.cue("r_7") as d:
            self.clear_stage(run_time=0.5)
            card = rule_card(5, "Phase-coded data needs a reference.").to_edge(UP, buff=0.5)
            self.play(FadeIn(card, shift=DOWN * 0.2), run_time=0.7)
            pil = VGroup(T("pilot tones, training symbols:", 28), T("measure θ, then undo it", 28, GRN)).arrange(DOWN, buff=0.15)
            pil.move_to(LEFT * 3.6 + DOWN * 0.3)
            self.play(FadeIn(pil), run_time=0.8)
            self.wait(2.2)
            O = RIGHT * 3.2 + DOWN * 1.2
            rot = ValueTracker(0.0)
            def sym(a0, col):
                return always_redraw(lambda: Arrow(O, O + 1.5 * np.array([np.cos(a0 + rot.get_value()), np.sin(a0 + rot.get_value()), 0]),
                                                   buff=0, color=col, stroke_width=5, max_tip_length_to_length_ratio=0.15))
            s1, s2 = sym(np.radians(30), BLUE3), sym(np.radians(120), GOLD3)
            arc = always_redraw(lambda: Arc(radius=0.6, start_angle=np.radians(30) + rot.get_value(), angle=np.radians(90),
                                            arc_center=O, color=WHITE, stroke_width=3))
            dl = T("differential: data = the change", 28).next_to(O, UP, buff=2.0)
            dl2 = T("previous → next symbol", 24, GREY_B).next_to(dl, DOWN, buff=0.1)
            self.play(FadeIn(dl), FadeIn(dl2), GrowArrow(s1), GrowArrow(s2), Create(arc), run_time=1.2)
            self.play(rot.animate.set_value(np.radians(40)), run_time=2.0)
            same = T("rotate both: the change stays 90°", 24, GRN).next_to(O, DOWN, buff=0.3)
            self.play(FadeIn(same), run_time=0.6)
        self.clear_stage(run_time=0.6, full=True)


# ----------------------------------------------------------------------------------------------- Outro
ANSWERS = [("No. Only differences can be measured.", "rule 1"),
           ("A camera squares; two beams add before the square.", "rules 2, 1"),
           ("Mostly not: separate bands cannot interfere.", "rule 4"),
           ("The window: one giant window vs short ones.", "the window"),
           ("The data is in the angle: it needs a reference.", "rule 5")]


class Outro(VScene):
    def construct(self):
        rules = ["Only phase differences are measurable.", "Square-law detectors are blind to phase.",
                 "Phase linear in frequency is just a delay.", "Components in different bands cannot interfere.",
                 "Phase-coded data needs a reference."]
        with self.cue("o_1") as d:
            title = T("Five rules", 56, YEL).to_edge(UP, buff=0.5)
            self.play(Write(title), run_time=0.9)
        rows = VGroup(*[VGroup(T(f"{i + 1}", 34, YEL), T(r, 34)).arrange(RIGHT, buff=0.4) for i, r in enumerate(rules)])
        rows.arrange(DOWN, buff=0.38, aligned_edge=LEFT).next_to(title, DOWN, buff=0.6)
        with self.cue("o_2") as d:
            lens = np.array([len(tr(r)) for r in rules], float)
            for r, ln in zip(rows, lens):
                self.play(FadeIn(r, shift=RIGHT * 0.2), run_time=0.5)
                self.wait(max(0.0, (d - 0.3) * ln / lens.sum() - 0.5))

        # the five puzzles from the Intro, answered
        with self.cue("o_a0") as d:
            self.clear_stage(run_time=0.6)
            head = T("The five puzzles", 44, YEL).to_edge(UP, buff=0.35)
            self.play(Write(head), run_time=0.8)
        qa = VGroup()
        for i, (q, (a, tag)) in enumerate(zip(PUZZLES, ANSWERS)):
            body = VGroup(T(q, 24, GREY_B),
                          VGroup(T(a, 30), T(tr("({})").format(tr(tag)), 26, YEL)).arrange(RIGHT, buff=0.25))
            body.arrange(DOWN, buff=0.1, aligned_edge=LEFT)
            qa.add(VGroup(T(f"{i + 1}", 30, YEL), body).arrange(RIGHT, buff=0.35, aligned_edge=UP))
        qa.arrange(DOWN, buff=0.3, aligned_edge=LEFT).next_to(head, DOWN, buff=0.4)
        if qa.width > 13:
            qa.scale_to_fit_width(13)
        qa.set_x(0)
        for i, r in enumerate(qa):
            with self.cue(f"o_a{i + 1}") as d:
                self.play(FadeIn(r, shift=RIGHT * 0.2), run_time=0.6)

        with self.cue("o_3") as d:
            self.play(qa.animate.set_opacity(0.3), head.animate.set_opacity(0.3), run_time=0.8)
            self.clear_stage(run_time=0.5)
            q1 = T("What is it compared with?", 44, BLUE3)
            q2 = T("Is it squared or averaged away first?", 44, GOLD3)
            qs = VGroup(q1, q2).arrange(DOWN, buff=0.5)
            self.wait(0.5)
            self.play(FadeIn(q1, shift=UP * 0.2), run_time=0.6)
            self.wait(1.2)
            self.play(FadeIn(q2, shift=UP * 0.2), run_time=0.6)

        # end card: link + QR code + credits, held long enough to scan
        with self.cue("o_4") as d:
            self.clear_stage(run_time=0.6)
            qr = qr_code(REPO, size=3.8)
            scan = T("scan for the code", 24, GREY_B).next_to(qr, DOWN, buff=0.25)
            info = VGroup(T("What notices a phase shift?", 40),
                          M(REPO.replace("https://", ""), 30, BLUE3),
                          T("open source, MIT License", 26, GREY_B),
                          T(CREDIT, 34, BLUE3),
                          T(DATE, 28, GREY_B),
                          T("animation: Manim  ·  voice: Kokoro", 22, GREY_B)).arrange(DOWN, buff=0.32, aligned_edge=LEFT)
            info[3].shift(DOWN * 0.25)
            info[4].shift(DOWN * 0.25)
            info[5].shift(DOWN * 0.25)
            card = Group(Group(qr, scan), info).arrange(RIGHT, buff=0.9).move_to(ORIGIN)
            self.play(FadeIn(qr), FadeIn(scan), LaggedStart(*[FadeIn(m, shift=LEFT * 0.2) for m in info], lag_ratio=0.12),
                      run_time=1.6)
        self.wait(7.0)
        self.clear_stage(run_time=1.0, full=True)
