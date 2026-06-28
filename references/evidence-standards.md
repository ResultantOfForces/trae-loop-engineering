# Evidence Standards

Use this reference when arbitration, review, or any factual claim needs evidence. Arbitration decides by evidence, not by model identity.

## Strong Evidence

- Code: `path:line` plus the exact symbol or selector.
- Tests: full command and pass/fail count.
- UI/browser: screenshot path plus a visual inspection statement; DOM checks for dynamic linkage.
- Files/downloads: path, size, type check, checksum when useful.
- Git: `git status --short`, branch, staged files, commit SHA.

## Weak Evidence

- static UI copy treated as backend linkage proof;
- model citations without reopening files;
- screenshots generated but not inspected;
- tests that do not execute the changed file;
- a subagent claim about a path the main agent did not verify directly.

## Arbitration Hard Rules

- Weak evidence cannot be the sole basis for `accept`.
- Decisions must cite artifact evidence, not model or subagent identity.
- Every accepted P0 requires strong evidence.
- A P0 endorsed by both independent reviews cannot be rejected without `path:line` counter-evidence.
- `needs more evidence` means arbitration gathers evidence or stops; it must not average model opinions.
- `not verified` means unchecked, not correct.
- If a finding appears caused by prompt omission in a review subagent's bundle, label it `needs evidence` or reject it in arbitration with the missing context cited. The remedy is to improve future evidence-pack design, not to treat the finding as true or to hide the prompt limitation.

## Cross-Review Merge Discipline

- Review-A and review-B are independent inputs. Neither review is authoritative by itself.
- Do not spend a full verification cycle on every finding inside a review. Arbitration should merge both review artifacts, group common findings, identify conflicts, and then verify only the findings that affect acceptance, severity, repair scope, or user-visible risk.
- Shared findings deserve priority, but agreement is not proof. Conflicting findings, high-severity findings, and findings based on partial bundle evidence require live-path or artifact evidence before acceptance.
- Preserve review diversity: a review subagent can surface independent concerns from its bounded evidence, while arbitration checks whether those concerns survive the full merged plan, execution report, tests, and live files.
