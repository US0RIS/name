import numpy as np
from dipole_rt import *
from equilibrium import onaxis_state, find_eq
from check_eq import sim_from_eq
P = make_P(D2=0.006, f=200, alpha_deg=10)
roots,_,_ = find_eq(P); z = [r for r in roots if r[1]<0][0][0]
mh,F,B = onaxis_state(z,P,0,+1)
print("zeq", z, "m_hat", mh, "tilt deg", np.degrees(np.arccos(mh[2])), "|B| mT", np.linalg.norm(B)*1e3)
for label, kw in [("air, no damping", dict()),
                  ("air, light damping", dict(c_lin=1e-4, c_rot=1e-10)),
                  ("water", dict(rho_fluid=1000, mu_fluid=1e-3, c_quad='auto')),
                  ("glycerol-water 50%", dict(rho_fluid=1130, mu_fluid=6e-3, c_quad='auto')),
                  ("glycerol", dict(rho_fluid=1260, mu_fluid=1.0, c_quad='auto'))]:
    P = make_P(D2=0.006, f=200, alpha_deg=10, **kw)
    roots,_,_ = find_eq(P)
    st = [r for r in roots if r[1]<0]
    if not st: print(label, "no stable-z root", roots); continue
    z = st[0][0]
    Tt, Y = sim_from_eq(P, z, T=4.0, dz=1e-3, dx=1e-3, dtilt=0.05)
    r = Y[:,:3]; n=len(Tt)//4
    print(f"{label:22s} zeq={z*100:.2f} t_end={Tt[-1]:.2f}  last-quarter: z=[{r[-n:,2].min()*100:.2f},{r[-n:,2].max()*100:.2f}]cm  |xy|max={np.hypot(r[-n:,0],r[-n:,1]).max()*1e3:.3f}mm")
