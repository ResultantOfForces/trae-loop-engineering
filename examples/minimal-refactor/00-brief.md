# 00-brief.md — Minimal Refactor Example

> This is a sample T3 brief. Use it as a template and walk-through for the loop. Replace the file/symbol names with your real project.

## Goal

Convert the callback-based authentication in `src/auth/login.ts` to async/await while keeping the public API unchanged. Add error handling for network and token-expiry failures. Keep the change to one product surface.

## User Constraints

- Public function signatures must not change (callers must keep working without edits).
- No new runtime dependencies.
- TypeScript strict mode must stay green.
- Preserve existing test behavior; add tests for the new error paths.

## In Scope

- `src/auth/login.ts` (rewrite internals)
- `src/auth/__tests__/login.test.ts` (extend)
- Any shared type in `src/auth/types.ts` if the error shape needs it

## Out Of Scope

- Other auth flows (signup, password reset)
- Backend API changes
- UI/login form changes

## Expected Verification

- `npm run lint` passes
- `npm test -- src/auth` passes with new error-path tests green
- A diff showing only the auth surface changed

## Known Risk

- The current code mixes `request()` callbacks with a manual token refresh; naive conversion can drop the refresh-on-401 retry behavior. Review must verify the retry path is preserved.

## Strategic good_enough

The login flow is async/await end to end, the 401-retry behavior is preserved and covered by a test, public signatures are unchanged, and the auth test suite is green. A residual edge case (e.g. concurrent refresh races) may be deferred to a follow-up issue with a named reason.

## Route Tier

T3 — the change touches error-handling and retry logic across the auth surface and benefits from an independent plan and an independent read-only review.

## subagent_policy

dual plan: `required` (plan-B subagent)
dual review: `required` (two review subagents)
fallback_if_subagent_unavailable: stop-for-user-checkpoint
