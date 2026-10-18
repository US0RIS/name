"""Rotating-frame (autonomous) model of rotation-induced magnetic levitation.

Frame rotates with the rotor at Omega about lab z.  In this frame the rotor field is static,
so synchronous levitation states are *fixed points* and their stability follows from the
eigenvalues of an 11x11 Jacobian (3 position, 3 velocity, 2 orientation, 3 angular velocity).

Sources (all in rotating frame, all spheres => exact dipoles):
  * rotor: in-plane moment m_r (along x') plus optional tilt -> axial part, at origin
  * static axial magnet: moment m_s along +z at (0,0,z_s)   (does not rotate; axisymmetric
    so it is also static in the rotating frame)
Floater: sphere, moment m2 along its body axis m_hat, mass M (with added mass), inertia I.
Fluid at rest in lab: translational drag  -c1 v_lab - c2 |v_lab| v_lab,
                      rotational drag     -cr w_lab  (w_lab = lab angular velocity)
Gravity/buoyancy: -M_g * g_eff z_hat (floater weight minus buoyancy).
"""
import numpy as np
from scipy.optimize import root

MU0 = 4e-7*np.pi
ZH = np.array([0.0, 0.0, 1.0])

def dip_B(m, r):
    rn = np.linalg.norm(r); rh = r/rn
    return MU0/(4*np.pi)*(3*np.dot(m, rh)*rh - m)/rn**3

def dip_F(m1, m2, r):
    rn = np.linalg.norm(r); rh = r/rn
    a = np.dot(m1, rh); b = np.dot(m2, rh)
    return 3*MU0/(4*np.pi*rn**4)*(a*m2 + b*m1 + np.dot(m1, m2)*rh - 5*a*b*rh)

def sphere(D, Br=1.32, rho=7500.0):
    V = np.pi/6*D**3
    return Br*V/MU0, rho*V, 0.4*rho*V*(D/2)**2, V

class System:
    def __init__(self, D_rotor=0.019, f=200.0, alpha_deg=10.0, m_static=0.0, z_static=-0.03,
                 D_float=0.006, shell_D=None, shell_rho=0.0, rho_fluid=0.0, mu_fluid=0.0,
                 g=9.81, quad_drag=True, Br=1.32):
        mr, _, _, _ = sphere(D_rotor, Br)
        self.Om = 2*np.pi*f
        al = np.radians(alpha_deg)
        self.m_rot = mr*np.array([np.cos(al), 0.0, np.sin(al)])
        self.m_s = m_static; self.z_s = z_static
        m2, mag_mass, mag_I, Vm = sphere(D_float, Br)
        self.m2 = m2
        # optional low-density spherical shell around the magnet (for buoyancy tuning)
        if shell_D is not None and shell_D > D_float:
            Vs = np.pi/6*shell_D**3 - Vm
            shell_mass = shell_rho*Vs
            # I of thick spherical shell
            R2, R1 = shell_D/2, D_float/2
            shell_I = 0.4*shell_rho*(4/3*np.pi)*(R2**5 - R1**5)
            Dh = shell_D
        else:
            shell_mass = 0.0; shell_I = 0.0; Dh = D_float
        self.mass = mag_mass + shell_mass
        self.Vtot = np.pi/6*Dh**3
        self.Mi = self.mass + 0.5*rho_fluid*self.Vtot      # inertial mass incl. added mass
        self.I = mag_I + shell_I
        self.W = (self.mass - rho_fluid*self.Vtot)*g      # net weight (N), + = downward
        R = Dh/2
        self.c1 = 6*np.pi*mu_fluid*R
        self.c2 = 0.5*rho_fluid*0.47*np.pi*R**2 if quad_drag else 0.0
        self.cr = 8*np.pi*mu_fluid*R**3
        # high-Re rotational drag correction (rotating sphere, Re_w = w R^2/nu > ~10):
        # torque coefficient ~ C_M = 6.25/sqrt(Re) style; we keep it as an extra quadratic-ish
        # term c_r2 * |w|^{1.5}.  Lamb/Sawatzki correlation: M = 0.5*rho*w^2*R^5*C_M, C_M = 2*pi*... see docs
        self.rho_f = rho_fluid; self.mu_f = mu_fluid; self.R = R
        self.Dh = Dh
        # --- adversarial-review hooks (all off by default) ---
        self.extra_dipoles = []      # list of (moment vector, position) static in the rotating frame
        self.cyl = None              # exact finite-cylinder rotor field replaces the rotor dipole
        self.k_eddy = 0.0            # eddy torque coefficient (N m s / T^2) on the floater
        self.swirl = 0.0             # fluid solid-body rotation rate about z (rad/s, lab)
        self.drag_scale = 1.0        # multiplies all fluid drag terms
        self.drag_scale_t = 1.0      # extra factor, translational drag only
        self.drag_scale_r = 1.0      # extra factor, rotational drag only
        self.rotor_offset = np.zeros(3)   # rotor dipole position (eccentricity), rotating frame

    def rot_torque_drag(self, w):
        wn = np.linalg.norm(w)
        if self.mu_f == 0.0 or wn == 0.0:
            return -self.cr*w
        # laminar boundary-layer correlation for a rotating sphere (Sawatzki 1970 / Dennis):
        # C_M = 64/(3 Re) + 12.2/sqrt(Re)  for Re = w R^2 / nu up to ~1e5 ; M = 0.5 rho w^2 R^5 C_M
        nu = self.mu_f/self.rho_f
        Re = wn*self.R**2/nu
        CM = 64.0/(3*Re) + 12.2/np.sqrt(Re)
        M = 0.5*self.rho_f*wn**2*self.R**5*CM
        return -M*w/wn

    def fields(self, r):
        if self.cyl is not None:
            B = self.cyl.B(r)
        else:
            B = dip_B(self.m_rot, r - self.rotor_offset)
        for (m, p) in self.extra_dipoles:
            B = B + dip_B(m, r - p)
        if self.m_s != 0.0:
            rs = r - np.array([0, 0, self.z_s])
            B = B + dip_B(self.m_s*ZH, rs)
        return B

    def force(self, r, m2v):
        if self.cyl is not None:
            h = 2e-6
            F = np.array([(np.dot(m2v, self.cyl.B(r + h*e)) - np.dot(m2v, self.cyl.B(r - h*e)))/(2*h) for e in np.eye(3)])
        else:
            F = dip_F(self.m_rot, m2v, r - self.rotor_offset)
        for (m, p) in self.extra_dipoles:
            F = F + dip_F(m, m2v, r - p)
        if self.m_s != 0.0:
            F = F + dip_F(self.m_s*ZH, m2v, r - np.array([0, 0, self.z_s]))
        return F

    def rhs_full(self, r, v, mh, w):
        """rotating-frame derivatives. r,v: rotating-frame position/velocity;
        mh: floater axis (rot frame); w: lab angular velocity expressed in rot-frame axes."""
        Om = self.Om*ZH
        m2v = self.m2*mh
        F = self.force(r, m2v)
        B = self.fields(r)
        vlab = v + np.cross(Om, r)
        vrel = vlab - np.cross(self.swirl*ZH, r)
        ds = self.drag_scale
        F = F - ds*self.drag_scale_t*(self.c1*vrel + self.c2*np.linalg.norm(vrel)*vrel)
        F = F - self.W*ZH
        a = F/self.Mi - 2*np.cross(Om, v) - np.cross(Om, np.cross(Om, r))
        tau = np.cross(m2v, B) + self.drag_scale*self.drag_scale_r*self.rot_torque_drag(w - self.swirl*ZH)
        if self.k_eddy:
            nu = w - Om                        # body rotation relative to the (static) field
            tau = tau - self.k_eddy*(nu*np.dot(B, B) - np.dot(nu, B)*B)
        dw = tau/self.I - np.cross(Om, w)
        dmh = np.cross(w - Om, mh)
        return v, a, dmh, dw

def tangent_basis(m):
    t = np.array([1.0, 0, 0]) if abs(m[0]) < 0.9 else np.array([0, 1.0, 0])
    e1 = np.cross(m, t); e1 /= np.linalg.norm(e1)
    e2 = np.cross(m, e1)
    return e1, e2

def pack(sys, x, m0, e1, e2):
    r = x[0:3]; v = x[3:6]
    mh = m0 + x[6]*e1 + x[7]*e2; N = np.linalg.norm(mh); mh = mh/N
    w = x[8:11]
    dr, dv, dmh, dw = sys.rhs_full(r, v, mh, w)
    return np.r_[dr, dv, N*np.dot(dmh, e1), N*np.dot(dmh, e2), dw]

def find_fixed_point(sys, z_guess, mh_guess, p=0.0):
    """Solve for a synchronous state near the guess.  Returns (r, mh, w) or None."""
    m0 = mh_guess/np.linalg.norm(mh_guess)
    for it in range(4):
        e1, e2 = tangent_basis(m0)
        s = p - sys.Om*m0[2]
        w0 = sys.Om*ZH + s*m0
        x0 = np.r_[0.0, 0.0, z_guess, 0, 0, 0, 0, 0, w0]
        sol = root(lambda x: pack(sys, x, m0, e1, e2), x0, method='hybr', options=dict(xtol=1e-12, maxfev=20000))
        x = sol.x
        mh = m0 + x[6]*e1 + x[7]*e2; mh /= np.linalg.norm(mh)
        m0 = mh; z_guess = x[2]
        if np.max(np.abs(x[6:8])) < 1e-10: break
    res = np.max(np.abs(pack(sys, np.r_[x[0:6], 0, 0, x[8:11]], m0, *tangent_basis(m0))))
    if not sol.success and res > 1e-6:
        return None
    return x[0:3], m0, x[8:11], res

def jacobian(sys, r, mh, w, eps=None):
    e1, e2 = tangent_basis(mh)
    x0 = np.r_[r, 0, 0, 0, 0, 0, w]
    f0 = pack(sys, x0, mh, e1, e2)
    J = np.zeros((11, 11))
    scales = np.r_[1e-7*np.ones(3), 1e-6*np.ones(3), 1e-7, 1e-7, 1e-5*np.ones(3)]
    for i in range(11):
        h = scales[i]
        xp = x0.copy(); xp[i] += h
        xm = x0.copy(); xm[i] -= h
        J[:, i] = (pack(sys, xp, mh, e1, e2) - pack(sys, xm, mh, e1, e2))/(2*h)
    return J, f0

def stability(sys, r, mh, w):
    J, f0 = jacobian(sys, r, mh, w)
    ev = np.linalg.eigvals(J)
    return ev, f0

def onaxis_scan(sys, zs, p=0.0, branch=+1):
    """Quick on-axis force curve using the drag-free torque balance (for seeding)."""
    out = []
    for z in zs:
        r = np.array([0, 0, z])
        B = sys.fields(r)
        mh = np.array([0, 0, branch*1.0])
        for _ in range(400):
            s = p - sys.Om*mh[2]
            V = sys.m2*B + sys.I*s*sys.Om*ZH
            c = V/np.linalg.norm(V)
            if np.dot(c, mh) < 0: c = -c
            mn = 0.5*mh + 0.5*c; mn /= np.linalg.norm(mn)
            if np.linalg.norm(mn - mh) < 1e-13: break
            mh = mn
        F = sys.force(r, sys.m2*mh)[2] - sys.W
        out.append((z, F, mh))
    return out

def equilibria(sys, side=-1, zmin=0.011, zmax=0.12, n=300, branch=+1):
    zs = side*np.linspace(zmin, zmax, n)
    sc = onaxis_scan(sys, zs, branch=branch)
    res = []
    for i in range(len(sc)-1):
        if np.sign(sc[i][1]) != np.sign(sc[i+1][1]):
            fp = find_fixed_point(sys, 0.5*(sc[i][0]+sc[i+1][0]), sc[i][2])
            if fp is None: continue
            r, mh, w, resid = fp
            ev, _ = stability(sys, r, mh, w)
            res.append(dict(r=r, mh=mh, w=w, ev=ev, resid=resid,
                            maxre=np.max(ev.real), tilt=np.degrees(np.arccos(abs(mh[2])))))
    return res


class CylinderRotor:
    """Exact field of a uniformly, axially magnetised finite cylinder (equivalent surface
    current K = M on the mantle, discretised into N coaxial loops with elliptic-integral
    fields).  Axis u = (cos a, 0, sin a) in the rotating frame, centred at the origin."""
    def __init__(self, D, L, Br, alpha_deg, N=240, centre=(0, 0, 0)):
        from scipy.special import ellipk, ellipe
        self.K_, self.E_ = ellipk, ellipe
        self.a = D/2; self.L = L; self.M = Br/MU0
        al = np.radians(alpha_deg)
        u = np.array([np.cos(al), 0.0, np.sin(al)])
        e1 = np.cross(u, [0, 1.0, 0]); e1 /= np.linalg.norm(e1); e2 = np.cross(u, e1)
        self.R = np.vstack([e1, e2, u])          # rows: local x, y, z(axis)
        self.c = np.asarray(centre, float)
        self.zl = (np.arange(N) + 0.5)/N*L - L/2
        self.I = self.M*L/N
        self.m = self.M*np.pi*self.a**2*L*u      # equivalent dipole

    def B(self, r):
        p = self.R @ (np.asarray(r) - self.c)
        rho = np.hypot(p[0], p[1]); a = self.a
        z = p[2] - self.zl
        q = (a + rho)**2 + z**2
        m = 4*a*rho/q
        K = self.K_(m); E = self.E_(m)
        d = (a - rho)**2 + z**2
        pre = MU0*self.I/(2*np.pi)
        Bz = np.sum(pre/np.sqrt(q)*(K + (a**2 - rho**2 - z**2)/d*E))
        if rho > 1e-12:
            Brho = np.sum(pre/(rho*np.sqrt(q))*z*(-K + (a**2 + rho**2 + z**2)/d*E))
            Bl = np.array([Brho*p[0]/rho, Brho*p[1]/rho, Bz])
        else:
            Bl = np.array([0.0, 0.0, Bz])
        return self.R.T @ Bl
