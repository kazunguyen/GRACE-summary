#!/usr/bin/env python3
"""Build and verify the complete OSF Preregistration Bundle for GRACE replication.

This script:
1. Compiles preregistration.md into a PDF using ReportLab and Matplotlib mathtext:
   Runs-management/osf_registration_draft_20261102/output/pdf/GRACE_OSF_PREREGISTRATION_20261102.pdf
2. Computes and records SHA-256 digests for all protocol, data manifest, threshold lock, and code assets into:
   Runs-management/osf_registration_draft_20261102/attachment_sha256.json
3. Bundles the complete OSF pre-registration pack into a stand-alone reproducible archive:
   Runs-management/osf_registration_draft_20261102/GRACE_OSF_PREREGISTRATION_20261102.zip
4. Verifies the generated ZIP bundle for stand-alone completeness and hash reproducibility.
"""
import sys
if hasattr(sys.stdout, 'reconfigure'): sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'): sys.stderr.reconfigure(encoding='utf-8')

import hashlib
import html
import json
import os
import re
import tempfile
import zipfile
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
OSF_DIR = REPO_ROOT / "Runs-management" / "osf_registration_draft_20261102"
PDF_DIR = OSF_DIR / "output" / "pdf"
PDF_FILE = PDF_DIR / "GRACE_OSF_PREREGISTRATION_20261102.pdf"
ZIP_FILE = OSF_DIR / "GRACE_OSF_PREREGISTRATION_20261102.zip"
HASHES_FILE = OSF_DIR / "attachment_sha256.json"
PREREG_MD = REPO_ROOT / "preregistration.md"


def prereg_version() -> str:
    """Use the document's own version as the single source for PDF and bundle."""
    match = re.search(r"^- \*\*Version:\*\*\s*`([^`]+)`", PREREG_MD.read_text(encoding="utf-8"), re.MULTILINE)
    if not match:
        raise ValueError(f"Missing Version metadata in {PREREG_MD}")
    return match.group(1)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def markdown_to_pdf(md_path: Path, pdf_path: Path) -> None:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether, HRFlowable
    )
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.pdfgen import canvas
    from matplotlib.mathtext import math_to_image
    from matplotlib.font_manager import FontProperties
    from PIL import Image as PILImage

    version = prereg_version()

    # Register Unicode Arial fonts
    arial_path = "C:/Windows/Fonts/arial.ttf"
    arial_bold_path = "C:/Windows/Fonts/arialbd.ttf"
    arial_italic_path = "C:/Windows/Fonts/ariali.ttf"
    arial_bolditalic_path = "C:/Windows/Fonts/arialbi.ttf"

    if os.path.exists(arial_path):
        pdfmetrics.registerFont(TTFont("Arial", arial_path))
        pdfmetrics.registerFont(TTFont("Arial-Bold", arial_bold_path))
        pdfmetrics.registerFont(TTFont("Arial-Italic", arial_italic_path))
        pdfmetrics.registerFont(TTFont("Arial-BoldItalic", arial_bolditalic_path))
        body_font = "Arial"
        bold_font = "Arial-Bold"
        italic_font = "Arial-Italic"
    else:
        body_font = "Helvetica"
        bold_font = "Helvetica-Bold"
        italic_font = "Helvetica-Oblique"

    pdf_path.parent.mkdir(parents=True, exist_ok=True)

    class NumberedCanvas(canvas.Canvas):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self._saved_page_states = []

        def showPage(self):
            self._saved_page_states.append(dict(self.__dict__))
            self._startPage()

        def save(self):
            num_pages = len(self._saved_page_states)
            for state in self._saved_page_states:
                self.__dict__.update(state)
                self.draw_page_number(num_pages)
                super().showPage()
            super().save()

        def draw_page_number(self, page_count):
            self.saveState()
            self.setFont(body_font, 8)
            self.setFillColor(colors.HexColor("#555555"))
            
            # Header (pages > 1)
            if self._pageNumber > 1:
                self.drawString(54, 800, f"GRACE Preregistration {version} (Prepared for OSF)")
                self.setStrokeColor(colors.HexColor("#CCCCCC"))
                self.setLineWidth(0.5)
                self.line(54, 792, 541, 792)

            # Footer
            page_text = f"Page {self._pageNumber} of {page_count}"
            self.drawRightString(541, 35, page_text)
            self.drawString(54, 35, "Prepared for OSF Registry Submission • Not yet submitted")
            self.setStrokeColor(colors.HexColor("#CCCCCC"))
            self.setLineWidth(0.5)
            self.line(54, 45, 541, 45)
            self.restoreState()

    doc = SimpleDocTemplate(
        str(pdf_path),
        pagesize=A4,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54,
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "DocTitle",
        fontName=bold_font,
        fontSize=18,
        leading=22,
        textColor=colors.HexColor("#1A2B4C"),
        spaceAfter=12,
    )
    h1_style = ParagraphStyle(
        "Heading1_Custom",
        fontName=bold_font,
        fontSize=13,
        leading=16,
        textColor=colors.HexColor("#1E3A8A"),
        spaceBefore=14,
        spaceAfter=6,
        keepWithNext=True,
    )
    h2_style = ParagraphStyle(
        "Heading2_Custom",
        fontName=bold_font,
        fontSize=11,
        leading=14,
        textColor=colors.HexColor("#2563EB"),
        spaceBefore=10,
        spaceAfter=4,
        keepWithNext=True,
    )
    body_style = ParagraphStyle(
        "Body_Custom",
        fontName=body_font,
        fontSize=9,
        leading=13,
        textColor=colors.HexColor("#1F2937"),
        spaceAfter=6,
    )
    bullet_style = ParagraphStyle(
        "Bullet_Custom",
        fontName=body_font,
        fontSize=9,
        leading=13,
        textColor=colors.HexColor("#1F2937"),
        leftIndent=15,
        spaceAfter=3,
    )
    table_cell = ParagraphStyle(
        "TableCell",
        fontName=body_font,
        fontSize=7.5,
        leading=10,
        textColor=colors.HexColor("#111827"),
    )
    table_header = ParagraphStyle(
        "TableHeader",
        fontName=bold_font,
        fontSize=8,
        leading=11,
        textColor=colors.white,
    )
    math_block_style = ParagraphStyle(
        "MathBlock",
        parent=body_style,
        alignment=1,
        spaceBefore=5,
        spaceAfter=9,
    )

    math_dir = tempfile.TemporaryDirectory(prefix="grace-osf-math-")
    math_cache: dict[tuple[str, float, float], str] = {}
    inline_token = re.compile(
        r"\$\$.*?\$\$|\$[^$]+\$|\[[^\]]+\]\(https?://[^)]+\)|`[^`]+`|\*\*.*?\*\*|\*[^*]+\*",
        re.DOTALL,
    )

    def render_math(expr: str, font_size: float, max_width: float) -> str:
        """Render LaTeX-style math as a sharp PNG for ReportLab paragraphs."""
        expr = re.sub(r"\\operatorname\{([^{}]+)\}", r"\\mathrm{\1}", expr.strip())
        expr = re.sub(r"\\text\{([^{}]+)\}", r"\\mathrm{\1}", expr)
        expr = re.sub(r"\\ge(?![A-Za-z])", r"\\geq", expr)
        expr = re.sub(r"\\le(?![A-Za-z])", r"\\leq", expr)
        key = (expr, font_size, max_width)
        if key in math_cache:
            return math_cache[key]
        digest = hashlib.sha256(repr(key).encode("utf-8")).hexdigest()[:20]
        path = Path(math_dir.name) / f"{digest}.png"
        dpi = 240
        math_to_image(f"${expr}$", path, prop=FontProperties(size=font_size), dpi=dpi, format="png")
        with PILImage.open(path) as im:
            width, height = (dimension * 72.0 / dpi for dimension in im.size)
        scale = min(1.0, max_width / width)
        width *= scale
        height *= scale
        markup = (f"<img src='{html.escape(path.as_posix(), quote=True)}' "
                  f"width='{width:.2f}' height='{height:.2f}' valign='middle'/>")
        math_cache[key] = markup
        return markup

    def render_inline(value: str, font_size: float = 9, max_width: float = 470) -> str:
        """Convert supported Markdown inline tokens to safe ReportLab markup."""
        parts = []
        cursor = 0
        for match in inline_token.finditer(value):
            parts.append(html.escape(value[cursor:match.start()]))
            token = match.group(0)
            if token.startswith("$$"):
                parts.append(render_math(token[2:-2], font_size + 1, max_width))
            elif token.startswith("$"):
                parts.append(render_math(token[1:-1], font_size, max_width))
            elif token.startswith("["):
                label, url = re.fullmatch(r"\[([^\]]+)\]\((https?://[^)]+)\)", token).groups()
                parts.append(f"<link href='{html.escape(url, quote=True)}'>{render_inline(label, font_size, max_width)}</link>")
            elif token.startswith("`"):
                parts.append(f"<font face='Courier'>{html.escape(token[1:-1])}</font>")
            elif token.startswith("**"):
                parts.append(f"<b>{render_inline(token[2:-2], font_size, max_width)}</b>")
            else:
                parts.append(f"<i>{render_inline(token[1:-1], font_size, max_width)}</i>")
            cursor = match.end()
        parts.append(html.escape(value[cursor:]))
        return "".join(parts)

    story = []
    lines = md_path.read_text(encoding="utf-8").splitlines()

    i = 0
    in_table = False
    table_rows: list[list[str]] = []

    def flush_table():
        nonlocal in_table, table_rows
        if not table_rows:
            in_table = False
            return
        # Parse table cells, using visible link labels instead of printing URLs.
        data = []
        is_hdr = True
        first_cells = [c.strip() for c in table_rows[0].split("|")[1:-1]]
        col_width = 487.0 / len(first_cells)
        for row in table_rows:
            cells = [c.strip() for c in row.split("|")[1:-1]]
            if not cells or all(re.match(r"^:?-+:?$", c) for c in cells):
                continue
            row_data = []
            for cell in cells:
                st = table_header if is_hdr else table_cell
                clean = render_inline(cell, font_size=8 if is_hdr else 7.5, max_width=col_width - 10)
                row_data.append(Paragraph(clean, st))
            data.append(row_data)
            is_hdr = False

        if data:
            num_cols = max(len(r) for r in data)
            avail_width = 487.0
            col_width = avail_width / num_cols
            t = Table(data, colWidths=[col_width] * num_cols, repeatRows=1)
            t.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1E3A8A")),
                ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E5E7EB")),
                ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#9CA3AF")),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.HexColor("#F9FAFB"), colors.white]),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]))
            story.append(Spacer(1, 4))
            story.append(t)
            story.append(Spacer(1, 6))
        table_rows = []
        in_table = False

    while i < len(lines):
        line = lines[i].rstrip()
        i += 1

        if line.startswith("|") and line.endswith("|"):
            in_table = True
            table_rows.append(line)
            continue
        elif in_table:
            flush_table()

        if not line.strip():
            continue

        if line.startswith("# "):
            story.append(Paragraph(render_inline(line[2:], font_size=18), title_style))
            story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#1E3A8A"), spaceAfter=10))
        elif line.startswith("## "):
            story.append(Paragraph(render_inline(line[3:], font_size=13), h1_style))
            story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#DBEAFE"), spaceAfter=6))
        elif line.startswith("### "):
            story.append(Paragraph(render_inline(line[4:], font_size=11), h2_style))
        elif line.startswith("- ") or line.startswith("* "):
            content = render_inline(line[2:])
            story.append(Paragraph(f"• {content}", bullet_style))
        elif re.match(r"^\d+\.\s", line):
            m = re.match(r"^(\d+\.)\s(.*)", line)
            content = render_inline(m.group(2))
            story.append(Paragraph(f"<b>{m.group(1)}</b> {content}", bullet_style))
        elif line.strip().startswith("$$") and line.strip().endswith("$$"):
            story.append(Paragraph(render_inline(line.strip(), font_size=11), math_block_style))
        elif line.strip() == "---":
            story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#D1D5DB"), spaceBefore=6, spaceAfter=6))
        else:
            content = render_inline(line)
            story.append(Paragraph(content, body_style))

    if in_table:
        flush_table()

    doc.build(story, canvasmaker=NumberedCanvas)
    math_dir.cleanup()
    print(f"Generated PDF successfully: {pdf_path} ({pdf_path.stat().st_size:,} bytes)")


def build_inventory_and_zip():
    OSF_DIR.mkdir(parents=True, exist_ok=True)
    PDF_DIR.mkdir(parents=True, exist_ok=True)

    # 1. Compile the current PDF. Historical DRAFT aliases are not recreated.
    markdown_to_pdf(PREREG_MD, PDF_FILE)

    # 2. Gather assets to register
    assets = [
        # Preregistration documents
        ("preregistration.md", PREREG_MD),
        ("preregistration_en.md", REPO_ROOT / "preregistration_en.md"),
        ("preregistration_vi.md", REPO_ROOT / "preregistration_vi.md"),
        ("CHANGES_AFTER_PREREG.md", REPO_ROOT / "CHANGES_AFTER_PREREG.md"),
        ("output/pdf/GRACE_OSF_PREREGISTRATION_20261102.pdf", PDF_FILE),
        # Protocol configs
        ("configs/protocol.yaml", REPO_ROOT / "configs" / "protocol.yaml"),
        ("configs/protocol_en.yaml", REPO_ROOT / "configs" / "protocol_en.yaml"),
        ("configs/arms.yaml", REPO_ROOT / "configs" / "arms.yaml"),
        ("configs/thresholds.json", REPO_ROOT / "configs" / "thresholds.json"),
        ("configs/thresholds_flat.json", REPO_ROOT / "configs" / "thresholds_flat.json"),
        ("Runs-management/thresholds.json", REPO_ROOT / "Runs-management" / "thresholds.json"),
        ("01_Author_Baseline_Unified/diagnostic_kit/configs/protocol.yaml", REPO_ROOT / "01_Author_Baseline_Unified" / "diagnostic_kit" / "configs" / "protocol.yaml"),
        ("01_Author_Baseline_Unified/diagnostic_kit/configs/arms.yaml", REPO_ROOT / "01_Author_Baseline_Unified" / "diagnostic_kit" / "configs" / "arms.yaml"),
        ("01_Author_Baseline_Unified/diagnostic_kit/configs/thresholds.json", REPO_ROOT / "01_Author_Baseline_Unified" / "diagnostic_kit" / "configs" / "thresholds.json"),
        ("Runs-management/threshold_lock_status.json", REPO_ROOT / "Runs-management" / "threshold_lock_status.json"),
        # Analysis locks
        ("Runs-management/analysis_lock_20261101/CHANGES_AFTER_ANALYSIS_LOCK.md", REPO_ROOT / "Runs-management" / "analysis_lock_20261101" / "CHANGES_AFTER_ANALYSIS_LOCK.md"),
        ("Runs-management/analysis_lock_20261101/preregistration.md", REPO_ROOT / "Runs-management" / "analysis_lock_20261101" / "preregistration.md"),
        ("Runs-management/analysis_lock_20261101/protocol.analysis.json", REPO_ROOT / "Runs-management" / "analysis_lock_20261101" / "protocol.analysis.json"),
        ("Runs-management/analysis_lock_20261101/protocol.template.snapshot.yaml", REPO_ROOT / "Runs-management" / "analysis_lock_20261101" / "protocol.template.snapshot.yaml"),
        ("Runs-management/analysis_lock_20261101/SHA256SUMS.json", REPO_ROOT / "Runs-management" / "analysis_lock_20261101" / "SHA256SUMS.json"),
        ("Runs-management/analysis_lock_20261101/thresholds.initial.json", REPO_ROOT / "Runs-management" / "analysis_lock_20261101" / "thresholds.initial.json"),
        ("Runs-management/analysis_lock_20261101/threshold_rules.json", REPO_ROOT / "Runs-management" / "analysis_lock_20261101" / "threshold_rules.json"),
        # Freeze manifest
        ("01_Author_Baseline_Unified/output/research_freeze_20261101/freeze_manifest.json", REPO_ROOT / "01_Author_Baseline_Unified" / "output" / "research_freeze_20261101" / "freeze_manifest.json"),
        # Step 0 Diagnostic reports (5,000 bootstrap reps)
        ("Runs-management/step0_diagnostic/devign/diagnostic_report_devign.json", REPO_ROOT / "Runs-management" / "step0_diagnostic" / "devign" / "diagnostic_report_devign.json"),
        ("Runs-management/step0_diagnostic/reveal/diagnostic_report_reveal.json", REPO_ROOT / "Runs-management" / "step0_diagnostic" / "reveal" / "diagnostic_report_reveal.json"),
        # 15-arm validation dry-run summary
        ("Runs-management/dry_run_validation_20261102/summary.json", REPO_ROOT / "Runs-management" / "dry_run_validation_20261102" / "summary.json"),
        # Core source code
        ("01_Author_Baseline_Unified/diagnostic_kit/src/grace_diag/probes.py", REPO_ROOT / "01_Author_Baseline_Unified" / "diagnostic_kit" / "src" / "grace_diag" / "probes.py"),
        ("01_Author_Baseline_Unified/diagnostic_kit/src/grace_diag/token_budget.py", REPO_ROOT / "01_Author_Baseline_Unified" / "diagnostic_kit" / "src" / "grace_diag" / "token_budget.py"),
        ("01_Author_Baseline_Unified/diagnostic_kit/src/grace_diag/sink_evidence.py", REPO_ROOT / "01_Author_Baseline_Unified" / "diagnostic_kit" / "src" / "grace_diag" / "sink_evidence.py"),
        ("01_Author_Baseline_Unified/diagnostic_kit/src/grace_diag/contrastive_pair_builder.py", REPO_ROOT / "01_Author_Baseline_Unified" / "diagnostic_kit" / "src" / "grace_diag" / "contrastive_pair_builder.py"),
        ("01_Author_Baseline_Unified/diagnostic_kit/src/grace_diag/prompt_audit.py", REPO_ROOT / "01_Author_Baseline_Unified" / "diagnostic_kit" / "src" / "grace_diag" / "prompt_audit.py"),
        ("01_Author_Baseline_Unified/diagnostic_kit/src/grace_diag/evaluate_final.py", REPO_ROOT / "01_Author_Baseline_Unified" / "diagnostic_kit" / "src" / "grace_diag" / "evaluate_final.py"),
        ("01_Author_Baseline_Unified/diagnostic_kit/src/grace_diag/thresholds.py", REPO_ROOT / "01_Author_Baseline_Unified" / "diagnostic_kit" / "src" / "grace_diag" / "thresholds.py"),
        ("01_Author_Baseline_Unified/diagnostic_kit/src/grace_diag/llm_backend.py", REPO_ROOT / "01_Author_Baseline_Unified" / "diagnostic_kit" / "src" / "grace_diag" / "llm_backend.py"),
        ("01_Author_Baseline_Unified/diagnostic_kit/src/grace_diag/stats.py", REPO_ROOT / "01_Author_Baseline_Unified" / "diagnostic_kit" / "src" / "grace_diag" / "stats.py"),
        ("01_Author_Baseline_Unified/diagnostic_kit/src/grace_diag/complementarity.py", REPO_ROOT / "01_Author_Baseline_Unified" / "diagnostic_kit" / "src" / "grace_diag" / "complementarity.py"),
        ("Runs-management/dry_run_full_validation.py", REPO_ROOT / "Runs-management" / "dry_run_full_validation.py"),
        ("Runs-management/finalize_prompt_audit.py", REPO_ROOT / "Runs-management" / "finalize_prompt_audit.py"),
        ("01_Author_Baseline_Unified/diagnostic_kit/CHANGELOG.md", REPO_ROOT / "01_Author_Baseline_Unified" / "diagnostic_kit" / "CHANGELOG.md"),
        ("CHANGELOG.md", REPO_ROOT / "CHANGELOG.md"),
    ]

    files_manifest = []
    for rel_name, path in assets:
        if not path.exists():
            raise FileNotFoundError(f"Missing required asset for OSF preregistration pack: {path}")
        f_size = path.stat().st_size
        f_sha = sha256_file(path)
        files_manifest.append({
            "path": rel_name,
            "bytes": f_size,
            "sha256": f_sha,
        })

    inventory = {
        "prepared_at_utc": datetime.now(timezone.utc).isoformat(),
        "study_id": "grace_diag_replication_v1",
        "version": prereg_version(),
        "status": "OSF_PREREGISTRATION_READY_FOR_REGISTRY_SUBMISSION",
        "target_model": "Qwen/Qwen3-Coder-30B-A3B-Instruct (GGUF Q4_K_M)",
        "model_sha256": "f6050b4da22869aa3fb9d94bb3314e9fc5a027d4741c1f97761c387d6b2b2335",
        "dry_run_15arms_status": {
            "rendered_prompts": 95095,
            "all_15_arms_complete": True,
            "blocked_arms": [],
            "n_label_leak": 0,
            "llm_calls": 0,
        },
        "files_count": len(files_manifest),
        "files": files_manifest,
    }

    with HASHES_FILE.open("w", encoding="utf-8", newline="\n") as output:
        output.write(json.dumps(inventory, ensure_ascii=False, indent=2) + "\n")
    print(f"Recorded SHA-256 for {len(files_manifest)} artifacts in {HASHES_FILE}")

    # 3. Create stand-alone ZIP archive
    with zipfile.ZipFile(ZIP_FILE, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
        for rel_name, path in assets:
            zf.write(path, arcname=rel_name)
        zf.write(HASHES_FILE, arcname="attachment_sha256.json")

    zip_size = ZIP_FILE.stat().st_size
    zip_sha = sha256_file(ZIP_FILE)
    print(f"Created OSF Preregistration Bundle ZIP: {ZIP_FILE} ({zip_size:,} bytes, SHA-256: {zip_sha})")

    # 4. Stand-alone reproducibility test (extract in temp dir)
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)
        with zipfile.ZipFile(ZIP_FILE, "r") as zf:
            zf.extractall(tmp_path)

        # Verify all extracted files match their recorded SHA-256
        for item in files_manifest:
            extracted_f = tmp_path / item["path"]
            assert extracted_f.exists(), f"File {item['path']} missing from ZIP bundle!"
            extracted_sha = sha256_file(extracted_f)
            assert extracted_sha == item["sha256"], f"Hash mismatch for {item['path']} inside ZIP: {extracted_sha} vs {item['sha256']}"

    print("All bundle files successfully extracted and verified against SHA-256 digests.")


if __name__ == "__main__":
    build_inventory_and_zip()
