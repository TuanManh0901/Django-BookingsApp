#!/usr/bin/env python3
"""Generate multi-resolution favicon.ico from a PNG.

Usage:
  python tools/generate_favicon.py

This script expects the source PNG at:
  static/argon-dashboard-master/assets/img/favicon-custom.png

It will create:
  static/favicon.ico

Requires: Pillow (`pip install Pillow`)
"""
from PIL import Image
import os
import sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(BASE, 'static', 'argon-dashboard-master', 'assets', 'img', 'favicon-custom.png')
OUT = os.path.join(BASE, 'static', 'favicon.ico')

def main():
    if not os.path.exists(SRC):
        print(f"Source PNG not found: {SRC}")
        print("Please place your favicon PNG at that path (see workspace instructions).")
        sys.exit(1)

    im = Image.open(SRC)
    # Ensure RGBA
    if im.mode != 'RGBA':
        im = im.convert('RGBA')

    # Sizes to include in ICO
    sizes = [(16,16),(24,24),(32,32),(48,48),(64,64),(128,128)]
    icons = [im.resize(s, Image.LANCZOS) for s in sizes]
    # Save multi-size ICO
    icons[0].save(OUT, format='ICO', sizes=sizes)
    print(f'Wrote {OUT} (sizes: {sizes})')

if __name__ == '__main__':
    main()
