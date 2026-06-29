#!/usr/bin/env python3
"""Validate a TRAE Loop Engineering contract, merged plan, or handoff artifact.

Python 3.8+ cross-platform port of validate-loop-contract.ps1 (standard library
only: re, json, sys, argparse, pathlib).

Checks route tier, six-interface fields (T2+), done/stop conditions (T2+),
strategic good_enough and expected artifacts (T3+), subagent_policy required
fields, and strategy-gap / plan-gap / loop-limit-reached markers.

Fixes versus the PowerShell original:
  P3-4  The Has-Key token matcher now uses (?:^|_)key(?:_|$) instead of _key_,
        so a key occurring at the start or end of the normalized text is still
        detected (the original required an underscore on both sides and missed
        leading/trailing occurrences).

Exit codes:
  0  validation ok
  1  validation failed (or empty file)
  2  file not found / unreadable

Examples:
  python validate-loop-contract.py ./12-plan-merged.md
  python validate-loop-contract.py ./contract.md --json
"""
import argparse
import json
import re
import sys
from pathlib import Path


def has_key(text, key):
    """Return True if the normalized text contains ``key`` as a token.

    Mirrors the PowerShell Has-Key helper, with the P3-4 fix: the match pattern
    is ``(?:^|_)key(?:_|$)`` instead of ``_key_`` so that keys sitting at the
    very start or end of the normalized string are still recognized.
    """
    k = re.sub(r'[^a-z0-9]+', '_', key)
    return re.search(r'(?:^|_)' + re.escape(k) + r'(?:_|$)', text) is not None


def detect_route_tier(raw):
    """Extract the route tier (e.g. 'T3') from the raw text, or None."""
    m = re.search(r'route[_\s-]?tier\s*[:=]\s*"?T([0-5])"?', raw, re.IGNORECASE)
    if m:
        return 'T' + m.group(1)
    return None


def validate(raw):
    """Run all contract checks. Returns (route_tier, errors, warnings)."""
    errors = []
    warnings = []

    # Normalize for keyword scanning: lowercase, non-alphanumeric -> underscore,
    # then collapse runs of underscores so "route_tier" / "route tier" /
    # "route-tier" all match.
    norm = re.sub(r'[^a-z0-9]+', '_', raw.lower())
    norm = re.sub(r'_+', '_', norm)

    # --- Route tier detection ---
    route_tier = detect_route_tier(raw)

    # --- Six-interface fields (T2+) ---
    six_interfaces = ['goal', 'state', 'context', 'act', 'capture', 'stop']
    if route_tier in ('T2', 'T3', 'T4', 'T5'):
        for iface in six_interfaces:
            if not has_key(norm, iface):
                errors.append('missing six-interface field: %s' % iface)
        # done / stop condition
        has_done = (has_key(norm, 'done')
                    or has_key(norm, 'done_check')
                    or has_key(norm, 'completion_criteria')
                    or has_key(norm, 'stop_condition'))
        if not has_done:
            errors.append('missing done/stop condition '
                         '(done_check | completion_criteria | stop_condition)')

    # --- T3/T4 strategic requirements ---
    if route_tier in ('T3', 'T4'):
        if not has_key(norm, 'good_enough'):
            errors.append('missing strategic good_enough target')
        if not has_key(norm, 'expected_artifacts') and not has_key(norm, 'expected_artifact'):
            warnings.append('T3+ contract should list expected_artifacts')
        if not has_key(norm, 'blocker_signal'):
            warnings.append('T3+ contract should define blocker_signal')

    # --- subagent_policy: required must list required_subagent_artifact + fallback ---
    if has_key(norm, 'subagent_policy'):
        policy_required = False
        m = re.search(r'subagent_policy\s*[:=]\s*"?([a-z_]+)"?', raw, re.IGNORECASE)
        if m and m.group(1).lower() == 'required':
            policy_required = True
        if policy_required:
            if not has_key(norm, 'required_subagent_artifact'):
                errors.append('subagent_policy: required is missing required_subagent_artifact')
            if not has_key(norm, 'fallback_if_subagent_unavailable'):
                errors.append('subagent_policy: required is missing fallback_if_subagent_unavailable')

    # --- Gap markers ---
    if has_key(norm, 'strategy_gap'):
        warnings.append('strategy-gap marker present; execution should not start')
    if has_key(norm, 'plan_gap'):
        warnings.append('plan-gap marker present; merged plan cannot satisfy brief')
    if has_key(norm, 'loop_limit_reached'):
        warnings.append('loop-limit-reached marker present; loop is stopped for user input')

    return route_tier, errors, warnings


def build_result(path, ok, route_tier, errors, warnings):
    """Build the JSON-serializable result object (same shape as PowerShell)."""
    return {
        'path': path,
        'ok': ok,
        'route_tier': route_tier,
        'errors': errors,
        'warnings': warnings,
    }


def main(argv=None):
    parser = argparse.ArgumentParser(
        description='Validate a TRAE Loop Engineering contract / merged plan / '
                    'handoff markdown file.',
        epilog='Exit codes: 0=ok, 1=validation fail, 2=file not found.',
    )
    parser.add_argument('path',
                        help='Path to the contract / merged-plan / handoff markdown file.')
    parser.add_argument('--json', dest='as_json', action='store_true',
                        help='Emit a structured JSON object instead of human-readable text.')
    args = parser.parse_args(argv)

    path_obj = Path(args.path)

    # --- File not found / unreadable (exit 2) ---
    if not path_obj.is_file():
        msg = 'file not found: %s' % args.path
        if args.as_json:
            print(json.dumps(build_result(args.path, False, None, [msg], []), indent=2))
        else:
            print('FAIL: %s' % msg)
        return 2

    try:
        raw = path_obj.read_text(encoding='utf-8')
    except OSError as exc:
        msg = 'could not read file: %s: %s' % (args.path, exc)
        if args.as_json:
            print(json.dumps(build_result(args.path, False, None, [msg], []), indent=2))
        else:
            print('FAIL: %s' % msg)
        return 2

    # --- Empty file (exit 1: file was found but content is invalid) ---
    if not raw.strip():
        msg = 'empty file: %s' % args.path
        if args.as_json:
            print(json.dumps(build_result(args.path, False, None, [msg], []), indent=2))
        else:
            print('FAIL: %s' % msg)
        return 1

    route_tier, errors, warnings = validate(raw)
    ok = len(errors) == 0

    if args.as_json:
        print(json.dumps(build_result(args.path, ok, route_tier, errors, warnings), indent=2))
    else:
        print('%s: %s' % ('OK' if ok else 'FAIL', args.path))
        if route_tier:
            print('route_tier: %s' % route_tier)
        for err in errors:
            print('ERROR: %s' % err)
        for warn in warnings:
            print('WARNING: %s' % warn)

    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
