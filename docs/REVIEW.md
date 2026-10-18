# Adversarial review: would the SpinTrap actually work?

This review was requested before finalising, with the instruction *not* to adjust results to
make the design look good. The first-pass design point was **α = 10°**, which was moved
to **α = 12°** *because of* what this review found (§3). That change and its reason are
recorded here.

## 1. What is already known (prior art) and what is not

| Element | Status | Source |
|---|---|---|
| A magnet levitates near a magnet spinning at ~200 Hz | **Known** | Ucar 2021; Hermansen et al., *Phys. Rev. Applied* 20, 044036 (2023) |
| Floater phase-locks to the rotor; its moment points close to the spin axis, tilted toward the rotor's like pole, nearly perpendicular to the local field | **Known** | Hermansen et al. 2023. *My model reproduces this orientation independently*: tilt β ≈ 15–19°, in-plane component parallel to the rotor's in-plane moment |
| Smaller floaters need faster rotors and levitate farther away | **Known** | Hermansen et al. 2023. My model reproduces the trend: d₀ ∝ R^(−2/3), and the minimum frequency rises for smaller floaters |
| Levitation force = repulsion from the rotating part + attraction from a static on-axis field; a static axial field lowers the needed frequency | **Known** | Hermansen, Durhuus & Bjørk, *APL* 127, 012402 (2025). **My §4 "bound state" analysis in PHYSICS.md is a re-derivation of this, not new** |
| Damping is needed to reach stable levitation; stability phase diagrams vs rotation speed and damping (copper board eddy currents) | **Known** | Fan et al., arXiv 2507.07478 (2025) |
| On-axis and off-axis levitation states | **Known** | Le Lay et al., arXiv 2503.22568 (2025); "Magnetic levitation in the field of a rotating dipole", arXiv 2410.22096 |
| Levitated magnetic mixers and pumps | **Known, but only with superconductors or active feedback** | LevTech (US 6,416,215), Alfa Laval UltraPure, CN116651287B |
| **Rotation-induced levitation of a floater *immersed in a liquid*, with the liquid as the dissipation that stabilises it** | **Not found** | my searches (see the limits below) |
| **Using it as a contactless, sensorless stir element (overhead and bottom-drive layouts) with a start-up and landing protocol** | **Not found** | |
| Body-force direction window; buoyancy/inertia trade-off (a shell moves the trap inward via d₀³ ∝ m₂/I) | **Not found in what I could access**; may be implicit in the gravity-free statements of prior work | |
| Rotor built as a tilted L/D ≈ √3/2 cylinder in a spherical hub (balanced and octupole-free; the tilt supplies the static axial field mechanically) | Engineering choice. The √3/2 octupole-free cylinder is, I believe, known magnetics lore. Applying it here is mine | |

**Limits of the prior-art check.** I could run web searches but could not open arXiv,
Google Patents or journal PDFs from this environment (DNS and proxy blocks), so the table
rests on abstracts and search summaries. A full-text check of the five papers above is
needed before claiming anything publicly. In particular, check Fan et al. and Le Lay et al.
for any liquid or viscous-damping experiments.

**Honest framing of the contribution.** The physical phenomenon is *not* mine, and neither
is its basic mechanism. What this project contributes:
1. **A new operating regime:** levitation inside a liquid. The model predicts it works
   *better* than in air, because the liquid supplies the dissipation that prior experiments
   had to get from copper plates. It also predicts that levitation depth is almost
   independent of viscosity while damping is not.
2. **A device built on it:** a feedback-free levitated stirrer, with the design rules this
   requires (body-force window, start-up and landing protocol, rotor construction, the
   bottom-drive inertia penalty).
3. **A quantitative, falsifiable test plan.**

That puts the project between the brief's Outcome A (buildable device) and Outcome B (a
computationally supported new regime). It is **not** a new physical principle.

## 2. Every simplifying assumption, and what happened when it was removed

The modelling assumptions are numbered A1–A10, matching the column below. "Verdict" is the
effect at the α = 12°, 200 Hz design point, except where a row says otherwise. Data:
`sim/adversarial*.json`, `sim/drag_ratio.json`, `sim/ripple.json`.

| # | Assumption | Test | Verdict |
|---|---|---|---|
| A1 | Rotor field = point dipole | Exact finite-cylinder field (240 elliptic-integral current loops, validated to 1e-6 against the analytic on-axis field) | Depth changes by 0.4 mm (3.62 → 3.66 cm at α = 10°). Still stable, decay 0.32 vs 0.33 s⁻¹. Transverse field error at the floater is 0.02 %. **Survives** |
| A2 | Floater = point dipole | Exact for a uniformly magnetised sphere (mean-value property) | Not an approximation |
| A3 | Rigid, uniform magnetisation | Fields ≤ 17 mT ≪ coercivity (> 900 kA/m); μr ≈ 1.05 | Negligible |
| A4 | 6-DOF rigid body | The model *is* full 6-DOF for a sphere (3 translation + 3 rotation, with the spin about the moment tracked). The rotor is kinematically prescribed: the floater's reaction torque on it is ~1 µN m against a motor that delivers ~0.1 N m | **Survives**. Lab-frame nonlinear integration reproduces the rotating-frame fixed points and their decay |
| A5 | No eddy currents | Added the low-frequency eddy torque on a conducting sphere, k = (2π/15)σa⁵, at ×1 and ×10 | In water: depth +0.2 mm, decay 0.33 → 0.30 s⁻¹. **Survives.** In air (not this design) it matters: with air drag the state becomes very weakly unstable (growth time ≈ 8 min). That is consistent with prior work needing extra damping in air |
| A6 | Quasi-steady drag laws (Stokes + form drag; steady rotating-sphere torque correlation) | (a) all drag ×0.3 / ×3; (b) translational and rotational drag scaled **independently**, 0.1–300× and 0.1–10× | (a) stable, decay 0.10 / 0.98 s⁻¹. (b) **Stable over 0.3–40× translational and 0.3–3× rotational.** Unstable only for lopsided ratios (translational ≤ 0.1× with rotational ≥ 3×, or translational ≥ 100× with rotational ≤ 0.3×). Oscillatory-boundary-layer theory suggests real translational damping is ~10–20× Stokes at the 10 Hz mode, which is the *more* stable side (decay ≈ 2 s⁻¹). **Survives, but is the least certain part of the model** |
| A7 | Fluid at rest in the lab | Solid-body swirl added to every drag term | **Unstable beyond ≈ ±20 rad/s of swirl** (threshold nearly independent of viscosity). An Ekman spin-down estimate says the floater's 0.8 µN m drive sustains only ≈ 0.4 rad/s of bulk swirl in the 80 mm jar, a ×50 margin. External flows (pouring, convection, a stirred neighbour) must not set the liquid around the floater rotating faster than ~20 rad/s (≈ 190 rpm). **Survives with margin; it is a named risk** |
| A8 | No steady-streaming / wall / free-surface forces | Not modelled. Scale estimate: ρU²R² ≈ 9–13 mN (U = ωR ≈ 1 m/s). For a sphere in unbounded fluid it cancels by symmetry; near the floor and free surface (≈ 3–4 R away) the residual is perhaps 5–15 %, i.e. ~0.5–2 mN | The trap tolerates a steady extra force of roughly −2.5 mN (away from the rotor) to +5 mN (toward it), and ±3.6 mN sideways (30° tilt test). **Unresolved: the largest modelling risk. Only an experiment settles it** |
| A9 | Perfect rotor speed | Lab-frame runs with ±0.5 % and ±1 % speed ripple at 2 Hz, at the trap mode, and at 30 Hz | see §4 |
| A10 | Ideal geometry | Tilt α ±2°; rotor Br 1.22–1.38 T; floater Br 1.08 T; rotor eccentricity 0.1–0.3 mm; motor stator iron (30 % image dipole at +80 mm) | **α = 8° at 200 Hz: NO EQUILIBRIUM** (weight exceeds the peak attraction). All others: depth changes ≤ 2.3 mm, still stable. α = 8° is rescued by re-tuning to 230 Hz (stable, 36.2 mm) |
| — | Combined worst case at α = 12° (cylinder field, Br 1.22, stator iron, eddy currents, swirl 8 rad/s, drag ×0.5, eccentricity 0.2 mm) | | **Stable**, depth 3.26 cm, decay 0.19 s⁻¹. At α = 10°, the same combination with a −2° error and 40 rad/s swirl had **no equilibrium**, which is why the nominal moved to 12° |

## 3. Design changes forced by this review

* **Nominal tilt 10° → 12°.** At 10° and 200 Hz the design sat ~2° from the edge of the
  region where an equilibrium exists. 12° is centred, and 10°/14° hubs are supplied. The
  firmware's frequency knob compensates any α between 8° and 16°.
* **Shroud windows removed, Hall pocket made blind.** The shroud is the containment.
* **Swirl:** the jar must be wide (≥ 75 mm), and the procedure keeps external flows away.
  Baffles are the standard remedy if T8 shows drift.

## 4. Speed ripple (A9)

Lab-frame nonlinear runs (dipole rotor, α = 12°, water, 200 Hz, 8 s each; `sim/ripple.py`).
The trap's lowest mode is at 11.0 Hz (lab frame), lightly damped (Q ≈ 85).

| Speed ripple | at 2 Hz | at 11.0 Hz (trap mode) | at 30 Hz |
|---|---|---|---|
| ±0.5 % (±1 Hz) | 0.30 mm p-p | **3.55 mm p-p** | 0.08 mm p-p |
| ±1.0 % (±2 Hz) | 0.58 mm p-p | **4.36 mm p-p** | 0.13 mm p-p |

The floater was never lost, but ripple at the trap mode is amplified about 12×. The speed
loop therefore must not have oscillation or limit cycles at 5–15 Hz. The firmware's PI
gains are conservative, and test T1 enforces < 0.1 Hz ripple in that band before any
levitation attempt. Cheap ESCs with coarse 50 Hz PWM can produce a few-Hz hunt, which is
why T1 comes first.

## 5. Verdict

**Would it work?** My estimates, not measured:

| Claim | Confidence | Why |
|---|---|---|
| A 6 mm sphere can be levitated near a ~200 Hz rotor at all | **High (~90 %)** | Independently reproduced by several groups in air at this scale; my model reproduces their qualitative observations |
| It levitates **in water**, captured with the raise-the-vessel protocol | **Moderate–high (~70 %)** | Every modelled perturbation leaves it stable, and liquid damping is the ingredient prior work found necessary. Unmodelled streaming and wall forces (A8) are the main way it could fail; tuning f and α gives ±5 mm of depth authority to compensate |
| Depth-vs-frequency within ±3 mm of the model (T4) | **Moderate (~50 %)** | Prior models match experiments in *trend* (Hermansen 2025 v3 wording); my rotor and drag models are untested |
| It is a *useful* mixer | **Low–moderate** | Mixing power is only 1–5 mW: fine for gentle mixing of 10–50 mL (cell culture, crystallisation seeds), useless for anything vigorous. Scaling to bioreactors needs larger magnets (power ∝ Ω³R⁵) and was not designed |
| The transformative versions (bearingless levitated pump impeller, capsule robots) | **Speculative** | With fluid drag the floater does not spin about its own axis (p → 0), so it cannot deliver shaft-like torque. A pump would need a different floater geometry. Not analysed |

**Bottom line.** This is a credible, cheap experiment with a real chance of a striking result:
a magnet hovering motionless-looking mid-liquid with no feedback, sensors or
superconductors. It also has a clear quantitative falsification test. It is an
**application and new operating regime of a known 2021–2025 phenomenon, not a new
physical principle**, and its practical value as a mixer is modest unless scaled.
