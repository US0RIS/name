import numpy as np, sys
from rotframe import System
from labsim import build, run
rng = np.random.default_rng(2)
s = System(D_float=0.006, f=200, alpha_deg=10, rho_fluid=1000, mu_fluid=1e-3)
def trial(floor_start, floor_end, approach_T, Tsim=5.0, seed=None):
    v = (floor_end - floor_start)/approach_T if approach_T > 0 else 0.0
    P = build(s, t_ramp=1e-4, floor_z=floor_start, floor_side=-1, wall_R=0.03, floor_v=v, floor_T=approach_T)
    y0 = np.zeros(13)
    y0[0:2] = rng.normal(0, 0.002, 2)
    y0[2] = floor_start + s.R
    mh = rng.normal(size=3); mh /= np.linalg.norm(mh); y0[6:9] = mh
    T, Y, hit = run(y0, P, Tsim, 2e-6, 5000)
    n = len(T)//5
    zend = Y[-n:, 2]
    fz = floor_end + s.R
    lev = (not hit) and zend.min() > fz + 1e-3 and np.ptp(zend) < 2e-3
    return ("LEV %.1fmm" % (zend.mean()*1e3)) if lev else ("HIT" if hit else "floor"), T, Y
if __name__ == "__main__":
    print("A) rotor already at speed, floater released on floor at distance d")
    for fz in [-0.030, -0.034, -0.038, -0.042, -0.046, -0.050, -0.060]:
        print(f"  floor {fz*100:.1f} cm:", [trial(fz, fz, 0.0, 3.0)[0] for _ in range(5)], flush=True)
    print("B) vessel raised slowly toward spinning rotor (floor from -8 cm to -4.5 cm in 3 s)")
    print("  ", [trial(-0.08, -0.045, 3.0, 6.0)[0] for _ in range(5)])
