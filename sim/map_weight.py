import numpy as np
from rotframe import *
# fixed floater dynamics (6 mm NdFeB), vary the net body force W artificially (N; + = toward -z)
base = System(D_float=0.006, f=200, alpha_deg=10, rho_fluid=1000, mu_fluid=1e-3)
W0 = base.mass*9.81
print("magnet weight in air (mN):", W0*1e3)
for side in (+1, -1):
    print("side", side)
    for ratio in [-3, -2, -1.5, -1, -0.5, -0.2, 0, 0.2, 0.5, 1.0, 1.5, 2, 3]:
        base.W = ratio*W0
        eqs = equilibria(base, side=side)
        out = []
        for e in eqs:
            if e['tilt'] < 60:
                out.append(f"z={e['r'][2]*100:+.2f} tilt={e['tilt']:.0f} maxRe={e['maxre']:+.2f}")
        print(f"  W/W0={ratio:+.1f}: ", " | ".join(out))
