# Six Avatars — v5: world in metres, movement, stability

> v5 moves the village from abstract coordinates to a world in **metres** and adds fixed places, a physical cost for movement and a daily rhythm. It publishes one 20,000-tick run with these features on and the results of the checks run on it. **Narration is off in this release.**

## What this is

The same six avatars as v1–v4 (BlueY, OrangeZ, GreenX, ChocoS, PurpleO, RediS), driven by the hormone / memory / relationship engine. What changed is the world they live in:

| | v1–v4 | v5 |
|---|---|---|
| World | 100 x 100 grid, abstract units | the same layout at 1 unit = 10 m: 1000 x 1000 m (1 km²), positions in metres |
| Places | zones (and resource nodes) | the same zones plus 15 fixed named places: a home per avatar and 9 shared places |

The v5 run switches on these optional behaviours (all of them are off by default in the engine):

- avatars choose a place in the zone their decision points to, walk there, stop on arrival, stay a few ticks and then move on;
- walking speed depends on the avatar's state, and distance costs energy and fatigue;
- fatigue and sleep follow a daily rhythm; sleeping at home is part of the behaviour.

Decisions are still taken once per tick (4 simulated hours). The world, movement and daily-rhythm work behind v5 does not modify the action selection logic: those layers decide *where* and *how*, the engine decides *what*. Some of the switched-on features (for example goal semantics and the micro-action ordering) do influence which goals an avatar pursues and in what order.

## What's in this folder

| file | what it is |
|---|---|
| `map_log_flags_on_20k.txt` | 20,000-tick run (about 9 simulated years), v5 features on, narrator off. Header `World : 1000x1000`. One line per avatar per tick: position (metres), zone, action, energy / cortisol / dopamine / valence (E, C, D, V), and event markers. |

Only the map log is published for v5. **Positions in this file are in metres.** The map logs of v3 and v4 are on a 100 x 100 grid in abstract units (the v5 world is that layout at 1 unit = 10 m); do not compare positions directly without converting. `tools/map_replay/map_replay.html` reads both conventions from the `World` line in the header.

## Run configuration

6 avatars, 20,000 ticks, 4 simulated hours per tick, world 1000 x 1000 m, faithful engine mode (the mode of the earlier 20,000-tick reference run). Behaviour features switched on: walking and arrival, physical movement cost, daily fatigue/sleep rhythm, fixed places, movement resonance, spatial and activity commitment, goal semantics and goal synergy, micro-action ordering after the world step and a micro-action stay decision. Features not part of this run: narration, memory maturation, multiple regions, place context.

## Results

### Run completed

- 20,000 of 20,000 ticks written, no errors, no NaN / infinite values in the map and event logs.
- Wall time on the author's workstation (Windows, MSYS2 UCRT64): 4,640 s with v5 features on (3,200 s for the same length with them off, in the previous 100 x 100 world). One run each; not a benchmark.

### Behaviour over the run

The run is split into ten windows of 2,000 ticks. Metric definitions are below the table.

| window | at a place % | places / day | km / day | zone changes / 100 | reversals % | nearby pairs / 100 | energy mean | energy p05 |
|---|---|---|---|---|---|---|---|---|
| 1 | 67.57 | 1.88 | 1.10 | 33.72 | 49.30 | 17.41 | 0.64 | 0.23 |
| 2 | 67.19 | 1.85 | 1.08 | 32.34 | 49.48 | 16.90 | 0.64 | 0.24 |
| 3 | 67.22 | 1.86 | 1.04 | 31.54 | 47.85 | 17.10 | 0.65 | 0.24 |
| 4 | 68.17 | 1.86 | 1.10 | 33.39 | 50.25 | 17.99 | 0.65 | 0.25 |
| 5 | 67.40 | 1.86 | 1.10 | 33.93 | 49.53 | 17.79 | 0.64 | 0.23 |
| 6 | 66.28 | 1.83 | 1.10 | 33.84 | 47.24 | 17.21 | 0.64 | 0.25 |
| 7 | 67.59 | 1.85 | 1.09 | 33.46 | 49.03 | 17.14 | 0.65 | 0.25 |
| 8 | 66.83 | 1.85 | 1.08 | 32.84 | 49.22 | 17.05 | 0.64 | 0.23 |
| 9 | 66.93 | 1.86 | 1.08 | 32.73 | 47.82 | 16.51 | 0.63 | 0.23 |
| 10 | 67.43 | 1.81 | 1.10 | 33.31 | 50.67 | 15.79 | 0.64 | 0.23 |


Energy is stable on average but varies widely within the run: the standard deviation is 0.235, values range from 0.00 to 1.00 (p05 0.24, p50 0.65, p95 1.00), and Rest ticks average about 0.82 while other actions average between 0.53 and 0.60. Autocorrelation is 0.88 at lag 1 tick and drops to 0.00 by lag 60 ticks (10 days), showing a mean-reverting process rather than a flattened variable. Per-avatar means range from 0.57 (RediS) to 0.72 (GreenX), and per-avatar window means drift between 0.59 and 0.64 across the run.

First window to last window: time at a place −0.2 %, places per day −4 %, km per day +0 %, zone changes −1 %, reversals +3 %, nearby pairs −9 %, energy mean and p05 +0 %. The largest change is −9 % in nearby pairs; places per day fall 4 % and reversals rise 3 %; every other metric changes by less than 1.5 %.

A 400-tick run of the previous version (before the move to metres) gave 67 % of time at a place, 1.84 places per day and 1.08 km per day; the 20,000-tick figures above are close to these.

**Metric definitions** (per avatar unless stated):
- *at a place*: share of avatar-ticks within 15 m of one of the 15 fixed places.
- *places / day*: distinct places visited per simulated day (6 ticks).
- *km / day*: straight-line distance between each avatar's positions at consecutive ticks, summed per day (a lower bound on the distance actually walked).
- *zone changes / 100*: zone changes per 100 avatar-ticks.
- *reversals*: share of consecutive steps (each longer than 3 m) in which the heading turns by more than 120°.
- *nearby pairs / 100*: avatar pairs within 180 m, per 100 pair-ticks.
- *energy*: the avatar's energy level (0–1), mean and 5th percentile.

The acceptance bands used to judge this run (for example 55–80 % at a place) were set by the author from shorter runs. They are internal checks, not external benchmarks.

### Compared with the previous reference

With v5 features off and the world set back to the old 100 x 100 grid, the current engine reproduces the earlier 20,000-tick reference run exactly: 64 output items compared (map log, event log, action-probability log, memory, DAI, world snapshot and all hormone logs), wall-clock timestamps ignored. This shows that the changes in v5 do not alter earlier behaviour when switched off (for this configuration).

### Engine checks

- Test suite: 64 tests, 62 passed, 0 failed, 2 skipped (two end-to-end tests that need Linux/WSL).
- Output parity between the Python engine and the C++ port: 7/7 output categories, with all features off (40 ticks) and with 15 features on (60 ticks), in the world in metres. These parity runs are short.

## Limitations

- Six avatars only. Behaviour at larger populations has not been measured.
- The Unreal Engine side has not been built or tested. Nothing here shows how the behaviour looks when embodied in a 3D scene.
- Narration is off. Memory maturation, multiple regions and place context were not part of this run.
- The behaviour results above come from one 20,000-tick run and one 400-tick baseline. Other configurations were not run at full length.
- Only the map log is published: the position, zone, action and energy / cortisol / dopamine / valence of each avatar at each tick. Schedules and other per-tick outputs are not published.