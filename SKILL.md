---
name: trae-loop-engineering
description: Use when a substantial coding, research, content, or long-running project needs structured loop orchestration in TRAE with six-interface contracts (goal/state/context/act/capture/stop), route tiers (T0-T5; dual plan-review via Task subagents at T3+), artifact-first handoffs (00-brief through 50-final-report), evidence-based arbitration, stop rules, and user checkpoints. The main agent acts as manager/planner/executor/arbitrator; Task subagents provide independent second plans and read-only reviews at T3+. Supports file-based memory (loop-state.md), cross-session resume, auto-iteration with TRAE auto-run, and hybrid dual (same-model auto default, cross-model manual upgrade for high-risk). Do not use for tiny edits, config tweaks, docs-only notes, or simple local bug fixes.
license: MIT
compatibility:
  - trae-work
  - trae-cli
metadata:
  version: 1.1.0
  min-trae-version: "2025.1"
  tags:
    - loop-engineering
    - multi-agent
    - artifact-driven
    - code-review
    - refactoring
allowed-tools:
  - Task
  - Read
  - Write
  - Edit
  - Grep
  - Glob
  - RunCommand
---

# TRAE Loop Engineering

## Table of Contents

1. [Purpose](#purpose)
2. [TRAE Adaptation Boundary](#trae-adaptation-boundary)
3. [TRAE Capability Facts](#trae-capability-facts)
4. [Quick Start / Decision Gate](#quick-start--decision-gate)
5. [Planning-Execution Firewall](#planning-execution-firewall)
6. [Route Tiers](#route-tiers)
7. [Admission Gates](#admission-gates)
8. [Six-Interface Contract](#six-interface-contract)
9. [Strategy, Tactical, Execution Layers](#strategy-tactical-execution-layers)
10. [Execution Batch Sizing](#execution-batch-sizing)
11. [Artifact Protocol](#artifact-protocol)
12. [File-Based Memory And Resume](#file-based-memory-and-resume)
13. [TRAE Memory, Rules, and MCP Integration](#trae-memory-rules-and-mcp-integration)
14. [The Workflow](#the-workflow)
15. [Quick Arbitration Output](#quick-arbitration-output)
16. [Subagent Dual Plan/Review](#subagent-dual-planreview)
17. [Hybrid Dual](#hybrid-dual)
18. [Stop Rules](#stop-rules)
19. [Evidence Standards](#evidence-standards)
20. [Auto-Iteration](#auto-iteration)
21. [User Checkpoints](#user-checkpoints)
22. [Skill Promotion](#skill-promotion)
23. [Roles](#roles)
24. [Common Mistakes](#common-mistakes)
25. [Resources](#resources)

## Purpose

Loop engineering is for substantial long-running work where a single-pass plan is likely to miss edge cases: deep refactors, large feature development, architecture-affecting fixes, research synthesis, content production workflows, multi-file migrations, or any project that benefits from explicit roles, artifacts, independent critique, and repair loops.

Run the loop in one thread by default. Scale up to Task subagents only when coordination, traceability, independent critique, or context isolation justifies it. Artifacts are the source of truth, not chat history; use the smallest role set that preserves quality.

For tiny edits, config tweaks, docs-only notes, or simple local bug fixes, do not run the full loop unless the user asks.

## TRAE Adaptation Boundary

This skill ports codex-loop-engineering to TRAE. TRAE has no persistent named lanes, no cross-thread messaging, and no second CLI process. The adaptation is:

| keep | drop | adapt |
|---|---|---|
| six-interface contract, T0-T5 tiers, artifact flow, stop rules, evidence standards, user checkpoints, planning-execution firewall | codex plugin system, persistent lanes, send_message_to_thread, macOS osascript launcher, heartbeat monitoring, async check_after/deadline | main agent owns manager/planner-A/executor/arbitrator; dual plan/review via one-shot Task subagents; subagent_policy replaces claude_policy |

The main agent is the only persistent context. Task subagents are one-shot: they return a result and cannot be reused, asked follow-ups, or message each other. Independence is preserved by feeding subagents only the brief/evidence bundle, never the main agent's conclusions or other subagents' output. The main agent is the first role allowed to compare across plans/reviews (as merger/arbitrator).

## TRAE Capability Facts

This skill depends on three TRAE behaviors. State them explicitly so the loop matches reality:

1. **Subagent = Task tool, inherits session model.** A Task subagent runs in the same model as the current session. Same-model dual plan/review can be automated via Task. Cross-model dual (different models for plan-A and plan-B) cannot be automated via Task — see `references/hybrid-dual.md` for the manual upgrade path.

2. **New session clears context.** Opening a new session clears prior chat context; only files survive. Therefore loop memory must live in artifacts, worklog, and `loop-state.md` — never in chat history. Cross-session continuation uses the Resume Protocol; see `references/resume-protocol.md`.

3. **Auto-run setting is the prerequisite for auto-iteration.** TRAE has an "auto-run" setting (Settings > Conversation flow > Auto-run). When enabled, the agent executes commands/MCP/subagent dispatches without per-step confirmation. Auto-iteration (the loop advancing phases without manual confirmation) requires this setting ON. If OFF, the loop still works but each execution step pauses for confirmation. See `references/auto-iteration.md`.

## Quick Start / Decision Gate

1. Choose the route tier before choosing roles.
2. For each new task, derive the project-specific roles first, then build the matching identity table and worklog before execution.
3. Verify the six-interface contract: goal, state, context, act, capture, stop.
4. For T3/T4, create or identify a Strategic Loop Contract; see `references/strategic-loop-contract.md`.
5. If the strategic target or "good enough" completion criterion is missing, write `strategy-gap: <missing decision>` and stop for a user checkpoint.
6. For multi-round work, define how state and feedback will be recorded; see `references/state-feedback-schema.md`.
7. Same active loop correction or continuation? Reuse the existing `loop_id` and owner role.
8. Choose `subagent_policy` for plan/review; see `references/subagent-dispatch.md`.
9. Critical direction or degraded-gate decision? Use `references/user-checkpoints.md`.
10. Context or handoff risk? Write a baton/state artifact before more work.

## Planning-Execution Firewall

Planning must never self-promote into execution. This is a hard boundary.

- A planning role may read broadly, consult a subagent, research references, write or repair planning/control artifacts, run validators, and update worklog/state-feedback.
- A planning role must not modify production code, frontend source, tests, generated data, package/config files, runtime scripts, or project structure.
- If the user interrupts planning, points out an error, says "continue", or asks the planner to reconsider, the planner revises the plan or asks for a checkpoint. It does not begin execution.
- Execution may start only from an explicit execution handoff, or from a new user instruction after the boundary that plainly asks the current role to implement. Ambiguous phrases such as "continue", "go on", "fix the plan" mean continue planning, not execute code.
- If a planning role accidentally touches implementation files, stop immediately, revert only that role's own out-of-scope edits, record the violation, and return to planning artifact repair.

## Route Tiers

Loop engineering means choosing the cheapest process that still controls the failure mode. "Use a loop" does not mean "start many agents."

| tier | route | use when | required fields |
|---|---|---|---|
| T0 | direct answer / current thread | question, tiny docs/config, one local fix | evidence if claiming completion |
| T1 | checklist in current thread | small multi-step task | goal, done check, capture |
| T2 | mini-loop | one surface, moderate uncertainty | six-interface contract |
| T3 | full loop | risky code/process, cross-module, architecture, user-visible workflow | independent plan/review via subagent(s) |
| T4 | custom role graph | large multi-domain project with parallel work | role contracts, budgets, worklog |
| T5 | skill promotion | repeated workflow or recurring failure pattern | harness/checker, trigger, stop rules |

Default to T0/T1/T2. T0-T2 run single-agent with self-constraint. T3+ dispatches Task subagents for dual plan/review and requires a short justification: what risk does the heavier route reduce?

## Admission Gates

Before starting a full loop (T3+), answer:

1. Is this worth the token spend for the expected value?
2. Is it complex or risky enough for more than a current-thread checklist?
3. What breaks if one agent handles it?
4. What is the cheapest route that controls that failure mode?
5. What is the max budget, max rounds, and stop condition?
6. What evidence proves done?

Dispatch a Task subagent only when it has most of: independent success/failure criteria; fixed output artifact; persistent context need; clear write scope; separable context boundary; meaningful risk, budget, quality, or coordination value. Otherwise keep it as a current-thread section, checklist, or one-off subtask.

## Six-Interface Contract

Before starting T2 or higher, define:

| interface | question | artifact |
|---|---|---|
| goal | What task is being pushed? | brief / completion criteria |
| state | What state is read each round? | worklog / known attempts |
| context | How does state become prompt input? | context pack / source artifacts |
| act | What can the agent do? | allowed tools / write scope |
| capture | What must be recorded? | command output / diff / finding |
| stop | When does it end or halt? | done check / budget / round cap / risk stop |

If done, capture, feedback, state, or stop is missing, do not run a loop. Downgrade to a checklist or stop for a checkpoint.

## Strategy, Tactical, Execution Layers

Large projects need separate planning layers.

Strategic plan answers: end-state; minimum useful "good enough" target; explicit non-goals; evidence that proves the target is met; budget/round cap and stop conditions; user checkpoints that can change direction.

Tactical plan answers: user-visible workflow slices; durable data contracts and state transitions; which slices group into larger execution batches; risk boundaries; deferred phases.

Execution plan answers: source strategy/tactical artifacts; write scope; tasks grouped by product surface or durable contract; verification commands; expected artifacts; review cadence; stop condition.

If the strategic target is absent, write `strategy-gap: <missing decision>` and do not start tactical or execution planning.

For T3/T4, the strategic plan and operational contract live together as a Strategic Loop Contract. Validate:

**Windows PowerShell:**
```powershell
powershell -File scripts/validate-loop-contract.ps1 -Path <contract-or-merged-plan.md>
```

**macOS/Linux Python 3.8+:**
```bash
python3 scripts/validate-loop-contract.py <contract-or-merged-plan.md>
```

## Execution Batch Sizing

Execution batches should be large enough to land one coherent outcome: a user-visible workflow state, a product surface, a durable data contract, a migration boundary, or a security boundary. Avoid helper-level execution batches that trigger a full dual-review cycle unless they carry security, data-loss, or user-visible regression risk.

Prefer fewer, larger execution phases after a strong strategy/tactical plan. Run full independent review when a stable workflow loop or contract slice lands. During implementation, local tests and execution reports can run without full dual review for every internal patch.

If the user complains that progress is too slow, treat that as a standing batching constraint: the next execution batch must land a substantial user-visible capability, folding safety and hygiene work into it as acceptance criteria.

## Artifact Protocol

Default bundle:

```text
docs/loop-engineering/YYYY-MM-DD-slug/
  00-brief.md
  10-plan-A.md
  11-plan-B.md
  12-plan-merged.md
  20-execution-report.md
  30-review-A.md
  31-review-B.md
  40-arbitration.md
  50-final-report.md
```

A/B replaces the original claude/codex naming because TRAE has no fixed second-model identity; A is the main agent, B is the subagent.

Rules:
- One artifact has one owner. Do not rewrite another role's artifact except for clearly marked append-only notes.
- Every artifact names its source artifacts.
- Every factual claim should carry `path:line`, command output, screenshot path, JSON path, git state, or `not verified`.
- Keep plan, execution report, review, arbitration, and final report separate. Handoffs are artifact-first: send artifact path + read requirement + boundaries + exit criteria; do not rewrite the artifact body into the message.
- T3/T4 loops should record state and feedback events when reviews, arbitration, repairs, or user corrections change the next prompt/context/owner/action; see `references/state-feedback-schema.md`.

## File-Based Memory And Resume

Because new sessions clear context, loop memory lives in files. Three layers:

| layer | file | role | update style |
|---|---|---|---|
| snapshot | `loop-state.md` | current phase/role/next_action/blockers — the first file read on resume | overwrite on each change |
| event stream | `worklog.md` + state/feedback events | history of phase transitions, decisions, repairs | append-only |
| artifacts | 00-brief through 50-final-report | durable outputs | one owner each, append-only notes |

`loop-state.md` sits at the artifact directory root (next to `00-brief.md`). It is a single YAML snapshot. On any new session, read it first to know where the loop is, then read worklog for why, then read the relevant artifacts. Field structure and update rules: `references/loop-state-schema.md`.

### Resume Protocol

To continue a loop after restart or interruption, send `resume loop <loop_id>` (or "continue the previous loop"). The agent:

1. locates the artifact directory by loop_id;
2. reads `loop-state.md` first (phase/role/next_action/blockers/gaps);
3. reads worklog/state-feedback for history;
4. reads the latest artifacts per current role's context rules;
5. validates artifact completeness (and worktree consistency if resuming mid-execution);
6. classifies the resume as clean / resume-with-gap / cannot-resume;
7. stops for a checkpoint if blockers or gaps exist;
8. continues from next_action, reusing the same loop_id;
9. updates loop-state.md (resume_count+1) and appends a resume event to worklog.

Full steps and gap handling: `references/resume-protocol.md`.

## TRAE Memory, Rules, and MCP Integration

TRAE has three capability pillars that interact with loop engineering:

- **Memory**: TRAE's Memory system (persistent preferences, max 20 items, auto-eviction) can store loop preferences — default route tier, subagent_policy tendency, stop-rule strictness. But loop state itself must live in `loop-state.md`, not Memory.
- **Rules**: TRAE Rules (hard constraints, always loaded) can enforce the planning-execution firewall. If a project requires "all T3+ work must go through dual plan," set it as a Rule rather than restating it each time.
- **MCP**: MCP Servers provide external tools (Playwright for UI testing, GitHub for PR checks, database connectors for data validation). The loop's capture interface can reference MCP tool output as evidence. MCP tools extend the `act` interface — list available MCP tools in the contract's allowed scope.

## The Workflow

### Phase 1: Brief
Create `00-brief.md`: goal, user constraints, in scope, out of scope, expected verification, known risk. For T3/T4, include a strategic "good enough" target.

### Phase 2: Dual Plan (T3+)
Main agent writes `10-plan-A.md` from the brief. Then dispatches a plan-B subagent whose Task prompt contains only the brief + context pack + required headings + independence declaration, never plan-A. Main agent writes the subagent's output verbatim into `11-plan-B.md` (adding only a provenance header), then as merger writes `12-plan-merged.md`. See `references/subagent-dispatch.md`.

If T0-T2, skip dual: main agent writes a single plan.

Plan required headings: Goal / Scope / Tasks / Tests / Verification / Risks / Not Doing. Large work must separate strategic/tactical/execution layers. If either plan only lists small tasks without a strategic target, mark it incomplete.

### Phase 3: Plan Merge
`12-plan-merged.md` required sections: Source Plans / Accepted From A / Accepted From B / Rejected / Third Path Decisions / Final Tasks / Verification / Optional / Skip Rules / Completion Criteria. Every substantive conflict needs a resolution note. If the merged plan cannot satisfy every brief goal, write `plan-gap: <unsatisfied goal>` and stop. If strategic target is missing, write `strategy-gap` and stop. The merged plan is the only plan executed.

### Phase 4: Execution
Follow `12-plan-merged.md`. Keep changes inside scope. Use TDD for behavior changes. Preserve unrelated dirty worktree changes. If a plan asks for a commit and the worktree is dirty, stage only the safe subset or record `commit skipped: <reason>`. If an optional task is skipped: `SKIP: <task-id> reason=<one-line> blocker=<dependency or "none">`.

### Phase 5: Execution Report
`20-execution-report.md`: Source / Scope / Changed Files / Task Status (each with Evidence) / Verification (command -> key output) / Artifacts / Git State / Known Gaps. Do not overstate. Generated screenshots are not the same as inspected screenshots.

### Phase 6: Dual Review (T3+)
Dispatch review-A and review-B subagents independently. Each receives the same evidence bundle (merged plan, execution report, changed diff, relevant complete functions, test output, acceptance criteria) plus a read-only constraint and required headings. Neither review reads the other before both are complete. Main agent writes each subagent output verbatim into `30-review-A.md` / `31-review-B.md`. Review headings: Source / Findings (P0/P1/P2/P3: title / Claim / Evidence / Why it matters / Suggested action) / Criteria Check. See `references/subagent-dispatch.md`.

If T0-T2, skip dual: main agent may self-review with bounded evidence, or skip review.

### Phase 7: Arbitration And Repair
Main agent (as arbitrator) writes `40-arbitration.md`, enumerating every P0/P1 finding from both reviews. Decision labels: `accept A` / `accept B` / `reject both` / `third path` / `defer` / `needs more evidence`. Hard evidence rules in `references/evidence-standards.md`. Repair accepted findings as coherent contract patches, not one helper at a time. Rerun verification.

### Phase 8: Final Report
Write `50-final-report.md` only when stop rules pass: final status, changed files, review findings and dispositions, verification output, artifact paths, git state, residual risks.

## Quick Arbitration Output

For quick arbitration (inline, no full artifact):

```markdown
**Verdict**
<short judgment>

**Findings**
- accept/reject/third path/defer: <claim> — <evidence>

**Next Actions**
- <fix or record>
```

For full loop work, create/update artifacts unless the user asks for inline-only work.

## Subagent Dual Plan/Review

T0-T2: single agent, `subagent_policy: not_needed`. T3+: dispatch plan-B and two review subagents; `subagent_policy: required` for high-risk, `conditional` for uncertain-value. Independence hard rule: subagent prompts contain only the brief/evidence bundle, never the main agent's conclusions or other subagents' output. Subagent output is written verbatim into artifacts (only a provenance header added). Full dispatch flow, Task prompt templates, and failure handling: `references/subagent-dispatch.md`.

## Hybrid Dual

Two paths: `same_model_auto` (Task subagent, inherits session model, T3+ default) or `cross_model_manual` (TRAE multi-task with different models, high-risk upgrade). Cross-model dual cannot use Task subagents — the manual path packs a task-packet, user transports it to a different model, output returns verbatim. Full flow and honesty rules: `references/hybrid-dual.md`.

## Stop Rules

Max 2 repair iterations per brief. Third new P0: write `loop-limit-reached` and stop. Any unresolved P0 blocks final report. P1 must be fixed, deferred with reason, or disputed. Two reviews agreeing on P0 without counter-evidence: stop for user decision. Full rules: `references/stop-rules.md`.

## Evidence Standards

Strong evidence: `path:line`, full test command with pass/fail count, screenshot path with inspection statement, git state. Weak evidence cannot be the sole basis for `accept`. Every accepted P0 requires strong evidence. `not verified` means unchecked, not correct. Full rules: `references/evidence-standards.md`.

## Auto-Iteration

With TRAE auto-run ON (Settings > Conversation flow > Auto-run), the loop auto-advances through phases, halting only at stop rules, must-ask checkpoints, blockers, and gap markers. If OFF, each step pauses for confirmation. The loop never bypasses a halt point. Full rules: `references/auto-iteration.md`.

## User Checkpoints

Stop and ask before: multiple plausible product directions; underspecified UX/success criteria; brief/goal changes; `plan-gap`; required subagent artifact missing/empty/malformed; proceeding degraded after a required dual gate; review/arbitration changing scope/architecture; user rejecting a preview direction; two reviews agreeing on P0 without counter-evidence; detected brief drift. Do not ask for ordinary implementation defects, routine test additions, formatting edits, or `third path` small repairs. Auto-dispatch after planning when the user already participated, the plan matches accepted strategy, gates are clean, and no gap remains. Full rules: `references/user-checkpoints.md`.

## Skill Promotion

Promote a repeated loop pattern to a skill only after the stable parts are known. Default threshold: 10+ repeated uses, or fewer when risk/cost is high and the pattern is already stable.

Promotion requires: stable context pack; route trigger; done check; checker or harness when practical; examples or forward tests; known failure modes; stop rules. Do not turn a one-off project lesson into a skill unless it generalizes beyond that project.

## Roles

Roles are contracts, not fixed titles. Default: planning, execution, review, arbitration, manager (all owned by main agent; review and plan-B delegated to subagents at T3+). Map to domain roles for non-code projects. Choose roles by task risk, not habit. Reviews stay independent. Arbitration repairs implementation defects; return to planning only for plan defects or scope changes. Full role definitions, independence constraints, and context rules: `references/lane-roles.md`.

## Common Mistakes

- Treating loop-engineering as "always create many agents" instead of choosing a route tier.
- Starting execution before defining the strategic "good enough" target.
- Creating subagents for role aesthetics rather than boundary value.
- Missing one of the six interfaces: goal, state, context, act, capture, stop.
- Running the full loop for tiny edits.
- Running full dual review after every helper-level patch instead of batching by product surface.
- Letting the main agent inject its own conclusions into a plan-B or review subagent prompt.
- Letting the main agent author or self-review code in the manager role instead of dispatching a fresh subagent review.
- Editing, summarizing, or compressing a subagent's output instead of writing it verbatim.
- Treating a same-context follow-up as an independent plan/review.
- Pretending a subagent reviewed when the Task call failed or returned empty.
- Replacing an unavailable subagent review with main-agent self-review instead of stopping for degraded-mode approval.
- Missing skip markers; claiming generated screenshots were inspected; committing unrelated dirty files.
- Relying on chat history instead of artifacts as loop memory.
- Sending unstructured "continue" messages; repeating artifact bodies in handoffs instead of sending paths.
- Auto-archiving work before the user has evaluated the loop.
- Stopping at every planning closeout as a user checkpoint even when the user already participated and gates passed.
- Starting a new loop instead of resuming when `loop-state.md` shows an active loop.
- Relying on chat history to recover loop state instead of reading loop-state.md and worklog.
- Bypassing a stop rule or must-ask checkpoint because auto-run is enabled.
- Pretending a cross-model manual dual was an automatic subagent dual, or leaking plan-A into a plan-B task-packet.

## Resources

- `references/lane-roles.md` — role definitions, independence constraints, hard boundaries, context rules
- `references/subagent-dispatch.md` — subagent_policy, dual plan/review dispatch flow, Task prompt templates, failure handling
- `references/strategic-loop-contract.md` — contract YAML structure and rules
- `references/state-feedback-schema.md` — state/feedback/superseding event schema
- `references/evidence-standards.md` — strong/weak evidence and arbitration hard rules
- `references/stop-rules.md` — stop rules and repair iteration caps
- `references/user-chec