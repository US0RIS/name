# Candidate screen (24 candidates)

Scoring 1-5 on the six criteria from the brief: **I**mpossibility (how strongly it contradicts
intuition), **U**sefulness, **N**ovelty (after the prior-art check, not before), **P**lausibility,
prototype **A**ccessibility, **T**ransformative potential. The prior-art notes come from the
searches logged in `RESEARCH_LOG.md`. Prior art marked † is from background knowledge and was **not**
re-verified by a search in this session. A low novelty score means the core mechanism is already
published or patented. It is not a judgement on whether the idea is good.

| # | Candidate | Physics lever | I | U | N | P | A | T | Verdict |
|---|-----------|---------------|---|---|---|---|---|---|---------|
| 1 | **Passively levitated, electronics-free stirring/pumping element (rotation-induced levitation in liquid)** | time-periodic field + rotating-frame Coriolis/gyroscopic terms, Earnshaw loophole | 5 | 4 | 4 | 4 | 5 | 4 | **SELECTED** |
| 2 | One actuator -> N independent bidirectional joints by frequency-multiplexed resonant ratchets | mechanical FDM, tuned reeds | 4 | 4 | 1 | 5 | 5 | 4 | Rejected: Penn, MIT PhD 2012 + US 8,736,148 already do it, bidirectionally |
| 3 | Passive carriage that climbs a vibrating vertical wire and parks at a frequency-selected antinode | slope x transverse acceleration rectification, F = (m/4)A^2 w^2 k sin 2kz | 4 | 2 | 3 | 3 | 4 | 2 | Rejected: needs string slope > friction angle; carriage must be << string mass per wavelength; low payload, weak use case |
| 4 | Macroscopic topologically-protected transport on a passive magnet floor by a single global field | Thouless-type adiabatic pumping | 5 | 3 | 1 | 4 | 3 | 3 | Rejected: Bayreuth group has done mm-scale and "macroscopic Floquet" versions |
| 5 | Ultrasonic friction gating of a capstan (exponential gain switch) | Euler-Eytelwein e^{mu theta} with vibration-modulated mu | 3 | 4 | 2 | 4 | 3 | 3 | Rejected: ultrasonic clutches (US 4,318,459, US 2005/0082137) + capstan-amplified electroadhesive clutch multiplexer (npj Robotics 2026) cover most of it |
| 6 | Vibration-erected multi-link "rope" that points along any commanded direction | tilted Kapitza averaging | 5 | 1 | 3 | 4 | 3 | 1 | Rejected: tilted-forcing Kapitza already analysed (Apffel et al. liquid walls); power-hungry, no use |
| 7 | Frequency-selected chain shapes (different tones -> different poses) | Kapitza with internal elastic resonances | 4 | 1 | 3 | 2 | 2 | 2 | Rejected: low usefulness; high-frequency limit makes shapes frequency-independent |
| 8 | Static passive permanent-magnet levitation | none | 5 | 4 | - | 0 | - | - | Impossible: Earnshaw/Braunbek (no static minimum of -m.B in free space for rigid moments) |
| 9 | Climbing aluminium walls with spinning magnets (eddy-current adhesion) | eddy currents | 4 | 3 | - | 0 | - | - | Falsified: image currents in a non-magnetic conductor are always repulsive -> no normal force toward the wall |
| 10 | Stationary-coil rotating-field levitation (no moving parts) | same as #1 with 3-phase coils | 5 | 3 | 3 | 3 | 2 | 3 | Deferred: 20-50 mT rotating at 200 Hz over cm needs ~2-3 kA-turns -> hundreds of W of copper loss. Kept as a future variant |
| 11 | Ucar levitation used as a contactless bearing for a torque-transmitting impeller (blood pump) | #1 plus a load torque | 5 | 5 | 4 | 2 | 2 | 5 | Folded into #1 as the long-term goal; the floater barely spins about its own axis (p -> 0), so torque transmission needs further work |
| 12 | Passively hovering flapping machine with no sensors | aerodynamic passive stability | 4 | 2 | 1 | 4 | 3 | 2 | Rejected: Ristroph & Childress 2014† |
| 13 | Gyro-monorail standing still | gyroscopic stabilisation | 4 | 2 | 1 | 5 | 4 | 1 | Rejected: Brennan 1907† |
| 14 | Self-calibrating zero-energy gravity balancer | zero-free-length springs, energy-free preload shift | 3 | 4 | 2 | 4 | 4 | 3 | Rejected: TU Delft static-balancing work† |
| 15 | Upside-down boat on a vibration-levitated liquid layer | Kapitza + Rayleigh-Taylor stabilisation | 5 | 1 | 1 | 4 | 2 | 1 | Rejected: Apffel et al., Nature 2020 |
| 16 | Single-actuator robot hand via selectable clutches | clutched underactuation | 2 | 5 | 1 | 5 | 4 | 3 | Rejected: many patents; capstan-EA clutch hand (npj Robotics 2026) |
| 17 | Gyroscopic one-way vibration isolator (mechanical circulator) | broken time-reversal | 4 | 2 | 2 | 4 | 3 | 2 | Rejected: gyroscopic metamaterials, Nash et al. PNAS 2015† |
| 18 | Swimming on a frictionless curved surface by shape change | geometric phase in curved space | 5 | 1 | 1 | 4 | 2 | 1 | Rejected: curved-space locomotion robots have been reported (Georgia Tech group)† |
| 19 | Cheap passive gyrocompass (finds true north) | Earth rotation coupling to a floated rotor | 4 | 3 | 1 | 3 | 2 | 2 | Rejected: Anschuetz 1908†; torque ~1e-6 N m needs flotation |
| 20 | Wind vehicle faster than wind, directly downwind | propeller/wheel coupling | 5 | 1 | 1 | 5 | 3 | 1 | Rejected: Blackbird 2010† |
| 21 | Ponderomotive "magnetic Paul trap" for a non-spinning dipole with an oscillating (not rotating) quadrupole | Kapitza averaging on -m.B | 5 | 3 | 3 | 2 | 2 | 3 | Rejected: orientation is unstable; a free dipole flips to become a high-field seeker, and |B| has no free-space maximum |
| 22 | Passive vibration-driven precision stage with exact digital steps (resonant escapement) | Accutron-type index wheel | 3 | 3 | 1 | 5 | 5 | 2 | Rejected: Bulova Accutron 1960† + #2 |
| 23 | Electro-mechanical tendon amplifier: one spinning drum, N friction-gated tendons | capstan amplification | 3 | 4 | 1 | 4 | 4 | 3 | Rejected: Nieman torque amplifier (1920s)†, npj Robotics 2026 EA capstan |
| 24 | Granular "Janssen lock" released by vibration | wall-friction saturation + fluidisation | 3 | 3 | 2 | 4 | 5 | 2 | Rejected: jamming-lock literature |

## Why #1 won

* **Apparent impossibility.** Earnshaw's theorem forbids stable static levitation of a magnet
  by magnets. Every commercial levitated mixer or pump therefore uses one of three things: a
  superconductor (LevTech patents, e.g. US 6,416,215), active position feedback with coils and
  sensors (Alfa Laval UltraPure; the 2026 Hunan Lingxiang patent CN116651287B; Levitronix and
  HeartMate 3†), or hydrodynamic bearings (HVAD†). This device uses none of them, only one spinning magnet on a hobby motor.
* **Physics is real and recent.** Rotation-induced levitation was reported by Ucar (2021) and
  explained by Hermansen et al. (Phys. Rev. Applied 20, 044036, 2023). Follow-ups in 2025 cover
  on/off-axis states and the role of a static axial field. Damping is already known to be necessary: Fan et al.
  (arXiv 2507.07478, 2025) used eddy currents in a copper board. **I found no prior work
  that runs the floater inside a liquid, uses the liquid as the damping, or uses the effect
  as a mixer.** The physics is not mine; the regime and the device are. See `REVIEW.md`
  for the full prior-art split.
* **Useful.** A stir element that never touches the vessel removes grinding (secondary
  nucleation in crystallisation, wear particles), shear hot-spots at the bearing (cell
  culture), and seals or feedthroughs (sealed single-use bags). It does this at hobby-motor
  cost instead of five figures.
* **Prototype-accessible.** It needs one hobby BLDC motor, two NdFeB magnets, printed parts and
  an Arduino.
* **Transformative path.** The long-term version is a sensorless, coil-free, passively
  levitated impeller (#11): a pump with no bearings and no levitation electronics.
