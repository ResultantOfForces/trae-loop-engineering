# State And Feedback Schema

Use this reference when a loop has multiple rounds, reviews, repairs, or user checkpoints. The goal is to make `capture -> feedback -> state -> next context` explicit so the next role does not rediscover the same facts from chat.

## Core Rule

Every meaningful loop event should answer:

```text
What changed?
What evidence proves it?
How does the next prompt, plan, or action change?
Who owns the next step?
Should the loop stop or continue?
```

## Snapshot vs Event Stream

There are two complementary state representations. Do not confuse them:

- `loop-state.md` is the **current snapshot** (overwrite on each change). It answers "where is the loop right now?". It is the first file read on resume.
- `worklog.md` + the `state_event`/`feedback_event` below is the **event stream** (append-only). It answers "how did the loop get here?".

After appending a `state_event` to the worklog, sync the matching fields (`phase`, `role`, `next_action`, `blockers`, `latest_artifacts`) into `loop-state.md`. The event records the transition; the snapshot records the resulting state. Field structure and update rules for the snapshot: see `loop-state-schema.md`. Cross-session resume procedure: see `resume-protocol.md`.

## State Event

Append state events to a worklog or dedicated state artifact.

```yaml
state_event:
  loop_id:
  event_id:
  created_at:
  phase:
  role:
  subagent_id:        # optional, when the event was produced by a subagent
  status: pending|active|blocked|completed|deferred
  latest_artifacts:
  accepted_decisions:
  open_blockers:
  user_decisions:
  next_role:
  next_action:
  stop_or_continue:
  evidence:
```

`role` replaces the codex `owner_lane`; `subagent_id` is added so one-shot subagent contributions are traceable.

## Feedback Event

Use feedback events after review, arbitration, repair, failed validation, or user corrections.

```yaml
feedback_event:
  loop_id:
  source_event:
  source_role:
  subagent_id:        # optional
  finding:
  evidence:
  decision: accept|reject|third_path|defer|needs_more_evidence|checkpoint
  next_prompt_delta:
  next_context_delta:
  next_action:
  next_role:
  stop_or_continue:
```

## Communication Rules

- Do not store hidden chain-of-thought. Store decisions, evidence, artifacts, and prompt/context deltas.
- A review finding is not feedback until it changes a decision, next prompt, next context, or next action.
- Arbitration must convert accepted review findings into feedback events or explain why no next-context change is needed.
- The manager role should read state/feedback artifacts before deciding the next handoff.
- If an event changes scope, product direction, architecture, data contract, source policy, or degraded-tool mode, mark `stop_or_continue: checkpoint`.
- If the same failure repeats and `next_prompt_delta` is empty, stop for a planning or user checkpoint instead of looping.
- If an event supersedes an active artifact, role route, or expected output, record what is now historical, what replaces it, and which stale checks must be updated.
- If the user correction changes the strategic target, execution boundary, or "good enough" definition, update or append the Strategic Loop Contract and rerun its validator before dispatching the next production execution.

## Superseding Event

Use this compact form when a user correction, planning decision, or failed preview invalidates an older route:

```yaml
superseding_event:
  loop_id:
  created_at:
  supersedes:
    artifacts:
    roles:
    subagents:
  reason:
  replacement_artifacts:
  new_role:
  next_action:
  validator_required: true|false
  stop_or_continue: checkpoint|continue
```

## Minimal Inline Form

For small loops (T0-T2), a compact markdown entry is enough:

```markdown
State:
- phase:
- status:
- latest artifacts:
- blockers:
- next role:

Feedback:
- finding:
- evidence:
- decision:
- next prompt/context change:
- next action:
- stop/continue:
```
