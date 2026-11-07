"""Render the five Mermaid documents locally; optionally build an ignored/private PDF report."""

import argparse
import os
import re
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--renderer", default=shutil.which("mmdc"))
    parser.add_argument("--puppeteer-config")
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    output = ROOT / ".local-evidence/diagrams"
    output.mkdir(parents=True, exist_ok=True)
    rendered = []
    for path in sorted((ROOT / "diagrams").glob("*.md")):
        source = re.search(r"```mermaid\s*\n(.*?)```", path.read_text(), re.S)
        if source is None:
            raise ValueError(f"Mermaid source missing: {path.name}")
        mmd = output / (path.stem + ".mmd")
        mmd.write_text(source.group(1))
        if args.renderer:
            for suffix in ("svg", "png"):
                command = [args.renderer, "-i", str(mmd), "-o", str(mmd.with_suffix("." + suffix)), "-b", "white"]
                if args.puppeteer_config:
                    command += ["-p", args.puppeteer_config]
                subprocess.run(command, check=True, env=os.environ.copy())
            rendered.append(mmd.with_suffix(".png"))
    if args.report:
        import markdown
        from weasyprint import HTML

        parts = ["<h1>Evidence before adjudication</h1><p>Zulfiqar Ali Ahmed — Workcats case study</p>"]
        for doc in sorted((ROOT / "docs").glob("*.md")):
            parts.append(
                '<section class="chapter">'
                + markdown.markdown(doc.read_text(), extensions=["tables", "fenced_code"])
                + "</section>"
            )
        for image in rendered:
            parts.append(
                '<section class="chapter"><h1>'
                + image.stem.replace("-", " ").title()
                + '</h1><img src="'
                + image.as_uri()
                + '"></section>'
            )
        if not rendered:
            for diagram in sorted((ROOT / "diagrams").glob("*.md")):
                parts.append(
                    '<section class="chapter">'
                    + markdown.markdown(diagram.read_text(), extensions=["fenced_code"])
                    + "</section>"
                )
        style = """@page {size:A4; margin:17mm; @bottom-right {content:counter(page);font-size:8pt;}}
        body{font:10pt/1.4 sans-serif;color:#163047} h1{font-size:22pt} h2{font-size:14pt}
        h1,h2,h3{break-after:avoid}.chapter{break-before:page}table{border-collapse:collapse;width:100%;font-size:8.4pt}
        td,th{border:1px solid #b9c9d3;padding:5px;vertical-align:top}tr{break-inside:avoid}
        th{background:#dcebf1}img{max-width:100%;max-height:235mm;object-fit:contain}
        pre{white-space:pre-wrap;overflow-wrap:anywhere;font-size:8pt}code{font-size:.86em}
        """
        args.report.parent.mkdir(parents=True, exist_ok=True)
        HTML(string="<style>" + style + "</style>" + "".join(parts), base_url=str(ROOT)).write_pdf(args.report)
        print("Private report built:", args.report)
    print("Mermaid sources:", len(list(output.glob("*.mmd"))), "rendered PNGs:", len(rendered))


if __name__ == "__main__":
    main()
