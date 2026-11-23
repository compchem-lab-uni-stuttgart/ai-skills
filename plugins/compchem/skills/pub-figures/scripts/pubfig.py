"""Publication-figure helpers for matplotlib.

Usage:
    import pubfig
    pubfig.setup(journal="aip")
    fig, ax = pubfig.subplots(width="single", aspect=0.8)
    ...
    pubfig.save(fig, "figs/parity")            # -> figs/parity.pdf

Column widths are typical values; verify against the target journal's
current author guidelines.
"""
from __future__ import annotations

import os
import warnings
from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
from cycler import cycler

# Inches. Typical values, NOT verified against current guidelines.
WIDTHS = {
    "acs": {"single": 3.25, "double": 7.0},
    "aip": {"single": 3.37, "double": 6.69},
    "aps": {"single": 3.37, "double": 6.69},
    "rsc": {"single": 3.27, "double": 6.69},
    "elsevier": {"single": 3.54, "onehalf": 5.51, "double": 7.48},
    "generic": {"single": 3.4, "double": 7.0},
}

# Okabe–Ito colorblind-safe palette (black omitted from the cycle start).
OKABE_ITO = ["#0072B2", "#D55E00", "#009E73", "#CC79A7",
             "#E69F00", "#56B4E9", "#F0E442", "#000000"]

_journal = "generic"


def setup(journal: str = "generic", fontsize: float = 8, serif: bool = False,
          usetex: bool = False) -> None:
    """Set rcParams for publication output."""
    global _journal
    if journal not in WIDTHS:
        raise ValueError(f"unknown journal {journal!r}; choose from {list(WIDTHS)}")
    _journal = journal
    family = "serif" if serif else "sans-serif"
    mpl.rcParams.update({
        # fonts: embed TrueType, not Type 3
        "pdf.fonttype": 42,
        "ps.fonttype": 42,
        "svg.fonttype": "none",
        "font.family": family,
        "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans"],
        "font.serif": ["Times New Roman", "Times", "DejaVu Serif"],
        "mathtext.fontset": "cm" if serif else "dejavusans",
        "text.usetex": usetex,
        # sizes at final print scale
        "font.size": fontsize,
        "axes.labelsize": fontsize,
        "axes.titlesize": fontsize,
        "xtick.labelsize": fontsize - 1,
        "ytick.labelsize": fontsize - 1,
        "legend.fontsize": fontsize - 1,
        "legend.frameon": False,
        # lines
        "lines.linewidth": 1.0,
        "lines.markersize": 3,
        "axes.linewidth": 0.7,
        "xtick.major.width": 0.7,
        "ytick.major.width": 0.7,
        "xtick.minor.width": 0.5,
        "ytick.minor.width": 0.5,
        "xtick.direction": "in",
        "ytick.direction": "in",
        "xtick.top": True,
        "ytick.right": True,
        # color
        "axes.prop_cycle": cycler(color=OKABE_ITO),
        "image.cmap": "viridis",
        # output
        "savefig.dpi": 600,
        "figure.dpi": 150,
    })


def figsize(width: str | float = "single", aspect: float = 0.75,
            journal: str | None = None) -> tuple[float, float]:
    """Return (w, h) in inches. width: preset key or inches; aspect = h/w."""
    j = journal or _journal
    w = WIDTHS[j][width] if isinstance(width, str) else float(width)
    return (w, w * aspect)


def subplots(nrows: int = 1, ncols: int = 1, width: str | float = "single",
             aspect: float = 0.75, journal: str | None = None, **kw):
    """plt.subplots at final print size with constrained layout."""
    kw.setdefault("layout", "constrained")
    return plt.subplots(nrows, ncols,
                        figsize=figsize(width, aspect, journal), **kw)


def check_sizes(fig, min_pt: float = 7.0, min_lw: float = 0.5) -> list[str]:
    """Warn about visible text < min_pt and lines thinner than min_lw (points).

    Sizes are at the figure's saved size; they are only the printed sizes if
    the figure is included in LaTeX without rescaling. Mathtext sub/superscripts
    render at ~70% of the reported font size and are not checked separately.
    """
    from matplotlib.text import Text
    from matplotlib.lines import Line2D
    fig.canvas.draw()  # populate tick labels
    issues = []
    for t in fig.findobj(Text):
        if t.get_visible() and t.get_text().strip() and t.get_fontsize() < min_pt - 1e-6:
            issues.append(f"text {t.get_text()[:30]!r}: {t.get_fontsize():.1f} pt < {min_pt} pt")
    for ln in fig.findobj(Line2D):
        if (ln.get_visible() and ln.get_linestyle() not in ("None", "", " ")
                and len(ln.get_xdata()) > 1 and ln.get_linewidth() < min_lw):
            issues.append(f"line {ln.get_label()!r}: {ln.get_linewidth():.2f} pt < {min_lw} pt")
    w, _ = fig.get_size_inches()
    if w > 7.5:
        issues.append(f"figure width {w:.2f} in exceeds any common page width; "
                      "it will be shrunk on inclusion and all sizes reduced")
    # deduplicate (shared tick labels repeat)
    issues = sorted(set(issues))
    for msg in issues:
        warnings.warn(msg)
    return issues


def save(fig, path: str | os.PathLike, formats=("pdf",), dpi: int = 600,
         check_fonts: bool = True, max_mb: float = 2.0,
         min_pt: float = 7.0) -> list[Path]:
    """Save fig in each format; warn on small text/lines, Type 3 fonts and
    oversized PDFs. Set min_pt=None to skip the size check.

    path: output stem; any extension is replaced.
    """
    if min_pt is not None:
        check_sizes(fig, min_pt=min_pt)
    stem = Path(path).with_suffix("")
    stem.parent.mkdir(parents=True, exist_ok=True)
    out = []
    for fmt in formats:
        p = stem.with_suffix("." + fmt)
        kw = {}
        if fmt in ("tiff", "tif"):
            kw["pil_kwargs"] = {"compression": "tiff_lzw"}
        if fmt == "jpg" or fmt == "jpeg":
            warnings.warn("JPEG is lossy and degrades line art; use PDF/PNG/TIFF.")
        fig.savefig(p, dpi=dpi, **kw)
        out.append(p)
        if fmt == "pdf":
            size_mb = p.stat().st_size / 1e6
            if size_mb > max_mb:
                warnings.warn(f"{p} is {size_mb:.1f} MB; rasterize dense artists "
                              "(rasterized=True on scatter/contourf/pcolormesh).")
            if check_fonts:
                from check_pdf_fonts import type3_fonts
                bad = type3_fonts(p)
                if bad:
                    warnings.warn(f"{p} contains Type 3 fonts: {sorted(bad)}")
    w, h = fig.get_size_inches()
    print(f"saved {[str(x) for x in out]}  ({w:.2f} x {h:.2f} in)")
    return out
