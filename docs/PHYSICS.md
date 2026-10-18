# Physics of the SpinTrap

## 1. Why it "shouldn't work"

**Earnshaw–Braunbek.** In a current-free region, every Cartesian component of a static
magnetic field is harmonic. The energy of a magnet with a rigid moment, U = −m·B, is
then harmonic too and has no local minimum, so no arrangement of permanent magnets can trap
another permanent magnet statically. A magnet that is free to rotate aligns with the field,
making U = −m|B|; |B| has no local maximum in free space, so a free magnet can't be trapped
either.

The known escapes are:
* diamagnetism (pyrolytic graphite, bismuth, superconductors);
* feedback (sensors, coils and a controller);
* spin, as in the Levitron, a gyroscopic low-field seeker;
* motion relative to a conductor (eddy-current or Inductrack levitation);
* **time-periodic fields**.

Industrial levitated mixers and pumps use the first two.

**The escape used here.** Make the source field time-periodic: a magnet spinning at
Ω = 2πf. Earnshaw's theorem concerns static fields. With a rotating source, the floater's
inertia and the Coriolis terms of the rotating frame enter the force balance and can create a
true bound state. The bound state was reported by Ucar (2021) and explained by Hermansen
et al. (*Phys. Rev. Applied* 20, 044036, 2023). The new results here are about what happens
when the floater is **immersed in a liquid**, and about how to turn that into a mixer.

## 2. Model

Both magnets are taken as uniformly magnetised bodies with rigid magnetisation (NdFeB:
μr ≈ 1.05, coercivity far above the fields involved).

* **Spheres are exact dipoles.** The external field of a uniformly magnetised sphere is
  exactly a point-dipole field, and the force and torque on it in an external harmonic field
  equal those on a point dipole at its centre (mean-value property). For two spheres, the
  dipole–dipole model is therefore exact, not an approximation.
* **The rotor is a "dynamically spherical" cylinder.** For a uniformly magnetised body,
  the magnetic potential is −M·∇Φ_shape, where Φ_shape is the potential of a uniform
  mass distribution with the same shape. Its first non-dipolar term (the octupole) is
  proportional to the shape's quadrupole moment, which is set by the inertia anisotropy.
  A cylinder with L/D = √3/2 ≈ 0.866 has an isotropic inertia tensor, so the same geometric
  condition gives
  1. **zero dynamic imbalance when it is spun about any axis**, and
  2. **zero octupole**, so its field is dipolar to order (D/r)⁴.

  The 3/4″ × 5/8″ stock magnet (L/D = 0.833) is close to this. In the CAD rotor its residual
  product of inertia gives a dynamic imbalance moment of only 0.012 N m at 200 Hz
  (`cad/check_massprops.py`). This is why the rotor magnet can be **tilted** in its holder
  without the rotor becoming unbalanced.

Floater equations (lab frame; sphere ⇒ isotropic inertia, so there is no Euler ω×Iω term):

```
M_i  dv/dt = ∇(m₂·B_rotor) − W ẑ − c₁ v − c₂|v| v                 (translation, added mass included in M_i)
I    dω/dt = m₂ × B_rotor + τ_drag(ω)                              (rotation)
     dm̂/dt = ω × m̂                                                 (moment is fixed in the body)
B_rotor(r,t) = μ₀/4π · [3(m₁·r̂)r̂ − m₁]/r³ ,  m₁(t) = m₁ (cosα cosΩt, cosα sinΩt, sinα)
```

Here α is the tilt of the rotor moment out of its spin plane. Its axial part m₁ sinα is
time-independent, so it is equivalent to a static coaxial magnet.

Fluid loads:
* Stokes drag c₁ = 6πμR plus form drag c₂ = ½ρC_D πR² (C_D = 0.47).
* Rotational drag from the rotating-sphere correlation M = ½ρω²R⁵C_M, with
  C_M = 64/(3Re) + 12.2/√Re and Re = ωR²/ν.
* Added mass ½ρV.
* W = (m − ρV)g.

## 3. Rotating-frame reduction

In a frame co-rotating with the rotor, B_rotor is static. With the fluid at rest in the lab,
the floater equations become **autonomous**:

```
dr/dt = v
dv/dt = F(r,m̂)/M_i − 2Ω×v − Ω×(Ω×r) − [drag evaluated at v_lab = v + Ω×r]/M_i
dm̂/dt = (ω − Ω) × m̂
dω/dt = [m₂ m̂ × B(r) + τ_drag(ω)]/I − Ω×ω          (ω = lab angular velocity, rotating-frame components)
```

Synchronous levitation states are therefore **fixed points**, and their stability is set by
the eigenvalues of an 11×11 Jacobian (3 position, 3 velocity, 2 tangent angles of m̂,
3 angular velocity). `sim/rotframe.py` implements this and validates it against brute-force
lab-frame integration (`sim/dipole_rt.py`, `sim/labsim.py`).

### Conserved spin and the "free" gyroscope

For a sphere, d(ω·m̂)/dt = (τ_mag + τ_drag)·m̂ / I, and the magnetic torque has no
component along m̂. Without drag, the spin p = ω·m̂ is conserved. With fluid drag it decays
to p = 0: **the floater ends up not spinning about its own magnetic axis**.

A fixed point then has ω = Ωẑ + s m̂ with s = −Ω cos θ. The body wobbles, its axis
sweeping a cone at Ω, and the torque needed to keep it wobbling is

```
I dω/dt = I s Ω (ẑ × m̂)   ⇒   m₂ m̂ × B = −I Ω² cosθ (ẑ × m̂)
⇒  m̂ ∥ ( m₂ B − I Ω² m̂_z ẑ )
```

So the floater behaves as if an extra "inertial field" of strength IΩ²/m₂ were added along
the axis. That term holds its moment close to the spin axis, against the in-plane rotating
field: it is the gyroscopic action of the wobble.

## 4. On-axis bound state (leading order)

> **Credit.** This decomposition (repulsion from the rotating field plus attraction from a
> static on-axis field) is the mechanism already published by Hermansen, Durhuus & Bjørk
> (*APL* 127, 012402, 2025), building on Hermansen et al. (2023). It is re-derived here only
> so that the scalings used in the design are explicit. It is **not** a contribution of this
> project.

On the axis at distance d below the rotor, B = b₀(−cosα, 0, 2 sinα) with b₀ = μ₀m₁/(4πd³).
Define K = IΩ²/(m₂b₀) (inertia over magnetic stiffness). For K ≫ 1 the torque balance gives a
moment near +ẑ (unlike poles facing the rotor's axial part), tilted by

```
sin β ≈ cosα / K                  toward +x', i.e. PARALLEL to the rotor's in-plane moment
```

That is the "wrong" way: anti-aligned with the local field, and held there gyroscopically.
The axial force on the floater is

```
F_z = (3μ₀ / 4π d⁴) · [ 3 m₁ sinα · m₂ cosβ  −  m₁ cosα · m₂ sinβ ]
         └── axial poles, attractive ∝ d⁻⁴ ──┘   └── in-plane, gyroscopically
                                                     anti-aligned ⇒ repulsive ∝ d⁻⁷ ┘
```

The axial term is a long-range attraction and the in-plane term a short-range repulsion,
which together form a potential well (Fig. 1). Setting F_z = 0 gives the force-free bound
distance

```
d₀³ ≈ μ₀ m₁ m₂ cos²α / (12π I Ω² sinα)  =  m₁ B_r cos²α / (12π · 0.4 ρ R² Ω² sinα)   (floater = sphere of radius R)
```

This is leading order. It gives 2.6 cm against 3.2 cm from the exact fixed-point solution,
because the real tilt (β ≈ 19°) isn't small. The scalings are what matter:

* **d₀ ∝ Ω^(−2/3)**: spin faster and the floater moves closer. This is the experimental
  knob, and it is the main falsifiable prediction (Fig. 2).
* **d₀ ∝ R^(−2/3)**: smaller floaters sit farther away. This matches Hermansen et al.'s
  observation.
* **d₀ ∝ (I/m₂)^(−1/3)**: a buoyancy shell that adds inertia moves the trap in. That is why
  the bottom-drive variant has to run 4× slower (Fig. 6).
* **Weight sets the window.** The equilibrium sits where F_z balances the net body force. If
  the body force exceeds the peak attraction (Fig. 1), there is no equilibrium.
* **Capture radius.** The second, unstable root (≈ 4.9 cm at 200 Hz) is the separatrix. A
  floater has to be brought inside it.

## 5. Stability: what the eigenvalues say

(The numbers in this section are for the first-pass design point, α = 10°. The final design
uses α = 12°; see `REVIEW.md` for why and for the α = 12° numbers.)

1. **In air** the levitated state has purely imaginary eigenvalues (to 10⁻¹³): it is
   neutrally stable, a Hamiltonian system stabilised by Coriolis and gyroscopic coupling.
   This is consistent with experiments in air needing some dissipation to capture the floater
   (Hermansen et al. invoke eddy currents).
2. **In a liquid** every eigenvalue moves into the left half-plane: the state becomes
   **asymptotically stable**. The slowest decay rate is 0.33 s⁻¹ in water and 7 s⁻¹ in
   glycerol (Fig. 4).

   That damping is *needed* is already known from experiments that use eddy currents in a
   copper board (Fan et al., arXiv 2507.07478, 2025). What is new here is that a **liquid**
   supplies it.

   This is not trivial. The Kelvin–Tait–Chetaev theorem says that *complete* dissipation
   destroys gyroscopic stabilisation of a potential saddle. But drag from a fluid at rest in
   the *lab* appears in the rotating frame as a dissipative force **plus** a circulatory
   force −c Ω×r (and the rotational analogue). That combination is outside the theorem's
   hypotheses, and here it stabilises.
3. **Body-force direction rule** (not found in the prior work I could access; see `REVIEW.md`). The state is stable only while the net body force
   (weight minus buoyancy) points **away** from the rotor, or toward it by at most
   ≈ 0.15 × the floater's weight in air (Fig. 3). Beyond that, a nutation-type mode at about
   the rotation frequency goes unstable, at a growth rate of 5–45 s⁻¹. Consequences:
   * **Overhead drive** (rotor above the vessel): a bare NdFeB sphere works directly.
     Water only reduces its weight, to 0.87 W₀.
   * **Bottom drive** (classic stirrer layout): the floater has to be neutral or buoyant, so
     it needs a shell. The shell's inertia then forces the rotor down to 40–60 Hz.
4. **Start-up rule** (engineering consequence; not found in accessible prior work). At low rotor speed the field is quasi-static. The floater aligns
   with it and is pulled into the rotor with about 14× its own weight. *Spinning up with
   the floater already near the rotor always fails* (0 of 48 simulated trials across both
   layouts). Bringing the vessel toward an **already spinning** rotor captured it in 5 of 5
   trials (overhead) and 4 of 4 (bottom drive, 45 Hz) (Fig. 5).
5. **Controlled landing.** Ramping 200 → 150 Hz over 2 s moves the equilibrium past the
   point of peak attraction, and the floater settles gently onto the vessel floor. Ramping
   further down, to 100 Hz or less, while the vessel is still close pulls the floater up into
   the shroud.

## 6. Energy

The power comes from the motor and is dissipated in the fluid by the floater's wobble.
At 200 Hz in water:
* the floater's body angular velocity is |ω| = 322 rad/s;
* its mean rotation about the vertical is ω_z = Ω sin²β ≈ 83 rad/s (≈ 790 rpm);
* the dissipated power is ≈ 1 mW (rising to 2 mW at 240 Hz).

That is about 50 W m⁻³ in a 20 mL vial, inside the usual 10–1000 W m⁻³ range for gentle
bioprocess mixing. It is not a vortex mixer. The magnetic torque available
(m₂|B| ≈ 0.12 A m² × 10 mT ≈ 1.2 mN m) is roughly 10× the drag torque, so the phase lag is
only 0.15°. Mixing power scales roughly as Ω³R⁵, so larger floaters and rotors gain quickly.
The motor itself mostly works against air drag on the hub and bearing friction, a few watts.

## 7. Assumptions that must hold (and how each is tested)

| Assumption | Risk | Test |
|---|---|---|
| Rigid magnetisation, no eddy currents | NdFeB resistivity ~1.5 µΩ m; Hermansen et al. found eddy effects negligible | Same levitation height in air and water at equal f (sim: 3.70 vs 3.62 cm at 200 Hz, α = 10°) |
| Dipole field of the rotor | Cylinder L/D = 0.83 rather than 0.866, plus steel in the motor 25 mm away | Measure the depth-vs-f curve. A uniform offset means a moment or tilt error; a wrong slope means a model error |
| Quasi-steady drag laws | Wobble at 200 Hz in a boundary-layer regime; correlation within ±30% | Bobbing decay time (prediction 3.0 s in water) |
| Fluid at rest in the lab | Swirl builds up in small vessels and changes the drag terms (not modelled in `labsim`) | Dye streaks; compare the depth just after capture with the depth after 5 min |
| Rotor speed stable to < 1 Hz | Depth gradient ≈ −0.02 cm/Hz at 200 Hz | Closed-loop firmware with Hall tachometer |
