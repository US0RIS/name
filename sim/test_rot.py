import numpy as np
from rotframe import *
for label, kw in [("air", {}), ("water", dict(rho_fluid=1000, mu_fluid=1e-3)), ("glycerol", dict(rho_fluid=1260, mu_fluid=1.0))]:
    s = System(D_float=0.006, f=200, alpha_deg=10, **kw)
    for side in (-1, +1):
        for e in equilibria(s, side=side):
            ev = e['ev']; idx = np.argsort(-ev.real)
            print(f"{label:8s} side={side:+d} z={e['r'][2]*100:+.2f}cm xy=({e['r'][0]*1e3:.2f},{e['r'][1]*1e3:.2f})mm tilt={e['tilt']:.1f} maxRe={e['maxre']:+.3e} resid={e['resid']:.1e}")
            print("      top eig:", np.round(ev[idx[:4]], 3))
