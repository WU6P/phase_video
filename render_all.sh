#!/bin/sh
# Render every scene in parallel (caching off: cached partials would drop add_sound audio).
# VLANG=zh ./render_all.sh renders the Chinese version into media_zh/; Q=-ql for a quick preview.
cd "$(dirname "$0")"
Q=${Q:--qh}
L=${VLANG:-en}
MEDIA=$(.venv/bin/python -c "from lang import MEDIA; print(MEDIA)")
mkdir -p logs
for S in ${SCENES:-$(.venv/bin/python -c "from narration import ORDER; print(' '.join(ORDER))")}; do
  .venv/bin/manim $Q --disable_caching --media_dir "$MEDIA" -o "$S" scenes.py "$S" > "logs/${L}_$S.log" 2>&1 &
done
wait
grep -lE "^[A-Za-z]*Error" logs/${L}_*.log && exit 1
echo "all scenes rendered ($L)"
