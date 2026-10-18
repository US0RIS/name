import numpy as np, json
from rotframe import System
from labsim import build, run
rng = np.random.default_rng(5)
def shell_system(f):
    s = System(D_rotor=0.0205, D_float=0.006, f=f, alpha_deg=10, rho_fluid=1000, mu_fluid=1e-3, Br=1.30)
    s.mass += 1.257e-3; s.I += 37e-9; Dh = 0.016
    s.Vtot = np.pi/6*Dh**3; s.R = Dh/2; s.Mi = s.mass + 0.5*1000*s.Vtot
    s.W = (s.mass - 1000*s.Vtot)*9.81
    s.c1 = 6*np.pi*1e-3*s.R; s.c2 = 0.5*1000*0.47*np.pi*s.R**2
    return s
FLOOR = 0.0245   # inner floor of vessel above rotor centre (m)
res = {}
for f in [45, 60]:
    s = shell_system(f)
    for start in ['floor', 'mid']:
        outc = []
        for k in range(4):
            P = build(s, t_ramp=2.0, floor_z=FLOOR, floor_side=-1, wall_R=0.028, rotor_R=0.0)
            y0 = np.zeros(13)
            y0[0:2] = rng.normal(0, 0.004, 2)
            y0[2] = FLOOR + s.R if start == 'floor' else 0.065
            mh = rng.normal(size=3); mh /= np.linalg.norm(mh); y0[6:9] = mh
            T, Y, hit = run(y0, P, 8.0, 4e-6, 4000)
            n = len(T)//6
            z = Y[-n:, 2]
            lev = z.min() > FLOOR + s.R + 1e-3 and np.ptp(z) < 2e-3
            outc.append(f"LEV z={z.mean()*1e3:.1f}mm" if lev else f"no (z={z.mean()*1e3:.1f})")
        res[f"{f}Hz_{start}"] = outc
        print(f, start, outc, flush=True)
json.dump(res, open('capture_bottom.json','w'), indent=1)
