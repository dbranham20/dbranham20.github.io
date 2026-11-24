# Photo gallery builder

Builds one page per location at `gallery/<slug>/`, for NFC map pins (or any link).

```bash
pip install pillow pillow-heif        # pillow-heif only needed for iPhone .heic files
python tools/gallery/make_gallery.py ~/Photos/barcelona barcelona --title "Barcelona" --subtitle "June 2025"
git add gallery && git commit -m "Add Barcelona gallery" && git push
```

The page is live at `https://dbranham20.github.io/gallery/barcelona/` about a minute after the push.

- Photos are resized (1600 px full, 640 px thumbnails) and re-saved as JPEG, which **strips EXIF data including GPS location**. Originals are never touched.
- Photos are ordered by capture time, falling back to file name.
- Re-running with the same slug rebuilds that gallery from scratch.
- Pages are marked `noindex`, so search engines are asked to skip them. The repo is public, so anyone with the link (or browsing the repo) can still see the photos.
- Layout and styling live in `template.html`; changes apply to galleries the next time they are built.
