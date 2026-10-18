"""Host script: step the rotor through a list of frequencies and record the controller log.
Pair each step with a video segment (or a manual height reading) to build the measured
height-vs-frequency curve that is compared with sim/design_chart_*.json.

  python freq_sweep.py /dev/ttyUSB0 --freqs 230 220 210 200 190 180 170 160 --dwell 20
Requires pyserial.  Always ends in LAND (not STOP) for safety.
"""
import argparse, time, serial, sys
ap = argparse.ArgumentParser()
ap.add_argument("port"); ap.add_argument("--freqs", nargs="+", type=float, required=True)
ap.add_argument("--dwell", type=float, default=20.0); ap.add_argument("--rate", type=float, default=5.0)
ap.add_argument("--out", default="sweep_log.csv")
a = ap.parse_args()
s = serial.Serial(a.port, 115200, timeout=0.1); time.sleep(2.0)
def cmd(c):
    s.write((c + "\n").encode()); time.sleep(0.05)
cmd(f"RATE {a.rate}"); cmd("LOG 1")
with open(a.out, "w") as fh:
    fh.write("step_hz,t_ms,setpoint_hz,measured_hz,throttle_us\n")
    try:
        for f in a.freqs:
            print(f"-> {f} Hz"); cmd(f"S {f}")
            t_end = time.time() + a.dwell
            while time.time() < t_end:
                ln = s.readline().decode(errors="ignore").strip()
                if ln and ln[0].isdigit():
                    fh.write(f"{f},{ln}\n")
    finally:
        print("landing"); cmd("L"); cmd("LOG 0")
