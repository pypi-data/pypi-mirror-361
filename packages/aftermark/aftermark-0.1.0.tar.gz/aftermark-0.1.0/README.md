# aftermark

[![PyPI](https://img.shields.io/pypi/v/aftermark.svg)](https://pypi.org/project/aftermark/)
![CLI Tool](https://img.shields.io/static/v1?label=CLI&message=Tool&color=000000&style=for-the-badge&logo=gnubash&logoColor=white)
![Anti-Watermark](https://img.shields.io/static/v1?label=Anti&message=Watermark&color=bd1e51&style=for-the-badge)
![Forensic Clean](https://img.shields.io/static/v1?label=Forensic&message=Clean&color=005f73&style=for-the-badge)

**Obliterate hidden watermarks from platform screenshots.**

## Why

Many modern platforms embed user-specific watermarks into app screenshots. These watermarks are **invisible** to the eye but **detectable** via equalization or frequency analysis. Some are LSB-based, some render [snow-like patterns](#before--after) across RGB channels. Some even survive compression. They are all *a form of tracking*. And no one should be silently tagged just for sharing a screenshot.

**Two-thirds** of high-traffic mobile apps in China now tag screenshots; many started in 2022 after [Douban](https://pandaily.com/douban-app-screenshots-contain-user-information-watermark) & [Zhihu](https://www.sixthtone.com/news/1011179) incidents. Outside China, it's still niche. Except for DRM-heavy verticals (video streaming, enterprise VDI) where "forensic" marks are universal. While tech diversity is widening, we still see classic LSB and DCT hacks. But 2024-25 papers (ScreenMark, CoreMark) chase *camera-shot-robust* patterns that sit in mid-frequency bands or irregular point clouds.

## Features

- **Crop** status bar or header manually
- **Jitter**, **blur**, and **add noise** to disrupt invisible alignment
- **Median filtering** to dissolve patterned bands
- All **automated** with CLI, batchable

## Quick Install

```bash
pip install aftermark
nuke myshot.png
```

## Tinker / Contribute

```bash
git clone https://github.com/kay-a11y/aftermark.git
cd aftermark
pip install -e .
```

<details> <summary>Optional OS tools</summary>

```bash
sudo apt install -y imagemagick libimage-exiftool-perl
```

* ImageMagick - equalize / compare / attacks
* ExifTool    - deep metadata wipe

</details>

## Usage

1. One-off file  →  result is saved next to your shell's CWD

    ```bash
    nuke demo/demo.jpg
    # ➜ ./demo_clean.jpg
    ```

2. One-off file with explicit output folder

    ```bash
    nuke demo/demo.jpg out/
    # ➜ out/demo_clean.jpg
    ```

3. Batch clean a whole folder

    ```bash
    nuke raw_screens/ out/
    # ➜ out/<each>_clean.jpg
    ```

Arguments:

`input`:
    Path to an *image file* **or** a *directory* of images.

`outdir`:
    Destination folder (created if missing). Optional for single-file mode;
    defaults to the current working directory (".").

`--crop`:
    crops a configurable top margin (default=0 px)

`--header`:
    applies a 3*3 median to the first PX pixels (default=32 px)

`--quality`:
    rewrites the image as low-quality JPEG (default=40)

## Before & After

All comparisons below are shown after applying `convert -equalize` for visibility. See [nuke folder](./artifacts/nuke/) for more examples.

| Original (Douban)          | Cleaned (aftermark)      |
| -------------------------- | ------------------------ |
| ![Before](artifacts/nuke/demo_eq.jpg) | ![After](artifacts/nuke/demo_clean_eq.jpg) |

This was scraped from a third party. The snow-pattern fingerprint of the original user still lingers beneath the surface.

## Documentation

See the [full walkthrough](https://kay-a11y.github.io/). Soon.

## Further Reading

* [Helpful Resource - Stgod](https://stgod.com/1482/) (ZH)
* [Interesting Discussion on Zhihu](https://www.zhihu.com/question/517690908) (ZH)
* [Weibo Censorship Insights](https://dpclab.org/china/dashboard/)
* [Twitter Post](https://x.com/inroading/status/1566338872837308416) (ZH)