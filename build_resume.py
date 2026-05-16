"""Build Daniel Branham's resume PDF — single page, matches the existing visual style."""

from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor, black, white
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas


OUTPUT = "assets/DanielBPublicResume.pdf"

# Colors (sampled from the existing resume)
ACCENT_BG = HexColor("#d4ede4")   # contact bar + skill pill background (light tint of brand teal)
ACCENT_LINE = HexColor("#49bf9d")  # underline beneath section headings (site brand teal)
TEXT = HexColor("#1f1f1f")
MUTED = HexColor("#555555")
LIGHT_MUTED = HexColor("#777777")


# ─── Layout ───────────────────────────────────────────────────────────────
PAGE_W, PAGE_H = letter
LEFT = 0.6 * inch
RIGHT = PAGE_W - 0.6 * inch
USABLE_W = RIGHT - LEFT


def section_heading(c, y, label, top_gap=16):
    y -= top_gap
    c.setFillColor(TEXT)
    c.setFont("Helvetica-Bold", 13)
    c.drawString(LEFT, y, label)
    c.setStrokeColor(ACCENT_LINE)
    c.setLineWidth(1)
    c.line(LEFT, y - 7, LEFT + 24, y - 7)
    return y - 20


def wrap_text(c, text, font, size, max_w):
    """Greedy word wrap. Returns list of lines."""
    c.setFont(font, size)
    words = text.split()
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if c.stringWidth(trial, font, size) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def draw_bullet(c, x, y, text, font="Helvetica", size=10, indent=12, line_h=13):
    """Draws a single bullet line, wrapping as needed. Returns new y."""
    c.setFillColor(TEXT)
    c.setFont(font, size)
    # bullet dot
    c.circle(x + 2.5, y + 3, 1.1, stroke=0, fill=1)
    # wrapped text
    lines = wrap_text(c, text, font, size, USABLE_W - indent)
    for i, ln in enumerate(lines):
        c.drawString(x + indent, y, ln)
        if i < len(lines) - 1:
            y -= line_h
    return y - line_h


def draw_role(c, y, title, company, location, dates, top_gap=6):
    """Renders a role header line + sub line. Returns new y."""
    y -= top_gap
    c.setFillColor(TEXT)
    c.setFont("Helvetica-Bold", 11)
    c.drawString(LEFT, y, title)
    title_w = c.stringWidth(title, "Helvetica-Bold", 11)
    c.setFont("Helvetica-Oblique", 10.5)
    c.setFillColor(MUTED)
    c.drawString(LEFT + title_w + 6, y, f"{company}, {location}")
    # dates right-aligned
    c.setFont("Helvetica-Oblique", 10)
    c.setFillColor(LIGHT_MUTED)
    dates_w = c.stringWidth(dates, "Helvetica-Oblique", 10)
    c.drawString(RIGHT - dates_w, y, dates)
    return y - 14


def draw_skill_pills(c, y, skills, max_w):
    """Draws skills as rounded-rect pill badges. Wraps to multiple rows."""
    font, size = "Helvetica", 10.5
    c.setFont(font, size)
    pad_x, pad_y = 8, 4
    gap_x, gap_y = 6, 6
    pill_h = 18

    x = LEFT
    row_top = y
    for s in skills:
        tw = c.stringWidth(s, font, size)
        pw = tw + pad_x * 2
        if x + pw > LEFT + max_w:
            x = LEFT
            row_top -= pill_h + gap_y
        c.setFillColor(ACCENT_BG)
        c.setStrokeColor(ACCENT_BG)
        c.roundRect(x, row_top - pill_h + pad_y, pw, pill_h, 3, stroke=0, fill=1)
        c.setFillColor(TEXT)
        c.drawString(x + pad_x, row_top - pill_h + pad_y + 4.5, s)
        x += pw + gap_x
    return row_top - pill_h - 2


def build():
    c = canvas.Canvas(OUTPUT, pagesize=letter)
    c.setTitle("Daniel Branham — Resume")
    c.setAuthor("Daniel Branham")

    y = PAGE_H - 0.65 * inch

    # ─── Name + title ─────────────────────────────────────────────────────
    c.setFillColor(TEXT)
    c.setFont("Helvetica-Bold", 26)
    c.drawString(LEFT, y, "Daniel Branham")
    y -= 20
    c.setFillColor(MUTED)
    c.setFont("Helvetica", 12)
    c.drawString(LEFT, y, "Senior Software Engineer")
    y -= 16

    # ─── Contact bar ──────────────────────────────────────────────────────
    bar_h = 22
    c.setFillColor(ACCENT_BG)
    c.rect(LEFT, y - bar_h + 5, USABLE_W, bar_h, stroke=0, fill=1)
    c.setFillColor(TEXT)
    c.setFont("Helvetica", 10)
    contact = "  idanielbranham@gmail.com    |    Charlotte, NC    |    dbranham20.github.io"
    c.drawString(LEFT + 4, y - 9, contact)
    y -= bar_h + 4

    # ─── Introduction ─────────────────────────────────────────────────────
    y = section_heading(c, y, "INTRODUCTION")
    intro = (
        "Senior software engineer focused on full-stack development, AWS cloud "
        "architecture, and staying ahead of the AI learning curve. Extensive " 
        "experience in collaborating closely with stakeholders and building systems "
        "that last."
    )
    c.setFillColor(TEXT)
    for ln in wrap_text(c, intro, "Helvetica", 10.5, USABLE_W):
        c.setFont("Helvetica", 10.5)
        c.drawString(LEFT, y, ln)
        y -= 13.5

    # ─── Skills ───────────────────────────────────────────────────────────
    y = section_heading(c, y, "SKILLS")
    skills = [
        "Python", "Plotly Dash", "Terraform", "PostgreSQL", "SQL Server",
        "MongoDB", "AWS ECS", "AWS Batch", "AWS Lambda", "AWS Step Functions",
        ".NET", "React", "Microservices", "Cloud Architecture",
        "Claude Code",
    ]
    y = draw_skill_pills(c, y, skills, USABLE_W)

    # ─── Experience ───────────────────────────────────────────────────────
    y = section_heading(c, y, "EXPERIENCE")

    # Ally
    y = draw_role(c, y, "Senior Software Engineer", "Ally Financial", "Charlotte, NC", "March 2024 – Present")
    y = draw_bullet(c, LEFT, y,
        "Lead full-stack development and cloud architecture on two internal Treasury platforms "
        "(FORT Pricing, CLEAR) supporting one of the largest digital-only banks in the U.S.")
    y = draw_bullet(c, LEFT, y,
        "Engineered AWS infrastructure patterns now reused across the team; designed a novel "
        "ETL job framework later extended into a third project and handed off to a sustain team")
    y = draw_bullet(c, LEFT, y,
        "Built CLEAR cloud-native from the ground up; consolidated disparate data sources into a "
        "real-time view of available liquid cash, supporting Fed compliance and daily obligations")
    # Global Custom Commerce
    y = draw_role(c, y, "Software Engineer", "Global Custom Commerce (Home Depot)", "Charlotte, NC", "June 2022 – January 2024")
    y = draw_bullet(c, LEFT, y,
        "Built features for The Home Depot's Design Builder, enabling customers and in-store "
        "associates to customize and order doors, window blinds, and other made-to-order products")
    # Honeywell
    y = draw_role(c, y, "Software Engineer II / III", "Honeywell", "Fort Mill, SC", "July 2019 – May 2022")
    y = draw_bullet(c, LEFT, y,
        "Joined a newly formed team in Safety and Productivity Solutions, building Operational "
        "Intelligence — a new product — from the ground up as part of Honeywell's push into software")
    y = draw_bullet(c, LEFT, y,
        "Co-owned multiple services across a 20+ microservice architecture and worked closely "
        "with the professional services team to support customer needs")
    # Delta Bravo
    y = draw_role(c, y, "Software Engineer Intern", "Delta Bravo AI", "Rock Hill, SC", "October 2018 – May 2019")
    y = draw_bullet(c, LEFT, y,
        "Built features at an early-stage AI-acceleration startup using Golang, EmberJS, and Python")
    # UNCC
    y = draw_role(c, y, "Undergraduate Researcher", "University of North Carolina", "Charlotte, NC", "May 2018 – August 2018")
    y = draw_bullet(c, LEFT, y,
        "Summer REU in the AR/VR lab — built an Augmented Reality application for First Responders using Unity3D")
    # SCANA
    y = draw_role(c, y, "Software Engineer Intern", "SCANA (now Dominion)", "Columbia, SC", "May 2017 – August 2017")
    y = draw_bullet(c, LEFT, y,
        "Developed tools for the Cyber Security team and shipped a media-team app during a 3-day hackathon")
    # ─── Education ────────────────────────────────────────────────────────
    y = section_heading(c, y, "EDUCATION", top_gap=18)
    col2_x = LEFT + USABLE_W / 2

    c.setFillColor(TEXT)
    c.setFont("Helvetica-Bold", 11)
    c.drawString(LEFT, y, "Bachelor of Science, Computer Science")
    c.drawString(col2_x, y, "High School Diploma")
    y -= 14
    c.setFont("Helvetica", 10.5)
    c.setFillColor(MUTED)
    c.drawString(LEFT, y, "Winthrop University, Rock Hill, SC")
    c.drawString(col2_x, y, "Thomas Sumter Academy, Sumter, SC")
    y -= 14
    c.setFillColor(LIGHT_MUTED)
    c.setFont("Helvetica-Oblique", 10)
    c.drawString(LEFT, y, "2015 – 2019")
    c.drawString(col2_x, y, "2011 – 2015")

    c.save()
    print(f"Wrote {OUTPUT}, final y = {y:.1f}")


if __name__ == "__main__":
    build()
