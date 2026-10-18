"""Generate the figures in docs/figures from the simulation outputs (and a few quick runs)."""
import json, numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from rotframe import System, equilibria, onaxis_scan
from labsim import build, run

C = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300"]   # validated categorical order
INK, INK2, GRID = "#0b0b0b", "#52514e", "#e4e3df"
plt.rcParams.update({"font.size": 10, "axes.edgecolor": INK2, "axes.labelcolor": INK, "xtick.color": INK2,
                     "ytick.color": INK2, "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.6,
                     "axes.spines.top": False, "axes.spines.right": False, "figure.facecolor": "#fcfcfb",
                     "axes.facecolor": "#fcfcfb", "lines.linewidth": 2, "legend.frameon": False})
OUT = "../docs/figures/"

# 1 --- on-axis averaged force curve (rotating-frame, drag-free torque balance), 6 mm floater
fig, ax = plt.subplots(figsize=(6.4, 4))
zs = -np.linspace(0.022, 0.08, 300)
for i, f in enumerate([150, 200, 250]):
    s = System(D_rotor=0.0205, D_float=0.006, f=f, alpha_deg=10, Br=1.30, rho_fluid=1000, mu_fluid=1e-3)
    s.W = 0.0
    sc = onaxis_scan(s, zs)
    F = np.array([c[1] for c in sc])
    ax.plot(-zs*100, F*1e3, color=C[i], label=f"{f} Hz")
s = System(D_float=0.006, rho_fluid=1000)
ax.axhline(s.W*1e3, color=INK2, lw=1, ls="--")
ax.text(7.9, s.W*1e3 + 0.6, "net weight in water", ha="right", color=INK2, fontsize=9)
ax.axhline(0, color=INK, lw=0.8)
ax.set_ylim(-40, 25)
ax.set_xlabel("floater distance below rotor centre (cm)")
ax.set_ylabel("synchronous magnetic force, + = toward rotor (mN)")
ax.set_title("Averaged on-axis force: short-range repulsion, long-range attraction", loc="left", fontsize=10.5)
ax.legend(title="rotor speed", loc="lower right")
fig.tight_layout(); fig.savefig(OUT + "fig1_force_curve.png", dpi=160); plt.close(fig)

# 2 --- design chart: predicted height vs frequency
fig, ax = plt.subplots(figsize=(6.4, 4.2))
d = json.load(open("design_chart_6mm_water.json"))
for i, al in enumerate([6, 8, 10, 12, 15, 20]):
    pts = sorted([r for r in d if r["al"] == al and r["maxre"] < 0 and r["tilt"] < 45 and -0.12 < r["z"] < -0.02], key=lambda r: r["f"])
    if not pts: continue
    ax.plot([p["f"] for p in pts], [-p["z"]*100 for p in pts], color=C[i], marker="o", ms=4, label=f"α = {al}°")
ax.axhspan(0, 2.7, color=GRID, alpha=0.6, lw=0)
ax.text(105, 2.35, "inside shroud / above liquid - unusable", fontsize=8.5, color=INK2, va="top")
ax.set_ylim(2, 8)
ax.set_xlabel("rotor frequency (Hz)")
ax.set_ylabel("stable levitation depth below rotor centre (cm)")
ax.set_title("Prediction to test: 6 mm NdFeB floater in water, 3/4\" x 5/8\" rotor", loc="left", fontsize=10.5)
ax.legend(title="rotor tilt", ncol=2)
fig.tight_layout(); fig.savefig(OUT + "fig2_design_chart.png", dpi=160); plt.close(fig)

# 3 --- stability vs net body force
fig, ax = plt.subplots(figsize=(6.4, 3.8))
base = System(D_rotor=0.0205, D_float=0.006, f=200, alpha_deg=10, Br=1.30, rho_fluid=1000, mu_fluid=1e-3)
W0 = base.mass*9.81
ratios = np.linspace(-0.6, 1.6, 45); mr = []
for r in ratios:
    base.W = r*W0
    eq = [e for e in equilibria(base, side=-1, zmin=0.022, n=160) if e["tilt"] < 45]
    eq = sorted(eq, key=lambda e: e["maxre"])
    mr.append(eq[0]["maxre"] if eq else np.nan)
mr = np.array(mr)
ax.plot(ratios, mr, color=C[0])
ax.axhline(0, color=INK, lw=0.8)
ax.axvline(1.0 - 1000/7500, color=INK2, lw=1, ls="--"); ax.text(0.89, 5, "bare NdFeB\nin water", fontsize=8.5, color=INK2)
ax.axvline(1.0, color=INK2, lw=1, ls=":"); ax.text(1.02, 9, "in air", fontsize=8.5, color=INK2)
ax.set_xlabel("net body force pulling the floater AWAY from the rotor  /  floater weight in air")
ax.set_ylabel("largest eigenvalue real part (1/s)")
ax.set_title("Stable (negative) only while the net body force pulls away from the rotor", loc="left", fontsize=10.5)
fig.tight_layout(); fig.savefig(OUT + "fig3_weight_window.png", dpi=160); plt.close(fig)
json.dump(dict(ratios=ratios.tolist(), maxre=[None if np.isnan(x) else float(x) for x in mr]), open("weight_window.json", "w"))

# 4 --- viscosity: decay rate of the slowest mode
fig, ax = plt.subplots(figsize=(6.4, 3.8))
mus = np.logspace(-5, 0.3, 18); rates = []
for mu in mus:
    rho = 1000.0   # density held fixed so only viscosity varies
    s = System(D_rotor=0.0205, D_float=0.006, f=200, alpha_deg=10, Br=1.30, rho_fluid=rho, mu_fluid=mu)
    eq = [e for e in equilibria(s, side=-1, zmin=0.022, n=160) if e["tilt"] < 45 and e["maxre"] < 1]
    rates.append(min(e["maxre"] for e in eq) if eq else np.nan)
rates = np.array(rates)
ax.semilogx(mus, -rates, color=C[0], marker="o", ms=4)
sa = System(D_rotor=0.0205, D_float=0.006, f=200, alpha_deg=10, Br=1.30, rho_fluid=1.2, mu_fluid=1.8e-5)
ea = [e for e in equilibria(sa, side=-1, zmin=0.022, n=160) if e["tilt"] < 45 and e["maxre"] < 1]
ra = -min(e["maxre"] for e in ea)
ax.plot([1.8e-5], [ra], marker="s", ms=7, color=C[1], ls="none", label="real air (density 1.2)")
ax.legend(loc="upper left", fontsize=8.5)
for x, lab in [(1e-3, "water"), (6e-3, "50% glycerol"), (1.0, "glycerol")]:
    ax.axvline(x, color=GRID, lw=1); ax.text(x*1.1, ax.get_ylim()[1]*0.9 if False else 0.02, lab, fontsize=8.5, color=INK2, rotation=90, va="bottom")
ax.set_xlabel("fluid viscosity (Pa s)")
ax.set_ylabel("decay rate of slowest mode (1/s)")
ax.set_yscale("log")
ax.set_title("Viscous drag turns neutral stability into asymptotic stability (density 1000)", loc="left", fontsize=10.5)
fig.tight_layout(); fig.savefig(OUT + "fig4_viscosity.png", dpi=160); plt.close(fig)
json.dump(dict(mu=mus.tolist(), maxre=[None if np.isnan(x) else float(x) for x in rates]), open("viscosity.json", "w"))

# 5 --- capture by raising the vessel toward the spinning rotor
s = System(D_float=0.006, f=200, alpha_deg=10, rho_fluid=1000, mu_fluid=1e-3)
rng = np.random.default_rng(3)
fig, ax = plt.subplots(figsize=(6.4, 3.8))
for k in range(3):
    P = build(s, t_ramp=1e-4, floor_z=-0.08, floor_side=-1, wall_R=0.03, floor_v=0.035/3.0, floor_T=3.0)
    y0 = np.zeros(13); y0[0:2] = rng.normal(0, 0.002, 2); y0[2] = -0.08 + s.R
    mh = rng.normal(size=3); y0[6:9] = mh/np.linalg.norm(mh)
    T, Y, hit = run(y0, P, 6.0, 2e-6, 3000)
    ax.plot(T, -Y[:, 2]*100, color=C[k], lw=1.5, label=f"trial {k+1}")
tt = np.linspace(0, 6, 100)
ax.plot(tt, (0.08 - 0.035/3.0*np.minimum(tt, 3.0))*100 - s.R*100, color=INK2, lw=1, ls="--", label="vessel floor (+ floater radius)")
ax.invert_yaxis()
ax.set_xlabel("time (s)"); ax.set_ylabel("floater depth below rotor centre (cm)")
ax.set_title("Start-up protocol: rotor at speed, vessel raised 35 mm in 3 s", loc="left", fontsize=10.5)
ax.legend(loc="lower right", fontsize=8.5)
fig.tight_layout(); fig.savefig(OUT + "fig5_capture.png", dpi=160); plt.close(fig)

# 6 --- bottom-drive variant
bd = json.load(open("bottom_drive.json"))
fig, ax = plt.subplots(figsize=(6.4, 3.8))
for i, name in enumerate([k for k in bd if "bare" not in k]):
    pts = [(r["f"], e["z"]) for r in bd[name] for e in r["eq"] if e["maxre"] < 0 and 0 < e["z"] < 0.12]
    if pts:
        pts.sort(); ax.plot([p[0] for p in pts], [p[1]*100 for p in pts], color=C[i], marker="o", ms=4, label=name.split(" (")[0])
ax.axhspan(0, 2.45 + 0.8, color=GRID, alpha=0.6, lw=0); ax.text(140, 1.0, "excluded: below vessel floor + floater radius", fontsize=8.5, color=INK2, va="top")
ax.set_xlabel("rotor frequency (Hz)"); ax.set_ylabel("stable height above rotor centre (cm)")
ax.set_title("Bottom-drive (stirrer form factor) needs a buoyant, low-inertia floater", loc="left", fontsize=10.5)
ax.legend(fontsize=8.5)
fig.tight_layout(); fig.savefig(OUT + "fig6_bottom_drive.png", dpi=160); plt.close(fig)
print("figures written")
