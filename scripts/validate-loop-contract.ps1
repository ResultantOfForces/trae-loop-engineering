<#
.SYNOPSIS
  Validates a TRAE Loop Engineering contract, merged plan, or handoff artifact.

.DESCRIPTION
  Ports codex-loop-engineering/scripts/validate-loop-contract.py to Windows PowerShell.
  Checks route tier, six-interface fields (T2+), done/stop conditions (T2+),
  strategic good_enough and expected artifacts (T3+), subagent_policy required
  fields, and strategy-gap / plan-gap markers. Prints OK/FAIL plus errors and
  warnings. Exit code 0 = ok, 1 = fail.

.PARAMETER Path
  Path to the contract / merged-plan / handoff markdown file.

.PARAMETER Json
  Output a JSON object instead of human-readable text.

.EXAMPLE
  powershell -File validate-loop-contract.ps1 -Path .\12-plan-merged.md
  powershell -File validate-loop-contract.ps1 -Path .\contract.md -Json
#>
[CmdletBinding()]
param(
  [Parameter(Mandatory = $true)]
  [string]$Path,

  [switch]$Json
)

$ErrorActionPreference = 'Stop'

if (-not (Test-Path -LiteralPath $Path)) {
  Write-Host "FAIL: file not found: $Path"
  exit 1
}

$raw = Get-Content -LiteralPath $Path -Raw -Encoding UTF8
if ([string]::IsNullOrWhiteSpace($raw)) {
  Write-Host "FAIL: empty file: $Path"
  exit 1
}

# Normalize: lowercase, collapse non-alphanumeric to underscores for keyword scanning.
$norm = $raw.ToLower()
$norm = $norm -replace '[^a-z0-9]+', '_'
# Collapse repeated underscores so "route_tier" / "route tier" / "route-tier" match.
$norm = $norm -replace '_+', '_'

$errors = New-Object System.Collections.Generic.List[string]
$warnings = New-Object System.Collections.Generic.List[string]

function Has-Key($text, $key) {
  $k = $key -replace '[^a-z0-9]+', '_'
  return $text -match "_$($k)_"
}

# --- Route tier detection ---
$routeTier = $null
$tierMatch = [regex]::Match($raw, '(?i)route[_\s-]?tier\s*[:=]\s*"?T([0-5])"?')
if ($tierMatch.Success) {
  $routeTier = "T$($tierMatch.Groups[1].Value)"
}

# --- Six-interface fields (T2+) ---
$sixInterfaces = @('goal', 'state', 'context', 'act', 'capture', 'stop')
if ($routeTier -and ($routeTier -eq 'T2' -or $routeTier -eq 'T3' -or $routeTier -eq 'T4' -or $routeTier -eq 'T5')) {
  foreach ($iface in $sixInterfaces) {
    if (-not (Has-Key $norm $iface)) {
      $errors.Add("missing six-interface field: $iface")
    }
  }
  # done / stop condition
  $hasDone = (Has-Key $norm 'done') -or (Has-Key $norm 'done_check') -or (Has-Key $norm 'completion_criteria') -or (Has-Key $norm 'stop_condition')
  if (-not $hasDone) {
    $errors.Add("missing done/stop condition (done_check | completion_criteria | stop_condition)")
  }
}

# --- T3/T4 strategic requirements ---
if ($routeTier -and ($routeTier -eq 'T3' -or $routeTier -eq 'T4')) {
  if (-not (Has-Key $norm 'good_enough')) {
    $errors.Add("missing strategic good_enough target")
  }
  if (-not (Has-Key $norm 'expected_artifacts') -and -not (Has-Key $norm 'expected_artifact')) {
    $warnings.Add("T3+ contract should list expected_artifacts")
  }
  if (-not (Has-Key $norm 'blocker_signal')) {
    $warnings.Add("T3+ contract should define blocker_signal")
  }
}

# --- subagent_policy: required must list required_subagent_artifact + fallback ---
if (Has-Key $norm 'subagent_policy') {
  $policyRequired = $false
  $m = [regex]::Match($raw, '(?i)subagent_policy\s*[:=]\s*"?([a-z_]+)"?')
  if ($m.Success -and $m.Groups[1].Value -eq 'required') {
    $policyRequired = $true
  }
  if ($policyRequired) {
    if (-not (Has-Key $norm 'required_subagent_artifact')) {
      $errors.Add("subagent_policy: required is missing required_subagent_artifact")
    }
    if (-not (Has-Key $norm 'fallback_if_subagent_unavailable')) {
      $errors.Add("subagent_policy: required is missing fallback_if_subagent_unavailable")
    }
  }
}

# --- Gap markers ---
if (Has-Key $norm 'strategy_gap') {
  $warnings.Add("strategy-gap marker present; execution should not start")
}
if (Has-Key $norm 'plan_gap') {
  $warnings.Add("plan-gap marker present; merged plan cannot satisfy brief")
}
if (Has-Key $norm 'loop_limit_reached') {
  $warnings.Add("loop-limit-reached marker present; loop is stopped for user input")
}

$ok = $errors.Count -eq 0

if ($Json) {
  $result = [ordered]@{
    path       = $Path
    ok         = $ok
    route_tier = $routeTier
    errors     = @($errors)
    warnings   = @($warnings)
  }
  $result | ConvertTo-Json -Depth 4
}
else {
  if ($ok) { Write-Host "OK: $Path" } else { Write-Host "FAIL: $Path" }
  if ($routeTier) { Write-Host "route_tier: $routeTier" }
  foreach ($e in $errors) { Write-Host "ERROR: $e" }
  foreach ($w in $warnings) { Write-Host "WARNING: $w" }
}

if ($ok) { exit 0 } else { exit 1 }
