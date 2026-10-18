import numpy as np, time, sys
from dipole_rt import *

def q_from_axis_angle(ax, ang):
    ax = np.asarray(ax, float); ax /= np.linalg.norm(ax)
    return np.r_[np.cos(ang/2), np.sin(ang/2)*ax]

def run(P, z0, tilt_deg=3.0, T=2.0, dt=2e-6, w0=None):
    q = q_from_axis_angle([1,0,0], np.pi - np.radians(tilt_deg))   # body z -> nearly lab -z
    y0 = np.zeros(13); y0[2] = z0; y0[6:10] = q
    if w0 is not None: y0[10:13] = w0
    Tt, Y = integrate(y0, P, 0.0, T, dt, 2000)
    return Tt, Y

if __name__ == "__main__":
    for D2 in [0.006, 0.010]:
        for al in [0, 5, 10, 20, 30]:
            for f in [100, 200, 300]:
                row = []
                for z0 in [-0.02, -0.03, -0.04, -0.06]:
                    P = make_P(D2=D2, f=f, alpha_deg=al, c_lin=2e-4, c_rot=2e-9)
                    Tt, Y = run(P, z0, T=1.0)
                    rn = np.linalg.norm(Y[-1,:3])
                    status = 'L' if Tt[-1] > 0.999 else ('C' if rn < 0.05 else 'E')
                    if status == 'L':
                        status += f"{Y[-200:,2].mean()*100:+.1f}"
                    row.append(status)
                print(f"D2={D2*1e3:.0f}mm alpha={al:2d} f={f}: ", row, flush=True)
