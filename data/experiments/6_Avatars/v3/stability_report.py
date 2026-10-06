#!/usr/bin/env python3
"""
stability_report.py - long-run stability metrics from EIONIC logs (stdlib only).

USAGE
  python stability_report.py PATH [--window 500] [--csv report.csv]

PATH can be:
  * a folder with multi_avatar_hormones_log_*.txt   (PREFERRED: 3-decimal values,
    cortisol/dopamine/serotonin/oxytocin/adrenaline/melatonin + energy/fatigue/
    valence/shadow/somatic/DAI/tension, zone and action per avatar per tick)
  * a single multi_avatar_hormones_log_NNN.txt file
  * a map_log.txt file, or a folder containing one  (published log; 2 decimals;
    only energy/cortisol/dopamine/valence + zone/action)
If a folder has both, the hormones logs are used.

WHAT IT MEASURES (per window of N ticks, pooled over avatars)
  mean and sd of each hormone, % of avatar-ticks stuck at the floor (<=0.005) or
  ceiling (>=0.995), action entropy (bits), zone shares, and between-avatar
  spread of cortisol (do avatars stay different from each other?).
Then it prints heuristic flags (thresholds are at the top of this file and are
rules of thumb, not scientific constants): SATURATION, ABSORBING ZONE, ENTROPY
COLLAPSE, HOMOGENIZATION, DRIFT, or STATIONARY.
"""
import argparse, csv, glob, math, os, re, sys
from collections import Counter, defaultdict

# ---- heuristic thresholds (edit freely) -------------------------------------
FLOOR, CEIL = 0.005, 0.995
SAT_PCT = 50.0            # >= this % of avatar-ticks at floor/ceiling in the last window
ABSORB_PCT = 95.0         # one zone holds >= this % of avatar-ticks in the last window
ENTROPY_DROP = 0.85       # last-window entropy < this fraction of first-window entropy
SPREAD_DROP = 0.5         # last-window cortisol spread < this fraction of first-window
DRIFT_ABS = 0.15          # |mean(last) - mean(first)| above this = drift
STATIONARY_ABS = 0.03     # all |changes| below this = stationary
VAL_NEAR_CAP = 0.7        # |mean valence| above this in last window is flagged
# -----------------------------------------------------------------------------

ZONES = ["sanctuary", "nexus", "void", "chaos_field", "earth_zone"]
UNIT_FIELDS = ["energy", "fatigue", "cortisol", "dopamine", "serotonin",
               "oxytocin", "adrenaline", "melatonin", "shadow", "somatic"]
ALL_FIELDS = UNIT_FIELDS + ["valence", "dai", "tension"]
# Floor-saturation only counts for variables that are supposed to hover mid-range.
# shadow/somatic are "load" variables: sitting at 0 just means no load, which is normal.
HOMEOSTATIC = {"energy", "fatigue", "cortisol", "dopamine", "serotonin",
               "oxytocin", "adrenaline", "melatonin"}


def norm_zone(s):
    for z in ZONES:
        if z.startswith(s) or s.startswith(z):
            return z
    return s


F = r"(-?\d+\.\d+)"
RE_STATE = re.compile(r"^\s+(\S+)\s+(\S+)\s+(\([^)]*\)|\S+)\s+" + F + r"\s+" + F +
                      r"\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+" + F + r"\s+" + F + r"\s*$")
RE_HORM = re.compile(r"^\s+(\S+)" + (r"\s+" + F) * 6 + r"\s*$")
RE_MEM = re.compile(r"^\s+(\S+)\s+(\S+)\s+" + F + r"\s+" + F + r"\s+([+-]\d+\.\d+)\s+.*$")
RE_MAP = re.compile(r"^\s{2}(\S+)\s+\(\s*[\d.]+,\s*[\d.]+\)\s+(\S+)\s+(\S+)\s+"
                    r"E:([\d.]+)\s+C:([\d.]+)\s+D:([\d.]+)\s+V:([+-][\d.]+)")


def parse_hormone_file(path, rows):
    tick, section, in_snap = None, None, False
    with open(path, encoding="utf-8", errors="replace") as f:
        for line in f:
            if in_snap:
                if line.startswith("-- END_SNAPSHOT_JSON"):
                    in_snap = False
                continue
            if line.startswith("TICK="):
                m = re.match(r"TICK=(\d+)", line)
                tick, section = (int(m.group(1)) if m else None), None
                continue
            if line.startswith("-- SNAPSHOT_JSON"):
                in_snap = True
                continue
            if line.startswith("-- "):
                section = line[3:].split()[0] if line[3:].strip() else None
                continue
            if tick is None or section not in ("STATE", "HORMONES", "MEMORY"):
                continue
            if section == "STATE":
                m = RE_STATE.match(line)
                if m and m.group(1) != "NAME":
                    r = rows[(tick, m.group(1))]
                    r.update(zone=norm_zone(m.group(2)), energy=float(m.group(4)),
                             fatigue=float(m.group(5)), action=m.group(6),
                             dai=float(m.group(10)), tension=float(m.group(11)))
            elif section == "HORMONES":
                m = RE_HORM.match(line)
                if m and m.group(1) != "NAME":
                    r = rows[(tick, m.group(1))]
                    for k, i in zip(("cortisol", "dopamine", "serotonin", "oxytocin",
                                     "adrenaline", "melatonin"), range(2, 8)):
                        r[k] = float(m.group(i))
            elif section == "MEMORY":
                m = RE_MEM.match(line)
                if m and m.group(1) != "NAME":
                    r = rows[(tick, m.group(1))]
                    r.update(shadow=float(m.group(3)), somatic=float(m.group(4)),
                             valence=float(m.group(5)))


def parse_map_file(path, rows):
    tick = None
    with open(path, encoding="utf-8", errors="replace") as f:
        for line in f:
            m = re.match(r"T:(\d+)", line.strip())
            if m:
                tick = int(m.group(1))
                continue
            m = RE_MAP.match(line)
            if m and tick:
                r = rows[(tick, m.group(1))]
                r.update(zone=norm_zone(m.group(2)), action=m.group(3),
                         energy=float(m.group(4)), cortisol=float(m.group(5)),
                         dopamine=float(m.group(6)), valence=float(m.group(7)))


def load(path):
    rows = defaultdict(dict)
    if not os.path.exists(path):
        sys.exit("Path not found: %r\n"
                 "Current folder: %s\n"
                 "In Windows cmd use a path relative to the current folder (e.g. 20k) or a full path "
                 "(e.g. D:\\EION\\20k). The /d/EION/... style only works inside MSYS2."
                 % (path, os.getcwd()))
    if os.path.isdir(path):
        hl = sorted(glob.glob(os.path.join(path, "multi_avatar_hormones_log_*.txt")))
        if hl:
            for p in hl:
                parse_hormone_file(p, rows)
            return rows, "hormones log (%d file(s))" % len(hl)
        mp = os.path.join(path, "map_log.txt")
        if os.path.exists(mp):
            parse_map_file(mp, rows)
            return rows, "map_log.txt"
        sys.exit("No multi_avatar_hormones_log_*.txt or map_log.txt in %s" % path)
    if "map_log" in os.path.basename(path).lower():
        parse_map_file(path, rows)
        return rows, "map_log.txt"
    parse_hormone_file(path, rows)
    return rows, "hormones log (1 file)"


def mean_sd(xs):
    n = len(xs)
    if n == 0:
        return float("nan"), float("nan")
    m = sum(xs) / n
    return m, math.sqrt(sum((x - m) ** 2 for x in xs) / n)


def entropy(counter):
    n = sum(counter.values())
    return -sum(c / n * math.log2(c / n) for c in counter.values() if c) if n else float("nan")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("path", nargs="?", help="log folder/file (omit when using --from-csv)")
    ap.add_argument("--window", type=int, default=500, help="ticks per window (default 500)")
    ap.add_argument("--csv", help="write all window numbers to this CSV file")
    ap.add_argument("--from-csv", help="skip log parsing: recompute tables and verdict from a CSV "
                                       "written earlier by --csv")
    a = ap.parse_args()

    if a.from_csv:
        if not os.path.exists(a.from_csv):
            sys.exit("CSV not found: %r (current folder: %s)" % (a.from_csv, os.getcwd()))
        with open(a.from_csv, encoding="utf-8") as fh:
            stats = []
            for r in csv.DictReader(fh):
                stats.append({k: (v if k == "window" else float(v)) for k, v in r.items() if v != ""})
        if not stats:
            sys.exit("CSV is empty: %s" % a.from_csv)
        fields = [f for f in ALL_FIELDS if "mean_" + f in stats[0]]
        print("source: %s (%d windows, %d avatar-ticks per window)" % (a.from_csv, len(stats), int(stats[0]["n"])))
    else:
        if not a.path:
            sys.exit("Give a log folder/file, or use --from-csv stability.csv")
        rows, src = load(a.path)
        rows = {k: v for k, v in rows.items() if "zone" in v or "cortisol" in v}
        if not rows:
            sys.exit("Parsed 0 rows. Is this an EIONIC hormones log / map_log? "
                     "(expected 'TICK=' + '-- STATE/HORMONES' tables, or 'T:' + 'E:..C:..D:..V:..' lines)")
        ticks = sorted({t for t, _ in rows})
        names = sorted({n for _, n in rows})
        fields = [f for f in ALL_FIELDS if any(f in r for r in rows.values())]
        print("source: %s | ticks %d-%d (%d) | avatars: %s | rows: %d"
              % (src, ticks[0], ticks[-1], len(ticks), ", ".join(names), len(rows)))
        if src.startswith("map_log"):
            print("note: map_log has 2-decimal values and only energy/cortisol/dopamine/valence. "
                  "Use the hormones log for full detail.")

        W = a.window
        by_win = defaultdict(list)
        for (t, n), r in rows.items():
            by_win[(t - 1) // W].append((t, n, r))
        wins = sorted(by_win)
        # drop a trailing partial window (< 50% of W) so it does not distort the verdict
        if len(wins) > 1 and len({t for t, _, _ in by_win[wins[-1]]}) < W * 0.5:
            dropped = wins.pop()
            print("note: dropped partial last window (%d ticks)" % len({t for t, _, _ in by_win[dropped]}))
        if len(wins) < 2:
            print("warning: fewer than 2 full windows; use a smaller --window for meaningful trends.")

        stats = []
        for w in wins:
            items = by_win[w]
            s = {"window": "%d-%d" % (w * W + 1, (w + 1) * W), "n": len(items)}
            for f in fields:
                xs = [r[f] for _, _, r in items if f in r]
                m, sd = mean_sd(xs)
                s["mean_" + f], s["sd_" + f] = m, sd
                if f in UNIT_FIELDS and xs:
                    s["floor_" + f] = 100.0 * sum(x <= FLOOR for x in xs) / len(xs)
                    s["ceil_" + f] = 100.0 * sum(x >= CEIL for x in xs) / len(xs)
            ac = Counter(r["action"] for _, _, r in items if "action" in r)
            zc = Counter(r["zone"] for _, _, r in items if "zone" in r)
            s["action_entropy"] = entropy(ac)
            nz = sum(zc.values())
            for z in ZONES:
                s["zone_" + z] = 100.0 * zc.get(z, 0) / nz if nz else float("nan")
            s["zone_top_pct"] = max(s["zone_" + z] for z in ZONES) if nz else float("nan")
            per_tick = defaultdict(list)
            for t, _, r in items:
                if "cortisol" in r:
                    per_tick[t].append(r["cortisol"])
            sp = [mean_sd(v)[1] for v in per_tick.values() if len(v) > 1]
            s["cortisol_spread"] = sum(sp) / len(sp) if sp else float("nan")
            stats.append(s)

    show = [f for f in ("cortisol", "dopamine", "serotonin", "oxytocin", "adrenaline",
                        "melatonin", "energy", "fatigue", "valence") if f in fields]
    ab = {"cortisol": "Cort", "dopamine": "Dopa", "serotonin": "Sero", "oxytocin": "Oxyt",
          "adrenaline": "Adre", "melatonin": "Mela", "energy": "Ener", "fatigue": "Fati", "valence": "Val"}
    print("\nWINDOW MEANS (pooled over avatars)")
    print("%-12s" % "ticks" + "".join("%7s" % ab[f] for f in show) + "%7s" % "H(act)" + "  zones")
    for s in stats:
        z = sorted(ZONES, key=lambda z: -s["zone_" + z])[:3]
        print("%-12s" % s["window"] + "".join("%7.2f" % s["mean_" + f] for f in show)
              + "%7.2f" % s["action_entropy"] + "  "
              + " ".join("%s%d" % (x[:4], round(s["zone_" + x])) for x in z if s["zone_" + x] >= 1))

    sat_fields = [f for f in UNIT_FIELDS if "floor_" + f in stats[0]]
    def hit(s, f):
        return (f in HOMEOSTATIC and s["floor_" + f] >= 5) or s["ceil_" + f] >= 5
    stuck = [(f, s["window"]) for s in stats for f in sat_fields if hit(s, f)]
    print("\nSATURATION (%% of avatar-ticks at floor<=%.3f / ceiling>=%.3f; shown only if >=5%%; floor counts only for homeostatic variables)" % (FLOOR, CEIL))
    if not stuck:
        print("  none")
    else:
        for f in sat_fields:
            line = [(s["window"], s["floor_" + f] if f in HOMEOSTATIC else 0.0, s["ceil_" + f])
                    for s in stats if hit(s, f)]
            if line:
                print("  %-10s " % f + "  ".join("%s: %s" % (w, ("floor %.0f%%" % fl if fl >= 5 else "") +
                                                          (" ceil %.0f%%" % ce if ce >= 5 else ""))
                                               for w, fl, ce in line))
    print("\nBETWEEN-AVATAR CORTISOL SPREAD (sd across avatars, avg per tick)")
    print("  " + "  ".join("%s: %.3f" % (s["window"], s["cortisol_spread"]) for s in stats))

    # Compare the mean of the early quarter of windows with the late quarter, so one noisy
    # window cannot decide the verdict.
    q = max(1, len(stats) // 4)
    early, late = stats[:q], stats[-q:]

    def avg(group, key):
        v = [s[key] for s in group if key in s and not math.isnan(s[key])]
        return sum(v) / len(v) if v else float("nan")

    flags = []
    for f in sat_fields:
        if f in HOMEOSTATIC and avg(late, "floor_" + f) >= SAT_PCT:
            flags.append("SATURATION: %s at floor in %.0f%% of avatar-ticks (late windows)" % (f, avg(late, "floor_" + f)))
        if avg(late, "ceil_" + f) >= SAT_PCT:
            flags.append("SATURATION: %s at ceiling in %.0f%% of avatar-ticks (late windows)" % (f, avg(late, "ceil_" + f)))
    if "valence" in fields and abs(avg(late, "mean_valence")) >= VAL_NEAR_CAP:
        flags.append("SATURATION: mean valence %+.2f in the late windows (near its cap)" % avg(late, "mean_valence"))
    if avg(late, "zone_top_pct") >= ABSORB_PCT:
        z = max(ZONES, key=lambda z: avg(late, "zone_" + z))
        flags.append("ABSORBING ZONE: %s holds %.0f%% of avatar-ticks (late windows)" % (z, avg(late, "zone_top_pct")))
    e0, e1 = avg(early, "action_entropy"), avg(late, "action_entropy")
    if e1 < ENTROPY_DROP * e0:
        flags.append("ENTROPY COLLAPSE: action entropy %.2f -> %.2f bits (early -> late)" % (e0, e1))
    s0, s1 = avg(early, "cortisol_spread"), avg(late, "cortisol_spread")
    if not math.isnan(s0) and s0 > 0 and s1 < SPREAD_DROP * s0:
        flags.append("HOMOGENIZATION: cortisol spread across avatars %.3f -> %.3f (early -> late)" % (s0, s1))
    deltas = {f: avg(late, "mean_" + f) - avg(early, "mean_" + f) for f in fields if f not in ("dai", "tension")}
    for f, d in deltas.items():
        if abs(d) > DRIFT_ABS:
            flags.append("DRIFT: mean %s moved %+.2f (early -> late)" % (f, d))
    # window-to-window noise, for context
    noise = {f: mean_sd([s["mean_" + f] for s in stats])[1] for f in deltas}
    big = max(deltas, key=lambda f: abs(deltas[f]))
    print("\nVERDICT (heuristic; early %d vs late %d windows of %d)" % (q, q, len(stats)))
    if flags:
        for x in flags:
            print("  - " + x)
    elif all(abs(d) < STATIONARY_ABS for d in deltas.values()):
        print("  - STATIONARY: no saturation, no collapse. Largest early->late change: %s %+.3f "
              "(window-to-window sd of that variable: %.3f)." % (big, deltas[big], noise[big]))
        print("    Stable, but also not evolving: the averages do not move over the whole run.")
    else:
        print("  - No collapse flags. Largest early->late change: %s %+.3f (window-to-window sd %.3f); inspect the table."
              % (big, deltas[big], noise[big]))

    if a.csv:
        cols = sorted({k for s in stats for k in s}, key=lambda k: (k != "window", k != "n", k))
        with open(a.csv, "w", newline="", encoding="utf-8") as fh:
            wr = csv.DictWriter(fh, fieldnames=cols)
            wr.writeheader()
            for s in stats:
                wr.writerow({k: ("%.6g" % v if isinstance(v, float) else v) for k, v in s.items()})
        print("\nCSV written: %s" % a.csv)


if __name__ == "__main__":
    main()
