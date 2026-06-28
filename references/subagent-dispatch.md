# Subagent Dispatch Reference

Use this reference when a T3+ loop dispatches Task subagents for dual plan or dual review. This is the core adaptation that replaces codex-loop-engineering's Claude Terminal lanes with TRAE's one-shot Task subagents.

## Table Of Contents

- TRAE Subagent Model Constraint
- Subagent Policy Tiers
- Dual Plan Dispatch
- Dual Review Dispatch
- Independence Hard Rules
- Evidence Bundle Construction
- Failure Handling
- Verbatim Write Rule

## TRAE Subagent Model Constraint

TRAE's Task tool dispatches subagents that run in the SAME model as the current session; there is no API to select a different model for a subagent. Consequences:

- Same-model dual (plan-A and plan-B from the same model, isolated contexts) CAN be automated via Task subagents — this is the default path below.
- Cross-model dual (plan-A from one model, plan-B from a different model) CANNOT be automated via Task. It requires manual transport via TRAE's multi-task feature; see `references/hybrid-dual.md`.

When `dual_mode: cross_model_manual` is set in `loop-state.md` / the contract, replace the Task dispatch steps (Step 3-4 of Dual Plan, Step 3-6 of Dual Review) with the manual transport flow in `hybrid-dual.md`. The independence rules, evidence standards, and verbatim write rule below still apply.

## Subagent Policy Tiers

`subagent_policy` replaces `claude_policy`. Choose by lane role and risk.

| subagent_policy | use when | required fields |
|---|---|---|
| `required` | risky architecture, migrations, auth/data-loss, frontend/backend linkage, process changes that affect future agent behavior, plan/review with lasting protocol impact, or substantive plan disagreement | `subagent_policy`, `subagent_mode`, `subagent_reason`, `required_subagent_artifact`, `fallback_if_subagent_unavailable` |
| `conditional` | a subagent may help but current evidence may make it unnecessary: implementation-risk consultation, unclear-plan analysis, review uncertainty, workflow pressure tests | include `subagent_policy`, `subagent_mode`, `subagent_reason`; if skipped, write `subagent skipped: <reason>` |
| `not_needed` | mechanical delivery, status lookup, worklog bookkeeping, tiny docs/config fixes, narrow already-reviewed execution | compact `subagent_policy: not_needed` plus a one-line reason |

### Required Close-Out Gate

A role with `subagent_policy: required` cannot close its final conclusion, execution report, review, or final report without either the `required_subagent_artifact` or a recorded `subagent-unavailable: <reason>` with an explicit block-or-degrade decision. The manager role may flag a missing required subagent artifact, but cannot satisfy it by self-reviewing.

When a required subagent artifact is unavailable, malformed, empty, or the Task call fails, do not silently continue. Write the unavailable marker first, then surface a user checkpoint before arbitration, repair, or execution proceeds as if dual review happened. Offer: retry the subagent; optimize/split the bounded prompt and retry once; proceed degraded with the main agent only, explicitly marking the missing subagent review; pause the loop.

## Dual Plan Dispatch

1. Main agent prepares `00-brief.md` + context pack (goal, scope, constraints, known risks, relevant complete code excerpts, prior final report if any, strategic good_enough target).
2. Main agent writes `10-plan-A.md` from the brief. Required headings: Goal / Scope / Tasks / Tests / Verification / Risks / Not Doing. Large work separates strategic/tactical/execution layers.
3. Main agent dispatches a plan-B subagent. The Task prompt contains ONLY: the brief full text, the context pack, an independence declaration, the required output headings, and a planning-only write constraint. It must NOT contain plan-A or any main-agent conclusion.
4. Main agent writes the subagent's returned output verbatim into `11-plan-B.md`, adding only a provenance header (`source: subagent plan-B / subagent_id: <id>`).
5. Main agent (as merger) reads both plans, writes `12-plan-merged.md` (Source Plans / Accepted From A / Accepted From B / Rejected / Third Path Decisions / Final Tasks / Verification / Completion Criteria). Every substantive conflict needs a resolution note. If the merged plan cannot satisfy every brief goal, write `plan-gap` and stop. If strategic target is missing, write `strategy-gap` and stop.
6. Run the validator: `powershell -File scripts/validate-loop-contract.ps1 -Path 12-plan-merged.md`.

### plan-B Task Prompt Template

```markdown
# Task: Independent Plan B

You are an independent planning agent. A separate planner has been working on the same brief, but you must NOT assume any prior plan exists. Produce your own independent plan from the brief below.

## Brief (00-brief.md)
<paste brief full text>

## Context Pack
<paste relevant complete code excerpts, constraints, known risks, prior final report summary>

## Required Output
Write a plan with exactly these sections:
## Goal
## Scope
## Tasks
## Tests / Verification
## Risks
## Not Doing

## Constraints
- Do not modify any code files. You are planning only.
- Do not ask follow-up questions. Work with the information provided.
- If the brief is missing a strategic "good enough" target, note it as `strategy-gap: <missing decision>` and still produce your best plan.

## Independence Declaration
No other plan has been shared with you. Your output will be compared against an independent Plan A only after both are complete.
```

## Dual Review Dispatch

1. Main agent executes `12-plan-merged.md`, writes `20-execution-report.md` (Source / Scope / Changed Files / Task Status with Evidence / Verification / Artifacts / Git State / Known Gaps).
2. Main agent prepares the evidence bundle: merged plan, execution report, changed diff (precise hunks with surrounding lines), relevant complete function bodies (no ellipses for judged logic), test output (full command + pass/fail count), acceptance criteria, known constraints.
3. Main agent dispatches review-A subagent. Task prompt contains ONLY: the evidence bundle, a read-only constraint, required output headings, and an independence declaration. It must NOT contain any other review.
4. Main agent writes the returned output verbatim into `30-review-A.md` (provenance header only).
5. Main agent dispatches review-B subagent. Task prompt contains the SAME evidence bundle and constraints. It must NOT contain review-A.
6. Main agent writes the returned output verbatim into `31-review-B.md`.
7. Main agent (as arbitrator) reads both reviews, enumerates every P0/P1 finding, and decides per finding: `accept A` / `accept B` / `reject both` / `third path` / `defer` / `needs more evidence`. Each decision cites artifact evidence (path:line / command output), not subagent identity. Writes `40-arbitration.md`.
8. Main agent repairs accepted issues, reruns verification, checks stop rules, writes `50-final-report.md`.

### review Task Prompt Template

```markdown
# Task: Independent Read-Only Review

You are an independent review agent. Perform a read-only review of the execution below. Do not modify any code. Do not assume any other review exists.

## Evidence Bundle

### Merged Plan (12-plan-merged.md)
<paste or attach path>

### Execution Report (20-execution-report.md)
<paste or attach path>

### Changed Diff
<paste precise diff hunks + surrounding lines>

### Relevant Complete Functions
<paste complete function bodies — do not replace judged logic with ellipses>

### Test Output
<paste full command + pass/fail count>

### Acceptance Criteria
<paste criteria>

## Required Output
Write a review with exactly these sections:
## Source
## Findings
- P0/P1/P2/P3: <title>
  Claim: <what is wrong>
  Evidence: <path:line / command output / artifact path>
  Why it matters: <impact>
  Suggested action: <fix>
## Criteria Check

## Constraints
- Read-only. Do not modify any files.
- Do not ask follow-up questions.
- Every factual claim must carry path:line, command output, or `not verified`.
- Focus on bugs, regressions, missing tests, evidence-boundary violations, and user workflow failures.

## Independence Declaration
No other review has been shared with you. Your output will be compared against an independent Review B only after both are complete.
```

## Independence Hard Rules

- A plan-B subagent prompt must contain only the brief/context pack. It must never contain plan-A or any main-agent conclusion.
- A review subagent prompt must contain only the evidence bundle. It must never contain another review.
- The main agent must not inject its own conclusions, expected answers, intended fixes, or prior conclusions into a subagent prompt.
- The main agent is the first role allowed to compare across plans/reviews (as merger/arbitrator).
- Subagents are one-shot and cannot be asked follow-ups. The bundle must be self-contained. If critical information is missing, the subagent cannot recover; build the bundle completely before dispatch.
- A same-context follow-up by the main agent is never an independent plan/review. Label such output as critique/pressure-test, not independent.

## Evidence Bundle Construction

- Include: source artifact paths, relevant diffs, complete critical function bodies, focused tests and verification output, review priorities, required headings.
- Accuracy beats compactness. Include the complete relevant function body or an exact diff hunk with enough surrounding lines to show inputs, branches, side effects, and return values. Do not replace reviewed logic with ellipses, pseudocode, invented placeholders, or rewritten summaries.
- If an accurate bundle would be too large, split it into staged packets (contract summary; critical functions; tests; disputed finding follow-up). Each packet must be internally truthful and state what was omitted.
- If the prompt intentionally omits details, label the omissions explicitly and instruct the subagent not to infer beyond the supplied evidence.
- For images, screenshots, PDFs, or binary inputs, the main agent should first extract visible text, structure, and observations, then pass that bounded representation. Do not give a subagent whole-directory access to discover images.
- When a subagent cannot read a required path, record `partial: <path> unreadable` or `subagent-unavailable: <reason>`. The main agent must verify live paths directly before accepting subagent claims about them.

## Failure Handling

| symptom | marker | next action |
|---|---|---|
| subagent returns empty / malformed | `subagent-unavailable: malformed-output` | shrink bundle, retry once in a fresh Task call |
| subagent times out / no return | `subagent-unavailable: timeout` | shrink scope, retry once |
| output missing required headings | `review-unavailable: malformed-output` | do not accept as review evidence |
| output non-empty + required headings present | usable subagent artifact | record subagent_id, bundle path, output path, omitted paths |

For `subagent_policy: required`, any unavailable marker is a stop-and-ask condition unless the user already approved degraded continuation for that exact phase. Do not convert "subagent failed" into "main agent proceeds normally"; ask whether to retry, optimize/split the prompt, proceed degraded, or pause.

## Verbatim Write Rule

When writing a subagent's returned output into an artifact, the main agent must write it verbatim, adding only a provenance header (source, subagent_id, dispatch time). It must not edit, summarize, compress, reorder, or "clean up" the output. Editing would undermine the independence that the dual plan/review gate depends on. If the output contains formatting issues, record them as notes appended after the verbatim body, never by rewriting the body.
