# Tools behind this page

- `to_page.py` — turns the Derecho web export (npz files, results repo `adhoc/<date>_web_export*/`) into the JSON files under `data/full/`. It first rebuilds one already-published pair and checks the decoded bytes are identical.
- `patch_page.py`, `patch_page2.py` — the edits applied to `index.html` on 2026-11-05 (NCAR-settings comparisons, hmF2/NmF2, scope note, contents, figure sections, lightbox). Kept as a record; the current `index.html` already contains them.
- `build_zh.py`, `align2.py`, `en2zh.json` — build `zh/index.html` from `index.html`: the translation table was derived by aligning the original Chinese page with the English page (`align2.py`), plus a manual table in `build_zh.py` for text added later. Rerun `build_zh.py index.html zh/index.html` after any change to `index.html`.
- `plot_cosmic3.py`, `plot_cosmic7.py` — draw the figures in `figs/cosmic/` from the tables in the results repo (`deep/20261102_duff1101_check/tables/`, `adhoc/20261103_cosmic_cfg/tables/`). They only read columns, aggregate and draw; the physical definitions are in the tables' README files.

Figures under `figs/runs/<experiment>/` are copied unchanged from the results repo (`runs/<experiment>/*.png`), where the computing system's post-run job writes them.
