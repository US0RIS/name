"""Position all parts (plus placeholder purchased parts) and export an assembly STEP (the
dimensioned section preview is produced by section_view.py).  Rotor-magnet centre = origin, final (levitating) configuration."""
import os, numpy as np, cadquery as cq
import spintrap_cad as S
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

FLOOR_IN = -45.0          # vessel inner floor below rotor centre at the end of the approach
JAR_H, JAR_WALL, JAR_BOT = 50.0, 2.5, 3.0
JACK_H = 70.0
up, lo = S.rotor_hub()
arm = S.motor_arm().translate((-70, 0, 0)).translate((0, 0, S.HUB_OD/2 + S.BOSS_H + S.MOTOR_STACK))
H = S.SHROUD_DROP + S.HUB_OD/2 + S.BOSS_H + S.MOTOR_STACK
shroud = S.rotor_shroud().translate((0, 0, -S.SHROUD_DROP))
z_arm = S.HUB_OD/2 + S.BOSS_H + S.MOTOR_STACK
motor = (cq.Workplane("XY").circle(14).extrude(26).translate((0, 0, z_arm - 26))
         .union(cq.Workplane("XY").circle(4).extrude(S.MOTOR_STACK - 26).translate((0, 0, S.HUB_OD/2 + S.BOSS_H))))
mag = (cq.Workplane("XY").circle(S.MAG_D/2).extrude(S.MAG_L).translate((0, 0, -S.MAG_L/2))
       .rotate((0, 0, 0), (0, 1, 0), 90 - S.ALPHA))
jar_z0 = FLOOR_IN - JAR_BOT
jar = (cq.Workplane("XY").circle(S.JAR_OD/2).extrude(JAR_H)
       .cut(cq.Workplane("XY").circle(S.JAR_OD/2 - JAR_WALL).extrude(JAR_H).translate((0, 0, JAR_BOT)))
       .translate((0, 0, jar_z0)))
water = cq.Workplane("XY").circle(S.JAR_OD/2 - JAR_WALL - 0.01).extrude(-S.SHROUD_DROP - 1.0 - FLOOR_IN).translate((0, 0, FLOOR_IN))
water = water.cut(cq.Workplane("XY").circle(S.SHROUD_ID/2 + S.SHROUD_WALL).extrude(10).translate((0, 0, -S.SHROUD_DROP)))
floater = cq.Workplane("XY").sphere(3.0).translate((0, 0, -34.0))
cradle = S.vessel_cradle().translate((0, 0, jar_z0 - 3))
jack = cq.Workplane("XY").rect(100, 100).extrude(JACK_H).translate((0, 0, jar_z0 - 3 - JACK_H))
z_foot = jar_z0 - 3 - JACK_H - 6
foot = S.column_foot().translate((-20, 0, z_foot))   # column socket sits 50 mm left of plate centre
col_x = -70
column = cq.Workplane("XY").rect(20, 20).extrude(z_arm + 40 - z_foot - 6).translate((col_x, 0, z_foot + 6))
arm = S.motor_arm().translate((col_x, 0, z_arm))
parts = dict(hub_upper=(up, "#2a78d6"), hub_lower=(lo, "#2a78d6"), magnet=(mag, "#52514e"), arm=(arm, "#eb6834"),
             shroud=(shroud, "#1baf7a"), motor=(motor, "#52514e"), jar=(jar, "#9ab"), water=(water, "#bfe0f5"),
             floater=(floater, "#e34948"), cradle=(cradle, "#eda100"), jack=(jack, "#cfcfca"), foot=(foot, "#eda100"),
             column=(column, "#8f8e89"))
asm = cq.Assembly()
for n, (p, c) in parts.items():
    asm.add(p, name=n, color=cq.Color(c))
os.makedirs("out", exist_ok=True)
asm.save("out/spintrap_assembly.step")
print("arm spin-axis x check: arm placed with column at x =", col_x, "; spin axis must be at x=0 ->", col_x + 70 - 0)

# 2D dimensioned section preview: see section_view.py
