"""Is stability sensitive to the ratio of translational to rotational fluid damping?"""
import numpy as np, json
from rotframe import System, equilibria
scales = [0.1, 0.3, 1.0, 3.0, 10.0]
out = {}
print("rows: translational drag scale; cols: rotational drag scale; entry: slowest decay rate (1/s), negative = UNSTABLE growth")
print("        " + "".join(f"{r:>9}" for r in scales))
for t in scales:
    row = []
    for r in scales:
        s = System(D_rotor=0.0205, D_float=0.006, f=200, alpha_deg=12, Br=1.30, rho_fluid=1000, mu_fluid=1e-3)
        s.drag_scale_t = t; s.drag_scale_r = r
        eqs = [e for e in equilibria(s, side=-1, zmin=0.022, n=150) if e['tilt'] < 50]
        v = -min(e['maxre'] for e in eqs) if eqs else float('nan')
        row.append(v); out[f"t{t}_r{r}"] = v
    print(f"t={t:<5}" + "".join(f"{v:9.3f}" for v in row), flush=True)
json.dump(out, open('drag_ratio.json', 'w'), indent=1)
