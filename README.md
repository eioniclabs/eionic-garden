# EIONIC-Labs

**Modular simulation engine for autonomous agents — bounded stochastic agency.**

> Can life-like behaviour emerge from rich internal blueprints, physiological dynamics, memory systems, and environmental interaction—without using an LLM as the cognitive core?

---

## About

EIONIC is an experimental **Artificial Life (ALife)** research project exploring how complex, persistent, and adaptive behaviour can emerge from rich internal architectures rather than from Large Language Models acting as the cognitive core.

The project focuses on autonomous agents with:

- Internal physiology (hormonal system)
- Memory dynamics
- Personality development
- Procedural decision making
- Long-term behavioural stability

Simulation runs have already completed **tens of thousands of simulation ticks**, spanning multiple in-game years while exhibiting measurable behavioural divergence between autonomous agents.

Although the current prototype is implemented in Python, the long-term objective is to integrate the simulation into **Unreal Engine 5**, allowing autonomous agents to exist as fully autonomous NPCs whose behaviour emerges from internal systems rather than scripted logic.

---

## Repository Status

This is the canonical development repository for **EIONIC**. 

The previous development repository became permanently inaccessible following an unrecoverable hardware failure. https://github.com/eionic/eionic-garden

The project itself has **not restarted from zero**. This repository continues several years of ongoing research, architecture refinement, experimentation, and simulation development.

Historical experiments, datasets, analyses, and documentation will be republished progressively as they are reviewed and reorganized.

---

## Research Philosophy

EIONIC explores Artificial Life through the interaction of multiple internal systems rather than relying on a centralized reasoning model.

Instead of explicitly scripting behaviour, the project investigates how physiology, memory, personality, environmental interaction, and long-term experience collectively shape autonomous behaviour over time.

Every experiment published in this repository should be interpreted as part of that ongoing research.

---

## Repository Structure

Simulation/
├── README.md
│
├── assets/
│   ├── graphics/
│   ├── visualizations/
│   └── media/
│
├── data/
│   └── experiments/
│       ├── 3_Avatars_Initial/
│       │   ├── logs/
│       │   ├── statistics/
│       │   ├── analysis.md
│       │
│       ├── 6_Avatars/
│       │   ├── v1_old/
│       │   │   ├── logs/
│       │   │   ├── conversation_logs/
│       │   │   └── selftalk_logs/
│       │   │
│       │   ├── v2_latest/
│       │   │   ├── logs/
│       │   │   ├── conversation_logs/
│       │   │   ├── selftalk_logs/
│       │   │   ├── statistics/
│       │   │   └── analysis.md
│       │
│       └── README.md
│
├── docs/
│   ├── architecture/
│   ├── papers/
│   ├── research_notes/
│   └── archive/
│
└── tools/
    └── map_replay/
        ├── replay.html
        ├── replay_script.js
        └── README.md

Detailed experiment data, logs, analyses, and replay files are organized under the experiments directory as the project continues to evolve.

---

Research Data

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

---

Current Progress

Current prototype includes:

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

The current implementation focuses on validating the behavioural architecture before migration into a real-time interactive environment.

---

Future Direction

The next major milestone is integrating the simulation into Unreal Engine 5.

Rather than replacing the existing simulation engine, Unreal Engine will serve as the embodiment and visualization layer for autonomous agents while the underlying behavioural architecture remains independent from the rendering layer.

Future development aims to explore:

- Fully autonomous NPCs
- Persistent simulated worlds
- Real-time embodied interaction
- Large-scale visualization
- Interactive debugging tools
- Research validation through Unreal Engine 5

---

Tools

Map Replay

A lightweight HTML-based replay tool is available in [`tools/map_replay/`](tools/map_replay/) to visualize simulation logs and agent movements.

**How to use:**
1. Open `tools/map_replay/replay.html` in your browser.
2. Load a valid `map_log.txt` file (located in `data/experiments/.../logs/`).
3. Use the playback controls to step through ticks or play the simulation.

This tool requires no server or internet connection, it runs entirely client-side.

---

Experimental Nature

EIONIC is an active research project.

Architectures, parameters, and experimental protocols will continue evolving as new findings emerge.

Negative results, unexpected behaviours, and failed experiments are considered valuable research outcomes and may also be published.

---

License

See the "LICENSE" file.

«History can be lost. Research should not be.»