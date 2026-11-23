---
name: pub-figures
description: Produce publication-quality scientific figures from Python (matplotlib) for journal papers and LaTeX manuscripts — correct export format (vector PDF, hybrid rasterization, TIFF/PNG when required), embedded TrueType fonts, true column-width sizing, and colorblind-safe colormaps. Use this skill whenever the user plots data for a paper, thesis, SI, poster, or preprint, asks which figure format/DPI/size to use, wants to export or fix a matplotlib figure, makes parity plots, learning curves, PES/contour maps, MD trajectory or distribution plots, or complains about huge/slow PDFs, blurry figures, wrong font sizes, or journal figure rejections — even if they don't say "publication".
---

# Publication figures from matplotlib

Goal: a figure that drops into the manuscript at 100% scale, with legible text, sharp lines, a sane file size, and fonts that pass journal production checks.

The helper module `scripts/pubfig.py` implements everything below. Prefer importing it over re-deriving settings:

```python
import sys; sys.path.insert(0, "<skill_dir>/scripts")
import pubfig
pubfig.setup()                                   # rcParams: fonts, sizes, Type 42
fig, ax = pubfig.subplots(width="single", aspect=0.8)
ax.scatter(x, y, s=2, rasterized=True)           # dense data → raster layer
pubfig.save(fig, "figs/parity")                  # writes parity.pdf, checks fonts
```

Run `python scripts/check_pdf_fonts.py file.pdf` on any final PDF (including ones produced elsewhere) to detect Type 3 fonts.

## 1. Format decision

Work through in order; stop at the first match.

1. **Journal guidelines specify a format** → follow them. They override everything here. Production systems at some publishers ask for TIFF at fixed DPI for certain figure categories; check the current author guide rather than assuming. Keep the plotting script so re-export is trivial (`pubfig.save(..., formats=("pdf", "tiff"))`).
2. **Figure will be post-edited in Inkscape/Illustrator** → also export SVG (`formats=("pdf","svg")`), with `svg.fonttype = "none"` so text stays editable. Final output still PDF.
3. **Default** → vector PDF.
4. **Pure raster content** (rendered snapshots, microscopy, VMD/OVITO images) → PNG at ≥ 600 dpi at final print size, or embed via `imshow` inside a PDF figure.
5. **Never** JPEG for plots: lossy compression smears lines and text.

EPS is acceptable but offers nothing over PDF from matplotlib and handles transparency (alpha) badly — avoid unless demanded.

## 2. Hybrid rasterization for dense data

Pure-vector PDFs of dense data become multi-MB, render slowly, and can choke production pipelines. Rasterize only the data artists; keep axes, ticks, and text vector:

- `scatter`/`plot` with ≳ 10⁴ points (parity plots, MD trajectories, sampled configurations) → `rasterized=True`
- `contourf`, `pcolormesh`, `imshow`, `hexbin`, `tricontourf` (PES maps, 2D histograms) → `rasterized=True`; for contourf on older matplotlib use `ax.set_rasterization_zorder(z)` and give the contour a lower zorder
- `savefig(dpi=600)` sets the resolution of the rasterized layer only

`pubfig.save` warns if the PDF exceeds ~2 MB, which almost always means a dense artist was left unrasterized.

Also consider whether 10⁵ overlapping points convey anything: a `hexbin` or 2D histogram with a log color scale often shows the error distribution better than an opaque blob of scatter.

## 3. Size: set it once, never rescale

Set `figsize` to the real printed width and include the figure at its natural size: `\includegraphics{fig.pdf}` with **no** `width=` or `scale=` option. Any rescaling in LaTeX changes every font size and line width, and Python-side checks cannot see it. If the figure overflows the column, fix `figsize`, not the include.

`pubfig.save` runs `check_sizes` before saving: it warns about visible text below `min_pt` (default 7 pt), lines thinner than 0.5 pt, and widths over 7.5 in. Fix every warning rather than lowering `min_pt`. Two gaps remain: mathtext sub/superscripts render at ~70% of the reported size (an 8 pt label gives a ~5.6 pt subscript — use 9 pt labels if subscripts carry meaning), and the check reflects the saved size only.

Presets in `pubfig.WIDTHS` (inches). **These are typical values from memory, not verified against current guidelines — confirm with the target journal:**

| key | single | double |
|---|---|---|
| `acs` | 3.25 | 7.0 |
| `aip` / `aps` | 3.37 | 6.69 |
| `rsc` | 3.27 | 6.69 |
| `elsevier` | 3.54 | 7.48 |
| `generic` | 3.4 | 7.0 |

Font size at final scale: 7–9 pt for labels and ticks (default here 8 pt). Line widths ≥ 0.75 pt; axes 0.6–0.8 pt.

Avoid `bbox_inches="tight"` for final figures: it crops to content and changes the dimensions you set. Use `fig.set_layout_engine("constrained")` (done by `pubfig.subplots`) instead. If tight cropping is truly needed, set `pad_inches` and check the final size.

## 4. Fonts

- `pdf.fonttype = 42` and `ps.fonttype = 42`: embed TrueType instead of matplotlib's default Type 3, which some submission systems and PDF/A or IEEE-style checks reject.
- Match the manuscript font family where possible (sans-serif is standard for figures in most chemistry journals; serif for many physics journals).
- `text.usetex=True` (`pubfig.setup(usetex=True)`) gives exact LaTeX typography but is slower, needs a TeX install, and fails opaquely on unescaped characters. Use for final versions only. With usetex, matplotlib may emit Type 3 fonts again depending on the TeX font setup — always run the font check.
- Math: `mathtext.fontset = "dejavusans"` (sans) or `"cm"` (serif) to match the body text.

## 5. Color and readability

- Sequential data: `viridis`, `cividis`, `magma`. Diverging (errors, ΔE around zero): `RdBu_r`, `coolwarm`, with `TwoSlopeNorm(vcenter=0)`. Never `jet`/`rainbow`: non-uniform lightness creates apparent features (spurious ridges/barriers on a PES).
- Categorical lines: colorblind-safe cycle (`pubfig.setup` sets Okabe–Ito). Also vary marker or linestyle so the figure survives grayscale printing.
- Label units on every axis, e.g. `Energy error (meV/atom)`.
- For parity plots: equal aspect, identical axis limits, y = x reference line, and report the metric (RMSE/MAE) on the plot or in the caption with the test-set definition.

## 6. Final checklist

Before declaring a figure done, verify:

- [ ] Saved at final size; included with plain `\includegraphics{}` (no width/scale)
- [ ] `check_sizes` reports no warnings
- [ ] PDF fonts are Type 42/TrueType (run `check_pdf_fonts.py`)
- [ ] Dense artists rasterized; PDF < ~2 MB
- [ ] Text ≥ 7 pt at print size; units on axes
- [ ] Colormap perceptually uniform; categorical colors distinguishable in grayscale
- [ ] Journal-specific format/DPI requirements checked in the current author guide
