#!/usr/bin/env python3
"""Set up photo galleries from folders of photos dropped into gallery/.

Workflow:
    1. Copy photos into gallery/<name>/   (e.g. gallery/barcelona/). Use COPIES, not originals.
    2. Run:  python tools/gallery/make_gallery.py
    3. Commit and push. The page is live at  <site>/gallery/<name>/

The script is safe to run any time. It only touches folders that contain new, unprocessed photos:
  * resizes each photo (full + thumbnail) into gallery/<name>/img/, as JPEG with all EXIF/GPS data removed
  * DELETES the raw copy once its processed version is saved (so raw photos never get committed)
  * records the gallery in gallery/<name>/gallery.json and writes gallery/<name>/index.html
Folders with nothing new are left alone. Add more photos to a folder later and re-run to add them.

Options:
    make_gallery.py barcelona                      only this folder
    make_gallery.py barcelona --title "Barcelona" --subtitle "June 2025"
    make_gallery.py --rebuild                      rewrite every page from gallery.json (after editing template.html)

Requires Pillow (pip install pillow). For iPhone HEIC files also: pip install pillow-heif
"""
import argparse
import html
import json
import re
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
SLUG_RE = re.compile(r"[a-z0-9]+(-[a-z0-9]+)*")


def default_title(slug):
    return slug.replace("-", " ").title()


def load_gallery(folder: Path):
    path = folder / "gallery.json"
    if path.exists():
        data = json.loads(path.read_text(encoding="utf-8"))
    else:
        data = {}
    data.setdefault("title", default_title(folder.name))
    data.setdefault("subtitle", "")
    data.setdefault("photos", [])
    return data


def unique_name(stem, used):
    base = re.sub(r"[^A-Za-z0-9_-]+", "-", stem).strip("-") or "photo"
    name, n = base, 2
    while name.lower() in used:
        name, n = f"{base}-{n}", n + 1
    used.add(name.lower())
    return name + ".jpg"


def process_photo(src: Path, name: str, img_dir: Path, args):
    """Write full + thumb copies of src as clean JPEGs. Returns the manifest entry."""
    with Image.open(src) as im:
        exif = im.getexif()
        taken = str(exif.get_ifd(0x8769).get(36867) or exif.get(306) or "")
        icc = im.info.get("icc_profile")  # colour profile only; contains no location data
        im = ImageOps.exif_transpose(im)  # bake rotation in, since EXIF is dropped
        if im.mode != "RGB":
            im = im.convert("RGB")
        kwargs = dict(format="JPEG", quality=args.quality, optimize=True, progressive=True)
        if icc:
            kwargs["icc_profile"] = icc  # note: no exif= argument, so all metadata is dropped
        full = im.copy()
        full.thumbnail((args.full, args.full), Image.LANCZOS)
        full.save(img_dir / "full" / name, **kwargs)
        thumb = im.copy()
        thumb.thumbnail((args.thumb, args.thumb), Image.LANCZOS)
        thumb.save(img_dir / "thumb" / name, **kwargs)
    return {"file": name, "taken": taken, "w": thumb.size[0], "h": thumb.size[1]}


def render_page(folder: Path, data):
    title = data["title"]
    cards = []
    for n, p in enumerate(data["photos"], 1):
        alt = html.escape(f"{title}, photo {n}")
        cards.append(
            f'      <a class="ph" href="img/full/{p["file"]}"><img src="img/thumb/{p["file"]}" '
            f'width="{p["w"]}" height="{p["h"]}" loading="lazy" decoding="async" alt="{alt}"></a>'
        )
    count = f"{len(cards)} photo" + ("" if len(cards) == 1 else "s")
    sub = f'{data["subtitle"].strip()} · {count}' if data["subtitle"].strip() else count
    page = (HERE / "template.html").read_text(encoding="utf-8")
    page = (page.replace("{{TITLE}}", html.escape(title))
                .replace("{{SUBTITLE}}", html.escape(sub))
                .replace("{{PHOTOS}}", "\n".join(cards)))
    (folder / "index.html").write_text(page, encoding="utf-8")


def sort_key(p):
    return (0 if p["taken"] else 1, p["taken"], p["file"].lower())


def handle_folder(folder: Path, args, explicit: bool):
    """Returns True if the folder's page was (re)built."""
    slug = folder.name
    if not SLUG_RE.fullmatch(slug):
        print(f"[skip] {slug}: folder names must be lowercase letters, numbers and hyphens "
              f"(e.g. 'mexico-city'). Rename it and re-run.")
        return False

    raws = sorted(f for f in folder.iterdir()
                  if f.is_file() and f.suffix.lower() in EXTS and not f.name.startswith("."))
    has_manifest = (folder / "gallery.json").exists()
    meta_change = explicit and (args.title is not None or args.subtitle is not None)
    needs_page = has_manifest and (args.rebuild or meta_change or not (folder / "index.html").exists())

    if not raws and not needs_page:
        if not has_manifest:
            print(f"[skip] {slug}: no photos found")
        else:
            print(f"[ok]   {slug}: up to date")
        return False

    data = load_gallery(folder)
    if explicit and args.title is not None:
        data["title"] = args.title
    if explicit and args.subtitle is not None:
        data["subtitle"] = args.subtitle

    img_dir = folder / "img"
    (img_dir / "full").mkdir(parents=True, exist_ok=True)
    (img_dir / "thumb").mkdir(parents=True, exist_ok=True)

    # forget photos whose image files were deleted by hand
    before = len(data["photos"])
    data["photos"] = [p for p in data["photos"]
                      if (img_dir / "full" / p["file"]).exists() and (img_dir / "thumb" / p["file"]).exists()]
    if len(data["photos"]) != before:
        print(f"       {slug}: dropped {before - len(data['photos'])} photo(s) no longer in img/")

    used = {p["file"][:-4].lower() for p in data["photos"]}
    added = failed = 0
    for src in raws:
        if src.suffix.lower() in (".heic", ".heif") and pillow_heif is None:
            print(f"       {slug}: left {src.name} alone (HEIC needs: pip install pillow-heif)")
            failed += 1
            continue
        name = unique_name(src.stem, used)
        try:
            entry = process_photo(src, name, img_dir, args)
        except Exception as e:  # leave the raw file in place so nothing is lost
            used.discard(name[:-4].lower())
            print(f"       {slug}: could not process {src.name}: {e}")
            failed += 1
            continue
        src.unlink()  # processed copy is saved; the raw copy must not be committed
        data["photos"].append(entry)
        added += 1

    if not data["photos"]:
        print(f"[skip] {slug}: no usable photos")
        return False

    data["photos"].sort(key=sort_key)
    (folder / "gallery.json").write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    render_page(folder, data)

    size = sum(f.stat().st_size for f in img_dir.rglob("*.jpg")) / 1e6
    note = f"added {added}" if added else "rebuilt page"
    if failed:
        note += f", {failed} left unprocessed"
    print(f"[done] {slug}: {note}; {len(data['photos'])} photos, {size:.1f} MB")
    return True


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("folders", nargs="*", help="only these gallery folders (default: all of gallery/)")
    ap.add_argument("--title", help="page title (single folder only; saved in gallery.json)")
    ap.add_argument("--subtitle", help="line under the title, e.g. a date (single folder only)")
    ap.add_argument("--rebuild", action="store_true", help="rewrite pages for all existing galleries")
    ap.add_argument("--full", type=int, default=1600, help="max size of full photos in px (default 1600)")
    ap.add_argument("--thumb", type=int, default=640, help="max size of grid thumbnails in px (default 640)")
    ap.add_argument("--quality", type=int, default=82, help="JPEG quality (default 82)")
    ap.add_argument("--base-url", default="https://dbranham20.github.io", help="used only to print URLs")
    ap.add_argument("--gallery", type=Path, default=REPO_ROOT / "gallery", help="gallery root folder")
    args = ap.parse_args()

    if (args.title is not None or args.subtitle is not None) and len(args.folders) != 1:
        sys.exit("--title/--subtitle need exactly one folder name, e.g.: make_gallery.py barcelona --title Barcelona")

    root = args.gallery
    if args.folders:
        targets = []
        for name in args.folders:
            f = root / name
            if not f.is_dir():
                sys.exit(f"no such folder: {f}")
            targets.append(f)
    else:
        if not root.is_dir():
            sys.exit(f"{root} doesn't exist yet. Create gallery/<name>/ (e.g. gallery/barcelona/) "
                     f"and copy photos into it.")
        targets = sorted(p for p in root.iterdir() if p.is_dir() and not p.name.startswith("."))

    if not targets:
        sys.exit("nothing to do: copy photos into gallery/<name>/ first")

    built = [f for f in targets if handle_folder(f, args, explicit=bool(args.folders))]
    if built:
        print("\nWhen you commit and push, these will be live at:")
        for f in built:
            print(f"  {args.base_url}/gallery/{f.name}/")


if __name__ == "__main__":
    main()
