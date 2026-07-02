# TRAE Loop Engineering

A TRAE Skill that ports the Loop Engineering methodology from `codex-loop-engineering` into TRAE. It gives a substantial coding, research, or content project a structured loop: route tiers, six-interface contracts, artifact-first handoffs, dual plan and dual review via Task subagents, evidence-based arbitration, stop rules, and user checkpoints.

This is **not** a drop-in install of the codex plugin. TRAE has no persistent named lanes, no cross-thread messaging, and no second CLI process. The methodology is preserved; the multi-lane mechanism is adapted to TRAE's one-shot Task subagents.

## What is Loop Engineering

Loop engineering chooses the cheapest process that still controls the failure mode, then runs explicit roles (planning, execution, review, arbitration, manager) through durable artifacts. For risky work it adds an **independent second plan** and **independent read-only reviews**, then arbitrates by evidence — not by which model said it. Stop rules and user checkpoints keep the loop from spinning or drifting.

## Relationship to codex-loop-engineering

| dimension | codex-loop-engineering | trae-loop-engineering |
|---|---|---|
| persistent context | multiple named lane threads | single main agent |
| independent planning | Claude lane + Codex lane | main agent (plan-A) + one Task subagent (plan-B) |
| independent review | Claude review lane + Codex review lane | two Task subagents (review-A/B) |
| cross-lane messaging | send_message_to_thread + ledger | none — main agent role transitions recorded in worklog/state |
| second-model policy | claude_policy + terminal lane lifecycle | subagent_policy + one-shot Task subagents |
| monitoring | heartbeat + check_after/deadline | synchronous (Task returns before continuing) |
| platform | macOS (osascript launcher) | Windows (PowerShell validator) |
| six-interface contract / T0-T5 / artifacts / stop rules / evidence / checkpoints / firewall | yes | yes (preserved) |

## TRAE Capability Facts

Three TRAE behaviors shape this skill:

1. **Subagent = Task tool, inherits session model.** Same-model dual plan/review can be automated; cross-model dual cannot — it needs manual multi-task transport (see `references/hybrid-dual.md`).
2. **New session clears context.** Only files survive across sessions, so loop memory lives in `loop-state.md` + `worklog.md` + artifacts, and a Resume Protocol reconstructs state on restart (see `references/resume-protocol.md`).
3. **Auto-run setting is the prerequisite for auto-iteration.** Enable it in TRAE IDE (Settings → Conversation flow → Auto-run) or TRAE Work (left sidebar → Settings → Conversation flow → Auto-run) so the loop can advance without per-step confirmation (see `references/auto-iteration.md`).

## Core capabilities

- **Route tiers** T0 direct / T1 checklist / T2 mini-loop / T3 full loop with dual plan-review / T4 custom / T5 skill promotion. T0-T2 run single-agent; T3+ dispatch Task subagents.
- **Six-interface contract**: goal / state / context / act / capture / stop.
- **Artifact flow**: `00-brief` → `10-plan-A` → `11-plan-B` → `12-plan-merged` → `20-execution-report` → `30-review-A` → `31-review-B` → `40-arbitration` → `50-final-report`.
- **Dual plan / dual review via subagents** with a hard independence rule: a subagent prompt contains only the brief/evidence bundle, never the main agent's conclusions or another subagent's output.
- **Evidence-based arbitration**, **stop rules** (max 2 repair iterations, third new P0 stops), **user checkpoints**, **planning-execution firewall**.
- **File-based memory and resume**: `loop-state.md` snapshot + `worklog.md` event stream + artifacts; cross-session resume via `resume loop <loop_id>` after restart/interruption.
- **Auto-iteration**: with TRAE auto-run ON, the loop advances through phases automatically, halting only at stop rules and must-ask checkpoints.
- **Hybrid dual**: same-model auto dual (Task subagent) by default; cross-model manual upgrade (TRAE multi-task with different models) for high-risk work.
- **PowerShell validators**: `scripts/validate-loop-contract.ps1` and `scripts/validate-loop-state.ps1`.

## Install

### TRAE IDE (Windows / macOS)

#### Option A — Global skill (recommended)

Copy this folder to the TRAE IDE built-in skills directory so that `SKILL.md` lives at:

```
%userprofile%\.trae-cn\builtin_skills\trae-loop-engineering\SKILL.md
```

PowerShell one-liner (run from the parent of this folder):

```powershell
Copy-Item -Recurse -Force '.\trae-loop-engineering' "$env:USERPROFILE\.trae-cn\builtin_skills\trae-loop-engineering"
```

Restart TRAE IDE. The skill `trae-loop-engineering` will appear in the Skill list and be available in SOLO mode.

#### Option B — Project skill

Copy this folder into your project so that `SKILL.md` lives at:

```
<project-root>\.trae\skills\trae-loop-engineering\SKILL.md
```

PowerShell (run from your project root):

```powershell
Copy-Item -Recurse -Force '<path-to>\trae-loop-engineering' '.\.trae\skills\trae-loop-engineering'
```

### TRAE Work

#### Option A — Global skill (recommended)

Copy this folder to the TRAE global skills directory so that `SKILL.md` lives at:

```
%userprofile%\.trae-cn\skills\trae-loop-engineering\SKILL.md
```

PowerShell one-liner (run from the parent of this folder):

```powershell
Copy-Item -Recurse -Force '.\trae-loop-engineering' "$env:USERPROFILE\.trae-cn\skills\trae-loop-engineering"
```

Then in TRAE Work: left sidebar → Skills (技能) → Installed tab, confirm `trae-loop-engineering` appears and is enabled.

#### Option B — Project skill

(Same as TRAE IDE Option B above)

#### Option C — Import as zip

In TRAE Work: left sidebar → Skills (技能) → Create > import a `SKILL.md` or a `.zip` containing this folder.

## Quick start

After install, trigger the skill in chat, for example:

> Use loop engineering to refactor `src/auth/login.ts` from callbacks to async/await, preserving the public API and the 401-retry behavior.

The main agent will: choose a route tier (likely T3) → write a brief → write plan-A → dispatch a plan-B subagent → merge → execute → dispatch two review subagents → arbitrate → final report. Artifacts land under `docs/loop-engineering/YYYY-MM-DD-slug/`. For long tasks, enable TRAE auto-run (TRAE IDE: Settings → Conversation flow → Auto-run; TRAE Work: left sidebar → Settings → Conversation flow → Auto-run) so the loop auto-iterates. If interrupted, resume with `resume loop <loop_id>` in a new session — the agent reads `loop-state.md` first and continues.

For a full walk-through with subagent prompt samples, see `examples/minimal-refactor/README.md`. For an interrupt-and-resume example, see `examples/resume-walkthrough/README.md`.

## When NOT to use

Tiny edits, config tweaks, docs-only notes, or simple local bug fixes. Do not run the full loop unless the user asks.

## Privacy

The skill is a set of instruction files and a local PowerShell validator. It does not call external services. Subagent Task prompts you construct may contain your project code; review them as you would any prompt that shares source.

## Layout

```
trae-loop-engineering/
├── SKILL.md                         main skill (<500 lines)
├── README.md                        this file
├── LICENSE                          MIT
├── references/                      one-level-deep reference docs (12 files)
├── scripts/                         validate-loop-contract.ps1, validate-loop-state.ps1
└── examples/                        minimal-refactor/ , resume-walkthrough/
```

## License

MIT — see `LICENSE`.
