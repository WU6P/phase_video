"""Narration for "What notices a phase shift?", one entry per audio clip.

Each scene is a list of (cue_id, text) or (cue_id, text, spoken). `text` is the subtitle; `spoken` (if given)
is what the TTS reads, for tokens a speech engine would mangle. The claims follow ../phase (index.html, core.js);
numbers that appear on screen are computed in dsp.py or scenes.py, not typed in.
"""

SCENES = {
"Intro": [
    ("i_1", "Take a pure tone, and slide it along in time by a fraction of a cycle. That is a phase shift."),
    ("i_2", "The question for today: who can tell?"),
    ("i_3", "Your ear, mostly, cannot. Your eye cannot. An AM radio cannot, and neither can a Morse code receiver.",
            "Your ear, mostly, cannot. Your eye cannot. An A.M. radio cannot, and neither can a Morse code receiver."),
    ("i_4", "But a QAM modem, the kind inside your Wi-Fi, falls apart if its phase is off by just a few degrees.",
            "But a kwam modem, the kind inside your Wi-Fi, falls apart if its phase is off by just a few degrees."),
    ("i_q0", "Along the way, we will answer five puzzles."),
    ("i_q1", "Can anyone measure the phase of a single wave?"),
    ("i_q2", "No camera can see the phase of light. So how do two beams make fringes?"),
    ("i_q3", "If you scramble the phases of a sound, does it sound different?"),
    ("i_q4", "Why do phases carry a picture, but hardly matter for sound?"),
    ("i_q5", "And why does a 64-QAM modem fail at less than eight degrees, while an AM radio never notices?",
             "And why does a sixty-four QAM modem fail at less than eight degrees, while an A.M. radio never notices?"),
    ("i_5", "Five simple rules answer all of them, and almost every other case. Let's find them."),
],
"Phasor": [
    ("p_1", "Here is a good way to picture a tone: an arrow spinning around a circle. Its shadow traces out the wave."),
    ("p_2", "The phase is the angle of the arrow at the moment you start your clock."),
    ("p_3", "But nature never tells you when that moment is. Start the clock a little later, and the phase changes, while nothing physical has changed at all."),
    ("p_4", "So the phase of one wave on its own cannot be measured. Only a difference can: between two waves, or between two parts of the same wave."),
    ("p_5", "That is rule one. Only phase differences are measurable."),
],
"Light": [
    ("l_1", "Light oscillates about five hundred trillion times a second. No eye or camera can follow that, so every light detector measures energy instead: the square of the amplitude."),
    ("l_2", "Squaring the length of the arrow throws its angle away. That is rule two: square-law detectors are blind to phase."),
    ("l_3", "But let two beams meet before the detector, and their arrows add first. Now the angle between them matters."),
    ("l_4", "In phase, the arrows reinforce. Half a cycle apart, they cancel to darkness."),
    ("l_5", "Across a screen, that makes interference fringes. Shift both beams together, and the fringes stay put. Shift only one, and they move. Rule one again: only the difference shows."),
],
"Kinds": [
    ("k_1", "Now build a sound from six harmonics, all starting in cosine phase. Together they make a sharp spike, once per cycle."),
    ("k_2", "Delay the whole sound, and each harmonic's phase shifts in proportion to its frequency. On a plot of phase against frequency, that is a straight line through zero."),
    ("k_3", "The spike just moves. Nothing about the sound has changed except when it happens."),
    ("k_4", "That is rule three. A phase shift that grows linearly with frequency is only a delay."),
    ("k_5", "Any other pattern changes the shape. Shift every harmonic by the same ninety degrees, and the spike turns into something completely different."),
    ("k_6", "But in every case, the strength of each harmonic stays exactly the same. So the real question is: what notices the shape, when the spectrum does not change?"),
],
"Ear": [
    ("e_1", "Let's test your ear. Here are those six harmonics of two hundred hertz, in cosine phase. Listen."),
    ("e_2", "Now the same six harmonics, at the same strengths, with random phases. The waveform looks nothing alike. Listen."),
    ("e_3", "To most ears, they sound almost the same. That is Ohm's acoustic law: the ear mostly hears the magnitude spectrum."),
    ("e_4", "Why? The cochlea is a bank of filters. Each low harmonic lands in a filter of its own, and each filter reports only how much energy passes through it."),
    ("e_5", "Phase can only matter where waves add together, and two harmonics in different filters never meet. That is rule four: components in different detector bands cannot interfere."),
    ("e_6", "The exceptions follow the same rule. Higher up, the filters get wider, and several harmonics crowd into one filter. There they do interfere."),
    ("e_7", "Here are harmonics twenty to thirty of one hundred hertz, first in cosine phase."),
    ("e_8", "And now with random phases."),
    ("e_9", "The cosine version buzzes. Inside one filter, phase has become a waveform that the ear can follow."),
],
"Window": [
    ("w_1", "Now a puzzle. Pictures seem to say the opposite."),
    ("w_2", "Take two pictures and compute their Fourier transforms. Keep the magnitudes of the first one, and the phases of the second."),
    ("w_3", "The result looks like the second picture. The phases carried it."),
    ("w_4", "So is phase important or not? Both. It depends on the size of the window you look through."),
    ("w_5", "Inside a window, the magnitudes say what is there: which frequencies, how strong. The phases say where things are inside the window."),
    ("w_6", "A picture transformed in one piece is one giant window. Every edge and every position lives in the phases."),
    ("w_7", "The ear does the opposite. It listens through short windows, a few milliseconds to a few tens of milliseconds, and when something happens is carried by which window lights up."),
    ("w_8", "Here is Morse code. In every thirty-two millisecond window, we keep the magnitudes and replace every phase with noise. Listen."),
    ("w_9", "The rhythm survives. Now one window, the whole message long. Same magnitudes, scrambled phases."),
    ("w_10", "The timing is gone. The same is true for the picture: scramble the phases in small tiles, and it survives. Only the giant window needs its phases."),
    ("w_11", "So the difference between sound and pictures is not in the senses. It is in the window."),
],
"Radio": [
    ("r_1", "Finally, radio. The AM detector follows the envelope, the length of the arrow, and never looks at its angle. Morse code is the same: tone on, tone off.",
            "Finally, radio. The A.M. detector follows the envelope, the length of the arrow, and never looks at its angle. Morse code is the same: tone on, tone off."),
    ("r_2", "So when the receiver's oscillator is off in phase, AM and CW do not care.",
            "So when the receiver's oscillator is off in phase, A.M. and C.W. do not care."),
    ("r_3", "QAM is different. It puts the data into the angle itself. Four points for QPSK, sixteen for 16-QAM.",
            "Kwam is different. It puts the data into the angle itself. Four points for Q.P.S.K., sixteen for sixteen kwam."),
    ("r_4", "The receiver decides which point was sent by the box it lands in. A phase error rotates the whole constellation."),
    ("r_5", "QPSK survives until its points reach the boundary, at forty-five degrees.",
            "Q.P.S.K. survives until its points reach the boundary, at forty-five degrees."),
    ("r_6", "In 16-QAM, the outer corners cross a boundary at only sixteen point nine degrees, and in 64-QAM at seven point seven.",
            "In sixteen QAM, the outer corners cross a boundary at only sixteen point nine degrees, and in sixty-four QAM at seven point seven."),
    ("r_7", "Rule five: phase-coded data needs a reference. Real systems send pilot tones or known training symbols, or they code the data as the change from one symbol to the next, so a constant error cancels."),
],
"Outro": [
    ("o_1", "So, five rules."),
    ("o_2", "Only phase differences are measurable. Square-law detectors are blind to phase. Phase linear in frequency is just a delay. Components in different bands cannot interfere. And phase-coded data needs a reference."),
    ("o_a0", "And the five puzzles from the start?"),
    ("o_a1", "No one can measure the phase of a single wave. Only a difference."),
    ("o_a2", "A camera squares the light, but two beams add before the square."),
    ("o_a3", "Scrambled phases in a sound mostly go unnoticed, because separate bands cannot interfere."),
    ("o_a4", "A picture is one giant window, and the ear listens through short ones."),
    ("o_a5", "And QAM puts its data in the angle itself, so it needs a reference. AM never looks at the angle.",
             "And kwam puts its data in the angle itself, so it needs a reference. A.M. never looks at the angle."),
    ("o_3", "Next time you wonder whether something notices phase, ask two questions. What is it compared with? And is it squared, or averaged away, before anyone looks?"),
    ("o_4", "The code for this video, with every sound and every check, is open source. The link is on the screen."),
],
}

from lang import LANG  # noqa: E402

if LANG == "zh":
    from narration_zh import SCENES  # noqa: E402,F811  same cue ids, Chinese text

ORDER = list(SCENES)


def cues():
    for scene in ORDER:
        for c in SCENES[scene]:
            cid, text = c[0], c[1]
            spoken = c[2] if len(c) > 2 else text
            yield scene, cid, text, spoken
