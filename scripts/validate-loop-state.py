#!/usr/bin/env python3
"""Validate a TRAE Loop Engineering loop-state.md snapshot file.

Python 3.8+ cross-platform port of validate-loop-state.ps1 (standard library
only: re, json, sys, argparse, pathlib).

Checks required fields, legal enum values (phase / loop_status / dual_mode /
auto_iteration / subagent_policy / route_tier) and consistency constraints
(blockers vs status, open_gaps vs status, user_decisions_pending vs status,
repair_iteration cap, dual_mode vs subagent_dispatches, phase=final but active).

Fixes versus the PowerShell original:
  P2-2  Added missing enum validation for subagent_policy
        (not_needed|conditional|required) and route_tier (T0..T5).
  P3-1  Fixed the redundant blockers condition. The original was
        `$blockersLine -ne '[]' -and ($blockersLine -ne '[]')` (a duplicate);
        the second clause now also excludes the values 'none' and '' so that
        an explicitly-empty blockers list is not treated as "has blockers".

Exit codes:
  0  validation ok
  1  validation failed (or empty file)
  2  file not found / unreadable

Examples:
  python validate-loop-state.py ./loop-state.md
  python validate-loop-state.py ./loop-state.md --json
"""
import argparse
import json
import re
import sys
from pathlib import Path


def has(text, key):
    """Return True if the normalized text contains ``key`` as a token.

    Mirrors the PowerShell Has helper: matches ``(?:^|_)key_`` on the
    already-normalized (lowercased, underscore-collapsed) text.
    """
    k = re.sub(r'[^a-z0-9]+', '_', key)
    return re.search(r'(?:^|_)' + re.escape(k) + r'_', text) is not None


def get_val(text, key):
    """Return the value for ``key`` in ``text`` (case-insensitive), or None.

    Mirrors Get-Val: matches ``key\\s*:\\s*(...)`` up to the next newline or
    markdown-comment hash, then strips surrounding whitespace and quotes.
    """
    m = re.search(re.escape(key) + r'\s*:\s*([^\r\n#]+)', text, re.IGNORECASE)
    if m:
        return m.group(1).strip().strip("'").strip('"')
    return None


def validate(raw):
    """Run all loop-state checks.

    Returns (phase, status, dual_mode, errors, warnings). The JSON output shape
    intentionally matches the PowerShell version (route_tier / subagent_policy
    are validated but not surfaced as top-level JSON keys).
    """
    errors = []
    warnings = []

    # Normalize for keyword scanning: lowercase, non-alphanumeric -> underscore,
    # collapse runs of underscores.
    norm = re.sub(r'[^a-z0-9]+', '_', raw.lower())
    norm = re.sub(r'_+', '_', norm)

    # --- Required fields ---
    required = [
        'loop_id', 'phase', 'phase_step', 'role', 'loop_status', 'next_action',
        'next_role', 'route_tier', 'subagent_policy', 'dual_mode', 'auto_iteration',
        'repair_iteration', 'resume_count', 'last_updated',
    ]
    for field in required:
        if not has(norm, field):
            errors.append('missing required field: %s' % field)

    # --- Enum: phase ---
    phase = get_val(raw, 'phase')
    valid_phases = ['brief', 'dual_plan', 'plan_merge', 'execution',
                    'execution_report', 'dual_review', 'arbitration', 'final']
    if phase and phase.lower() not in valid_phases:
        errors.append('invalid phase: %s (expected one of: %s)'
                      % (phase, ', '.join(valid_phases)))

    # --- Enum: loop_status ---
    status = get_val(raw, 'loop_status')
    valid_status = ['active', 'blocked', 'completed', 'paused', 'limit_reached']
    if status and status.lower() not in valid_status:
        errors.append('invalid loop_status: %s (expected one of: %s)'
                      % (status, ', '.join(valid_status)))

    # --- Enum: dual_mode ---
    dual_mode = get_val(raw, 'dual_mode')
    valid_dual = ['same_model_auto', 'cross_model_manual', 'not_needed']
    if dual_mode and dual_mode.lower() not in valid_dual:
        errors.append('invalid dual_mode: %s (expected one of: %s)'
                      % (dual_mode, ', '.join(valid_dual)))

    # --- Enum: auto_iteration ---
    auto_iter = get_val(raw, 'auto_iteration')
    if auto_iter and auto_iter.lower() not in ('enabled', 'disabled'):
        errors.append('invalid auto_iteration: %s (expected enabled|disabled)' % auto_iter)

    # P2-2: --- Enum: subagent_policy (missing from PowerShell original) ---
    subagent_policy = get_val(raw, 'subagent_policy')
    valid_policy = ['not_needed', 'conditional', 'required']
    if subagent_policy and subagent_policy.lower() not in valid_policy:
        errors.append('invalid subagent_policy: %s (expected one of: %s)'
                      % (subagent_policy, ', '.join(valid_policy)))

    # P2-2: --- Enum: route_tier (missing from PowerShell original) ---
    route_tier = get_val(raw, 'route_tier')
    valid_tiers = ['T0', 'T1', 'T2', 'T3', 'T4', 'T5']
    if route_tier and route_tier.upper() not in valid_tiers:
        errors.append('invalid route_tier: %s (expected one of: %s)'
                      % (route_tier, ', '.join(valid_tiers)))

    status_l = status.lower() if status else None

    # --- Consistency: blockers vs status (P3-1 fix for redundant condition) ---
    # Original duplicated `!= '[]'`; the second clause now also excludes
    # 'none' and the empty string, so an explicitly-empty blockers list is
    # not mistaken for "has blockers".
    blockers_line = get_val(raw, 'blockers')
    bl = blockers_line.lower() if blockers_line else ''
    has_blockers = (bool(blockers_line)
                    and bl != '[]'
                    and bl != 'none'
                    and bl.strip() != '')
    if has_blockers and status_l == 'active':
        warnings.append('blockers non-empty but loop_status=active; expected blocked')

    # --- Consistency: open_gaps vs status ---
    gaps_line = get_val(raw, 'open_gaps')
    has_gaps = bool(gaps_line) and gaps_line.lower() != '[]'
    if has_gaps and status_l in ('active', 'completed'):
        errors.append('open_gaps non-empty but loop_status=%s; '
                      'expected blocked/paused/limit_reached' % status)

    # --- Consistency: user_decisions_pending vs status ---
    udp_line = get_val(raw, 'user_decisions_pending')
    has_udp = bool(udp_line) and udp_line.lower() != '[]'
    if has_udp and status_l != 'blocked':
        errors.append('user_decisions_pending non-empty but loop_status=%s; '
                      'expected blocked' % status)

    # --- Consistency: repair_iteration cap ---
    repair = get_val(raw, 'repair_iteration')
    if repair:
        try:
            repair_n = int(repair)
        except (ValueError, TypeError):
            repair_n = 0
        if repair_n > 2:
            if not has(norm, 'loop_limit_reached'):
                errors.append('repair_iteration=%d exceeds cap 2 but no '
                              'loop-limit-reached marker in open_gaps' % repair_n)

    # --- Consistency: dual_mode=cross_model_manual vs subagent_dispatches ---
    if dual_mode and dual_mode.lower() == 'cross_model_manual':
        if has(norm, 'subagent_dispatches') and re.search(r'subagent_dispatches_.*_plan_b', norm):
            errors.append('dual_mode=cross_model_manual but subagent_dispatches contains a '
                          'plan_b entry; cross-model B is transported manually')

    # --- Consistency: phase=final but active ---
    if phase and phase.lower() == 'final' and status_l == 'active':
        warnings.append('phase=final but loop_status=active; final phase should complete or block')

    return phase, status, dual_mode, errors, warnings


def build_result(path, ok, phase, status, dual_mode, errors, warnings):
    """Build the JSON-serializable result object (same shape as PowerShell)."""
    return {
        'path': path,
        'ok': ok,
        'phase': phase,
        'status': status,
        'dual_mode': dual_mode,
        'errors': errors,
        'warnings': warnings,
    }


def main(argv=None):
    parser = argparse.ArgumentParser(
        description='Validate a TRAE Loop Engineering loop-state.md snapshot file.',
        epilog='Exit codes: 0=ok, 1=validation fail, 2=file not found.',
    )
    parser.add_argument('path', help='Path to the loop-state.md file.')
    parser.add_argument('--json', dest='as_json', action='store_true',
                        help='Emit a structured JSON object instead of human-readable text.')
    args = parser.parse_args(argv)

    path_obj = Path(args.path)

    # --- File not found / unreadable (exit 2) ---
    if not path_obj.is_file():
        msg = 'file not found: %s' % args.path
        if args.as_json:
            print(json.dumps(build_result(args.path, False, None, None, None, [msg], []), indent=2))
        else:
            print('FAIL: %s' % msg)
        return 2

    try:
        raw = path_obj.read_text(encoding='utf-8')
    except OSError as exc:
        msg = 'could not read file: %s: %s' % (args.path, exc)
        if args.as_json:
            print(json.dumps(build_result(args.path, False, None, None, None, [msg], []), indent=2))
        else:
            print('FAIL: %s' % msg)
        return 2

    # --- Empty file (exit 1: file was found but content is invalid) ---
    if not raw.strip():
        msg = 'empty file: %s' % args.path
        if args.as_json:
            print(json.dumps(build_result(args.path, False, None, None, None, [msg], []), indent=2))
        else:
            print('FAIL: %s' % msg)
        return 1

    phase, status, dual_mode, errors, warnings = validate(raw)
    ok = len(errors) == 0

    if args.as_json:
        print(json.dumps(build_result(args.path, ok, phase, status, dual_mode, errors, warnings), indent=2))
    else:
        print('%s: %s' % ('OK' if ok else 'FAIL', args.path))
        if phase:
            print('phase: %s' % phase)
        if status:
            print('loop_status: %s' % status)
        if dual_mode:
            print('dual_mode: %s' % dual_mode)
        for err in errors:
            print('ERROR: %s' % err)
        for warn in warnings:
            print('WARNING: %s' % warn)

    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
