"""SpinTrap prototype - parametric CAD (CadQuery 2.x).

Run:  python spintrap_cad.py           -> writes STEP + STL for every part into ./out
All dimensions in mm.  Coordinate convention: +Z up, spin axis = Z, rotor magnet centre at
the origin of the rotor parts.

Parts
  1  rotor_hub_upper / rotor_hub_lower : spherical two-piece rotor body (OD 36) holding a
     3/4" x 5/8" (19.05 x 15.88) axially magnetised N42/N52 cylinder with its axis tilted
     ALPHA degrees out of the spin plane.  Sphere minus an inertia-isotropic cylinder =>
     no dynamic imbalance.  Three M3 screws (3-fold symmetric) join the halves.
  2  motor_arm        : clamps to a 2020 aluminium extrusion column, carries a 22xx
     outrunner (16/19 mm bolt pattern), shaft pointing DOWN.
  3  rotor_shroud     : closed safety cup around motor + rotor (print in PETG/PC, 100% infill
     at the floor and lower 40 mm), 1.5 mm floor, pocket for the tachometer Hall latch.
  4  column_foot      : printed base foot for the 2020 column.
  5  vessel_cradle    : centring cradle for an 80 mm OD wide-mouth jar, sits on a lab jack.
  6  float_shell_upper/lower : optional 16 mm buoyancy shell for a 6 mm sphere magnet
     (bottom-drive variant), 0.8 mm wall.
  7  align_gauge      : go/no-go gauge that checks rotor-to-vessel axis alignment.
"""
import os, math
import cadquery as cq

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out")
os.makedirs(OUT, exist_ok=True)

# ----------------------------------------------------------------------------- parameters
ALPHA = float(os.environ.get("ALPHA", 12.0))   # rotor magnet tilt out of spin plane (deg)
MAG_D, MAG_L = 19.05, 15.88                    # rotor magnet (3/4" x 5/8")
MAG_CLR = 0.25                                 # radial clearance for epoxy
HUB_OD = 36.0                                  # spherical rotor body
BORE = 5.2                                     # prop-adapter thread / shaft (M5)
BOSS_D, BOSS_H = 14.0, 9.0
SCREW_R = 13.0                                 # radius of 3 joining screws
M3_CLR, M3_HEAD = 3.3, 6.0

MOTOR_HOLE_PCD = (16.0, 19.0)                  # typical 22xx bolt patterns (two of each)
MOTOR_BODY_D = 28.5
ARM_REACH = 70.0                               # column centreline -> spin axis
EXTR = 20.0                                    # 2020 profile

SHROUD_ID, SHROUD_WALL = 44.0, 2.4
SHROUD_FLOOR = 1.5
SHROUD_DROP = 21.0 + SHROUD_FLOOR             # rotor centre -> underside of shroud floor
MOTOR_STACK = 52.0                             # motor mount face -> top of hub boss (measure yours:
                                               # A2212 bell ~26 + prop adapter ~17 + spacer); motor hangs
                                               # UNDER the arm, shaft pointing down

JAR_OD = 80.0                                  # wide-mouth glass jar; shroud (OD 48.8) dips into it

FLOAT_MAG = 6.0
FLOAT_OD, FLOAT_WALL = 16.0, 0.8

def save(shape, name):
    cq.exporters.export(shape, os.path.join(OUT, name + ".step"))
    cq.exporters.export(shape, os.path.join(OUT, name + ".stl"), tolerance=0.02, angularTolerance=0.1)
    print("wrote", name)

# ----------------------------------------------------------------------------- 1 rotor hub
def magnet_pocket():
    # cylinder along Z, centred, then tilted so its axis = (cos a, 0, sin a)
    pocket = (cq.Workplane("XY").circle(MAG_D/2 + MAG_CLR).extrude(MAG_L + 0.3)
              .translate((0, 0, -(MAG_L + 0.3)/2)))
    return pocket.rotate((0, 0, 0), (0, 1, 0), 90.0 - ALPHA)

def rotor_hub():
    body = cq.Workplane("XY").sphere(HUB_OD/2)
    boss = (cq.Workplane("XY").workplane(offset=HUB_OD/2 - 3.0).circle(BOSS_D/2).extrude(BOSS_H + 3.0))
    body = body.union(boss)
    body = body.cut(magnet_pocket())
    # shaft bore in the boss only (stops 1 mm above the pocket)
    top = HUB_OD/2 + BOSS_H
    bore = cq.Workplane("XY").workplane(offset=HUB_OD/2 - 4.0).circle(BORE/2).extrude(top)
    body = body.cut(bore)
    # three joining screws, 3-fold symmetric -> no product of inertia about the spin axis
    for k in range(3):
        a = math.radians(120*k + 30)
        x, y = SCREW_R*math.cos(a), SCREW_R*math.sin(a)
        hole = cq.Workplane("XY").center(x, y).circle(M3_CLR/2).extrude(HUB_OD).translate((0, 0, -HUB_OD/2))
        body = body.cut(hole)
        # head/nut counterbores on the outer sphere surface
        cb_top = cq.Workplane("XY").workplane(offset=8.0).center(x, y).circle(M3_HEAD/2 + 0.2).extrude(HUB_OD)
        cb_bot = cq.Workplane("XY").workplane(offset=-8.0 - HUB_OD).center(x, y).polygon(6, 6.6).extrude(HUB_OD)
        body = body.cut(cb_top).cut(cb_bot)
    # alignment pins (2 x 3 mm dowels) at 90/270 deg, radius 9 (clear of the pocket)
    upper = body.cut(cq.Workplane("XY").box(200, 200, 200).translate((0, 0, -100)))
    lower = body.cut(cq.Workplane("XY").box(200, 200, 200).translate((0, 0, 100)))
    # two symmetric wrench flats on the boss (12 mm A/F); symmetric so they add no imbalance
    for sgn in (1, -1):
        flat = cq.Workplane("XY").box(4, 20, BOSS_H).translate((sgn*(6.0 + 2.0), 0, HUB_OD/2 + BOSS_H/2))
        upper = upper.cut(flat)
    return upper, lower

# ----------------------------------------------------------------------------- 2 motor arm
def motor_arm():
    t = 8.0
    plate = (cq.Workplane("XY").center(ARM_REACH/2 + EXTR/2 + 12, 0).rect(ARM_REACH + EXTR + 24, 76).extrude(t))
    # stiffening ribs (vertical webs) on top
    rib = cq.Workplane("XY").workplane(offset=t).center(ARM_REACH/2 + EXTR/2 + 6, 0).rect(ARM_REACH + 12, 4).extrude(16)
    rib2 = rib.translate((0, 24, 0)); rib3 = rib.translate((0, -24, 0))
    clamp = cq.Workplane("XY").center(0, 0).rect(EXTR + 12, 40).extrude(40)
    arm = plate.union(rib).union(rib2).union(rib3).union(clamp)
    # 2020 slot
    arm = arm.cut(cq.Workplane("XY").rect(EXTR + 0.4, EXTR + 0.4).extrude(60).translate((0, 0, -5)))
    # M5 T-nut screws into the column (2 on the far face)
    for z in (12, 30):
        arm = arm.cut(cq.Workplane("YZ").workplane(offset=-30).center(0, z).circle(2.75).extrude(30))
    # motor seat at the spin axis (x = ARM_REACH + EXTR/2)
    cx = ARM_REACH + EXTR/2 - EXTR/2
    arm = arm.cut(cq.Workplane("XY").center(cx, 0).circle(6.5).extrude(40).translate((0, 0, -5)))  # circlip / shaft-end clearance
    # 3 holes matching the shroud flange ears (shroud hangs under the arm, around the motor)
    for k in range(3):
        a = math.radians(120*k)
        arm = arm.cut(cq.Workplane("XY").center(cx + (SHROUD_ID/2 + 8)*math.cos(a), (SHROUD_ID/2 + 8)*math.sin(a)).circle(1.7).extrude(40).translate((0, 0, -5)))
    for pcd in MOTOR_HOLE_PCD:
        for k in range(2):
            a = math.radians(90*k + (0 if pcd == MOTOR_HOLE_PCD[0] else 45)) 
            for sgn in (1, -1):
                x = cx + sgn*pcd/2*math.cos(a); y = sgn*pcd/2*math.sin(a)
                arm = arm.cut(cq.Workplane("XY").center(x, y).circle(1.6).extrude(40).translate((0, 0, -5)))
    # central rib is interrupted over the motor screws so they stay accessible from above
    arm = arm.cut(cq.Workplane("XY").workplane(offset=t).center(cx, 0).circle(13).extrude(30))
    return arm

# ----------------------------------------------------------------------------- 3 shroud
def rotor_shroud():
    H = SHROUD_DROP + HUB_OD/2 + BOSS_H + MOTOR_STACK   # floor underside -> arm underside
    outer = cq.Workplane("XY").circle(SHROUD_ID/2 + SHROUD_WALL).extrude(H)
    inner = cq.Workplane("XY").workplane(offset=SHROUD_FLOOR).circle(SHROUD_ID/2).extrude(H)
    cup = outer.cut(inner)
    # flange with 3 screw ears to bolt under the motor arm
    fl = cq.Workplane("XY").workplane(offset=H - 4).circle(SHROUD_ID/2 + 12).extrude(4)
    fl = fl.cut(cq.Workplane("XY").workplane(offset=H - 5).circle(SHROUD_ID/2).extrude(10))
    cup = cup.union(fl)
    for k in range(3):
        a = math.radians(120*k)
        cup = cup.cut(cq.Workplane("XY").center((SHROUD_ID/2 + 8)*math.cos(a), (SHROUD_ID/2 + 8)*math.sin(a)).circle(1.7).extrude(H + 2))
    # Hall-latch boss at rotor-centre height: blind pocket from OUTSIDE, 0.6 mm skin left so
    # the containment wall stays closed (TO-92 / SIP-3 latch: 4.1 x 3 x 1.6 mm body)
    boss = cq.Workplane("XY").box(4.0, 9, 12).translate((SHROUD_ID/2 + SHROUD_WALL + 1.5, 0, SHROUD_DROP))
    cup = cup.union(boss)
    hall = cq.Workplane("XY").box(10, 4.6, 5.0).translate((SHROUD_ID/2 + 0.6 + 5.0, 0, SHROUD_DROP))
    cup = cup.cut(hall)
    # no viewing windows: the shroud is the containment for a 34 g magnet at 12 m/s rim speed
    return cup

# ----------------------------------------------------------------------------- 4 column foot
def column_foot():
    base = cq.Workplane("XY").rect(160, 120).extrude(6).edges("|Z").fillet(8)
    sock = cq.Workplane("XY").rect(EXTR + 10, EXTR + 10).extrude(30).translate((-50, 0, 0))
    foot = base.union(sock)
    foot = foot.cut(cq.Workplane("XY").rect(EXTR + 0.4, EXTR + 0.4).extrude(40).translate((-50, 0, 6)))
    foot = foot.cut(cq.Workplane("XY").center(-50, 0).circle(2.75).extrude(10).translate((0, 0, -1)))   # M5 into the profile core
    for (x, y) in [(70, 50), (70, -50), (-70, 50), (-70, -50)]:
        foot = foot.cut(cq.Workplane("XY").center(x, y).circle(2.2).extrude(10).translate((0, 0, -1)))
    return foot

# ----------------------------------------------------------------------------- 5 vessel cradle
def vessel_cradle():
    c = cq.Workplane("XY").circle(JAR_OD/2 + 8).extrude(12)
    c = c.cut(cq.Workplane("XY").workplane(offset=3).circle(JAR_OD/2 + 0.4).extrude(20))
    # crosshair centring marks (match the alignment gauge)
    for a in (0, 90):
        c = c.cut(cq.Workplane("XY").box(JAR_OD + 20, 1.0, 1.0).rotate((0, 0, 0), (0, 0, 1), a).translate((0, 0, 3)))
    return c

# ----------------------------------------------------------------------------- 6 float shell
def float_shell():
    R, r_in = FLOAT_OD/2, FLOAT_OD/2 - FLOAT_WALL
    shell = cq.Workplane("XY").sphere(R).cut(cq.Workplane("XY").sphere(r_in))
    seat = cq.Workplane("XY").sphere(FLOAT_MAG/2 + 1.0)             # spherical seat
    # three radial webs to hold the seat
    webs = None
    for k in range(3):
        w = cq.Workplane("XY").box(r_in*2, 0.8, r_in*2).rotate((0, 0, 0), (0, 0, 1), 60*k)
        webs = w if webs is None else webs.union(w)
    webs = webs.intersect(cq.Workplane("XY").sphere(r_in + 0.1))
    body = shell.union(seat).union(webs).cut(cq.Workplane("XY").sphere(FLOAT_MAG/2 + 0.05))
    upper = body.cut(cq.Workplane("XY").box(50, 50, 50).translate((0, 0, -25)))
    lower = body.cut(cq.Workplane("XY").box(50, 50, 50).translate((0, 0, 25)))
    return upper, lower

# ----------------------------------------------------------------------------- 7 gauge
def align_gauge():
    # sits in the vessel cradle (OD = jar OD) and has a 6 mm centre hole + 1 mm crosshair
    g = cq.Workplane("XY").circle(JAR_OD/2).extrude(4)
    g = g.cut(cq.Workplane("XY").circle(1.0).extrude(10).translate((0, 0, -1)))
    g = g.union(cq.Workplane("XY").circle(4).extrude(80).cut(cq.Workplane("XY").circle(1.0).extrude(90)))
    return g

if __name__ == "__main__":
    up, lo = rotor_hub()
    save(up, f"rotor_hub_upper_a{int(ALPHA)}")
    save(lo, f"rotor_hub_lower_a{int(ALPHA)}")
    save(motor_arm(), "motor_arm")
    save(rotor_shroud(), "rotor_shroud")
    save(column_foot(), "column_foot")
    save(vessel_cradle(), "vessel_cradle")
    fu, fl = float_shell()
    save(fu, "float_shell_upper"); save(fl, "float_shell_lower")
    save(align_gauge(), "align_gauge")
