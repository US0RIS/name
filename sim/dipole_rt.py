"""Rigid-body simulation of a uniformly magnetised sphere ("floater") in the field of a
spinning uniformly magnetised sphere ("rotor").  For uniformly magnetised spheres the
point-dipole force/torque is exact (outside field of a sphere is exactly dipolar), so the
only modelling assumptions are rigid magnetisation (NdFeB, mu_r~1.05) and the drag laws.

State y = [r(3), v(3), q(4) body->lab quaternion, w(3) lab-frame angular velocity]
Isotropic inertia (sphere) => I dw/dt = torque, no Euler gyroscopic term.
"""
import numpy as np
from numba import njit

MU0 = 4e-7 * np.pi

@njit(cache=True)
def qmul(a, b):
    return np.array([a[0]*b[0]-a[1]*b[1]-a[2]*b[2]-a[3]*b[3],
                     a[0]*b[1]+a[1]*b[0]+a[2]*b[3]-a[3]*b[2],
                     a[0]*b[2]-a[1]*b[3]+a[2]*b[0]+a[3]*b[1],
                     a[0]*b[3]+a[1]*b[2]-a[2]*b[1]+a[3]*b[0]])

@njit(cache=True)
def qrot(q, v):
    # rotate body vector v into lab frame
    w, x, y, z = q
    return np.array([
        (1-2*(y*y+z*z))*v[0] + 2*(x*y-w*z)*v[1] + 2*(x*z+w*y)*v[2],
        2*(x*y+w*z)*v[0] + (1-2*(x*x+z*z))*v[1] + 2*(y*z-w*x)*v[2],
        2*(x*z-w*y)*v[0] + 2*(y*z+w*x)*v[1] + (1-2*(x*x+y*y))*v[2]])

@njit(cache=True)
def dip_field(m, r):
    rn = np.sqrt(r[0]**2+r[1]**2+r[2]**2)
    rh = r/rn
    return MU0/(4*np.pi) * (3*np.dot(m, rh)*rh - m)/rn**3

@njit(cache=True)
def dip_force(m1, m2, r):
    # force on dipole m2 located at r relative to m1
    rn = np.sqrt(r[0]**2+r[1]**2+r[2]**2)
    rh = r/rn
    a = np.dot(m1, rh); b = np.dot(m2, rh)
    return 3*MU0/(4*np.pi*rn**4) * (a*m2 + b*m1 + np.dot(m1, m2)*rh - 5*a*b*rh)

@njit(cache=True)
def rotor_moment(t, P):
    # P: [m1, Omega, alpha(tilt of rotor moment out of the spin plane), Bz_static, ...]
    m1 = P[0]; Om = P[1]; al = P[2]
    return np.array([m1*np.cos(al)*np.cos(Om*t), m1*np.cos(al)*np.sin(Om*t), m1*np.sin(al)])

@njit(cache=True)
def deriv(t, y, P):
    # P layout:
    # 0 m1, 1 Omega, 2 alpha, 3 Bz_static(uniform, T), 4 m2, 5 mass, 6 inertia,
    # 7 g_eff (m/s^2, positive = pulls toward -z), 8 c_lin (N s/m), 9 c_rot (N m s),
    # 10 c_quad (N s^2/m^2), 11 tau_load (N m, opposes w component along body axis? -> along lab z),
    # 12 fluid swirl rate (rad/s, fluid rotates about z at this rate; drag acts on relative motion)
    r = y[0:3]; v = y[3:6]; q = y[6:10]; w = y[10:13]
    m1v = rotor_moment(t, P)
    m2v = qrot(q, np.array([0.0, 0.0, P[4]]))
    F = dip_force(m1v, m2v, r)
    B = dip_field(m1v, r)
    B[2] += P[3]
    tau = np.cross(m2v, B)
    F[2] -= P[5]*P[7]
    # fluid: optional solid-body swirl about z
    ufl = np.array([-P[12]*r[1], P[12]*r[0], 0.0])
    vr = v - ufl
    vn = np.sqrt(vr[0]**2+vr[1]**2+vr[2]**2)
    F -= P[8]*vr + P[10]*vn*vr
    wr = w - np.array([0.0, 0.0, P[12]])
    tau -= P[9]*wr
    tau[2] -= P[11]*np.sign(w[2])
    dq = 0.5*qmul(np.array([0.0, w[0], w[1], w[2]]), q)
    out = np.empty(13)
    out[0:3] = v
    out[3:6] = F/P[5]
    out[6:10] = dq
    out[10:13] = tau/P[6]
    return out

@njit(cache=True)
def integrate(y0, P, t0, t1, dt, nsave):
    n = int((t1-t0)/dt)
    every = max(1, n//nsave)
    ns = n//every + 1
    Y = np.empty((ns, 13)); T = np.empty(ns)
    y = y0.copy(); t = t0; k = 0
    Y[0] = y; T[0] = t
    for i in range(n):
        k1 = deriv(t, y, P)
        k2 = deriv(t+dt/2, y+dt/2*k1, P)
        k3 = deriv(t+dt/2, y+dt/2*k2, P)
        k4 = deriv(t+dt, y+dt*k3, P)
        y = y + dt/6*(k1+2*k2+2*k3+k4)
        y[6:10] /= np.sqrt(np.sum(y[6:10]**2))
        t += dt
        rn = np.sqrt(y[0]**2+y[1]**2+y[2]**2)
        if (i+1) % every == 0 and k+1 < ns:
            k += 1; Y[k] = y; T[k] = t
        if rn < P[13] or rn > 0.5:   # contact with rotor or escaped
            k += 1
            if k < ns:
                Y[k] = y; T[k] = t
            return T[:k+1], Y[:k+1]
    return T[:k+1], Y[:k+1]

def sphere_params(D, Br=1.32, rho=7500.0):
    V = np.pi/6*D**3
    m = Br*V/MU0
    mass = rho*V
    I = 0.4*mass*(D/2)**2
    return m, mass, I, V

def make_P(D1=0.019, D2=0.010, f=200.0, alpha_deg=5.0, Bz=0.0, g=9.81, rho_fluid=0.0,
           mu_fluid=0.0, c_lin=None, c_rot=None, c_quad=0.0, tau_load=0.0, swirl=0.0):
    m1, _, _, _ = sphere_params(D1)
    m2, mass, I, V = sphere_params(D2)
    geff = g*(1 - rho_fluid/7500.0)
    R = D2/2
    if c_lin is None:
        c_lin = 6*np.pi*mu_fluid*R
    if c_rot is None:
        c_rot = 8*np.pi*mu_fluid*R**3
    if c_quad == 'auto':
        c_quad = 0.5*rho_fluid*0.47*np.pi*R**2
    # added mass of sphere in fluid: 0.5*rho_f*V
    mass_eff = mass + 0.5*rho_fluid*V
    P = np.array([m1, 2*np.pi*f, np.radians(alpha_deg), Bz, m2, mass_eff, I, geff*mass/mass_eff,
                  c_lin, c_rot, c_quad, tau_load, swirl, (D1+D2)/2])
    return P
