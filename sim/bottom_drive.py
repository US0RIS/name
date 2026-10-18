"""Bottom-drive variant (rotor under the vessel, floater above it): the floater must be
roughly neutrally buoyant, which needs a shell.  The shell adds inertia, which (d0^3 ~ m2/(I W^2))
pulls the trap closer, so the rotor must run slower.  Evaluate PETG-shell and foam-shell floaters."""
import numpy as np, json
from rotframe import System, equilibria
DR = 0.0205
cases = {
  # name: (extra mass g, extra I g mm^2, hydrodynamic diameter m)
  "bare 6mm (reference)": (0.0, 0.0, 0.006),
  "PETG hollow shell 16mm (CAD: 1.26 g, 37 g mm^2)": (1.257, 37.0, 0.016),
  "EPS/PU foam sphere 14mm, rho=0.15 (0.19 g, ~4.1 g mm^2)": (0.15e-3*np.pi/6*(14**3-6**3), 0.4*0.15e-3*np.pi/6*(14**5-6**5)/4, 0.014),
}
out = {}
for name, (dm, dI, Dh) in cases.items():
    print(name, flush=True)
    out[name] = []
    for f in [40, 50, 60, 70, 80, 100, 120, 150, 200]:
        s = System(D_rotor=DR, D_float=0.006, f=f, alpha_deg=10, rho_fluid=1000, mu_fluid=1e-3, Br=1.30)
        s.mass += dm*1e-3; s.I += dI*1e-9
        s.Vtot = np.pi/6*Dh**3; s.R = Dh/2
        s.Mi = s.mass + 0.5*1000*s.Vtot
        s.W = (s.mass - 1000*s.Vtot)*9.81
        s.c1 = 6*np.pi*1e-3*s.R; s.c2 = 0.5*1000*0.47*np.pi*s.R**2; s.cr = 8*np.pi*1e-3*s.R**3
        W0 = 0.848e-3*9.81
        try:
            eqs = [e for e in equilibria(s, side=+1, zmin=0.020, zmax=0.12, n=200) if e['tilt'] < 60]
        except Exception as ex:
            eqs = []
        st = [f"z=+{e['r'][2]*100:.2f}cm maxRe={e['maxre']:+.2f}" for e in eqs]
        out[name].append(dict(f=f, W_over_W0=s.W/W0, eq=[dict(z=float(e['r'][2]), maxre=float(e['maxre'])) for e in eqs]))
        print(f"   f={f:3d}Hz  W/W0={s.W/W0:+.2f}: ", " | ".join(st), flush=True)
json.dump(out, open('bottom_drive.json', 'w'), indent=1)
