# JevOss brand kit

The JevOss mark is three evaluation bars on a baseline, the tallest one in terracotta between two sage bars. The logo pairs it with the wordmark `JevOss` set in Newsreader.

## Files

| Use | File |
|---|---|
| Logo on a light background | `svg/jevoss-logo-on-light.svg`, `png/jevoss-logo-on-light-1600.png` |
| Logo on a dark background | `svg/jevoss-logo-on-dark.svg`, `png/jevoss-logo-on-dark-1600.png` |
| Mark alone on a light background | `svg/jevoss-mark.svg`, `png/jevoss-mark-1024.png` |
| Mark alone on a dark background | `svg/jevoss-mark-on-dark.svg` |
| App icon (512 px tile, corner radius 112) | `svg/jevoss-appicon.svg`, `png/jevoss-appicon-1024.png` |
| Favicon, the app icon tile at small size (reads on light and dark tabs) | `favicon/favicon.svg` |
| The same favicon for older browsers (16, 32 and 48 px in one file) | `favicon/favicon.ico` |
| The same favicon as a 32 px PNG | `favicon/favicon-32.png` |
| Home screen icon (180 px, opaque) | `favicon/apple-touch-icon.png` |

The logo and mark PNGs have transparent backgrounds. The app icon PNG and the favicons have transparent rounded corners. The home screen icon is a full opaque square, because iOS rounds the corners itself.

The sage side bars use `#71967F` on light surfaces, because the site sage `#9CC3AA` measures 1.94:1 on white. On dark surfaces they keep `#9CC3AA`.

## Colour

| Role | Light surfaces | Contrast on #FFFFFF / #FDF8F1 | Dark surfaces | Contrast on #0D1117 / #12171D |
|---|---|---|---|---|
| Ink | `#2F4A3A` | 9.72 / 9.19 | `#E6EEE5` | 15.97 / 15.20 |
| Accent | `#C8693F` | 3.78 / 3.58 | `#E08A63` | 7.20 / 6.85 |
| Secondary | `#71967F` | 3.30 / 3.12 | `#9CC3AA` | 9.73 / 9.26 |

| App icon | Colour | Contrast on the tile |
|---|---|---|
| Tile | `#2F4A3A` | |
| Ink | `#E6EEE5` | 8.20 |
| Accent | `#E08A63` | 3.69 |
| Secondary | `#9CC3AA` | 5.00 |

README icon colour: `#BC5F34`, 4.35 on #FFFFFF and 4.35 on #0D1117.

## Usage

- Pick the file that matches the background: on-light files for white or paper, on-dark files for dark surfaces. In a README, use a `<picture>` element with the dark logo as the `prefers-color-scheme: dark` source.
- Keep clear space around the logo of at least half the height of the mark.
- Smallest sizes: 16 px for the mark, 120 px wide for the logo.
- The wordmark is drawn as outlined paths, so it looks the same everywhere. Use the supplied files and leave the letters as they are.
- Do not recolour, rotate, stretch, outline or add effects to the mark.

## Font

Newsreader, wght 600, opsz 48. Source: `Newsreader[opsz,wght].ttf` from [google/fonts](https://github.com/google/fonts/tree/86aced91de05cd4f96a06838124cca45be337b2b/ofl/newsreader) at commit `86aced91de05`. Licence: SIL Open Font License 1.1. The letters are converted to paths, so the font is not needed to display the logo.
