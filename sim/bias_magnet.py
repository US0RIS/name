"""Replace the hard-to-build rotor tilt (alpha) by a stationary, adjustable axial bias magnet
mounted coaxially ABOVE the rotor (overhead layout, floater hangs below)."""
import numpy as np
from rotframe import System, equilibria, sphere
# bias magnet: N52 disc approximated as dipole; moment for a 12x6 mm disc
def disc_moment(D, H, Br=1.32):
    return Br*np.pi*(D/2)**2*H/(4e-7*np.pi)
print("rotor 19mm sphere moment", sphere(0.019)[0])
for (D, H) in [(0.010, 0.005), (0.012, 0.006), (0.015, 0.008), (0.020, 0.010)]:
    ms = disc_moment(D, H)
    for zs in [0.020, 0.025, 0.030, 0.040]:
        s = System(D_float=0.006, f=200, alpha_deg=0.0, m_static=ms, z_static=zs, rho_fluid=1000, mu_fluid=1e-3)
        eqs = [e for e in equilibria(s, side=-1, n=200) if e['tilt'] < 60]
        st = [f"z={e['r'][2]*100:.2f}cm maxRe={e['maxre']:+.2f}" for e in eqs]
        print(f"bias disc {D*1e3:.0f}x{H*1e3:.0f}mm (m={ms:.2f}) at z_s=+{zs*100:.1f}cm: ", " | ".join(st), flush=True)
