import numpy as np, json
from rotframe import System, CylinderRotor, equilibria
from adversarial import base, report

def stable_at(s):
    eqs = [e for e in equilibria(s, side=-1, zmin=0.022, zmax=0.12, n=150) if e['tilt'] < 50]
    return any(e['maxre'] < 0 for e in eqs)

def swirl_threshold(mk):
    lo, hi = 0.0, 80.0
    for _ in range(9):
        mid = 0.5*(lo + hi); s = mk(); s.swirl = mid
        if stable_at(s): lo = mid
        else: hi = mid
    return lo

out = {}
print("== swirl threshold (rad/s) for several design points ==")
for (f, al, mu, rho, label) in [(200, 10, 1e-3, 1000, "water 200Hz a10"), (200, 12, 1e-3, 1000, "water 200Hz a12"),
                                (180, 15, 1e-3, 1000, "water 180Hz a15"), (200, 10, 6e-3, 1130, "50% glycerol 200Hz a10"),
                                (200, 10, 0.05, 1200, "80% glycerol 200Hz a10")]:
    mk = lambda f=f, al=al, mu=mu, rho=rho: System(D_rotor=0.0205, D_float=0.006, f=f, alpha_deg=al, Br=1.30, rho_fluid=rho, mu_fluid=mu)
    th = swirl_threshold(mk); out[label] = th
    print(f"  {label:26s}: stable for |swirl| < {th:5.1f} rad/s ({th*60/2/np.pi:4.0f} rpm)", flush=True)

# Ekman spin-down estimate of the bulk swirl the floater can sustain in an 80 mm jar, 22 mm deep
s = base(); e = [e for e in equilibria(s, side=-1, zmin=0.022) if e['maxre'] < 0][0]
tau = s.rot_torque_drag(e['w']); tau_z = abs(tau[2])
Rv, H, nu, rho = 0.0375, 0.022, 1e-6, 1000.0
Ifl = 0.5*rho*np.pi*Rv**4*H
# torque needed to hold solid-body swirl Wf against Ekman-layer spin-down: Ifl*Wf/T_E, T_E = H/sqrt(nu*Wf)
Wf = (tau_z*H/(Ifl*np.sqrt(nu)))**(2/3)
print(f"floater z-torque on fluid {tau_z*1e6:.2f} uN m -> sustainable bulk swirl ~ {Wf:.2f} rad/s (Ekman estimate)")
out["ekman_bulk_swirl_rad_s"] = float(Wf); out["floater_z_torque_uNm"] = float(tau_z*1e6)

print("== tolerance battery at alternative nominal alpha = 14 deg, 200 Hz ==")
R = {}
for al in (12.0, 14.0, 16.0):
    s = base(al=al); s.cyl = CylinderRotor(0.01905, 0.01588, 1.30, al); report(f"cyl, tilt {al:.0f}°, 200 Hz", s, store=R)
for al, f in ((8.0, 230), (8.0, 250)):
    s = base(f=f, al=al); s.cyl = CylinderRotor(0.01905, 0.01588, 1.30, al); report(f"cyl, tilt {al:.0f}°, re-tuned to {f} Hz", s, store=R)
k0 = 2*np.pi/15*(1/1.5e-6)*(0.003)**5
s = base(al=14.0, Br=1.22); s.cyl = CylinderRotor(0.01905, 0.01588, 1.22, 14.0); s.k_eddy = k0; s.swirl = 8.0; s.drag_scale = 0.5
m = s.m_rot.copy(); s.extra_dipoles = [(0.3*np.array([-m[0], -m[1], m[2]]), np.array([0, 0, 0.080]))]; s.rotor_offset = np.array([0.2e-3, 0, 0])
report("COMBINED @a14: Br1.22, iron, eddy, swirl 8, drag x0.5, ecc 0.2", s, store=R)
s = base(al=12.0, Br=1.22); s.cyl = CylinderRotor(0.01905, 0.01588, 1.22, 12.0); s.k_eddy = k0; s.swirl = 8.0; s.drag_scale = 0.5
s.extra_dipoles = [(0.3*np.array([-m[0], -m[1], m[2]]), np.array([0, 0, 0.080]))]; s.rotor_offset = np.array([0.2e-3, 0, 0])
report("COMBINED @a12: Br1.22, iron, eddy, swirl 8, drag x0.5, ecc 0.2", s, store=R)
out["battery_alt"] = R
json.dump(out, open("adversarial2.json", "w"), indent=1)
