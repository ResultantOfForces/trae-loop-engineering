# Lane Roles Reference

Use this reference when a loop needs named roles, handoffs, role-specific context rules, or independence constraints. In TRAE, roles are contracts executed by the main agent and one-shot Task subagents; there are no persistent lane threads.

## Table Of Contents

- Core Principle
- Role Types
- Independence And One-Shot Subagents
- Planning Role
- Planning Hard Boundary
- Execution Role
- Review Role
- Arbitration Role
- Repair Routing
- Manager Role
- Context Rules By Role
- Handoff Requirements

## Core Principle

Artifacts are the shared memory. Chat history may help the main agent think, but coordination must flow through explicit artifacts, worklogs, and handoffs. Treat orchestration as event/state driven: the manager role tracks role state, artifacts, and blockers; it should not continuously re-derive facts already captured in artifacts.

For multi-round loops, use `state-feedback-schema.md` to record how capture changes the next prompt, context, owner, or action. Feedback is not just a review comment; it is a recorded state transition.

In TRAE the main agent is the only persistent context. When a role needs independent judgment (dual plan, dual review), dispatch a one-shot Task subagent. The subagent returns a result and is gone; its artifact is the only durable trace.

## Role Types

| role | who | typical artifact |
|---|---|---|
| planning / product | main agent (plan-A) + subagent (plan-B, T3+) | brief, plan-A, plan-B, merged plan |
| execution / maker | main agent | execution report, changed files |
| review / QA | subagent (review-A/B, T3+) | review findings |
| arbitration / editor-in-chief | main agent | arbitration, repair report, final report |
| manager | main agent (coordination mode) | worklog, state-feedback, handoffs |

For non-code workflows, map roles to the task instead of forcing coding labels. Example content workflow: topic planner -> researcher -> scriptwriter -> editor -> QA -> publisher, with the main agent coordinating artifacts.

## Independence And One-Shot Subagents

Independence is a context boundary, not only a file name.

- Formal independent planning uses at least two judgment contexts that start from the same brief/context pack. plan-A (main agent) must not see plan-B (subagent), and plan-B must not see plan-A, before both artifacts exist.
- If the main agent writes its own plan and later asks a subagent for feedback on that plan, the subagent output is a critique or pressure test, not an independent plan. Label it honestly.
- The main agent may mechanically deliver a packet to a subagent (build the Task prompt, dispatch, validate the returned artifact). It must not make the subagent's planning/review judgment for it.
- The main agent must not write a review in its own manager context and treat that reasoning as independent evidence. Independent review must come from a fresh subagent with a bounded prompt.
- A subagent is acceptable as an isolated review/planning lane only if the prompt is bounded, it does not receive sibling artifacts before allowed, and it returns a formal artifact.

Because TRAE subagents are one-shot and cannot be asked follow-ups:
- The dispatch prompt must be self-contained and accurate. Include complete relevant function bodies, not ellipses, for any logic the subagent may judge.
- After a subagent returns, the main agent writes its output verbatim into the artifact (adding only a provenance header). It must not edit, summarize, or compress the output, because that would undermine independence.
- A subagent cannot be reused. If a second independent pass is needed, dispatch a fresh subagent with a fresh bounded prompt.

## Planning Role

Planning is allowed to be context-heavy. It should read more of the project than other roles, because a weak plan makes later execution worse.

Planning should:
- read the brief, prior final reports, specs, relevant code/project structure, and domain workflow skills;
- define the strategic end-state, "good enough" target, non-goals, and stop condition before tactical or execution planning;
- split large plans into strategic, tactical, and execution layers when the user goal is broad;
- ask targeted user checkpoints when goals, UX expectations, phase boundaries, or acceptance criteria are unclear;
- use a plan-B subagent as an independent second planner when risk is high;
- summarize any subagent discussion into formal artifacts, not rely on hidden chat memory;
- produce a merged plan with accepted/rejected/third-path decisions.

### Parallel Dual Planning

When a loop requires dual plans (T3+):
- The main agent prepares one brief/context pack, writes plan-A itself, then dispatches a plan-B subagent from the same pack. The plan-B Task prompt contains only the brief/context pack, never plan-A.
- plan-A must be written without reference to plan-B, and plan-B must be written without reference to plan-A. The merge step is the first place cross-plan comparison is allowed.
- If independent parallel dispatch is impossible (e.g. subagent tooling unavailable), mark the limitation, classify any later output honestly as critique/pressure-test, and use the degraded-mode checkpoint rules before treating the result as dual planning.

## Planning Hard Boundary

Planning is not execution. A planning role must not implement the plan it writes, even when implementation appears straightforward, the user says "continue", or the user corrects the plan midstream.

Allowed planning writes: briefs, plans, merged plans, design specs, strategy/tactical/execution contracts, prompt packets, unavailable markers, validator outputs, worklogs, state-feedback, and small repairs to those control-plane artifacts.

Forbidden planning writes: production source files; frontend components, CSS, generated app data, tests, package/config files, runtime scripts, project folders, git state, commits, or pushes; any TDD red/green cycle or app build/test run for implementation.

Interpretation rule: in a planning role, "continue", "go on", "fix it", or a user correction means continue planning, research, merged-plan repair, validator repair, or checkpoint writing. It does not authorize execution unless the user explicitly switches the current role to execution and names the implementation scope.

If planning discovers the next useful action is implementation, write an execution handoff and stop. If planning violates the boundary: stop immediately, revert only the planning role's own out-of-scope edits, record the violation, and return to planning artifact repair.

## Execution Role

Execution follows only the merged plan. It should not casually reopen product direction.

Execution should:
- keep changes inside the accepted phase boundary;
- use TDD for behavior changes where practical;
- write one execution report for the whole product/contract slice;
- use a review subagent only conditionally for plan gaps, source-policy uncertainty, or risk-boundary questions;
- record `plan-gap: <reason>` if the merged plan cannot be safely executed.

For large refactors, use fewer, larger execution phases that land a user-visible workflow state or durable data contract. Do not turn helper-level patches into full review loops.

### Execution-Owned Subagents

For large execution slices, the execution role (main agent) may use its own Task subagents to improve throughput. These are implementation helpers owned by execution, not separate loop phases.

Rules:
- Every large execution slice contract should state `execution_owned_subagents: allowed|not_needed|forbidden`. Default `allowed` when the slice contains separable data/UI/style/test/docs work.
- Keep every helper inside the execution contract, write scope, and stop condition.
- Do not turn helper subtasks into full plan -> review -> arbitration loops.
- The execution role remains responsible for integration, conflict resolution, tests, verification, and one consolidated execution report stating whether subagents were used and what each contributed.
- If a helper discovers a plan gap or scope change, record the blocker and stop instead of silently expanding scope.

## Review Role

Review must be independent. Review subagents must be fresh one-shot Task calls, not continuations of planning.

Review should:
- read the merged plan, execution report, test output, changed files/diff, and relevant complete functions;
- use a bounded evidence bundle that is accurate enough for real review;
- not read the other review before both reviews are complete;
- focus on bugs, regressions, missing tests, evidence-boundary violations, and user workflow failures;
- write findings with severity, claim, evidence, impact, and suggested action.

The main agent (manager mode) does not perform formal review. It dispatches review subagents, validates review artifacts, and routes arbitration. If a subagent is unavailable, the fallback is not main-agent self-review: dispatch an independent review subagent, or stop for degraded-mode approval per `user-checkpoints.md`. After valid review artifacts land, record completion in the worklog. Do not leave review results as hidden state for later phases.

## Arbitration Role

Arbitration decides by evidence, not by model identity.

Arbitration should:
- enumerate every P0/P1 finding from both reviews;
- accept, reject, defer, or request more evidence with path/command/artifact support;
- repair accepted findings as coherent contract patches, not one tiny helper at a time;
- run targeted and required verification;
- write the final report only when stop rules pass.

## Repair Routing

After review finds a problem, route it by defect type:

| defect type | owner | action |
|---|---|---|
| implementation defect inside the merged plan | arbitration | accept/reject, repair, verify |
| missing test/evidence for planned behavior | arbitration | add focused test/evidence or defer with reason |
| unclear evidence | arbitration | gather evidence or mark `needs more evidence`; do not average opinions |
| plan cannot satisfy the brief | planning | write `plan-gap: <unsatisfied goal>` and return to planning/user |
| fix changes scope, product direction, architecture, or data contract beyond the phase | planning | stop repair, open a planning update or next phase |
| user-goal mismatch discovered during review | planning / user | stop for clarified brief before more execution |

Default rule: arbitration repairs in-scope implementation defects. Do not send ordinary accepted review findings back to planning. Planning reopens only when the accepted finding proves the merged plan itself is wrong, incomplete, or unsafe to execute. For borderline findings, arbitration may choose `third path`: keep the current phase scope, make the smallest contract-safe repair, and defer broader redesign to the next planning phase.

## Manager Role

Manager is a status and recovery role, not a boss model.

Manager should:
- inspect artifacts and worklog to know where the loop is;
- detect missing, empty, stale, or malformed artifacts;
- decide whether to route planning, execution, review, or arbitration next;
- update worklog when process lessons emerge;
- read state/feedback events before deciding the next handoff when diagnosing repeated failures;
- resolve non-blocking planning checkpoints itself when the user already participated, gates passed, the plan stays inside the accepted strategy, and no scope/risk uncertainty remains; record the decision and dispatch execution instead of asking the user again by reflex;
- keep the loop moving when the user asks it to.

Manager must not silently execute business-code changes, overrule arbitration without evidence, or centralize all role communication as hidden chat.

## Context Rules By Role

| role | context style |
|---|---|
| planning | broad project context, prior artifacts, domain skills, subagent consultation allowed |
| execution | merged plan + local code/tests needed for implementation |
| review | fresh bounded evidence bundle; no inherited planning context |
| arbitration | both reviews + live evidence + execution report |
| manager | worklog, artifact paths, role state, blockers first |

Handoffs should send artifact paths and exact read requirements, not pasted full artifacts, when the artifact already exists. Only planning should routinely rebuild broad project context. Other roles must justify broad reads with a concrete gap.

## Handoff Requirements

In TRAE there are no cross-thread messages; handoffs are internal role transitions of the main agent, recorded in the worklog/state-feedback. Every role transition should record:

```text
loop_id
from_role / to_role
source artifacts
task
boundaries
write scope
required output
exit criteria
context_sources
expected_artifacts
subagent_policy (when a subagent is involved)
```

Never send an unstructured "continue" for loop work. When a subagent is dispatched, its Task prompt is the handoff; it must carry the bounded context, required headings, independence declaration, and exit criteria, since the subagent cannot ask follow-ups.
