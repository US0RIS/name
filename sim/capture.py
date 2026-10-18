import numpy as np, sys
from rotframe import System
from labsim import build, run
rng = np.random.default_rng(1)
# Overhead layout: rotor at origin, floater hangs below in water; vessel floor at z=floor_z
s = System(D_float=0.006, f=200, alpha_deg=10, rho_fluid=1000, mu_fluid=1e-3)
print("net weight mN", s.W*1e3)
for floor_z in [-0.036, -0.040, -0.044, -0.048]:
    res = []
    for trial in range(6):
        P = build(s, t_ramp=0.5, floor_z=floor_z, floor_side=-1, wall_R=0.03)
        y0 = np.zeros(13)
        y0[0:2] = rng.normal(0, 0.003, 2)
        y0[2] = floor_z + s.R
        mh = rng.normal(size=3); mh /= np.linalg.norm(mh)
        y0[6:9] = mh
        T, Y, hit = run(y0, P, 4.0, 2e-6, 4000)
        n = len(T)//5
        zend = Y[-n:, 2]; xy = np.hypot(Y[-n:,0], Y[-n:,1])
        lev = (not hit) and zend.min() > floor_z + s.R + 1e-3 and np.ptp(zend) < 2e-3
        res.append(("LEV z=%.1fmm" % (zend.mean()*1e3)) if lev else ("HIT" if hit else "floor z=%.1f" % (zend.mean()*1e3)))
    print(f"floor at {floor_z*100:.1f} cm:", res, flush=True)
