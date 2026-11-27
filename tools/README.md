# Map Replay Tool

A lightweight, client-side HTML tool for visualizing agent movement and zone activity from Eionic simulation logs.

---

## How to Use

1. Open `map_replay.html` in any modern browser (Chrome, Firefox, Edge, etc.).
2. Click "Load map_log.txt" and select a `map_log.txt` file from an experiment folder.
3. Use the playback controls:
   - **PLAY** — run the log continuously (press again to pause)
   - **Previous / next buttons** — step tick by tick
   - **SPEED** — cycles through the playback speeds
   - **Scrubber** — jump to any tick
4. Agent positions and zone boundaries will be rendered on the map.

---

## Requirements

- No server needed — runs entirely in your browser.
- No internet connection required.
- The parser handles the map logs of v3, v4 and v5 and the bundled sample.
- Reads both coordinate conventions: logs up to v4 (header `World    : 100x100`) and v5 logs (header `World    : 1000x1000`, positions in metres). The header decides; the map is always drawn on the same square.

---

## File Format

The tool expects a `map_log.txt` file in the format the engine writes: a header (`World`, `Zones`, `Avatars`, ...) followed by one block per tick, with one line per avatar. Columns: position, zone, action, energy / cortisol / dopamine / valence (E, C, D, V), and an optional event marker. Example from the v3 log:

```text
T:000002 | 2026-09-15 07:02 | waxing_crescent
  BlueY      ( 21.0, 23.3)  sanctuary     Seek          E:0.55  C:0.79  D:0.81  V:+0.10 →vitality_node
  OrangeZ    ( 80.0, 24.1)  void          Confront      E:0.51  C:0.90  D:0.63  V:-0.29 →self_loop
  GreenX     ( 25.3, 75.3)  earth_zone    Withdraw      E:0.51  C:0.54  D:0.64  V:+0.11
```

In v5 logs the positions are in metres.
