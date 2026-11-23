"""Report fonts embedded in a PDF and flag Type 3 fonts.

Usage: python check_pdf_fonts.py fig1.pdf [fig2.pdf ...]
Exit code 1 if any file contains Type 3 fonts.
Requires pypdf (pip install pypdf).
"""
from __future__ import annotations

import sys
from pathlib import Path


def _walk_fonts(resources, seen, out):
    if resources is None:
        return
    resources = resources.get_object()
    fonts = resources.get("/Font")
    if fonts is not None:
        for _, ref in fonts.get_object().items():
            f = ref.get_object()
            key = id(f)
            if key in seen:
                continue
            seen.add(key)
            out.append((str(f.get("/BaseFont", "?")), str(f.get("/Subtype", "?"))))
    xobjs = resources.get("/XObject")
    if xobjs is not None:
        for _, ref in xobjs.get_object().items():
            x = ref.get_object()
            if x.get("/Subtype") == "/Form":
                _walk_fonts(x.get("/Resources"), seen, out)


def list_fonts(path) -> list[tuple[str, str]]:
    from pypdf import PdfReader
    reader = PdfReader(str(path))
    seen, out = set(), []
    for page in reader.pages:
        _walk_fonts(page.get("/Resources"), seen, out)
    return out


def type3_fonts(path) -> set[str]:
    return {name for name, sub in list_fonts(path) if sub == "/Type3"}


def main(argv):
    if not argv:
        print(__doc__)
        return 2
    status = 0
    for p in argv:
        fonts = list_fonts(Path(p))
        bad = [n for n, s in fonts if s == "/Type3"]
        flag = "FAIL (Type 3)" if bad else "ok"
        print(f"{p}: {flag}")
        for name, sub in fonts:
            print(f"    {sub:10s} {name}")
        status |= bool(bad)
    return status


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
