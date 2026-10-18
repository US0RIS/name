"""Speed ripple of the rotor (ESC / control loop) vs the ~7 Hz vertical trap mode."""
import numpy as np, json
from rotframe import System, equilibria
from labsim import build, run
out = {}
for al in (12.0,):
    s = System(D_rotor=0.0205, D_float=0.006, f=200, alpha_deg=al, Br=1.30, rho_fluid=1000, mu_fluid=1e-3)
    e = [e for e in equilibria(s, side=-1, zmin=0.022) if e['tilt'] < 50 and e['maxre'] < 0][0]
    lowf = [abs(x.imag)/2/np.pi for x in e['ev'] if 1 < abs(x.imag) < 300]
    print(f"alpha {al}: trap low-frequency modes (Hz): {np.round(sorted(set(np.round(lowf, 2))), 2)}")
    y0 = np.zeros(13); y0[0:3] = e['r']; y0[6:9] = e['mh']; y0[9:12] = e['w']
    for amp in (0.005, 0.01):
        for fr in (2.0, round(min(lowf), 2), 30.0):
            P = build(s, t_ramp=1e-6, floor_z=-0.07, floor_side=-1, wall_R=0.04, ripple=(amp, fr))
            T, Y, hit = run(y0, P, 8.0, 2.5e-6, 4000)
            n = len(T)//3; z = Y[-n:, 2]
            lost = hit or T[-1] < 7.99 or z.min() < -0.07 + s.R + 1e-3
            key = f"a{al}_amp{amp}_f{fr}"
            out[key] = dict(lost=bool(lost), pp_mm=float(np.ptp(z)*1e3))
            print(f"   ripple ±{amp*100:.2f}% ({amp*200:.1f} Hz) at {fr:5.2f} Hz -> {'LOST' if lost else f'p-p depth {np.ptp(z)*1e3:.2f} mm'}", flush=True)
json.dump(out, open('ripple.json', 'w'), indent=1)
