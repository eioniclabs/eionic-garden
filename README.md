# EIONIC-Labs

Modular simulation engine for autonomous agents — bounded stochastic agency.

> Can life-like behaviour emerge from rich internal blueprints, physiological dynamics, memory systems, and environmental interaction—without using an LLM as the cognitive core?

---

## About

EIONIC is an experimental Artificial Life (ALife) research project exploring how complex, persistent, and adaptive behaviour can emerge from rich internal architectures rather than from Large Language Models acting as the cognitive core.

The project focuses on autonomous agents with:

- Internal physiology (hormonal system)
- Memory dynamics
- Personality development
- Procedural decision making
- Long-term behavioural stability

Simulation runs have already completed up to 20,000 ticks in a single published run, spanning about 9 simulated years while exhibiting measurable behavioural divergence between autonomous agents.

The engine has been ported from Python to C++. The C++ port is the primary deployment target; development follows a Python-first, C++-mirror workflow. The long-term objective is to integrate the simulation into Unreal Engine 5, allowing autonomous agents to exist as fully autonomous NPCs whose behaviour emerges from internal systems rather than scripted logic.

---

## Repository Status

This is the canonical development repository for EIONIC.

The previous development repository became permanently inaccessible following an unrecoverable hardware failure.

https://github.com/eionic/eionic-garden

The project itself has not restarted from zero. This repository continues several years of ongoing development, architecture refinement, experimentation, and simulation development.

Historical experiments, datasets, analyses, and documentation will be republished progressively as they are reviewed and reorganized.

---

## Engine Port Status

The EIONIC engine has been ported from Python to C++.

### Port status

- Parity with Python engine: 7/7 output categories matched (hormone log, world snapshot, map log, event log, action-probability log, memory, DAI)
- Test suite: 64 tests — 62 passed, 0 failed, 2 skipped (two end-to-end tests that need Linux/WSL)
- Parity re-verified after the v5 changes, with all behaviour flags off and with 15 flags on (short runs: 40 and 60 ticks)
- 20,000-tick regression: with the v5 features off and the previous 100x100 world, identical to the earlier reference run (64 output items compared, timestamps ignored)
- Determinism verified: two runs with identical seed produce byte-identical output, excluding wall-clock timestamps

### Known differences from Python

- Micro-action tie-break: the C++ port uses a fixed rule. Python used string-set ordering, which varied between processes. See v3 README for details.

First published C++ run: **6 Avatars, v3 — 3,500 ticks + 20,000-tick stability check.**

Latest release: **6 Avatars, v5 — world in metres, fixed places, behaviour flags on, 20,000-tick stability run** (see below).

---

## What's new in v5

v5 moves the simulated village from abstract coordinates to a world in **metres**, so that what the engine does can be mapped onto a real-time 3D scene later.

- **World in metres.** 1000 x 1000 m (1 km²). Earlier map logs (v3 and v4) use a 100 x 100 grid in abstract units; the v5 world is the same layout scaled so that one old unit is 10 m, and v5 map logs record positions in metres.
- **Fixed places.** 15 named places (a home for each avatar plus shared places in the five zones). Avatars choose where to go from the places in the zone their decision points to, stay for a while, and move on.
- **Movement with a physical cost.** Walking speed depends on the avatar's state, and distance costs energy and fatigue. Avatars stop when they arrive instead of drifting.
- **A daily rhythm.** Fatigue and sleep follow a day/night cycle; sleeping at home is part of the behaviour.
- **Each 4-hour decision is expanded into a schedule** (walk, stay, sleep, talk) intended for a real-time 3D client to play back (a 2D viewer plays it back today). This schedule is derived from the decision; it does not add new decisions. It is **not published** in this repository.
- **Stability.** A 20,000-tick run with these features on (about 9 simulated years) completed without errors, and the behavioural metrics stayed within a narrow range (the largest change between the first and last 2,000 ticks was −9 % in how often two avatars are near each other). Details in [`v5`](data/experiments/6_Avatars/v5/).

**Terminology used in this README:**

- **Faithful engine mode:** A run mode (`--faithful`) in which three optional fixes (`valence_fix`, `nearby_fix`, `snapshot_real`) are off. With the behaviour flags also off, the C++ output follows the original Python engine (the one exception is the micro-action tie-break, see Known differences). It is the mode used for parity testing and for the historical reference runs. The v5 run uses this mode with the v5 behaviour flags switched on, so its behaviour differs from the original Python engine by design.
- **Micro-action ordering:** Within each 4-hour tick the avatar has four hourly micro-steps (for example `internalize`, `avoid`, `connect`, `hold`), drawn from the pool of the action it chose. In the original order they are picked before the world resolves the action; in v5 they are picked after, so they reflect what actually happened (for example that nobody was there to talk to). The v5 run also lets the avatar decide, after its micro-steps, whether to stay at the place of its errand for another tick. Micro-steps do not change the action chosen for the tick.
- **Goal semantics:** Instead of a goal ending the moment an avatar reaches its target zone, a goal ends when the need that raised it is actually relieved. Goals can be deferred, time out, or become moot.

The Unreal Engine side has **not been built or tested yet**. What exists is the engine-side output that such a client would read.

---

## Research Philosophy

EIONIC explores Artificial Life through the interaction of multiple internal systems rather than relying on a centralized reasoning model.

Instead of explicitly scripting behaviour, the project investigates how physiology, memory, personality, environmental interaction, and long-term experience collectively shape autonomous behaviour over time.

Every experiment published in this repository should be interpreted as part of that ongoing research.

---

## Repository Structure

```text
eionic-garden/
├── README.md
├── license.txt
├── ATTRIBUTION-OEWN.md
│
├── assets/
│   ├── graphics/
│   │   ├── baseline/
│   │   │   └── grafik_analisis_avatar*.png
│   │   └── enhanced-model/
│   │       └── Plot_*.png
│   └── visual/
│       └── *.mp4
│
├── data/
│   └── experiments/
│       ├── 3_avatars_initial/
│       │   ├── 11557 ticks.xlsx
│       │   ├── logs/
│       │   │   ├── baseline/
│       │   │   │   └── multi_avatar_hormones_log*.txt
│       │   │   └── enhanced-model/
│       │   │       └── multi_avatar_hormones_log_60_*.txt
│       │   └── statistics/
│       │       ├── action_diversity
│       │       ├── action_evolution
│       │       ├── hormone_entropy
│       │       └── readme.md
│       │
│       └── 6_Avatars/
│           ├── v1/
│           │   ├── Six_Avatars.xlsx
│           │   └── graphics/
│           │       └── avatar_*.png
│           ├── v2/
│           │   ├── conversation_log.txt
│           │   ├── eionic_analysis_6_ava_newconvo.xlsx
│           │   ├── event_log.txt
│           │   ├── inner_log.txt
│           │   ├── narrative_log.txt
│           │   └── graphics/
│           │       └── avatar_*.png
│           ├── v3/
│           │   ├── README.md
│           │   ├── SixAvatars_v3.xlsx
│           │   ├── map_log.txt
│           │   ├── stability.csv
│           │   ├── stability_report.py
│           │   └── stability_report.txt
│           ├── v4/
│           │   ├── README.md
│           │   ├── baseline.xlsx
│           │   ├── narrated.xlsx
│           │   ├── map_log_base.txt
│           │   ├── map_log_narrated.txt
│           │   ├── narrative_log.txt
│           │   ├── conversation_log.txt
│           │   └── inner_log.txt
│           │
│           └── v5/
│               ├── README.md
│               └── map_log_flags_on_20k.txt
│
├── docs/
│   ├── architecture/
│   │   └── eionic_architecture.docx
│   └── research/
│       ├── eionic - bounded stochastic agency.pdf
│       ├── eionic_whitepaper.pdf
│       └── README_old.md
│
└── tools/
    ├── README.md
    └── map_replay/
        ├── map_log.txt
        ├── map_replay.html
        └── readme.md
```

Detailed experiment data, logs, analyses, and replay files are organized under the experiments directory as the project continues to evolve.

---

## Research Data

This repository progressively publishes:

- Simulation logs
- Conversation logs
- Self-talk logs
- Statistical analyses
- Experimental datasets
- Replay tools
- Behaviour visualizations
- Research documentation

The objective is to make experimental results as transparent, inspectable, and reproducible as possible.

**What is and is not published.** This repository publishes aggregated analyses, the logs listed under each experiment, map logs, and replay tools. The engine source code and detailed structured per-tick outputs are not published.

---

## Experiments

- [v1](data/experiments/6_Avatars/v1/) — first six-avatar run
- [v2](data/experiments/6_Avatars/v2/) — conversation logging
- [v3](data/experiments/6_Avatars/v3/) — stability analysis
- [v4](data/experiments/6_Avatars/v4/) — **lexicon narration**. First release where narration is generated locally by a lexicon instead of an external language model.
- [v5](data/experiments/6_Avatars/v5/) — **world in metres + movement**. Fixed places, physical movement cost, daily rhythm; 20,000-tick stability run. Narration is off in this release.

---

## Current Progress

Current implementation includes:

- Long-running autonomous simulations
- Internal physiology
- Episodic and procedural memory
- Personality divergence
- Multi-agent interaction
- Conversation system
- Self-talk system
- Statistical logging
- Replay visualization
- Epoch-based world priors
- C++ engine port (parity 7/7 with Python; 62 of 64 tests passed, 2 skipped)
- World in metres with fixed places, physical movement cost and a daily rhythm (v5)
- Determinism verification (byte-identical output across runs)

The current implementation focuses on validating the behavioural architecture before migration into a real-time interactive environment.

---

## Future Direction

The next major milestone is integrating the simulation into Unreal Engine 5.

Rather than replacing the existing simulation engine, Unreal Engine will serve as the embodiment and visualization layer for autonomous agents while the underlying behavioural architecture remains independent from the rendering layer.

The engine already produces, for each decision, a schedule and a stream intended for a real-time client. The Unreal side (placing the places in a level, walking, animation, playback and catch-up) has not been started. By design the engine stays authoritative: a client may lag behind and catch up without affecting the simulation (not yet exercised with an Unreal client).

Future development aims to explore:

- Fully autonomous NPCs
- Persistent simulated worlds
- Real-time embodied interaction
- Large-scale visualization
- Interactive debugging tools
- Research validation through Unreal Engine 5

---

## Tools

### Map Replay

A lightweight HTML-based replay tool is available in `tools/map_replay/` to visualize simulation logs and agent movements.

### How to use

1. Open `tools/map_replay/map_replay.html` in your browser.
2. Load a valid `map_log.txt` file (for example the one in `data/experiments/6_Avatars/v5/`).
3. Use the playback controls to step through ticks or play the simulation.

This tool requires no server or internet connection; it runs entirely client-side.

It reads both coordinate conventions: logs up to v4 (header `World : 100x100`) and v5 logs (header `World : 1000x1000`, positions in metres). Both are drawn on the same square; positions from the two conventions differ by a factor of 10 and are not directly comparable without converting.

---

## Experimental Nature

EIONIC is an active research project.

Architectures, parameters, and experimental protocols will continue evolving as new findings emerge.

Negative results, unexpected behaviours, and failed experiments are considered valuable research outcomes and may also be published.

---

## License

See [`license.txt`](license.txt).

---

## Attribution

The v4 lexicon uses data from **Open English WordNet** (2025 Edition),
licensed under CC BY 4.0. See [`ATTRIBUTION-OEWN.md`](ATTRIBUTION-OEWN.md)
for details.

---

> *“History can be lost. Research should not be.”*
