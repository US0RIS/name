"""Adversarial robustness battery for the design point (overhead drive, water, 200 Hz,
alpha = 10 deg, 6 mm N42 sphere floater, 3/4" x 5/8" N42 cylinder rotor).
Each line: perturbation -> equilibrium depth, tilt, slowest decay rate (negative = stable).
Nothing is tuned per case: the same solver and stability criterion are used throughout."""
import numpy as np, json, copy
from rotframe import System, CylinderRotor, equilibria, MU0

def base(f=200, al=10.0, Br=1.30, **kw):
    s = System(D_rotor=0.0205, D_float=0.006, f=f, alpha_deg=al, Br=Br, rho_fluid=1000, mu_fluid=1e-3, **kw)
    return s

def report(name, s, side=-1, store=None):
    eqs = [e for e in equilibria(s, side=side, zmin=0.022, zmax=0.12, n=180) if e['tilt'] < 50]
    st = [e for e in eqs if e['maxre'] < 0]
    if st:
        e = min(st, key=lambda e: abs(e['r'][2]))
        line = f"{name:58s} STABLE   depth {-e['r'][2]*100:5.2f} cm  xy-offset {np.hypot(*e['r'][:2])*1e3:5.2f} mm  tilt {e['tilt']:5.1f}°  slowest decay {-e['maxre']:6.3f} 1/s"
        res = dict(stable=True, depth_cm=float(-e['r'][2]*100), offset_mm=float(np.hypot(*e['r'][:2])*1e3), decay=float(-e['maxre']))
    elif eqs:
        e = min(eqs, key=lambda e: e['maxre'])
        line = f"{name:58s} UNSTABLE depth {-e['r'][2]*100:5.2f} cm  growth {e['maxre']:+.3f} 1/s"
        res = dict(stable=False, depth_cm=float(-e['r'][2]*100), growth=float(e['maxre']))
    else:
        line = f"{name:58s} NO EQUILIBRIUM"
        res = dict(stable=False)
    print(line, flush=True)
    if store is not None: store[name] = res

R = {}
report("baseline: dipole rotor (as in the design chart)", base(), store=R)

# 1. realistic magnetic model of the rotor (exact finite cylinder, 3/4" x 5/8")
s = base(); s.cyl = CylinderRotor(0.01905, 0.01588, 1.30, 10.0); report("exact finite-cylinder rotor field", s, store=R)

# 2. manufacturing tolerances
for al in (8.0, 12.0):
    s = base(al=al); s.cyl = CylinderRotor(0.01905, 0.01588, 1.30, al); report(f"cylinder rotor, tilt {al:.0f}° (±2° holder/magnetisation error)", s, store=R)
for Br in (1.22, 1.38):
    s = base(Br=Br); s.cyl = CylinderRotor(0.01905, 0.01588, Br, 10.0); report(f"cylinder rotor, Br {Br} T (N38 .. N50 spread)", s, store=R)
s = base(); s.m2 *= 1.08/1.30; report("floater Br 1.08 T (cheap N35 sphere, weaker)", s, store=R)
for e in (0.1e-3, 0.3e-3):
    s = base(); s.rotor_offset = np.array([e, 0, 0]); report(f"rotor eccentricity {e*1e3:.1f} mm", s, store=R)

# 3. motor iron above the rotor: image dipole (-mx,-my,+mz) x 0.3 at +80 mm (upper bound)
s = base(); m = s.m_rot.copy(); s.extra_dipoles = [(0.3*np.array([-m[0], -m[1], m[2]]), np.array([0, 0, 0.080]))]
report("motor stator iron (30% image dipole at +80 mm)", s, store=R)

# 4. eddy currents in the floater: k = (2 pi/15) sigma a^5 (low-frequency sphere), and x10
sig = 1/1.5e-6; k0 = 2*np.pi/15*sig*(0.003)**5
for mult in (1, 10):
    s = base(); s.k_eddy = mult*k0; report(f"floater eddy currents x{mult} (k={mult*k0:.2e} N m s/T^2)", s, store=R)

# 5. realistic damping uncertainty
for ds in (0.3, 3.0):
    s = base(); s.drag_scale = ds; report(f"all fluid drag x{ds}", s, store=R)

# 6. fluid swirl spun up by the floater (mean body rotation about z ~ 83 rad/s)
for sw in (10.0, 40.0, 83.0, -40.0):
    s = base(); s.swirl = sw; report(f"fluid swirl {sw:+.0f} rad/s (co-rotating {'+' if sw>0 else '-'})", s, store=R)

# 7. combined worst-ish case
s = base(al=8.0, Br=1.22); s.cyl = CylinderRotor(0.01905, 0.01588, 1.22, 8.0); s.k_eddy = k0; s.swirl = 40.0; s.drag_scale = 0.5
m = s.m_rot.copy(); s.extra_dipoles = [(0.3*np.array([-m[0], -m[1], m[2]]), np.array([0, 0, 0.080]))]; s.rotor_offset = np.array([0.2e-3, 0, 0])
report("COMBINED: cyl 8°, Br1.22, iron, eddy, swirl 40, drag x0.5", s, store=R)

# 8. other frequencies with the exact cylinder model
for f in (180, 240):
    s = base(f=f); s.cyl = CylinderRotor(0.01905, 0.01588, 1.30, 10.0); report(f"exact cylinder, {f} Hz", s, store=R)
json.dump(R, open("adversarial.json", "w"), indent=1)
