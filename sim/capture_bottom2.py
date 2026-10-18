import numpy as np, json
from labsim import build, run
from capture_bottom import shell_system, FLOOR
rng = np.random.default_rng(11)
res = {}
for f in [45, 60]:
    s = shell_system(f)
    for label, kw, z0 in [("at-speed, floater released mid-liquid 6.5 cm", dict(t_ramp=1e-4), 0.065),
                          ("at-speed, vessel lowered from +6 cm onto stand, floater mid", dict(t_ramp=1e-4, floor_z=0.060, floor_v=-(0.060-FLOOR)/3.0, floor_T=3.0), 0.075),
                          ("spin-up 0->f in 2 s, floater on floor, mu=0.05 (PTFE)", dict(t_ramp=2.0, mu_c=0.05), None)]:
        outc = []
        for k in range(4):
            kk = dict(floor_z=FLOOR, floor_side=-1, wall_R=0.028, rotor_R=0.0); kk.update(kw)
            P = build(s, **kk)
            y0 = np.zeros(13); y0[0:2] = rng.normal(0, 0.003, 2)
            y0[2] = (FLOOR + s.R) if z0 is None else z0
            mh = rng.normal(size=3); y0[6:9] = mh/np.linalg.norm(mh)
            T, Y, hit = run(y0, P, 8.0, 4e-6, 4000)
            n = len(T)//6; z = Y[-n:, 2]
            lev = z.min() > FLOOR + s.R + 1e-3 and np.ptp(z) < 2e-3
            outc.append(f"LEV {z.mean()*1e3:.1f}mm" if lev else f"no ({z.mean()*1e3:.1f})")
        res[f"{f}Hz: {label}"] = outc
        print(f, label, outc, flush=True)
json.dump(res, open('capture_bottom2.json', 'w'), indent=1)
