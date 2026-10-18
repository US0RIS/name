# Research log

Chronological. "H" = hypothesis, "R" = result, "D" = decision.

### 1. Framing and candidate generation
* Generated 24 candidates across mechanics, fluids, magnetics, acoustics, locomotion and
  energy (`CANDIDATES.md`).
* Ruled out on physics alone:
  * static magnet levitation (Earnshaw/Braunbek);
  * eddy-current wall climbing on aluminium (image currents in a non-magnetic conductor
    only repel, so there is no normal force toward the wall);
  * an oscillating-quadrupole "magnetic Paul trap" for a free dipole (it flips into a
    high-field seeker, and |B| has no free-space maximum).

### 2. Prior-art screen (web search only; full texts were not reachable from this environment)
* **R:** The first favourite, frequency-multiplexed resonant ratchets (one actuator driving
  N independent bidirectional joints), is Penn's 2012 MIT thesis and US 8,736,148.
  **Rejected.**
* **R:** Macroscopic topological transport has been done (Bayreuth group). Ultrasonic
  clutches exist. A capstan electroadhesive multiplexer was published in 2026.
  **Rejected.**
* **R:** Rotation-induced magnetic levitation is known (Ucar 2021; Hermansen 2023), with
  2025 follow-ups. **No liquid-phase or mixer use found.** Levitated mixers exist, but only
  with superconductors or active control.
* **D:** Pursue "rotation-induced levitation in a liquid as a feedback-free levitated stir
  element". Novelty is at the level of regime and device, not physics.

### 3. Modelling
* **H1:** The floater sits on the axis with its moment hanging down, like poles facing.
  **R:** No levitation in 30 scan cases. Wrong guess.
* **R:** A rotating-frame torque balance shows the floater's moment points *toward* the
  rotor's axial part (unlike poles, attractive ∝ d⁻⁴), with a gyroscopically enforced
  in-plane tilt that is anti-aligned with the field (repulsive ∝ d⁻⁷). Equilibrium solver
  plus lab-frame integration reproduced levitation at 3.4 cm, 200 Hz.
  *(Later found to be the mechanism already published in APL 2025.)*
* Built the rotating-frame autonomous model (`rotframe.py`). Fixed points plus an 11×11
  Jacobian gave **R:** neutral stability in air, asymptotic in liquid.
* **H2:** The stirrer layout (floater above the rotor) works with a bare magnet.
  **R:** Unstable, at 18–45 s⁻¹ growth. Mapping the net body force showed a
  direction-dependent window. **D:** Overhead drive for the bare magnet; a buoyancy shell
  for the bottom drive.
* **H3:** Spin up with the floater in the vessel. **R:** 0/24 captures; the floater
  slams into the rotor because low speed means a static field.
  **D:** Spin up first, then bring the vessel in. **R:** 5/5.
* **H4:** A stationary disc bias magnet can replace the rotor tilt. **R:** Too weak, or
  unstable. A concentric ring works but loads the motor bearings with 0.12 N m of rotating
  moment. **D:** Tilt the rotor magnet in its holder.
* Found the rule: a tilted cylinder with L/D ≈ √3/2 is dynamically balanced *and*
  octupole-free. Confirmed in CAD (0.012–0.014 N m residual).
* **H5:** A 16 mm PETG shell makes the bottom drive work at 200 Hz. **R:** No. The shell's
  inertia pulls the trap inward (d₀³ ∝ m₂/I). It works at 40–100 Hz. Capture needs the
  vessel lowered onto a spinning rotor (4/4 at 45 Hz).

### 4. Adversarial review (requested by the user)
* Found published work matching my §4 mechanism (Hermansen, Durhuus & Bjørk, APL 2025) and
  the role of damping (Fan et al. 2025). **D:** Re-scoped the novelty claims in every
  document.
* Exact cylinder field, eddy currents, iron, eccentricity, Br spread: **survive.**
* **R:** α = 8° at 200 Hz has **no equilibrium**. **D:** Nominal α 10° → 12°, with 10° and
  14° hubs provided.
* **R:** Fluid swirl beyond ±20 rad/s destabilises. The Ekman estimate of the swirl the
  floater can sustain is 0.4 rad/s. Named risk, with margin.
* **R:** Stability depends on the *ratio* of translational to rotational drag. It is stable
  over 0.3–40× and 0.3–3× respectively, which brackets realistic values.
* **R:** Speed ripple at the 11 Hz trap mode is amplified 12×. Not lost at ±1 %, but the
  speed loop must be clean in 5–15 Hz. Added to test T1.
* Unresolved: steady streaming and wall forces (A8). Only an experiment can settle them.

### 5. Discarded side results worth keeping
* **Bead on a vibrating string:** the time-averaged axial force is
  F = (m/4)A²ω²k sin 2kz, pointing toward the *antinodes*, a slope × normal-acceleration
  rectification. It only works if the string slope exceeds the friction angle and the
  carriage is much lighter than the string mass per wavelength. A plausible "vibrational
  elevator", but with little use.
* **Isotropic sphere in a rotating field without drag:** spin about the moment axis is
  exactly conserved, so the undamped system has a continuous family of fixed points.
  Fluid drag selects p = 0.
