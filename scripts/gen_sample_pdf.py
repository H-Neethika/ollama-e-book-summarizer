#!/usr/bin/env python
from __future__ import annotations

import sys
from pathlib import Path

def main(out_path: str) -> None:
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.pdfgen import canvas
    except ImportError:
        print("reportlab not installed. Install with: pip install reportlab", file=sys.stderr)
        sys.exit(1)

    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    c = canvas.Canvas(str(out), pagesize=letter)
    width, height = letter
    c.setFont("Helvetica", 14)
    c.drawString(72, height - 72, "Sample PDF for Pipeline Integration Test")
    textobject = c.beginText(72, height - 100)
    textobject.setFont("Helvetica", 10)
    textobject.textLines(
        [
            "This is a minimal 1-page PDF generated at runtime.",
            "It exists only to exercise the extract→chunk→summarize pipeline.",
            "Feel free to replace with a real eBook in production.",
        ]
    )
    c.drawText(textobject)
    c.showPage()
    c.save()
    print(f"Wrote: {out}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: gen_sample_pdf.py <output_path>", file=sys.stderr)
        sys.exit(2)
    main(sys.argv[1])

