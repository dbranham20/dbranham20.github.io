#!/usr/bin/env python3
"""Build a photo gallery page for the site from a folder of photos.

Example:
    python tools/gallery/make_gallery.py ~/Photos/barcelona barcelona --title "Barcelona" --subtitle "June 2025"

Creates gallery/<slug>/index.html plus resized copies of the photos in gallery/<slug>/img/.
Photos are re-encoded as JPEG, which also strips all EXIF metadata (including GPS location).
Your originals are never modified.

Requires Pillow (pip install pillow). For iPhone HEIC files also: pip install pillow-heif
"""
import argparse
import html
import re
import shutil
import sys
from pathlib import Path

from PIL import Image, ImageOps

try:  # optional: lets Pillow open iPhone .heic files
    import pillow_heif
    pillow_heif.register_heif_opener()
except ImportError:
    pillow_heif = None

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parent.parent
EXTS = {".jpg", ".jpeg", ".png", ".webp", ".heic", ".heif"}


def taken_key(path: Path):
    """Sort by capture time when available, otherwise by file name."""
    try:
        with Image.open(path) as im:
            exif = im.getexif()
            dt = exif.get_ifd(0x8769).get(36867) or exif.get(306)  # DateTimeOriginal / DateTime
            if dt:
                return (0, str(dt), path.name.lower())
    except Exception:
        pass
    return (1, "", path.name.lower())


def process(src: Path, full_path: Path, thumb_path: Path, full_px: int, thumb_px: int, quality: int):
    with Image.open(src) as im:
        icc = im.info.get("icc_profile")  # keep colour profile (no location data in it)
        im = ImageOps.exif_transpose(im)  # bake in rotation, since EXIF is being dropped
        if im.mode not in ("RGB",):
            im = im.convert("RGB")
        full = im.copy()
        full.thumbnail((full_px, full_px), Image.LANCZOS)
        save_kwargs = dict(format="JPEG", quality=quality, optimize=True, progressive=True)
        if icc:
            save_kwargs["icc_profile"] = icc
        full.save(full_path, **save_kwargs)
        thumb = im.copy()
        thumb.thumbnail((thumb_px, thumb_px), Image.LANCZOS)
        thumb.save(thumb_path, **save_kwargs)
        return thumb.size


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("source", type=Path, help="folder containing the photos")
    ap.add_argument("slug", help="URL name, e.g. mexico-city -> /gallery/mexico-city/")
    ap.add_argument("--title", help="page title (default: made from the slug)")
    ap.add_argument("--subtitle", default="", help="line under the title, e.g. a date")
    ap.add_argument("--full", type=int, default=1600, help="max size of full photos in px (default 1600)")
    ap.add_argument("--thumb", type=int, default=640, help="max size of grid thumbnails in px (default 640)")
    ap.add_argument("--quality", type=int, default=82, help="JPEG quality (default 82)")
    ap.add_argument("--base-url", default="https://dbranham20.github.io", help="used only to print the final URL")
    ap.add_argument("--out", type=Path, default=REPO_ROOT / "gallery", help="gallery root folder")
    args = ap.parse_args()

    if not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", args.slug):
        sys.exit("slug must be lowercase letters, numbers and hyphens, e.g. mexico-city")
    if not args.source.is_dir():
        sys.exit(f"not a folder: {args.source}")

    files = sorted((p for p in args.source.iterdir() if p.suffix.lower() in EXTS and not p.name.startswith(".")),
                   key=taken_key)
    if not files:
        sys.exit("no photos found (looked for jpg, png, webp, heic)")
    if any(p.suffix.lower() in (".heic", ".heif") for p in files) and pillow_heif is None:
        sys.exit("HEIC photos found; run: pip install pillow-heif")

    title = args.title or args.slug.replace("-", " ").title()
    page_dir = args.out / args.slug
    img_dir = page_dir / "img"
    if img_dir.exists():
        shutil.rmtree(img_dir)  # rebuild cleanly so removed photos don't linger
    (img_dir / "full").mkdir(parents=True)
    (img_dir / "thumb").mkdir(parents=True)

    cards = []
    for n, src in enumerate(files, 1):
        name = f"{n:03d}.jpg"
        try:
            w, h = process(src, img_dir / "full" / name, img_dir / "thumb" / name,
                           args.full, args.thumb, args.quality)
        except Exception as e:
            print(f"  skipped {src.name}: {e}")
            continue
        alt = html.escape(f"{title}, photo {n}")
        cards.append(
            f'      <a class="ph" href="img/full/{name}"><img src="img/thumb/{name}" '
            f'width="{w}" height="{h}" loading="lazy" decoding="async" alt="{alt}"></a>'
        )
        print(f"  {src.name} -> {name}")

    if not cards:
        sys.exit("no photos could be processed")

    subtitle = args.subtitle.strip()
    count = f"{len(cards)} photo" + ("" if len(cards) == 1 else "s")
    subtitle = f"{subtitle} · {count}" if subtitle else count

    page = (HERE / "template.html").read_text(encoding="utf-8")
    page = (page.replace("{{TITLE}}", html.escape(title))
                .replace("{{SUBTITLE}}", html.escape(subtitle))
                .replace("{{PHOTOS}}", "\n".join(cards)))
    (page_dir / "index.html").write_text(page, encoding="utf-8")

    total = sum(f.stat().st_size for f in img_dir.rglob("*.jpg")) / 1e6
    print(f"\nBuilt {len(cards)} photos, {total:.1f} MB total, in {page_dir}")
    print(f"After you commit and push, the page will be at:\n  {args.base_url}/gallery/{args.slug}/")


if __name__ == "__main__":
    main()
