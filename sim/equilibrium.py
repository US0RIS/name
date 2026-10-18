"""Synchronous on-axis equilibria of the floater in the rotating frame.
Floater on the spin axis at z (z<0: below rotor).  Its moment m_hat is fixed in the rotating
frame, its lab angular velocity is w = Omega z_hat + s m_hat with s = p - Omega*m_z and
p = w.m_hat the (conserved, or drag-zeroed) spin about its own magnetic axis.
Torque balance:  m2 (m_hat x B) = I s Omega (z_hat x m_hat).
"""
import numpy as np
from scipy.optimize import brentq
from dipole_rt import MU0, sphere_params, dip_force

def onaxis_state(z, P, p=0.0, branch=+1):
    m1, Om, al, Bz, m2, mass, I = P[0], P[1], P[2], P[3], P[4], P[5], P[6]
    m1v = m1*np.array([np.cos(al), 0, np.sin(al)])
    r = np.array([0, 0, z])
    rn = abs(z); rh = r/rn
    B = MU0/(4*np.pi)*(3*np.dot(m1v, rh)*rh - m1v)/rn**3 + np.array([0, 0, Bz])
    # fixed point iteration for theta: m_hat || (m2 B + I s Om z) with sign chosen by branch
    mh = np.array([0, 0, branch*1.0])
    for _ in range(500):
        s = p - Om*mh[2]
        V = m2*B + I*s*Om*np.array([0, 0, 1.0])
        cand = V/np.linalg.norm(V)
        # choose the root continuously connected to the requested branch
        if np.dot(cand, mh) < 0: cand = -cand
        mh_new = 0.5*mh + 0.5*cand
        mh_new /= np.linalg.norm(mh_new)
        if np.linalg.norm(mh_new-mh) < 1e-13: break
        mh = mh_new
    F = dip_force(m1v, m2*mh, r)
    return mh, F, B

def find_eq(P, branch=+1, p=0.0, zmin=-0.012, zmax=-0.15, g_include=True):
    mass, geff = P[5], P[7]
    zs = np.linspace(zmin, zmax, 400)
    Fz = np.array([onaxis_state(z, P, p, branch)[1][2] - (mass*geff if g_include else 0) for z in zs])
    roots = []
    for i in range(len(zs)-1):
        if np.sign(Fz[i]) != np.sign(Fz[i+1]):
            zr = brentq(lambda z: onaxis_state(z, P, p, branch)[1][2] - (mass*geff if g_include else 0), zs[i], zs[i+1])
            # stability along z: dFz/dz < 0 needed (for z coordinate)
            h = 1e-6
            k = (onaxis_state(zr+h, P, p, branch)[1][2]-onaxis_state(zr-h, P, p, branch)[1][2])/(2*h)
            roots.append((zr, k))
    return roots, zs, Fz

if __name__ == "__main__":
    from dipole_rt import make_P
    for D2 in [0.006, 0.010]:
        for al in [2, 5, 10, 20]:
            for f in [100, 200, 300]:
                P = make_P(D2=D2, f=f, alpha_deg=al)
                roots, zs, Fz = find_eq(P, branch=+1)
                s = ", ".join(f"z={z*100:.2f}cm k={k:+.3g}" for z, k in roots)
                print(f"D2={D2*1e3:.0f} al={al:2d} f={f}: {s}")
