# Strategic Loop Contract

Use this reference when a T3/T4 loop needs a strategic target that can be dispatched, checked, and stopped. The strategic document and the operational contract are one artifact, not two competing files.

## When Required

Create or update a Strategic Loop Contract before execution when:

- route tier is T3 or T4;
- the work changes product direction, architecture, workflow boundaries, or cross-role coordination;
- the user asks for a manager-driven loop that should keep moving;
- a prior plan lacks a clear "good enough" target or stop condition.

For T0/T1/T2, use the fields lightly in the current thread or checklist. Do not create heavyweight documents for small work.

## Contract Shape

```yaml
strategy:
  loop_id:
  goal:
  end_state:
  good_enough:
  non_goals:
  user_value:
  evidence_of_success:
  stop_condition:
  user_checkpoints:

operation:
  route_tier: T0|T1|T2|T3|T4|T5
  route_justification:
  six_interfaces:
    goal:
    state:
    context:
    act:
    capture:
    stop:
  roles:
    - name:
      role:
      who: main_agent|subagent
      decision_rights:
      write_scope:
      output_artifact:
  state_sources:
  context_pack:
  allowed_actions:
  capture_required:
  expected_artifacts:
  subagent_policy:
  required_subagent_artifact:
  fallback_if_subagent_unavailable:
  blocker_signal:
  loop_state_path:               # path to loop-state.md (T3/T4 mandatory)
  dual_mode: same_model_auto     # same_model_auto|cross_model_manual|not_needed
  auto_iteration: enabled        # enabled|disabled
```

Differences from the codex version: `lanes` is renamed `roles` with a `who` field (main_agent / subagent); `claude_policy` / `required_claude_artifact` / `fallback_if_claude_unavailable` are replaced by `subagent_policy` / `required_subagent_artifact` / `fallback_if_subagent_unavailable`; `check_after` and `deadline` are removed because TRAE Task subagents return synchronously and there is no async lane monitoring.

## Rules

- `strategy.good_enough` is mandatory for T3/T4. If absent, write `strategy-gap: missing good_enough` and stop before tactical or execution planning.
- `operation.route_tier` must be chosen before roles are created.
- T3/T4 execution batches must be product-surface, workflow-state, durable-contract, migration, source-policy, or security slices. Do not make helper-level batches full review units.
- `state_sources` should point to worklogs, prior final reports, specs, or durable state files. Chat history alone is not state.
- `capture_required` must name what evidence will be written: command output, diff, screenshot, review finding, artifact path, or decision log.
- `stop_condition` must include done evidence and hard stops such as user checkpoint, max rounds, budget cap, no new evidence, production/destructive risk, or route-tier mismatch.
- `blocker_signal` must include user-visible completion/blocker corrections. A user saying "this is done" or "the review is missing" is a state signal that triggers immediate artifact-first checking.
- T3/T4 contracts must specify `loop_state_path` pointing at the loop's `loop-state.md`; this is the file resume reads first.
- `dual_mode` decides whether plan-B/review-B go through Task subagents (`same_model_auto`) or manual transport (`cross_model_manual`, see `hybrid-dual.md`).
- `auto_iteration` records whether the loop may auto-advance; it requires TRAE auto-run ON to take effect (see `auto-iteration.md`).
- Frontend/product-surface execution contracts must describe the visible UI shape and user calibration point, including placeholder/degraded states when backend behavior is deferred.

## Dispatch Use

The main agent (manager mode) should send artifact paths and exact read requirements from the contract. Do not paste the whole contract into every handoff when the artifact exists.

The execution role reads the merged plan and the contract. The review subagent receives the contract (or relevant excerpt), execution report, changed diff, tests, and relevant complete functions. Arbitration reads the contract, both reviews, execution report, and live evidence.
