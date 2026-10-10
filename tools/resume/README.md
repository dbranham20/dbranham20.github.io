# Resume builder

`build_resume.py` generates `assets/DanielBPublicResume.pdf`, the PDF linked from the
"View Resume (PDF)" button in `index.html`. The PDF is built entirely from the content
hard-coded in the script, so **edit the script, never the PDF**.

## Quick start

```sh
pip install reportlab pypdfium2      # pypdfium2 is only needed for --preview
python tools/resume/build_resume.py --preview
```

This overwrites `assets/DanielBPublicResume.pdf` and writes `assets/resume_preview_p1.png`.
Look at the preview before committing. Preview PNGs are git-ignored. To experiment
without touching the real file, pass an output path:
`python tools/resume/build_resume.py /tmp/test.pdf --preview`.

## Instructions for an LLM / future editor

1. **Keep it to one page.** The script prints a warning if the output is longer. Always run
   with `--preview` and look at the PNG before replacing the real PDF. If it overflows, trim
   wording or the Skills lines first, then spacing (`spaceBefore`, `Spacer` sizes, margins in
   `SimpleDocTemplate`). Do not shrink the base font below ~9pt.
2. **Keep the PDF and the website in sync.** Job titles, dates, awards, and education also
   appear in `index.html` (`#work`, `#edu`, `#awards`). When one changes, update the other.
   LinkedIn is the source of truth for dates.
3. **Public document.** It is downloadable by anyone, so no phone number or street address.
4. **Don't invent facts or metrics.** Only use what the owner provided. Ask before adding numbers.
5. **Owner preferences so far:**
   - Keep award descriptions modest. Don't add selectivity stats like "~80 recipients from
     thousands of nominees" (the owner found it too gratuitous).
   - Show promotions as stacked roles under one company (Ally, Honeywell), newest first.
   - Internships live in the compact "Earlier Experience" section, one line each.

## Where things are in the script

| To change… | Edit… |
|---|---|
| Name, headline, contact links | `story = [...]` at the top of the content |
| Summary | `section("Summary")` paragraph |
| A full-time job | the matching `job(company, location, roles, bullets, tech)` call; `roles` is a list of `(title, dates)`, newest first |
| Add a new job | add a `job(...)` call above the current first one |
| Internships | the list under `section("Earlier Experience")` |
| Skills | the `skills` list |
| Education / Awards | the last two sections |
| Colors / fonts | `NAVY`, `ACCENT`, `MUTED`, `INK`, and the `S` style dict |

Text goes through reportlab `Paragraph` markup: escape `&` as `&amp;`, use `<b>`/`<i>` for
emphasis, and use `–` (en dash) for date ranges and `·` (middle dot) as a separator.
The built-in Helvetica font has no glyphs for emoji or Unicode sub/superscripts.

## After rebuilding

Commit both the script change and the regenerated PDF together.
