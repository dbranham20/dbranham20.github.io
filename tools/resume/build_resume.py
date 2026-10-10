"""Build Daniel Branham's one-page public resume with reportlab.

Usage (from the repo root):
    python tools/resume/build_resume.py              # writes assets/DanielBPublicResume.pdf
    python tools/resume/build_resume.py out.pdf      # writes somewhere else
    python tools/resume/build_resume.py --preview    # also renders resume_preview_p*.png next to the PDF

See tools/resume/README.md before editing.
"""
import sys
from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_RIGHT, TA_CENTER
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table,
                                TableStyle, HRFlowable, KeepTogether)

REPO = Path(__file__).resolve().parents[2]
_args = [a for a in sys.argv[1:] if not a.startswith("--")]
PREVIEW = "--preview" in sys.argv
OUT = _args[0] if _args else str(REPO / "assets" / "DanielBPublicResume.pdf")

NAVY = HexColor("#0f1833")
ACCENT = HexColor("#c2703d")
MUTED = HexColor("#5b6478")
INK = HexColor("#1b1f2a")

base = dict(fontName="Helvetica", fontSize=9.5, leading=12.5, textColor=INK)
S = {
    "name": ParagraphStyle("name", fontName="Helvetica-Bold", fontSize=22, leading=26, textColor=NAVY, alignment=TA_CENTER),
    "title": ParagraphStyle("title", fontName="Helvetica", fontSize=11, leading=14, textColor=ACCENT, alignment=TA_CENTER),
    "contact": ParagraphStyle("contact", fontName="Helvetica", fontSize=9, leading=12, textColor=MUTED, alignment=TA_CENTER),
    "h": ParagraphStyle("h", fontName="Helvetica-Bold", fontSize=10.5, leading=13, textColor=NAVY, spaceBefore=7, spaceAfter=1),
    "body": ParagraphStyle("body", **base),
    "company": ParagraphStyle("company", fontName="Helvetica-Bold", fontSize=10.5, leading=13, textColor=INK),
    "right": ParagraphStyle("right", fontName="Helvetica", fontSize=9, leading=13, textColor=MUTED, alignment=TA_RIGHT),
    "role": ParagraphStyle("role", fontName="Helvetica-Bold", fontSize=9.5, leading=12.5, textColor=ACCENT),
    "roledate": ParagraphStyle("roledate", fontName="Helvetica-Oblique", fontSize=9, leading=12.5, textColor=MUTED, alignment=TA_RIGHT),
    "bullet": ParagraphStyle("bullet", leftIndent=12, bulletIndent=2, spaceAfter=1.5, **base),
    "tech": ParagraphStyle("tech", fontName="Helvetica-Oblique", fontSize=8.8, leading=11.5, textColor=MUTED, spaceBefore=1),
}

W = letter[0] - 1.3 * inch - 12  # content width (frame has 6pt padding per side)


def two_col(left, right, lstyle, rstyle, ratio=0.68):
    t = Table([[Paragraph(left, S[lstyle]), Paragraph(right, S[rstyle])]],
              colWidths=[W * ratio, W * (1 - ratio)])
    t.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "BOTTOM"),
                           ("LEFTPADDING", (0, 0), (-1, -1), 0),
                           ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                           ("TOPPADDING", (0, 0), (-1, -1), 0),
                           ("BOTTOMPADDING", (0, 0), (-1, -1), 0)]))
    return t


def section(title):
    return [Paragraph(title.upper(), S["h"]),
            HRFlowable(width="100%", thickness=0.8, color=ACCENT, spaceBefore=0, spaceAfter=4)]


def bullets(items):
    return [Paragraph(i, S["bullet"], bulletText="•") for i in items]


def job(company, location, roles, items, tech):
    """roles: list of (title, dates); newest first."""
    block = [two_col(company, location, "company", "right")]
    for title, dates in roles:
        block.append(two_col(title, dates, "role", "roledate"))
    block += bullets(items)
    if tech:
        block.append(Paragraph(tech, S["tech"]))
    block.append(Spacer(1, 4))
    return KeepTogether(block)


story = [
    Paragraph("Daniel Branham", S["name"]),
    Paragraph("Principal Software Engineer", S["title"]),
    Spacer(1, 2),
    Paragraph('Charlotte, NC &nbsp;·&nbsp; <a href="mailto:idanielbranham@gmail.com">idanielbranham@gmail.com</a> '
              '&nbsp;·&nbsp; <a href="https://dbranham20.github.io/">dbranham20.github.io</a> '
              '&nbsp;·&nbsp; <a href="https://github.com/dbranham20">github.com/dbranham20</a> '
              '&nbsp;·&nbsp; <a href="https://www.linkedin.com/in/daniel-branham-928033152/">linkedin.com/in/daniel-branham-928033152</a>',
              S["contact"]),
]

story += section("Summary")
story.append(Paragraph(
    "Full-stack software engineer with 7+ years of experience building data-forward web applications and "
    "platforms. Currently leading full-stack development and cloud architecture on internal Treasury platforms "
    "at Ally, with Python, Dash, PostgreSQL, and AWS. I enjoy turning messy workflows into reliable, observable systems.",
    S["body"]))

story += section("Experience")
story.append(job(
    "Ally Financial", "Charlotte, NC · Hybrid",
    [("Principal Software Engineer", "August 2026 – Present"),
     ("Senior Software Engineer", "March 2024 – July 2026")],
    ["Lead full-stack development and cloud architecture across two flagship internal platforms supporting the "
     "Treasury of one of the largest digital-only banks in the U.S.",
     "Build data applications with Python and Dash backed by PostgreSQL.",
     "Deploy event-driven pipelines on AWS (Lambda, Batch, ECS, SQS), with infrastructure managed in Terraform."],
    "Python · Dash · PostgreSQL · AWS (Lambda, Batch, ECS, SQS) · Terraform"))
story.append(job(
    "Global Custom Commerce (A Home Depot Company)", "Charlotte, NC · Remote",
    [("Software Engineer (Contract)", "June 2022 – January 2024")],
    ["Developed features for Design Builder, one of The Home Depot's flagship products, letting customers and "
     "in-store associates customize and order products.",
     "Full-stack development with React and .NET, backed by MongoDB and SQL Server."],
    "React · .NET · MongoDB · SQL Server · Git · Jira"))
story.append(job(
    "Honeywell", "Fort Mill, SC",
    [("Software Engineer III", "October 2021 – May 2022"),
     ("Software Engineer II", "July 2019 – October 2021")],
    ["Joined a newly formed team in the Safety and Productivity Solutions business group to build an entirely new "
     "product, Operational Intelligence, from the ground up.",
     "Maintained and implemented features across 20+ microservices; co-owner and point of contact for several.",
     "Partnered closely with the professional services team to relay customer needs into the product."],
    "React · .NET · MongoDB · Microservices · Git · Jira"))
story += section("Earlier Experience")
for org, role, dates, desc in [
    ("Delta Bravo Artificial Intelligence", "Software Engineer Intern", "Oct 2018 – May 2019",
     "AI startup: Golang APIs, Ember/Handlebars front end, PostgreSQL, ML in Python."),
    ("UNC Charlotte", "Undergraduate Researcher", "May 2018 – Jul 2018",
     "AR/VR lab: Unity3D and C#, Vuforia AR, networking, iOS builds."),
    ("SCANA Corporation", "Software Engineer / Infrastructure Analyst Intern", "May 2017 – Aug 2017",
     "Internal security team: PowerShell, C#, Ionic mobile apps."),
]:
    story.append(two_col(f"<b>{role}</b>, {org}", dates, "body", "roledate", ratio=0.72))
    story.append(Paragraph(desc, S["bullet"], bulletText="•"))

story += section("Skills")
skills = [
    ("Languages &amp; Frameworks", "Python, JavaScript, C#, Go, SQL, Shell · Dash, React, .NET, Ember.js"),
    ("Cloud &amp; Data", "AWS, Terraform, Microservices · PostgreSQL, SQL Server, MongoDB, Pandas"),
    ("Tools", "Git, GitHub, Jira"),
]
for k, v in skills:
    story.append(Paragraph(f"<b>{k}:</b> {v}", S["body"]))

story += section("Education")
story.append(two_col("<b>Winthrop University</b> — B.S. Computer Science, Minor in Mathematics",
                     "Rock Hill, SC · May 2019", "body", "right", ratio=0.7))

story += section("Awards")
story += bullets([
    "<b>I'm an Ally Award</b>, Ally Financial (April 2026): enterprise-wide peer recognition.",
    "<b>Honorable Mention</b>, COMAP Mathematical Contest in Modeling (2019): top 16% of 14,108 teams.",
])

doc = SimpleDocTemplate(OUT, pagesize=letter, leftMargin=0.65 * inch, rightMargin=0.65 * inch,
                        topMargin=0.45 * inch, bottomMargin=0.45 * inch,
                        title="Daniel Branham — Resume", author="Daniel Branham")
doc.build(story)
print(f"wrote {OUT} ({doc.page} page{'s' if doc.page != 1 else ''})")
if doc.page != 1:
    print("WARNING: resume is longer than one page; trim content or spacing.")

if PREVIEW:
    import pypdfium2  # pip install pypdfium2
    out = Path(OUT)
    for i, page in enumerate(pypdfium2.PdfDocument(OUT)):
        png = out.with_name(f"resume_preview_p{i + 1}.png")
        page.render(scale=1.6).to_pil().save(png)
        print(f"preview: {png}")
