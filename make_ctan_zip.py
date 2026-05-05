#!/usr/bin/env -S uv run --script
import os
import zipfile

TOPDIR = "quantumcubemodel"
OUT_ZIP = "quantumcubemodel.zip"

# Top-level files (relative to project root)
FILES = [
    "LICENSE.md",
    "README.md",
    "quantumcubemodel.sty",
    "quantumcubemodel-doc.pdf",
    "quantumcubemodel-bib.bib",
]

EXAMPLES_TEX_DIR = "examples"
EXAMPLES_PDF_DIR = "examples/out"


def add_file(zf, path):
    arcname = os.path.join(TOPDIR, path)
    zf.write(path, arcname)


def add_examples_tex(zf):
    for root, dirs, files in os.walk(EXAMPLES_TEX_DIR):
        for name in files:
            if not name.endswith(".tex"):
                continue
            fs_path = os.path.join(root, name)
            rel = os.path.relpath(fs_path, start=".")
            arcname = os.path.join(TOPDIR, rel)
            zf.write(fs_path, arcname)


def add_examples_pdf(zf):
    for root, dirs, files in os.walk(EXAMPLES_PDF_DIR):
        for name in files:
            if not name.endswith(".pdf"):
                continue
            fs_path = os.path.join(root, name)
            rel = os.path.relpath(fs_path, start=".")
            arcname = os.path.join(TOPDIR, rel)
            zf.write(fs_path, arcname)


def main():
    with zipfile.ZipFile(OUT_ZIP, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        # top-level files
        for f in FILES:
            add_file(zf, f)
        # examples/*.tex
        add_examples_tex(zf)
        # examples/out/*.pdf
        add_examples_pdf(zf)


if __name__ == "__main__":
    main()