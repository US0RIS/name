import numpy as np, sys
from dipole_rt import *
from equilibrium import onaxis_state, find_eq

def quat_from_z_to(v):
    v = v/np.linalg.norm(v); z = np.array([0,0,1.0])
    ax = np.cross(z, v); s = np.linalg.norm(ax); c = np.dot(z, v)
    if s < 1e-12: return np.array([1.0,0,0,0]) if c > 0 else np.array([0,1.0,0,0])
    ang = np.arctan2(s, c); ax /= s
    return np.r_[np.cos(ang/2), np.sin(ang/2)*ax]

def sim_from_eq(P, z, p=0.0, T=2.0, dt=2e-6, dz=0.0, dx=0.0, dtilt=0.0, nsave=4000):
    mh, F, B = onaxis_state(z, P, p, +1)
    if dtilt:
        mh = mh + np.array([0, dtilt, 0]); mh /= np.linalg.norm(mh)
    Om = P[1]; s = p - Om*mh[2]
    w = Om*np.array([0,0,1.0]) + s*mh
    y0 = np.zeros(13); y0[0] = dx; y0[2] = z+dz; y0[6:10] = quat_from_z_to(mh); y0[10:13] = w
    return integrate(y0, P, 0.0, T, dt, nsave)

if __name__ == "__main__":
    for (D2, al, f) in [(0.010,10,200),(0.010,5,200),(0.006,10,200),(0.006,20,300),(0.010,20,200)]:
        P = make_P(D2=D2, f=f, alpha_deg=al)
        roots, _, _ = find_eq(P)
        for z, k in roots:
            if k < 0:
                Tt, Y = sim_from_eq(P, z, T=1.0, dz=0.5e-3, dx=0.5e-3, dtilt=0.02)
                r = Y[:, :3]
                print(f"D2={D2*1e3:.0f} al={al} f={f} zeq={z*100:.2f}cm -> t_end={Tt[-1]:.3f}s "
                      f"z range [{r[:,2].min()*100:.2f},{r[:,2].max()*100:.2f}] cm, max|xy|={np.hypot(r[:,0],r[:,1]).max()*1e3:.2f} mm")
