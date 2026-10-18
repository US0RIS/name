import numpy as np, json, itertools, time
from rotframe import System, equilibria
rows = []
t0 = time.time()
for Dr, Df, f, al in itertools.product([0.019, 0.0254], [0.005, 0.006, 0.008, 0.010], [100, 150, 200, 250, 300], [5, 10, 15, 20, 30]):
    s = System(D_rotor=Dr, D_float=Df, f=f, alpha_deg=al, rho_fluid=1000, mu_fluid=1e-3)
    try:
        eqs = equilibria(s, side=-1, zmin=Dr/2+Df/2+0.002, zmax=0.15, n=200)
    except Exception as ex:
        continue
    for e in eqs:
        if e['tilt'] < 60:
            rows.append(dict(Dr=Dr, Df=Df, f=f, al=al, z=float(e['r'][2]), tilt=float(e['tilt']), maxre=float(e['maxre'])))
json.dump(rows, open('sweep_design.json', 'w'), indent=0)
print("done", len(rows), "eq in", time.time()-t0, "s")
stable = [r for r in rows if r['maxre'] < -0.05]
stable.sort(key=lambda r: r['z'])
for r in stable[:25]:
    print(r)
