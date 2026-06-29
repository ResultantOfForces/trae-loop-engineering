# Strategic Loop Contract — Fillable Template

> Copy this file to `docs/loop-engineering/<YYYY-MM-DD-slug>/strategic-loop-contract.md`, fill the YAML, and validate with `powershell -File scripts/validate-loop-contract.ps1 -Path <this-file>` (macOS/Linux: `python3 scripts/validate-loop-contract.py <this-file>`). Required for T3/T4 loops; use the fields lightly for T0-T2 and do not create heavyweight documents for small work. The rules behind each field live in `references/strategic-loop-contract.md`.

```yaml
strategy:
  loop_id: <YYYY-MM-DD-slug>
  goal: <what the loop must accomplish>
  end_state: <the durable end state when the loop is done>
  good_enough: <minimum useful completion target + the evidence that proves it>   # mandatory for T3/T4
  non_goals: <explicitly out of scope>
  user_value: <the user-visible value delivered>
  evidence_of_success: <commands / artifacts / screenshots that prove success>
  stop_condition: <done evidence + hard stops: user checkpoint, max rounds, budget cap, no new evidence, production/destructive risk, route-tier mismatch>
  user_checkpoints: <critical direction changes and degraded gates that pause the loop>

operation:
  route_tier: <T0|T1|T2|T3|T4|T5>
  route_justification: <what risk does this heavier route reduce>
  six_interfaces:
    goal: <brief / completion criteria>
    state: <worklog / known attempts>
    context: <context pack / source artifacts>
    act: <allowed tools / write scope>
    capture: <command output / diff / finding / artifact path>
    stop: <done check / budget / round cap / risk stop>
  roles:
    - name: <role name>
      role: <planning|execution|review|arbitration|manager>
      who: <main_agent|subagent>
      decision_rights: <what this role may decide>
      write_scope: <what files/artifacts this role may write>
      output_artifact: <artifact this role produces>
  state_sources: <worklogs, prior final reports, specs, durable state files — never chat history alone>
  context_pack: <how state becomes prompt input for the next role>
  allowed_actions: <tools and write scope available to the loop>
  capture_required: <what evidence will be written: command output, diff, screenshot, review finding, artifact path, decision log>
  expected_artifacts: <00-brief.md ... 50-final-report.md subset>
  subagent_policy: <not_needed|conditional|required>
  required_subagent_artifact: <artifact a required subagent must return before close-out>
  fallback_if_subagent_unavailable: <retry|optimize-and-retry|stop-for-checkpoint|proceed-degraded>
  blocker_signal: <user-visible completion/blocker corrections that trigger artifact-first checking>
  loop_state_path: docs/loop-engineering/<YYYY-MM-DD-slug>/loop-state.md   # T3/T4 mandatory
  dual_mode: <same_model_auto|cross_model_manual|not_needed>
  auto_iteration: <enabled|disabled>
```

## Rules To Remember

- `strategy.good_enough` is mandatory for T3/T4. If absent, write `strategy-gap: missing good_enough` and stop before tactical or execution planning.
- `operation.route_tier` must be chosen before roles are created.
- T3/T4 execution batches must be product-surface, workflow-state, durable-contract, migration, source-policy, or security slices. Do not make helper-level batches into full review units.
- `state_sources` should point to worklogs, prior final reports, specs, or durable state files. Chat history alone is not state.
- `capture_required` must name what evidence will be written: command output, diff, screenshot, review finding, artifact path, or decision log.
- `stop_condition` must include done evidence and hard stops such as user checkpoint, max rounds, budget cap, no new evidence, production/destructive risk, or route-tier mismatch.
- `blocker_signal` must include user-visible completion/blocker corrections. A user saying "this is done" or "the review is missing" is a state signal that triggers immediate artifact-first checking.
- T3/T4 contracts must specify `loop_state_path` pointing at the loop's `loop-state.md`; this is the file resume reads first.
- `dual_mode` decides whether plan-B/review-B go through Task subagents (`same_model_auto`) or manual transport (`cross_model_manual`, see `references/hybrid-dual.md`).
- `auto_iteration` records whether the loop may auto-advance; it requires TRAE auto-run ON to take effect (see `references/auto-iteration.md`).
- Frontend/product-surface execution contracts must describe the visible UI shape and user calibration point, including placeholder/degraded states when backend behavior is deferred.
