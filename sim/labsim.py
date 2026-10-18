"""Lab-frame nonlinear simulation with spin-up, vessel floor/wall contact and fluid drag.
Reduced rigid-body state for a sphere (isotropic inertia, axisymmetric dipole):
   y = [r(3), v(3), m_hat(3), w(3), phi_rotor]
Contact: floor plane z = zf (floater below the rotor: floor under floater) or ceiling
(floater above rotor: vessel floor at z = zf, floater above it), cylindrical wall radius Rw.
"""
import numpy as np
from numba import njit

MU0 = 4e-7*np.pi

@njit(cache=True)
def dB(m, r):
    rn = np.sqrt(r[0]**2+r[1]**2+r[2]**2); rh = r/rn
    return MU0/(4*np.pi)*(3*np.dot(m, rh)*rh - m)/rn**3

@njit(cache=True)
def dF(m1, m2, r):
    rn = np.sqrt(r[0]**2+r[1]**2+r[2]**2); rh = r/rn
    a = np.dot(m1, rh); b = np.dot(m2, rh)
    return 3*MU0/(4*np.pi*rn**4)*(a*m2 + b*m1 + np.dot(m1, m2)*rh - 5*a*b*rh)

# parameter vector indices
# 0 m_rotor, 1 alpha, 2 Omega_target, 3 t_ramp, 4 m_static, 5 z_static,
# 6 m2, 7 Mi(inertial mass), 8 I, 9 W(net weight N, + = -z), 10 c1, 11 c2, 12 rho_f, 13 mu_f, 14 R (hydro radius)
# 15 floor z (contact plane), 16 floor side (+1: floater above plane, -1: floater below plane), 17 wall radius
# 18 contact stiffness, 19 contact damping, 20 friction coeff, 21 gx (lateral gravity fraction, tilt)
# 22 rotor radius (collision), 23 kick time, 24 kick dv, 25 floor velocity (m/s), 26 floor travel time (s)

@njit(cache=True)
def omega_t(t, P):
    # optional speed change: from P[27] (s) to P[28] (s) go linearly to P[29] (rad/s)
    if P[28] > 0 and t > P[27]:
        if t >= P[28]:
            return P[29]
        return P[2] + (P[29]-P[2])*(t-P[27])/(P[28]-P[27])
    if t < P[3]:
        return P[2]*t/P[3]
    return P[2]*(1.0 + P[30]*np.sin(2*np.pi*P[31]*t))      # optional speed ripple

@njit(cache=True)
def rot_drag(w, P):
    wn = np.sqrt(w[0]**2+w[1]**2+w[2]**2)
    if wn == 0.0:
        return np.zeros(3)
    if P[12] == 0.0:
        return -8*np.pi*P[13]*P[14]**3*w
    nu = P[13]/P[12]
    Re = wn*P[14]**2/nu
    CM = 64.0/(3*Re) + 12.2/np.sqrt(Re)
    M = 0.5*P[12]*wn**2*P[14]**5*CM
    return -M*w/wn

@njit(cache=True)
def deriv(t, y, P):
    r = y[0:3]; v = y[3:6]; mh = y[6:9]; w = y[9:12]; ph = y[12]
    al = P[1]
    m1 = P[0]*np.array([np.cos(al)*np.cos(ph), np.cos(al)*np.sin(ph), np.sin(al)])
    m2v = P[6]*mh
    F = dF(m1, m2v, r)
    B = dB(m1, r)
    if P[4] != 0.0:
        ms = np.array([0.0, 0.0, P[4]])
        rs = r - np.array([0.0, 0.0, P[5]])
        F += dF(ms, m2v, rs)
        B += dB(ms, rs)
    tau = np.cross(m2v, B)
    # weight (with optional tilt of the apparatus -> lateral component)
    F[2] -= P[9]*np.sqrt(1 - P[21]**2)
    F[0] -= P[9]*P[21]
    vn = np.sqrt(v[0]**2+v[1]**2+v[2]**2)
    F -= P[10]*v + P[11]*vn*v
    tau += rot_drag(w, P)
    # contacts
    R = P[14]
    zf = P[15] + P[25]*min(t, P[26])
    pen = 0.0
    if P[16] < 0:   # floater above floor plane? -1 => floater must stay above z=zf (floor below)
        pen = (zf + R) - r[2]
        nvec = np.array([0.0, 0.0, 1.0])
    else:           # floater must stay below plane z=zf (ceiling above)
        pen = r[2] - (zf - R)
        nvec = np.array([0.0, 0.0, -1.0])
    if pen > 0:
        vnorm = np.dot(v, nvec) - (P[25] if t < P[26] else 0.0)*nvec[2]
        N = P[18]*pen - P[19]*vnorm
        if N < 0: N = 0.0
        # slip velocity of contact point
        cp = -R*nvec
        vs = v + np.cross(w, cp)
        vs = vs - np.dot(vs, nvec)*nvec
        sn = np.sqrt(vs[0]**2+vs[1]**2+vs[2]**2)
        Ff = -P[20]*N*vs/np.sqrt(sn**2 + 1e-6)
        F += N*nvec + Ff
        tau += np.cross(cp, Ff)
    rho = np.sqrt(r[0]**2 + r[1]**2)
    penw = rho + R - P[17]
    if penw > 0 and rho > 0:
        nvec = -np.array([r[0]/rho, r[1]/rho, 0.0])
        vnorm = np.dot(v, nvec)
        N = P[18]*penw - P[19]*vnorm
        if N < 0: N = 0.0
        cp = -R*nvec
        vs = v + np.cross(w, cp); vs = vs - np.dot(vs, nvec)*nvec
        sn = np.sqrt(vs[0]**2+vs[1]**2+vs[2]**2)
        Ff = -P[20]*N*vs/np.sqrt(sn**2 + 1e-6)
        F += N*nvec + Ff
        tau += np.cross(cp, Ff)
    out = np.empty(13)
    out[0:3] = v
    out[3:6] = F/P[7]
    out[6:9] = np.cross(w, mh)
    out[9:12] = tau/P[8]
    out[12] = omega_t(t, P)
    return out

@njit(cache=True)
def run(y0, P, T, dt, nsave):
    n = int(T/dt); every = max(1, n//nsave)
    ns = n//every + 2
    Y = np.empty((ns, 13)); TT = np.empty(ns)
    y = y0.copy(); t = 0.0; k = 0
    Y[0] = y; TT[0] = 0.0
    kicked = False
    for i in range(n):
        if (not kicked) and P[23] > 0 and t >= P[23]:
            y[3] += P[24]; kicked = True
        k1 = deriv(t, y, P); k2 = deriv(t+dt/2, y+dt/2*k1, P)
        k3 = deriv(t+dt/2, y+dt/2*k2, P); k4 = deriv(t+dt, y+dt*k3, P)
        y = y + dt/6*(k1+2*k2+2*k3+k4)
        nm = np.sqrt(y[6]**2+y[7]**2+y[8]**2); y[6:9] /= nm
        t += dt
        if (i+1) % every == 0:
            k += 1; Y[k] = y; TT[k] = t
        rn = np.sqrt(y[0]**2+y[1]**2+y[2]**2)
        if rn < P[22] + P[14]:     # hit the rotor housing
            k += 1; Y[k] = y; TT[k] = t
            return TT[:k+1], Y[:k+1], 1
    return TT[:k+1], Y[:k+1], 0

def build(sysobj, t_ramp=0.5, floor_z=-0.05, floor_side=-1, wall_R=0.04, k_c=2e4, c_c=2.0,
          mu_c=0.3, tilt_deg=0.0, rotor_R=0.0095+0.004, kick_t=0.0, kick_dv=0.0, floor_v=0.0, floor_T=0.0, ramp2=(0.0, 0.0, 0.0), ripple=(0.0, 0.0)):
    s = sysobj
    m_r = np.linalg.norm(s.m_rot); al = np.arctan2(s.m_rot[2], s.m_rot[0])
    P = np.array([m_r, al, s.Om, t_ramp, s.m_s, s.z_s, s.m2, s.Mi, s.I, s.W, s.c1, s.c2,
                  s.rho_f, s.mu_f, s.R, floor_z, floor_side, wall_R, k_c, c_c, mu_c,
                  np.sin(np.radians(tilt_deg)), rotor_R, kick_t, kick_dv, floor_v, floor_T, ramp2[0], ramp2[1], ramp2[2], ripple[0], ripple[1]])
    return P
