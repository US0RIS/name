"""Verify the rotor assembly is statically AND dynamically balanced about the spin axis."""
import math, numpy as np, cadquery as cq
from OCP.GProp import GProp_GProps
from OCP.BRepGProp import BRepGProp
import spintrap_cad as S

def props(shape, rho):
    g = GProp_GProps(); BRepGProp.VolumeProperties_s(shape.val().wrapped, g)
    V = g.Mass(); c = g.CentreOfMass(); M = g.MatrixOfInertia()
    I = np.array([[M.Value(i, j) for j in (1, 2, 3)] for i in (1, 2, 3)])   # about COM, per unit density
    com = np.array([c.X(), c.Y(), c.Z()])
    # shift to origin (parallel axis) so everything refers to the spin-axis origin
    d = com; I0 = I + V*(np.dot(d, d)*np.eye(3) - np.outer(d, d))
    return V*rho, com, I0*rho

up, lo = S.rotor_hub()
rho_pla = 1.24e-3   # g/mm^3
mu, cu, Iu = props(up, rho_pla); ml, cl, Il = props(lo, rho_pla)
# magnet: cylinder 19.05 x 15.88, tilted
mag = (cq.Workplane("XY").circle(S.MAG_D/2).extrude(S.MAG_L).translate((0, 0, -S.MAG_L/2))
       .rotate((0, 0, 0), (0, 1, 0), 90 - S.ALPHA))
mm, cm, Im = props(mag, 7.5e-3)
M = mu + ml + mm
com = (mu*cu + ml*cl + mm*cm)/M
I = Iu + Il + Im
print(f"plastic upper {mu:.2f} g, lower {ml:.2f} g, magnet {mm:.2f} g, total {M:.2f} g")
print("COM offset from spin axis (mm):", np.hypot(com[0], com[1]), " z:", com[2])
print("inertia tensor about origin (g mm^2):\n", np.round(I, 1))
print("products Ixz, Iyz (cause dynamic imbalance):", I[0, 2], I[1, 2])
Om = 2*math.pi*200
print("dynamic imbalance moment at 200 Hz: %.4f N m" % (Om**2*math.hypot(I[0, 2], I[1, 2])*1e-9))
print("static imbalance force at 200 Hz:  %.3f N" % (M*1e-3*Om**2*np.hypot(com[0], com[1])*1e-3))
# magnet alone, to show the L/D trick
print("magnet alone: Ixz = %.1f g mm^2 (would be %.1f for an L=D cube-like cylinder)" % (Im[0, 2], 0))
