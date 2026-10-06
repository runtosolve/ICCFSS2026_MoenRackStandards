# ICCFSS 2026 talk — Moen, recent updates to ANSI MH16.1

**View the presentation: https://runtosolve.github.io/ICCFSS2026_MoenRackStandards/**

Two versions of the same 11-slide talk on the MH16.1 (2012 → 2021 → 2023) member design
provisions for perforated rack sections and where the Direct Strength Method enters:

| File | What it is |
|---|---|
| `deck/slides.md` | the talk in [deckmd](https://github.com/KristofferC/deckmd) Markdown — edit this |
| `index.html` | the deck as one self-contained page, served on [GitHub Pages](https://runtosolve.github.io/ICCFSS2026_MoenRackStandards/) (open in a browser; `→`/`←` navigate, `f` fullscreen, `t` light/dark) |
| `Moen_ICCFSS_2026_rack_standards_slides.pdf` | one slide per page (handout) |
| `Moen_ICCFSS_2026_rack_standards.pptx` | PowerPoint version built from `template.pptx` with the same content |
| `build_pptx.py` | builds the .pptx (python-pptx) |
| `template.pptx` | the conference PowerPoint template (CCFSS logo, Aptos theme, date footer) |

The deckmd engine (`deck/build.jl`, `serve.jl`, `publish.jl`, `template.html`, `vendor/`) is copied unchanged from the
Moen & Shabhari ICCFSS 2026 talk (`Papers/Moen_Shabhari_2026_ICCFSS 2026/paper/presentation`), so both talks share
the same look: navy 0E2841, blue 156082, orange E97132, conference logo on the title slide, logo + conference footer.

## Sources
- ANSI MH16.1-2012, RMI 16.1-2021, ANSI MH16.1-2023 (`Projects/RMI/RMI_standards`, `Projects/OneRack/analysis_engine_2022/RMI_codes`)
- RMI 2026 committee activity (`Projects/RMI/Meetings/Palm_Springs_September_2026`)

## Figures (`deck/data/`)
| File | Source |
|---|---|
| `fig_strips.png` | MH16.1-2023 Figure 8.2-1 (PDF p. 46), cropped at 220 dpi |
| `fig_cufsm.png` | MH16.1-2023 Commentary Figure C8.2-5 (PDF p. 108) |
| `fig_local_global.png`, `fig_dist_curve.png`, `fig_timeline.png` | `julia data/make_figs.jl` (CairoMakie, temporary environment) |
| `eq/*.png` | PowerPoint equations typeset with LaTeX: `python3 data/make_eqs.py` (needs pdflatex, pdftoppm) |
| `qr.svg`, `qr.png` | encode `https://runtosolve.github.io/ICCFSS2026_MoenRackStandards` |

## Rebuild
```
cd deck
julia data/make_figs.jl        # strength curves and timeline
julia serve.jl                 # live preview at http://localhost:8383 while editing slides.md
julia build.jl --single --pdf  # deck.html, deck-single.html (= ../index.html), deck.pdf (needs Google Chrome)
cd ..
cp deck/deck-single.html index.html; cp deck/deck.pdf Moen_ICCFSS_2026_rack_standards_slides.pdf
python3 deck/data/make_eqs.py   # LaTeX equation images for the .pptx
python3 build_pptx.py          # Moen_ICCFSS_2026_rack_standards.pptx
```
`julia deck/scripts/qr.jl <url>` regenerates `qr.svg` if the GitHub Pages URL changes (regenerate `qr.png` to match).
