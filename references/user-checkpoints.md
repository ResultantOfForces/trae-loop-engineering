# User Checkpoints Reference

Use this reference when a loop decision may change project direction, when a required subagent is unavailable, or when the environment needs independent planning/review.

## Principle

Long-running loops need a few explicit user calibration points. Do not ask for every small choice, but do stop before decisions that can redirect scope, product goals, architecture, source policy, review quality, or degraded-tool mode.

## Auto-Iteration Context

When the loop is auto-iterating (see `references/auto-iteration.md`):

- the **Must Ask** list below = forced halt points; the loop stops and asks;
- the **Should Usually Not Ask** list = auto-advance is allowed;
- the **Auto-Dispatch After Planning** conditions = the gate for auto-advancing from planning to execution; if all hold and TRAE auto-run is ON, the main agent dispatches execution without asking again.

Auto-run only removes per-step command confirmation; it never bypasses a Must Ask halt point.

## Must Ask

Create a user checkpoint before proceeding when:

- planning has multiple plausible product directions and the choice affects implementation shape;
- user experience expectations, success criteria, or "what good looks like" are underspecified;
- the brief, product goal, or user-facing success criterion changes;
- the merged plan cannot satisfy the brief and a `plan-gap` is written;
- a required subagent planning or review artifact is missing, empty, malformed, or the Task call failed/timed out;
- the loop would proceed degraded after a required dual gate;
- review or arbitration would change scope, data contract, architecture, source policy, or phase boundary;
- a frontend/product preview is technically valid but the user says it does not match the intended visual direction, workflow feel, or "what good looks like";
- user correction would supersede an active execution, review, arbitration, or expected artifact path;
- two independent reviews agree on a P0 and arbitration cannot disprove it with strong evidence;
- the manager detects context drift between the original brief and current output;
- a role wants to replace a formal artifact with chat memory or a summary.

Do not continue to execution, repair, or final report through these gates unless the user has explicitly approved that exact degraded path or direction change.

## Should Usually Not Ask

Avoid interrupting the user for:

- ordinary implementation defects inside the merged plan;
- test additions for planned behavior;
- formatting or documentation edits inside accepted scope;
- choosing a smaller safe repair in arbitration via `third path`;
- routine retries within the recorded subagent policy wait/retry rules.

## Auto-Dispatch After Planning

A planning checkpoint is a judgment gate, not a mandatory pause after every valid plan. After a merged plan or Strategic Loop Contract passes required heading checks and validator gates, the manager may dispatch execution without asking the user again when all of these are true:

- the user already participated in the planning direction or explicitly asked to keep the loop moving;
- the plan selects the user-confirmed strategic direction rather than creating a new product/architecture route;
- subagent/validator/required-gate status is clean, or the user has already approved the recorded degraded mode;
- there is no `plan-gap`, `strategy-gap`, disputed scope, malformed artifact, destructive action, live-runtime expansion, or unclear acceptance criterion;
- the next execution handoff preserves the plan's hard boundaries and stop condition.

In that case, record `checkpoint_resolved_by: manager` in state/worklog, optionally send a short summary for visibility, and route the execution handoff. Do not turn every planning closeout into a user-blocking checkpoint.

Stop for the user instead when the manager is unsure whether the plan matches the user's intent, when the plan changes strategy, when the user was not part of the decision, or when the next action would expand into mutation/runtime/tooling that was not already accepted.

## Checkpoint Shape

Keep checkpoint prompts short and decision-oriented:

```text
Checkpoint: <decision name>
Why it matters: <one sentence>
Current evidence: <artifact paths / failure marker>
Options:
1. Retry / gather more evidence
2. Proceed degraded with explicit marker
3. Return to planning / revise brief
4. Pause
Recommended: <one option + reason>
```

## Planning Calibration

Planning checkpoints should happen before a merged plan becomes executable when user intent is ambiguous. Keep them sparse and high leverage:

- ask about product direction, workflow feel, priority tradeoffs, and acceptance criteria;
- present 2-3 concrete choices and one recommended option;
- write the user's answer into the brief, merged plan, or decision log;
- do not ask the user to decide internal helper structure unless it changes workflow, risk, or maintainability;
- if the user rejects the generated plan's direction, revise the plan artifact before execution instead of relying on chat correction.

## Preview Calibration

For frontend or product-surface work, the preview checkpoint is an acceptance gate, not a courtesy update. Offer:

1. Accept the visible direction and proceed to review or backend continuation.
2. Revise the visible shape before deeper wiring.
3. Run a bounded design critique over the screenshot and touched files.
4. Pause.

If the user rejects the preview, update the relevant plan/contract or write a superseding decision artifact before more implementation. Do not rely on chat correction alone. The manager may resolve a preview checkpoint and move into formal review when the preview is a continuation of a user-approved direction, execution evidence is clean, safety boundaries passed, and the next step is review/arbitration rather than more implementation. Record this as `preview_checkpoint_resolved_by: manager`.

## Subagent-Unavailable Planning

If a required plan-B subagent is unavailable:

1. Write `subagent-unavailable: <reason>` in the plan-B artifact path or an adjacent marker.
2. Stop at a user checkpoint before merging.
3. Offer: retry the subagent; split/optimize the prompt and retry once; proceed main-agent-only with two isolated main-agent planning passes (honestly labeled, not "independent subagent"); pause until subagent tooling is fixed.

Do not fabricate `11-plan-B.md` from the main agent's own plan-A.

## Main-Agent-Only Independent Planning

When no subagent is available or the user approves main-agent-only mode:

- keep the artifact structure explicit, but rename sources honestly, e.g. `10-plan-A.md` and `11-plan-A-isolated.md`;
- run two isolated main-agent planning passes with different prompts or roles (product/planning vs architecture/risk), in separate context windows if possible;
- prevent cross-contamination: the second pass must not read the first before both artifacts exist;
- merge them with the same conflict-resolution discipline;
- mark the merged plan `plan_mode: main_agent_only_independent` and the reason no subagent was used.

Main-agent-only mode is valid but is a degraded/capability-different path when the brief asked for a subagent. Be honest in artifacts.

## Main-Agent-Only Independent Review

When a review subagent is unavailable:

- if possible, produce two independent main-agent review passes from fresh isolated contexts;
- neither review reads the other before arbitration;
- use the same bounded evidence bundle standards;
- arbitration merges findings by evidence, not by reviewer identity;
- the final report records `review_mode: main_agent_only_independent` and the reason no subagent was used.

Do not call a single same-context self-review or manager-thread review an independent review. The manager may dispatch and validate review artifacts, but it must not be the reviewer. If only the current thread is available, mark `independent-review-unavailable` and ask the user whether to proceed degraded.

## Drift Control

At each major phase boundary, the manager/arbitration should compare:

- original brief / user constraints;
- merged plan;
- execution report;
- review findings;
- proposed next action.

If the proposed next action changes the project direction instead of completing the accepted phase, stop for a checkpoint.
