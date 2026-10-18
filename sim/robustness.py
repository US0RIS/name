"""Lab-frame robustness tests starting from the levitated state (overhead layout, water)."""
import numpy as np, json, sys
from rotframe import System, find_fixed_point, onaxis_scan, equilibria
from labsim import build, run

def eq_state(s):
    e = [e for e in equilibria(s, side=-1) if e['tilt'] < 60 and e['maxre'] < 0][0]
    # rotating frame at t=0 coincides with lab frame
    y0 = np.zeros(13); y0[0:3] = e['r']; y0[6:9] = e['mh']; y0[9:12] = e['w']
    return e, y0

test = sys.argv[1]
s = System(D_float=0.006, f=200, alpha_deg=10, rho_fluid=1000, mu_fluid=1e-3)
e, y0 = eq_state(s)
out = {}
if test == 'tilt':
    for tilt in [0, 2, 5, 10, 15, 20, 30]:
        P = build(s, t_ramp=1e-6, floor_z=-0.06, floor_side=-1, wall_R=0.04, tilt_deg=tilt)
        T, Y, hit = run(y0, P, 4.0, 2e-6, 2000)
        n = len(T)//4
        ok = (not hit) and T[-1] > 3.99 and Y[-1, 2] > -0.06 + s.R + 1e-3
        out[tilt] = dict(ok=bool(ok), x=float(Y[-n:,0].mean()), z=float(Y[-n:,2].mean()))
        print("tilt", tilt, out[tilt], flush=True)
if test == 'kick':
    for dv in [0.05, 0.1, 0.2, 0.3, 0.5, 0.8]:
        P = build(s, t_ramp=1e-6, floor_z=-0.06, floor_side=-1, wall_R=0.04, kick_t=0.2, kick_dv=dv)
        T, Y, hit = run(y0, P, 3.0, 2e-6, 2000)
        ok = (not hit) and T[-1] > 2.99 and abs(Y[-1,2]-e['r'][2]) < 1e-3
        out[dv] = bool(ok); print("lateral kick dv", dv, "m/s ->", "recovered" if ok else ("hit rotor" if hit else "lost"), flush=True)
if test == 'rampdown':
    for f_end, Tr in [(150, 2.0), (120, 3.0), (100, 3.0), (80, 4.0), (50, 4.0)]:
        P = build(s, t_ramp=1e-6, floor_z=-0.05, floor_side=-1, wall_R=0.04, ramp2=(0.5, 0.5+Tr, 2*np.pi*f_end))
        T, Y, hit = run(y0, P, 1.0+Tr, 2e-6, 3000)
        zf = Y[-1,2]
        st = "HIT ROTOR" if hit else ("landed on floor" if zf < -0.05 + s.R + 5e-4 else f"still levitating z={zf*1e3:.1f}mm")
        out[f_end] = st; print(f"ramp 200->{f_end} Hz in {Tr}s:", st, flush=True)
json.dump({str(k): v for k, v in out.items()}, open(f'robust_{test}.json', 'w'), indent=1)
