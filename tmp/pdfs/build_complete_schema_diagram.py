from pathlib import Path

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor, Color
from reportlab.lib.pagesizes import A3, landscape
from reportlab.lib.utils import ImageReader


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "output" / "pdf" / "llm_prompt_eval_registry_complete_schema.pdf"
OUT.parent.mkdir(parents=True, exist_ok=True)

PAGE_W, PAGE_H = landscape(A3)

NAVY = HexColor("#152A42")
BLUE = HexColor("#246B9C")
LIGHT_BLUE = HexColor("#E9F3FA")
PALE_BLUE = HexColor("#F5FAFD")
INK = HexColor("#17202A")
MUTED = HexColor("#566573")
GRID = HexColor("#C9D6E0")
SOFT = HexColor("#F4F6F7")
GREEN = HexColor("#1E7A5C")
GOLD = HexColor("#B47A17")
RED = HexColor("#A43E3E")
WHITE = HexColor("#FFFFFF")


def setup_fonts():
    candidates = [
        ("/System/Library/Fonts/Supplemental/Arial.ttf", "/System/Library/Fonts/Supplemental/Arial Bold.ttf"),
        ("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"),
    ]
    for regular, bold in candidates:
        if Path(regular).exists() and Path(bold).exists():
            pdfmetrics.registerFont(TTFont("SchemaSans", regular))
            pdfmetrics.registerFont(TTFont("SchemaSansBold", bold))
            return
    raise RuntimeError("No supported TrueType font found")


def rounded_box(c, x, y, w, h, radius=10, fill=WHITE, stroke=GRID, width=1):
    c.setFillColor(fill)
    c.setStrokeColor(stroke)
    c.setLineWidth(width)
    c.roundRect(x, y, w, h, radius, fill=1, stroke=1)


def text(c, x, y, value, size=8, color=INK, font="SchemaSans", align="left"):
    c.setFillColor(color)
    c.setFont(font, size)
    if align == "center":
        c.drawCentredString(x, y, value)
    elif align == "right":
        c.drawRightString(x, y, value)
    else:
        c.drawString(x, y, value)


def fitted_text(c, x, y, value, max_width, size=7.2, min_size=5.2,
                color=INK, font="SchemaSans"):
    chosen = size
    while chosen > min_size and pdfmetrics.stringWidth(value, font, chosen) > max_width:
        chosen -= 0.2
    text(c, x, y, value, chosen, color, font)


def table_box(c, x, y, w, title, rows, constraints=None, row_h=20, col_ratios=(0.40, 0.25, 0.35)):
    header_h = 38
    constraint_lines = constraints or []
    footer_h = 10 + 13 * len(constraint_lines) if constraint_lines else 8
    h = header_h + row_h * (len(rows) + 1) + footer_h

    rounded_box(c, x, y, w, h, radius=9, fill=WHITE, stroke=HexColor("#AFC1CF"), width=1.2)
    c.setFillColor(NAVY)
    c.roundRect(x, y + h - header_h, w, header_h, 9, fill=1, stroke=0)
    c.rect(x, y + h - header_h, w, header_h - 9, fill=1, stroke=0)
    text(c, x + 12, y + h - 24, title, 13, WHITE, "SchemaSansBold")

    col_x = [x, x + w * col_ratios[0], x + w * (col_ratios[0] + col_ratios[1]), x + w]
    table_top = y + h - header_h
    c.setFillColor(LIGHT_BLUE)
    c.rect(x, table_top - row_h, w, row_h, fill=1, stroke=0)
    for cx in col_x[1:-1]:
        c.setStrokeColor(GRID)
        c.setLineWidth(0.5)
        c.line(cx, y + footer_h, cx, table_top)
    text(c, col_x[0] + 7, table_top - row_h + 6, "FIELD", 7.2, NAVY, "SchemaSansBold")
    text(c, col_x[1] + 5, table_top - row_h + 6, "TYPE", 7.2, NAVY, "SchemaSansBold")
    text(c, col_x[2] + 5, table_top - row_h + 6, "RULES", 7.2, NAVY, "SchemaSansBold")

    for idx, (field, dtype, rules, kind) in enumerate(rows):
        row_y = table_top - row_h * (idx + 2)
        if idx % 2:
            c.setFillColor(PALE_BLUE)
            c.rect(x, row_y, w, row_h, fill=1, stroke=0)
        c.setStrokeColor(GRID)
        c.setLineWidth(0.35)
        c.line(x, row_y, x + w, row_y)
        field_color = GREEN if kind == "pk" else BLUE if kind == "fk" else INK
        field_font = "SchemaSansBold" if kind in ("pk", "fk") else "SchemaSans"
        fitted_text(c, col_x[0] + 7, row_y + 6, field,
                    col_x[1] - col_x[0] - 12, 7.45, 5.6, field_color, field_font)
        fitted_text(c, col_x[1] + 5, row_y + 6, dtype,
                    col_x[2] - col_x[1] - 10, 7.1, 5.2, INK)
        fitted_text(c, col_x[2] + 5, row_y + 6, rules,
                    col_x[3] - col_x[2] - 11, 6.9, 5.1, MUTED)

    c.setStrokeColor(GRID)
    c.line(x, y + footer_h, x + w, y + footer_h)
    for idx, line in enumerate(constraint_lines):
        fitted_text(c, x + 8, y + footer_h - 13 * (idx + 1) + 3,
                    line, w - 16, 6.8, 5.4, MUTED)
    return {"x": x, "y": y, "w": w, "h": h, "left": (x, y + h / 2), "right": (x + w, y + h / 2)}


def arrowhead(c, x, y, direction="right", color=BLUE):
    c.setFillColor(color)
    c.setStrokeColor(color)
    if direction == "right":
        points = [(x, y), (x - 7, y + 4), (x - 7, y - 4)]
    elif direction == "left":
        points = [(x, y), (x + 7, y + 4), (x + 7, y - 4)]
    elif direction == "up":
        points = [(x, y), (x - 4, y - 7), (x + 4, y - 7)]
    else:
        points = [(x, y), (x - 4, y + 7), (x + 4, y + 7)]
    p = c.beginPath()
    p.moveTo(*points[0])
    p.lineTo(*points[1])
    p.lineTo(*points[2])
    p.close()
    c.drawPath(p, fill=1, stroke=0)


def relationship(c, x1, y1, x2, y2, label, via_y=None):
    c.setStrokeColor(BLUE)
    c.setLineWidth(1.6)
    if via_y is None:
        c.line(x1, y1, x2, y2)
    else:
        mid_x = (x1 + x2) / 2
        c.line(x1, y1, mid_x, y1)
        c.line(mid_x, y1, mid_x, via_y)
        c.line(mid_x, via_y, x2, y2)
    arrowhead(c, x2, y2, "right")
    label_y = (y1 + y2) / 2 + 7
    text(c, x1 + 5, label_y, "1", 6.8, BLUE, "SchemaSansBold")
    text(c, x2 - 4, label_y, "0..*", 6.8, BLUE, "SchemaSansBold", "right")


def draw_enum_panel(c, x, y, w, h):
    rounded_box(c, x, y, w, h, radius=9, fill=SOFT, stroke=GRID, width=1)
    text(c, x + 12, y + h - 23, "ENUM AND CHECK CONSTRAINT VALUES", 9.6, NAVY, "SchemaSansBold")
    c.setStrokeColor(GRID)
    c.line(x + 12, y + h - 31, x + w - 12, y + h - 31)

    text(c, x + 12, y + h - 49, "[1] outputcategories", 8.2, BLUE, "SchemaSansBold")
    text(c, x + 130, y + h - 49, "SPT = Support ticket   |   BUG = Bug", 7.3, INK)
    text(c, x + 130, y + h - 63, "FEAT = Feature Request   |   BILL = Billing", 7.3, INK)
    text(c, x + 12, y + h - 84, "[2] eval_result_status_enum", 8.2, BLUE, "SchemaSansBold")
    text(c, x + 170, y + h - 84, "COMPLETED  |  INVALID_OUTPUT  |  MODEL_ERROR  |  TIMEOUT", 7.2, INK)

    text(c, x + 12, y + h - 107, "[3] prompt_family_enum", 8.2, BLUE, "SchemaSansBold")
    values = [
        "SUPPORT_TICKET_TRIAGE", "SUPPORT_REPLY_GENERATION",
        "TICKET_SUMMARIZATION", "TICKET_PRIORITY_CLASSIFICATION",
        "TICKET_ROUTING", "SENTIMENT_ANALYSIS",
        "CUSTOMER_INTENT_CLASSIFICATION", "TICKET_ENTITY_EXTRACTION",
        "DUPLICATE_TICKET_DETECTION", "ESCALATION_DETECTION",
        "URGENCY_DETECTION", "LANGUAGE_DETECTION",
        "RESPONSE_QUALITY_EVALUATION", "RESPONSE_TONE_EVALUATION",
        "KNOWLEDGE_BASE_SEARCH_QUERY",
    ]
    col_w = (w - 30) / 2
    for i, value in enumerate(values):
        col = i % 2
        row = i // 2
        text(c, x + 16 + col * col_w, y + h - 124 - row * 14, "• " + value, 6.85, INK)


def draw_legend(c, x, y):
    items = [
        ("PK", GREEN, "primary key"),
        ("FK", BLUE, "foreign key"),
        ("NN", INK, "NOT NULL"),
        ("UQ", GOLD, "unique"),
        ("ORM", RED, "application-side default only"),
    ]
    cursor = x
    for code, color, meaning in items:
        text(c, cursor, y, code, 7.3, color, "SchemaSansBold")
        text(c, cursor + 20, y, meaning, 7.1, MUTED)
        cursor += 105 if code != "ORM" else 178


def build():
    setup_fonts()
    c = canvas.Canvas(str(OUT), pagesize=(PAGE_W, PAGE_H))
    c.setTitle("LLM Prompt Eval Registry Complete Schema")
    c.setAuthor("OpenAI Codex")
    c.setSubject("Complete migrated database schema through Alembic revision fdd324cb4b25")

    # Background and title band
    c.setFillColor(HexColor("#F8FAFC"))
    c.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)
    c.setFillColor(NAVY)
    c.rect(0, PAGE_H - 78, PAGE_W, 78, fill=1, stroke=0)
    text(c, 34, PAGE_H - 36, "LLM Prompt Eval Registry Complete Schema", 22, WHITE, "SchemaSansBold")
    text(c, 34, PAGE_H - 58, "Current migrated PostgreSQL structure through Alembic head fdd324cb4b25", 9.5, HexColor("#D9E7F2"))
    text(c, PAGE_W - 34, PAGE_H - 40, "ENTITY RELATIONSHIP DIAGRAM", 9, HexColor("#D9E7F2"), "SchemaSansBold", "right")

    draw_legend(c, 38, PAGE_H - 99)

    family_rows = [
        ("id", "INTEGER", "PK; NN", "pk"),
        ("name", "VARCHAR [3]", "NN; UQ; CHECK", ""),
        ("created_at", "TIMESTAMPTZ", "NN; no DB default", ""),
        ("updated_at", "TIMESTAMPTZ", "NN; no DB default", ""),
    ]
    version_rows = [
        ("id", "INTEGER", "PK; NN", "pk"),
        ("text", "TEXT", "NN", ""),
        ("version", "VARCHAR", "NN; composite UQ", ""),
        ("is_active", "BOOLEAN", "NULL; ORM=false", ""),
        ("created_at", "TIMESTAMPTZ", "NN; no DB default", ""),
        ("updated_at", "TIMESTAMPTZ", "NN; no DB default", ""),
        ("prompt_family_id", "INTEGER", "FK; NN", "fk"),
    ]
    run_rows = [
        ("id", "INTEGER", "PK; NN", "pk"),
        ("p95_latency_ms", "FLOAT", "NN; ORM=0.0", ""),
        ("accuracy", "FLOAT", "NN; ORM=0.0", ""),
        ("average_cost", "FLOAT", "NN; ORM=0.0", ""),
        ("model_used", "VARCHAR", "NN", ""),
        ("prompt_version_id", "INTEGER", "FK; NN", "fk"),
        ("created_at", "TIMESTAMPTZ", "NN; no DB default", ""),
        ("updated_at", "TIMESTAMPTZ", "NN; no DB default", ""),
    ]
    golden_rows = [
        ("id", "INTEGER", "PK; NN", "pk"),
        ("input", "VARCHAR", "NN", ""),
        ("expected_output", "VARCHAR [1]", "NN; CHECK", ""),
        ("is_active", "BOOLEAN", "NN", ""),
        ("created_at", "TIMESTAMPTZ", "NN; no DB default", ""),
        ("updated_at", "TIMESTAMPTZ", "NN; no DB default", ""),
    ]
    result_rows = [
        ("id", "INTEGER", "PK; NN", "pk"),
        ("input", "VARCHAR", "NN", ""),
        ("predicted_category", "VARCHAR [1]", "NULL; CHECK", ""),
        ("raw_output", "TEXT", "NULL", ""),
        ("input_tokens", "INTEGER", "NN; ORM=0", ""),
        ("output_tokens", "INTEGER", "NN; ORM=0", ""),
        ("total_tokens", "INTEGER", "NN; ORM=0", ""),
        ("passed", "BOOLEAN", "NN", ""),
        ("latency_ms", "INTEGER", "NULL; ORM=0", ""),
        ("cost", "FLOAT", "NN; ORM=0.0", ""),
        ("error_message", "TEXT", "NULL", ""),
        ("status", "VARCHAR [2]", "NN; CHECK", ""),
        ("created_at", "TIMESTAMPTZ", "NN; no DB default", ""),
        ("updated_at", "TIMESTAMPTZ", "NN; no DB default", ""),
        ("golden_example_id", "INTEGER", "FK; NN", "fk"),
        ("eval_run_id", "INTEGER", "FK; NN", "fk"),
    ]

    family = table_box(c, 34, 488, 200, "prompt_families", family_rows,
                       ["UQ: uq_prompt_families_name (name)"], row_h=20, col_ratios=(0.39, 0.28, 0.33))
    version = table_box(c, 276, 420, 228, "prompt_versions", version_rows,
                        ["FK: prompt_family_id → prompt_families.id",
                         "UQ: uq_prompt_versions_family_version"], row_h=20, col_ratios=(0.42, 0.24, 0.34))
    run = table_box(c, 546, 398, 224, "eval_runs", run_rows,
                    ["FK: prompt_version_id → prompt_versions.id"], row_h=20, col_ratios=(0.43, 0.23, 0.34))
    result = table_box(c, 814, 262, 342, "eval_results", result_rows,
                       ["FK: eval_run_id → eval_runs.id",
                        "FK: golden_example_id → golden_examples.id"], row_h=20, col_ratios=(0.42, 0.24, 0.34))
    golden = table_box(c, 532, 106, 264, "golden_examples", golden_rows,
                       ["Referenced by eval_results.golden_example_id"], row_h=20, col_ratios=(0.43, 0.25, 0.32))

    relationship(c, family["x"] + family["w"], family["y"] + family["h"] * 0.55,
                 version["x"], version["y"] + version["h"] * 0.55, "1   →   0..*")
    relationship(c, version["x"] + version["w"], version["y"] + version["h"] * 0.55,
                 run["x"], run["y"] + run["h"] * 0.55, "1   →   0..*")
    relationship(c, run["x"] + run["w"], run["y"] + run["h"] * 0.62,
                 result["x"], result["y"] + result["h"] * 0.62, "1   →   0..*")

    # Golden example relationship: route around the lower edge of eval_results.
    c.setStrokeColor(BLUE)
    c.setLineWidth(1.6)
    gx = golden["x"] + golden["w"]
    gy = golden["y"] + golden["h"] * 0.45
    rx = result["x"]
    ry = result["y"] + 42
    bend_x = (gx + rx) / 2
    c.line(gx, gy, bend_x, gy)
    c.line(bend_x, gy, bend_x, ry)
    c.line(bend_x, ry, rx, ry)
    arrowhead(c, rx, ry, "right")
    text(c, gx + 5, gy + 7, "1", 6.8, BLUE, "SchemaSansBold")
    text(c, rx - 4, ry + 7, "0..*", 6.8, BLUE, "SchemaSansBold", "right")

    draw_enum_panel(c, 34, 82, 462, 286)

    # Notes and footer.
    text(c, 34, 56, "Relationship rule", 7.2, NAVY, "SchemaSansBold")
    text(c, 113, 56, "Every child foreign key is required (NN); no ON DELETE cascade is declared.", 7.2, MUTED)
    text(c, 34, 40, "Default rule", 7.2, NAVY, "SchemaSansBold")
    text(c, 91, 40, "ORM defaults apply through SQLAlchemy; the migrated database columns shown as 'no DB default' require supplied values.", 7.2, MUTED)
    text(c, 34, 22, "Source: fastapi_eval_prompt_registry/models.py and Alembic revisions through fdd324cb4b25", 7, MUTED)
    text(c, PAGE_W - 34, 22, "Generated 2026-09-06", 7, MUTED, align="right")

    c.showPage()
    c.save()
    print(OUT)


if __name__ == "__main__":
    build()
