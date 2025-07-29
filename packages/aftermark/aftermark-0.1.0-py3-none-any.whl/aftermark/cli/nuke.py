"""
nuke - tiny CLI to strip fragile watermarks from screenshots
=============================================================

Usage
-----------

# 1)  One-off file  →  result is saved next to your shell's CWD
$ nuke demo/demo.jpg
# ➜ ./demo_clean.jpg

# 2)  One-off file with explicit output folder
$ nuke demo/demo.jpg out/
# ➜ out/demo_clean.jpg

# 3)  Batch clean a whole folder
$ nuke raw_screens/ out/
# ➜ out/<each>_clean.jpg

Arguments
---------

input
    Path to an *image file* **or** a *directory* of images.
outdir
    Destination folder (created if missing). Optional for single-file mode;
    defaults to the current working directory (".").

The script:
• crops a configurable top margin             (--crop  default=0 px)
• applies a 3*3 median to the first PX pixels (--header default=32 px)
• rewrites the image as low-quality JPEG      (--quality default=40)

Run ``nuke -h`` for all flags.
Repo  https://github.com/kay-a11y/aftermark
"""

import argparse, pathlib
import numpy as np
from PIL import Image, ImageFilter

def clean_image(path, crop_top=0, header_h=0):
    img = Image.open(path).convert("RGB")
    w, h = img.size

    if crop_top:
        img = img.crop((0, crop_top, w, h))

    new_w, new_h = int(img.width * 0.96), int(img.height * 0.96)
    img = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
    img = img.resize((w, h), Image.Resampling.LANCZOS)

    img = img.filter(ImageFilter.GaussianBlur(radius=1.3))

    arr = np.array(img, dtype=np.int16)
    noise = np.random.randint(-1, 2, arr.shape)   # -1, 0, or +1
    arr = np.clip(arr + noise, 0, 255).astype(np.uint8)
    img = Image.fromarray(arr, mode="RGB")

    jit_x, jit_y = 0.37, 0.19
    img = img.transform(
            img.size,
            Image.AFFINE,
            (1, 0, jit_x, 0, 1, jit_y),
            resample=Image.Resampling.BICUBIC)

    if header_h > 0:
        w, h = img.size
        header = img.crop((0, 0, w, min(header_h, h))) 
        header = header.filter(ImageFilter.MedianFilter(3))
        img.paste(header, (0, 0))

    return img

def iter_inputs(path: pathlib.Path):
    if path.is_file():
        yield path
    else: 
        yield from path.glob("*.[pjPJ][pnN]*")

# =============== CLI =============== #

def main() -> None:
    ap = argparse.ArgumentParser(
            formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    ap.add_argument("input",  
                    help="image *file* or *folder* of images to clean")
    ap.add_argument("outdir",  nargs="?", default=".", 
                    help="where cleaned files go (default: current dir)")
    ap.add_argument("--crop", type=int, default=0,
                    help="pixels to crop off the very top")
    ap.add_argument("--header", type=int, default=0,
                    help="height (px) of header band to median-filter; 0 = skip")
    
    args = ap.parse_args()
    in_path  = pathlib.Path(args.input).expanduser()
    out_dir  = pathlib.Path(args.outdir).expanduser()
    out_dir.mkdir(exist_ok=True)

    for p in iter_inputs(in_path):
        cleaned = clean_image(p, crop_top=args.crop, header_h=args.header)
        out_name = f"{p.stem}_clean.jpg"
        cleaned.save(out_dir / out_name, 
                     format="JPEG", quality=40, optimize=True, subsampling=2)
        print(f"✔ {out_name}  →  {out_dir}")

if __name__ == "__main__":
    main()
