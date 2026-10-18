"""Predicted levitation height vs rotor frequency for the as-built rotor
(3/4" x 5/8" N42 cylinder ~ dipole-equivalent sphere D=20.5 mm), floater 6 mm sphere, water."""
import numpy as np, json, sys
from rotframe import System, equilibria
DR = 0.0205
Df = float(sys.argv[1]) if len(sys.argv) > 1 else 0.006
fluid = sys.argv[2] if len(sys.argv) > 2 else 'water'
FL = dict(water=dict(rho_fluid=1000, mu_fluid=1.0e-3), air=dict(rho_fluid=1.2, mu_fluid=1.8e-5),
          gly50=dict(rho_fluid=1130, mu_fluid=6e-3))[fluid]
res = []
for al in [6, 8, 10, 12, 15, 20]:
    for f in range(100, 321, 10):
        s = System(D_rotor=DR, D_float=Df, f=f, alpha_deg=al, Br=1.30, **FL)
        try:
            eqs = equilibria(s, side=-1, zmin=0.020, zmax=0.12, n=220)
        except Exception:
            continue
        for e in eqs:
            if e['tilt'] < 60:
                res.append(dict(al=al, f=f, z=float(e['r'][2]), tilt=float(e['tilt']), maxre=float(e['maxre'])))
    print("alpha", al, "done", flush=True)
json.dump(res, open(f'design_chart_{int(Df*1e3)}mm_{fluid}.json', 'w'))
