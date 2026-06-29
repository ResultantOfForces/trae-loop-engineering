# 00-brief.md — Fillable Template

> Copy this file to `docs/loop-engineering/<YYYY-MM-DD-slug>/00-brief.md` and replace every `<...>` placeholder with your real project details. Delete the guidance notes (in `<angle brackets>`) before the loop begins. A worked example lives in `examples/minimal-refactor/00-brief.md`.

## Goal

<One-paragraph statement of what the loop must accomplish. Name the product surface, the behavior change, and the user-visible outcome. Keep it to one product surface.>

## User Constraints

- <Public API / function signatures must not change — callers keep working.>
- <No new runtime dependencies.>
- <Type-checking / lint / strict mode must stay green.>
- <Preserve existing test behavior; add tests for the new paths.>
- <...add project-specific hard constraints...>

## In Scope

- `<path/to/source/file>` — <what changes here>
- `<path/to/test/file>` — <extend / add>
- `<shared types or contract file if the change needs it>`

## Out Of Scope

- <Adjacent flows that must not be touched.>
- <Backend / API changes.>
- <UI / login-form changes.>
- <Anything explicitly deferred.>

## Expected Verification

- `<lint command>` passes.
- `<test command>` passes with new tests green.
- A diff showing only the in-scope surface changed.
- <project-specific verification, e.g. migration dry-run, screenshot inspection, manual repro step.>

## Known Risk

- <The most likely failure mode of this change. Be specific about which existing behavior could regress and why a naive approach gets it wrong.>

## Strategic good_enough

<Required for T3/T4. Define the minimum useful completion target: the behavior that must be true end-to-end, the evidence that proves it, and which residual edge case may be deferred to a follow-up issue with a named reason. If absent, the loop writes `strategy-gap: missing good_enough` and stops before tactical or execution planning.>

## Route Tier

< T0 | T1 | T2 | T3 | T4 | T5 > — <one-line justification of the risk this tier controls. T3+ requires a short reason for the heavier route.>

## subagent_policy

- dual plan: `< not_needed | conditional | required >` — <reason>
- dual review: `< not_needed | conditional | required >` — <reason>
- fallback_if_subagent_unavailable: < retry-once | stop-for-user-checkpoint | proceed-degraded >
