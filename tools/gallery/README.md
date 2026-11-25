# Photo gallery builder

One page per location at `gallery/<name>/`, meant for NFC map pins (or any link).

## Adding a gallery

1. Make a folder named in lowercase with hyphens, e.g. `gallery/barcelona/`, and **copy** your photos into it.
2. Run the script from the repo root:
   ```bash
   pip install pillow pillow-heif     # once; pillow-heif is only for iPhone .heic files
   python tools/gallery/make_gallery.py
   ```
3. Commit and push. The page is live at `https://dbranham20.github.io/gallery/barcelona/` about a minute later.

Optional title and date line (otherwise the title comes from the folder name):
```bash
python tools/gallery/make_gallery.py barcelona --title "Barcelona" --subtitle "June 2025"
```

## How it behaves

- Safe to re-run any time. Folders with nothing new are left alone ("up to date").
- Add more photos to a folder later and re-run; they are merged in by date taken.
- Each photo becomes a 1600 px JPEG plus a 640 px thumbnail in `img/`, with **all EXIF data, including GPS location, removed**.
- **The raw copies you dropped into the folder are deleted** once their processed versions are saved, so work from copies, never originals. Anything that can't be processed is left in place and reported.
- To remove a photo, delete its files from `img/full/` and `img/thumb/` and re-run; it drops off the page.
- `gallery.json` in each folder stores the title, subtitle and photo list (edit it by hand if you like, then run with `--rebuild`).
- `gallery/index.html` is a simple contents list of every gallery (title, subtitle, photo count). The script rewrites it on every run, so new galleries appear automatically. To keep a gallery reachable by its URL but **off the list**, add `"unlisted": true` to its `gallery.json` and re-run.
- `--rebuild` rewrites every page from its `gallery.json`, e.g. after changing `template.html`.
- Pages are marked `noindex`, but the repo is public, so anyone with the link (or browsing the repo) can see the photos.
