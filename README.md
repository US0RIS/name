# SpinTrap: a feedback-free magnet that levitates inside a liquid

**What it is.** A 6 mm NdFeB sphere hovers motionless in the middle of a jar of water,
touching nothing, while a hobby motor spins a tilted magnet above the jar at ~200 Hz. There
are no sensors, no position feedback, no coils and no superconductors. Earnshaw's theorem
forbids this with static fields; a *rotating* field plus the floater's inertia gets around
it. The liquid, which would normally be a nuisance, supplies the damping that makes the
state asymptotically stable. Used as a stir element, it never touches the vessel: no
grinding, no wear particles, no seals.

**What is new and what is not.** The levitation phenomenon and its basic mechanism are
**prior art**:
* Ucar 2021;
* Hermansen et al., *Phys. Rev. Applied* 2023;
* Hermansen, Durhuus & Bjørk, *APL* 2025;
* Fan et al., arXiv 2025.

This project contributes:
1. the **liquid-immersed regime**, where the liquid provides the stabilising dissipation;
2. a **device** built on it, with its design rules (body-force window, start-up and landing
   protocol, a balanced octupole-free tilted-cylinder rotor, the inertia penalty of buoyancy
   shells);
3. a falsifiable test plan.

See [`docs/REVIEW.md`](docs/REVIEW.md) for the adversarial review and the exact prior-art
split.

**Status: simulated and designed, NOT built or measured.** All numbers are model
predictions.

![section](docs/figures/fig0_section.png)

| Doc | Contents |
|---|---|
| [`docs/CANDIDATES.md`](docs/CANDIDATES.md) | 24 candidate inventions, scores, rejections |
| [`docs/RESEARCH_LOG.md`](docs/RESEARCH_LOG.md) | Hypotheses, failures, decisions |
| [`docs/PHYSICS.md`](docs/PHYSICS.md) | Model, rotating-frame reduction, scaling laws, stability |
| [`docs/RESULTS.md`](docs/RESULTS.md) | Computational results and figures |
| [`docs/REVIEW.md`](docs/REVIEW.md) | **Adversarial review: assumptions removed one by one, verdict** |
| [`docs/PROTOTYPE.md`](docs/PROTOTYPE.md) | Architecture, BOM (~$125), assembly, operation, test plan, proof criteria |
| `cad/` | CadQuery source, STEP/STL for all printed parts, assembly STEP, balance check |
| `firmware/` | Arduino closed-loop speed controller (Hall tach, ramps, land/stop interlocks) |
| `sim/` | Rotating-frame eigenvalue model, lab-frame 6-DOF integrator, all studies |
| `tools/` | Video height tracker, frequency-sweep logger |

Key predictions for the build:
* Floater: 6 mm N42 sphere. Rotor: 3/4″ × 5/8″ N42 cylinder tilted 12°. Liquid: water.
* At 200 Hz the floater levitates **34 mm** below the rotor centre; depth changes by about
  −0.15 mm/Hz.
* Lowest trap mode ≈ 11 Hz with τ ≈ 2.5 s; capture radius ≈ 53 mm.
* Safety rule: **never stop the motor with the floater close.** Use `L` (land), lower the
  vessel, then stop.

**Verdict of the review:** levitation in water is likely, about 70 % by my estimate. The
main unmodelled risk is steady-streaming and wall forces. Quantitative agreement is about a
coin flip. As a mixer it delivers only 1–5 mW: useful for gentle small-volume mixing, not
yet transformative.
