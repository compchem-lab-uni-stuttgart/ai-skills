---
name: chemshell
description: Practical know-how for DFT reaction-mechanism studies with ChemShell + Turbomole + DL-FIND - transition-state search strategy (dimer, NEB, restrained scans, P-RFO, distort/kick checks, CREST), restraint force constants, P-RFO Hessian settings, 1-based atom indexing, coordinate choice for minimizations, judging stalled restrained optimizations, and instanton tunneling rate calculations. Use this skill whenever the user writes, edits, copies or debugs a ChemShell .chm script or a dl-find call, searches for or verifies a transition state, sets up a relaxed/restrained scan, NEB, dimer or P-RFO run, interprets imaginary frequencies, decides whether a running optimization is stuck, or computes instanton/tunneling rates - even if they only say "TS search", "optimize this structure" or "Turbomole job" without naming ChemShell.
---

# ChemShell + Turbomole + DL-FIND

Lessons from several DFT reaction-mechanism projects run with ChemShell
(Tcl), Turbomole and DL-FIND. Apply them when writing `.chm` drivers,
choosing a TS-search strategy, and judging running jobs. Each rule says
why, so you can judge edge cases.

## Quick checklist for every new .chm script

- Atom indices in `restraints=`, `constraints=`, `active_atoms=`, `frozen=`
  etc. are **1-based**. Add 1 to any Python/numpy index.
- Minimizations: use `coordinates=dlc`, never `coordinates=mass`.
- `optimiser=prfo` with `theory=turbomole`: **no** `initial_hessian=twopoint/onepoint`.
- Torsion restraints: K ≈ 0.3 Ha/rad²; bond restraints: K ≈ 0.5 Ha/Bohr².
- `weights=` needs a space before its opening brace, and must not share a
  script with a later unweighted dl-find call.

---

## Transition-state search strategies

Methods used so far to find/characterize transition states, with an
honest effectiveness verdict for each. Use this to pick a strategy
rather than defaulting to the dimer method alone.

**1. Dimer method (DL-FIND `dimer=true`)** — the main TS search tool.
`coords=` is the starting midpoint, `coords2=` gives the initial dimer
direction (doesn't need to be close to `coords`). Works well ONLY when
the midpoint start is already close to the true saddle; dimers seeded
from NEB peak images several reaction-coordinate steps away from the
real TS reliably diverged badly (confirmed repeatedly). For floppy substituents (e.g. isopropyl
groups), down-weighting those atoms via `weights=` (e.g. 0.1 vs 1.0)
stops spurious low-frequency rotation modes from dominating the dimer
rotation and lets it converge to the correct heavy-atom-framework TS
instead. CRITICAL bug: `weights=` in one dl-find call corrupts a later
unweighted dl-find call in the SAME script ("Error in reading weights")
— always run the weighted dimer and any follow-up Hessian as separate
jobs/scripts.

**2. NEB** — good for getting an approximate reaction-PATH SHAPE between
two confirmed minima and for generating candidate seed geometries for a
dimer search. NOT reliable for pinpointing the TS itself in a multi-step
proton-relay-type mechanism — the climbing image repeatedly landed too
far toward product ("reaction already over") instead of at the true
saddle. Treat its peak image as one candidate seed among several, never
as the answer.

**3. Restrained/relaxed scans along a reaction coordinate** — chained
restrained minimizations (`restraints= { bond i j r0 K }` or
`bonddiff2 i j k l r0 K` for a difference-of-two-bonds coordinate),
stepping r0 and reusing each converged point as the next step's start.
This was the single most reliable way to actually locate WHERE a
barrier is before trying to characterize it — essential once dimer/NEB
kept misidentifying the TS region. A 2D grid of such scans (fix one
coordinate, scan a second) plus a quadratic fit (#4) correctly predicted
a genuine saddle region. K=0.5 Ha/Bohr² used for bond-type restraints
(see the torsion-restraint section below for the K≈0.3 Ha/rad² case —
different coordinate type, not a contradiction). Syntax trap: `weights=`
needs a space before the opening brace or ChemShell's tokenizer
mis-parses it.

**4. Quadratic response-surface fit** to a sparse scan-energy grid
(least-squares E=a+bx+cy+dx²+ey²+fxy, solve ∇E=0, check Hessian
eigenvalue signs) — cheap, no extra QM calculations, good for predicting
roughly where to seed a real TS search from a coarse 2D grid. Only as
good as the grid's sparsity/extrapolation risk — treat the predicted
point as a seeding hint, not a confirmed TS.

**5. Direct Hessian on a scan's local-energy-maximum point**
("approximate TS") — cheapest first read on whether a scan-located
maximum is a genuine single-imaginary-mode saddle, without a full
dimer/P-RFO search. Worked well twice (clean single imaginary modes
found this way). Caveat: the point is still under the scan's restraint
when it "converged," so this is diagnostic, not a confirmed unrestrained
stationary point.

**6. P-RFO (DL-FIND `optimiser=prfo`)** — alternative TS-search algorithm
used alongside the dimer method. See the P-RFO Hessian section below:
never set `initial_hessian=twopoint/onepoint` with prfo+turbomole; let
Turbomole supply the analytic Hessian.

**7. Distort checks** (± displacement along a confirmed TS's imaginary
mode, then unrestrained reoptimization) — the standard cheap
IRC-substitute used to confirm a TS connects the expected reactant and
product minima. Also repeatedly and unexpectedly served as a
rotamer-trap detector: distort-and-reoptimize found previously
uncatalogued LOWER-energy rotamers of "already confirmed" minima that
plain optimization had missed — treat every distort-check result as a
potential new best minimum, not just a connectivity confirmation.

**8. "Kick" jobs** (small perturbation + reoptimize + Hessian) — not a TS
search, but the standard fix for a stationary point that converges with
a small residual imaginary mode (<15 cm⁻¹, likely numerical/shallow
rather than real saddle character) — used to turn "NOT CLEAN" results
into "PLAUSIBLE" ones.

**9. CREST (GFN2-xTB) conformer search** — not a TS method, but a
broader/cheaper alternative to manual kick/distort rotamer-hunting for a
MINIMUM, especially floppy multi-fragment non-covalent complexes. Worked
very well once: found a genuinely lower, clean conformer that a whole DFT-only search had missed. CREST and xtb may be installed
outside the module system; ask the user for the paths if `crest`/`xtb`
are not on `PATH`. Submit through a plain batch script, not the
ChemShell submission script — the same resource profile as a standard
ChemShell job is fine. Not yet tried for actual TS searching (CREST has
a `-tnmd`/TS mode too), only for ground-state conformer sampling so far.

**10. Restrain to a known analogous TS's bond lengths, then dimer** —
when a TS for a similar/related system is already known (e.g. a
different substituent, or a neighboring state in the same mechanism),
restrain the new system's main reacting bond lengths to the reference
TS's values (same `restraints= { bond i j r0 K }` mechanism as #3),
optimize under those restraints, then start a dimer search (#1) from
that restrained result. This gives the dimer a midpoint that is already
close to the right saddle region instead of a generic minimum or NEB
image, directly addressing dimer's main weakness (#1: it only converges
reliably when seeded close to the true saddle). Use it whenever a
same-family reference TS exists.

**Recommended pipeline for a genuinely unknown/hard TS**: if an
analogous TS is already known (#10), restrain to its bond lengths and
seed the dimer from that result first — it's cheaper than the full
pipeline below. Otherwise: NEB for rough path shape → restrained scan(s)
to find the real barrier region, don't trust the NEB peak image →
quadratic fit if a 2D grid exists → dimer (or P-RFO) seeded tightly from
the scan maximum/fit prediction, with `weights=` down-weighting for
floppy substituents → distort checks to confirm connectivity (watch for
new lower rotamers) → kick if the result has a small residual imaginary
mode.

---

## Restraint force constants

For DL-FIND relaxed torsion scans (`restraints= { { torsion i j k l
target K } }`), a force constant of K=0.1 Hartree/rad² let the achieved
angle drift several degrees off the nominal target. Use roughly three
times that (~0.3 Hartree/rad²) to pin the angle more tightly.

**Why:** the restraint is a soft harmonic potential, not a hard
constraint; at K=0.1 the true PES gradient along the torsion can pull
the converged geometry several degrees away from the requested target,
especially near steep/curved regions of the surface.

**How to apply:** when building a new relaxed torsion scan (single- or
multi-dimensional), default to K≈0.3 Hartree/rad² rather than 0.1, and
still report the *achieved* angle from the converged geometry (not just
the nominal target) in any results table, since some residual deviation
is expected regardless of K. For bond-type restraints (not torsions),
K≈0.5 Ha/Bohr² is used instead — different coordinate type, not a
contradiction.

---

## P-RFO Hessian setting

Never set `initial_hessian=twopoint` (or `onepoint`) in a DL-FIND
`optimiser=prfo` call when `theory=turbomole`. Omit `initial_hessian`
entirely (default is `external`).

**Why:** `initial_hessian=twopoint`/`onepoint` forces DL-FIND to compute
the starting Hessian itself via numerical finite differences (two extra
energy/gradient evaluations per variable, i.e. many extra hours). Leaving it at the default (`external`) lets Turbomole
compute its own analytic Hessian directly — faster and more accurate.
Confirmed by the startup log line: `Initial Hessian from external
program` (analytic) vs the numerical finite-difference variable-by-
variable log lines (`Finite-difference Hessian: variable i/N
direction=...`).

This mistake has been made (and corrected) more than once across
projects — a cheap check worth doing every time a P-RFO script is
written from scratch or copied from an older one.

**How to apply:** any time you build a `dl-find ... optimiser=prfo`
ChemShell/DL-FIND script with `theory=turbomole`, do not add
`initial_hessian=twopoint` or `initial_hessian=onepoint`. If an existing
P-RFO script has it, that is the bug to fix, not a valid starting point
to copy forward.

---

## ChemShell indexing gotcha

ChemShell and DL-FIND number atoms starting at 1, not 0, in every
keyword that takes explicit atom indices (`restraints= {{bond i j ...}}`,
and very likely `constraints`, `connect`, `active_atoms`, `frozen`,
`residues` too). `weights=` is the exception — it's a full-length
ordered-by-position list, so there's no index label to get offset.

**Why this matters:** building a `restraints=` block from 0-based
Python/numpy atom indices restrained the wrong atom one position off —
the job ran without error or warning, it just silently did the wrong
physics.

**How to apply:** any time an atom index is computed in Python (0-based)
and then goes into a ChemShell keyword that takes explicit atom numbers,
add 1 before writing it into the `.chm` script. After writing any
index-pair restraint/constraint, sanity-check by grepping the echoed
`rst_parm(...)` (or equivalent) in the job's early output and
independently re-deriving what atom each number should be, rather than
trusting the Python-side identification alone.

---

## Coordinates for minimizations

Use `coordinates=dlc` (delocalized internal coordinates) for DL-FIND
minimizations, plain or restrained. Never use `coordinates=mass`:
mass-weighted coordinates are very inefficient for minimization. Watch
for it when copying older `.chm` inputs (e.g. student/thesis inputs),
which sometimes carry it.

**Why:** in a benchmark from an identical start, `coordinates=dlc`
converged in far fewer cycles than default Cartesians, which also
stopped spuriously on a flat shoulder well above the true minimum;
`coordinates=mass` was by far the slowest. DLC's extra cost per cycle
is small.

---

## Restrained-optimization plateau judgment

Don't conclude a restrained-optimization job is stuck/plateaued just
because the *restrained* coordinates and the energy have stopped
changing much — check Max step and RMS step too. Other (unrestrained)
degrees of freedom can still be moving significantly even while the
restrained coordinates and energy look flat.

**Why:** confirmed twice in practice — a ring-restraint minimization had
all restrained bond distances stable for many cycles while Max/RMS step
were still well above target (the rest of the molecule was still
relaxing around the new geometry); a proton-relay restrained pull
oscillated near threshold for dozens of cycles with all restraints
already satisfied, then genuinely converged much later at a measurably
lower energy. Oscillation-near-threshold in a restrained optimization is
not evidence of a dead end — it's normal while unrestrained degrees of
freedom keep settling, and the job usually finishes if left alone,
especially when feeding a subsequent TS search.

**How to apply:** before recommending an early stop on a "plateaued" or
"oscillating" restrained optimization, always report Max step/RMS step
(or whichever criteria aren't yet met) alongside the restraint-distance
table, not just energy and restrained distances. Default to patience.

---

## Instanton (tunneling) rate-constant calculations

Practical parameters for DL-FIND instanton work (`qts=true`/
`qtsrate=true`, see the DL-FIND manual, section 5.2):

- Start with **nimage=10** for the first instanton optimization.
- The crossover temperature T_c is already printed in the output of any
  TS Hessian calculation (`thermal=true` on the TS) — no need to compute
  it manually from the imaginary frequency.
- For the temperature-cooling schedule (successive instanton
  optimizations at decreasing T), reduce temperature by a factor of
  **~0.8 per step**, rounding to integer Kelvin values close to the
  resulting 0.8×T.
- Reporting: tabulate rate constant vs. temperature, but plot
  **log(k) vs. 1/T** (Arrhenius-style), not k vs. T directly.

If the user has a working instanton example (a cooling-schedule driver
script with nimage/distort/`optimiser=NR` mechanics), read it first
before reconstructing the ChemShell driver from the manual alone.

---

## Working conventions

- **Energy units:** report absolute energies in Hartree, relative/
  difference energies (barriers, reaction energies) in kJ/mol — not
  kcal/mol or eV (fine as a secondary aside).
- **Job identification:** identify jobs by their directory name in
  conversation, never by raw queue job ID alone — directory names are
  what persists and is meaningful to the user; queue numbers are still
  needed internally for `qstat`/`qdel` but shouldn't appear in
  user-facing status sentences.
- **Proactive follow-up:** for "once job X finishes, do Y"-type
  requests, treat it as a standing instruction — launch Y autonomously
  the moment X is detected complete (e.g. via `ScheduleWakeup` with the
  follow-up instructions embedded in the wakeup prompt), rather than
  waiting to be asked again. Start with a wider polling interval (15-20
  min) while a job is clearly far from done, and shrink it (down to the
  60s floor) as convergence criteria get closer to being met, to cut
  detection lag right when it matters most.
