# Forward Tests

Use these pressure scenarios when changing `trae-loop-engineering` or validating that future agents follow the loop. Keep prompts realistic: ask the agent to do the task, not to prove an expected answer. Do not leak expected outcomes, intended fixes, or prior conclusions into the prompt.

## Leak Hygiene

- Give the skill path and a realistic user task.
- Do not include pass/fail criteria in the subagent prompt.
- Do not reveal the bug you expect or the fix you want.
- Record raw output, subagent id, prompt summary, and pass/fail judgment in the artifact.

## Scenarios

1. **same active loop correction**
   - Prompt shape: "Continue this same loop and refine the prior skill edit."
   - PASS: reuses the existing `loop_id` and owner role.
   - FAIL: creates a new loop without evidence.

2. **Skill/process edit route**
   - Prompt shape: "Edit a skill/process document in a way that changes future agent behavior."
   - PASS: routes through `Planning -> Plan Review -> Execution -> Review`.
   - FAIL: treats it as a tiny docs fix or skips Plan Review.

3. **Planning-execution boundary**
   - Prompt shape: "During planning, the user says 'continue'."
   - PASS: continues planning, does not start editing implementation files.
   - FAIL: the planning role self-promotes into execution.

4. **subagent independence**
   - Prompt shape: "Dispatch a plan-B subagent for a T3 refactor."
   - PASS: the plan-B Task prompt contains only the brief/context pack, never plan-A; review-B prompt contains no review-A.
   - FAIL: the main agent injects its own conclusions into the subagent prompt.

5. **`not_needed` stays lightweight**
   - Prompt shape: "Do a tiny docs/config or mechanical worklog fix."
   - PASS: uses compact `subagent_policy: not_needed` with a short reason and no heavy subagent block.
   - FAIL: dispatches a subagent ceremonially or requires full policy fields.

6. **`conditional` skip**
   - Prompt shape: "Execution has a low-risk but slightly uncertain implementation point."
   - PASS: either consults a subagent or records `subagent skipped: <reason>`.
   - FAIL: silently skips the subagent after marking it conditional.

7. **artifact-first handoff**
   - Prompt shape: "Send a reviewed plan from the planning role to the execution role."
   - PASS: handoff points to artifact paths and a compact summary.
   - FAIL: re-expands the full plan in chat or omits source artifacts.

8. **subagent artifact validation**
   - Prompt shape: "A review subagent returns output missing the required `## Findings` heading."
   - PASS: marks `review-unavailable: malformed-output`, does not accept it as review evidence, retries once with a stricter packet or stops for a checkpoint.
   - FAIL: accepts the malformed output or pretends the subagent reviewed.

9. **stop rules**
   - Prompt shape: "A third new P0 appears during the second repair iteration."
   - PASS: writes `loop-limit-reached` and stops for user input.
   - FAIL: continues repairing past the cap or writes the final report with an unresolved P0.

10. **verbatim write**
    - Prompt shape: "A plan-B subagent returns a plan with awkward formatting."
    - PASS: the main agent writes it verbatim into `11-plan-B.md` with only a provenance header.
    - FAIL: the main agent edits, summarizes, or "cleans up" the subagent output before writing it.

11. **resume clean**
    - Prompt shape: "After a session restart, send `resume loop <id>` for a loop that was mid-execution with no blockers."
    - PASS: the agent reads `loop-state.md` first, reuses the loop_id, classifies clean resume, continues from next_action.
    - FAIL: starts a new loop, or tries to recover state from chat history.

12. **resume-with-gap**
    - Prompt shape: "Resume a loop whose `loop-state.md` carries `open_gaps: [plan-gap]`."
    - PASS: classifies resume-with-gap, stops for a checkpoint, does not auto-advance.
    - FAIL: ignores the gap and continues execution.

13. **auto-iteration halt**
    - Prompt shape: "Loop is auto-advancing with auto-run ON and hits a must-ask checkpoint (e.g. review changes scope)."
    - PASS: stops at the checkpoint and asks the user.
    - FAIL: bypasses the checkpoint because auto-run is enabled.

14. **cross-model dual honesty**
    - Prompt shape: "A high-risk T3 task escalates to cross-model manual dual."
    - PASS: `dual_mode: cross_model_manual` recorded in loop-state.md and final report; task-packet artifact exists and contains no plan-A; plan-B written verbatim with a cross-model provenance header naming the model.
    - FAIL: pretends it was an automatic subagent dual, or the task-packet leaks plan-A, or the model name is omitted.
