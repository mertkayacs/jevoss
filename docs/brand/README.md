# JevOss logo

A tuning fork rings one true note that every instrument is checked against. JevOss does the same for decision
models: the same probes for every model, and a check on whether its confidence rings true. The single clay ball at
the foot is the one warm accent in the mark.

## Files

| File | Use |
|---|---|
| `svg/jevoss-mark.svg` | the mark on white and light grounds |
| `svg/jevoss-mark-on-dark.svg` | the mark on #0D1117, #1F2430 and other dark grounds |
| `svg/jevoss-mark-black.svg`, `svg/jevoss-mark-white.svg` | one colour; the white file is thinned by 0.75 units per side so it does not look heavier than the black one |
| `svg/jevoss-sticker.svg` | the mark on a white die-cut body (15-unit offset, about 6 %), for coloured sheets |
| `svg/jevoss-logo-on-light.svg`, `svg/jevoss-logo-on-dark.svg` | horizontal logo, height 256 |
| `svg/jevoss-logo-stacked.svg` | mark above the wordmark |
| `svg/jevoss-appicon.svg` | 1024 tile in forest with the mark in parchment |
| `png/` | renders of the files above at 1024, 1600 and 512 px |
| `favicon/` | `favicon.svg` (16 px cut, switches colours in dark mode), `favicon.ico` (16, 32, 48), `favicon-32.png`, `apple-touch-icon.png` (180, full bleed), `icon-192.png`, `icon-512.png`, `icon-maskable-512.png` (mark inside the 80 % safe circle) |

Every PNG is rendered with rsvg-convert, from these SVGs or from the sources in `../build/` (the favicon cut without
its dark-mode style, the full-bleed tile for `apple-touch-icon.png` and the maskable tile). The SVGs contain only
paths, rectangles and circles, plus one small `<style>` block in `favicon.svg` for dark mode: no live text, rasters,
filters, masks or gradients.

## Colours

Contrast is the WCAG 2 ratio, measured on each ground.

| Colour | HEX | on #FFFFFF | on #FDF8F1 | on #0D1117 | Use |
|---|---|---|---|---|---|
| Forest | `#2F4A3A` | 9.72 | 9.19 | 1.95 | fork and wordmark on light grounds; app tile |
| Clay | `#C8693F` | 3.78 | 3.58 | 5.00 | the ball on light grounds |
| Sage | `#9CC3AA` | 1.94 | 1.84 | 9.73 | fork on dark grounds (7.98 on #1F2430) |
| Light clay | `#E08A63` | 2.63 | 2.49 | 7.20 | the ball on dark grounds (5.90 on #1F2430) and on the forest tile (3.69) |
| Cream | `#F1E9DC` | 1.20 | 1.14 | 15.71 | wordmark on dark grounds (12.88 on #1F2430) |
| Parchment | `#FDF8F1` | | | 17.91 | the fork on the forest app tile (9.19) |

## Clear space and minimum sizes

- Clear space: the diameter of the ball (30 units in the 256 mark, about 14 % of the mark's height) on every side of
  the mark and of both logos.
- Mark: 20 px high on screen keeps the ball; below 20 px use `favicon/favicon.svg`, which is drawn on whole pixels for
  16 px.
- Horizontal logo: 24 px high on screen. Stacked logo: 64 px high.
- Print (not proofed yet): mark 6 mm, horizontal logo 7 mm high.

## Typeface

The wordmark is Newsreader by Production Type, SIL Open Font License 1.1 ("Copyright 2020 The Newsreader Project
Authors"), taken from github.com/google/fonts (`ofl/newsreader`). Instance: weight 560, optical size 18; tracking
-20 units; J and e kerned -40 units. Two changes make it ours: the top edge of the e's crossbar is level (Newsreader
tilts it about 3 degrees), and the diagonal cuts of the s terminals are trued to 60 degrees. The letters are outlined
paths, so no font is needed to show the logo. On the JevOss site, Newsreader sets headings and Geist sets body text.

## Do

- Use the light files on white and parchment, the on-dark files on dark grounds, the sticker on coloured sheets.
- Keep the fork forest (or sage on dark) and the ball clay (or light clay on dark).
- Keep the fork upright and the ball at the foot.
- Use `favicon.svg` and the favicon set for browser tabs and home screens.

## Don't

- Put the light mark on a dark ground (forest on #0D1117 is 1.95:1).
- Recolour the ball to match the fork, or colour the fork clay.
- Rotate, tilt, stretch or outline the fork, or add sound waves, motion lines, shadows or gradients.
- Place the mark on a busy photo without the sticker body.
- Retype the wordmark in any font; use the outlined files.
- Use the full mark below 20 px.

## Rebuilding

`FONT_DIR=<folder with Newsreader[opsz,wght].ttf> tools/build_kit.sh` (run from `logos/jevoss/`) regenerates the
wordmark outlines, every SVG, every PNG and the favicon set; `tools/kit.py` holds the geometry and colours, and
`tools/kit_preview.py` rebuilds `preview-final.png`.
