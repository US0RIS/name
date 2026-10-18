"""Dimensioned XZ cross-section of the assembly (y = 0 plane) -> docs/figures/fig0_section.png"""
import numpy as np, cadquery as cq, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import assembly as A
import spintrap_cad as S

def section_xz(shape):
    # rotate +90 deg about X: (x,y,z) -> (x,-z,y); section at the new z=0 (old y=0)
    sh = shape.rotate((0, 0, 0), (1, 0, 0), 90)
    try:
        sec = sh.section(0.0)
    except Exception:
        return []
    faces = []
    for f in sec.faces().vals():
        loops = []
        for w in [f.outerWire()] + f.innerWires():
            pts = [w.positionAt(t) for t in np.linspace(0, 1, 400)]
            loops.append(np.array([(p.x, -p.y) for p in pts]))
        faces.append(loops)
    return faces

fig, ax = plt.subplots(figsize=(7.2, 8.6))
for n, (p, c) in A.parts.items():
    from matplotlib.path import Path
    from matplotlib.patches import PathPatch
    for loops in section_xz(p):
        verts, codes = [], []
        for L in loops:
            verts += list(L) + [L[0]]
            codes += [Path.MOVETO] + [Path.LINETO]*(len(L) - 1) + [Path.CLOSEPOLY]
        ax.add_patch(PathPatch(Path(verts, codes), fc=c, alpha=0.45 if n in ("water", "jar") else 0.9, lw=0.6, ec="#0b0b0b"))
INK2 = "#52514e"
def dim(z1, z2, x, text):
    ax.annotate("", xy=(x, z1), xytext=(x, z2), arrowprops=dict(arrowstyle="<->", color=INK2, lw=0.8))
    ax.text(x + 2, (z1 + z2)/2, text, fontsize=8, color=INK2, va="center")
dim(0, -34.0, 40, "34.0 mm  (200 Hz, α=12°)")
dim(0, -S.SHROUD_DROP, 60, f"{S.SHROUD_DROP:.1f}")
dim(0, A.FLOOR_IN, 80, "45 (vessel floor)")
ax.axhline(0, color=INK2, lw=0.5, ls=":"); ax.text(-118, 1.5, "rotor-magnet centre", fontsize=8, color=INK2)
ax.text(8, -35, "floater", fontsize=8, color="#e34948")
ax.text(12, 6, f"rotor magnet\ntilted {S.ALPHA:.0f}°", fontsize=8, color="#0b0b0b")
ax.set_aspect("equal"); ax.set_xlim(-120, 130); ax.set_ylim(-170, 140)
ax.set_xlabel("x (mm)"); ax.set_ylabel("z (mm)")
ax.set_title("SpinTrap, overhead drive: section at y = 0 (levitating state)", loc="left", fontsize=10)
for s in ("top", "right"): ax.spines[s].set_visible(False)
fig.tight_layout(); fig.savefig("../docs/figures/fig0_section.png", dpi=150)
print("ok")
