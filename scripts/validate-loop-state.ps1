<#
.SYNOPSIS
  Validates a TRAE Loop Engineering loop-state.md snapshot file.

.DESCRIPTION
  Checks required fields, legal enum values (phase/loop_status/dual_mode/auto_iteration),
  and consistency constraints (blockers vs status, open_gaps vs status,
  user_decisions_pending vs status, repair_iteration cap, dual_mode vs subagent_dispatches).
  Exit code 0 = ok, 1 = fail.

.PARAMETER Path
  Path to the loop-state.md file.

.PARAMETER Json
  Output a JSON object instead of human-readable text.

.EXAMPLE
  powershell -File validate-loop-state.ps1 -Path .\loop-state.md
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

# Normalize for keyword scanning: lowercase, non-alphanumeric -> underscore, collapse.
$norm = $raw.ToLower() -replace '[^a-z0-9]+', '_' -replace '_+', '_'

$errors = New-Object System.Collections.Generic.List[string]
$warnings = New-Object System.Collections.Generic.List[string]

function Has($text, $key) {
  $k = $key -replace '[^a-z0-9]+', '_'
  return $text -match "(?:^|_)$($k)_"
}

function Get-Val($text, $key) {
  $m = [regex]::Match($text, "(?i)$key\s*:\s*([^\r\n#]+)")
  if ($m.Success) { return ($m.Groups[1].Value.Trim().Trim("'").Trim('"')) } else { return $null }
}

# --- Required fields ---
$required = @('loop_id', 'phase', 'phase_step', 'role', 'loop_status', 'next_action',
              'next_role', 'route_tier', 'subagent_policy', 'dual_mode', 'auto_iteration',
              'repair_iteration', 'resume_count', 'last_updated')
foreach ($f in $required) {
  if (-not (Has $norm $f)) { $errors.Add("missing required field: $f") }
}

# --- Enum: phase ---
$phase = Get-Val $raw 'phase'
$validPhases = @('brief','dual_plan','plan_merge','execution','execution_report','dual_review','arbitration','final')
if ($phase -and $validPhases -notcontains $phase) {
  $errors.Add("invalid phase: $phase (expected one of: $($validPhases -join ', '))")
}

# --- Enum: loop_status ---
$status = Get-Val $raw 'loop_status'
$validStatus = @('active','blocked','completed','paused','limit_reached')
if ($status -and $validStatus -notcontains $status) {
  $errors.Add("invalid loop_status: $status (expected one of: $($validStatus -join ', '))")
}

# --- Enum: dual_mode ---
$dualMode = Get-Val $raw 'dual_mode'
$validDual = @('same_model_auto','cross_model_manual','not_needed')
if ($dualMode -and $validDual -notcontains $dualMode) {
  $errors.Add("invalid dual_mode: $dualMode (expected one of: $($validDual -join ', '))")
}

# --- Enum: auto_iteration ---
$autoIter = Get-Val $raw 'auto_iteration'
if ($autoIter -and @('enabled','disabled') -notcontains $autoIter) {
  $errors.Add("invalid auto_iteration: $autoIter (expected enabled|disabled)")
}

# --- Consistency: blockers vs status ---
$blockersLine = (Get-Val $raw 'blockers')
$hasBlockers = $blockersLine -and ($blockersLine -ne '[]') -and ($blockersLine -ne '[]')
if ($hasBlockers -and $status -eq 'active') {
  $warnings.Add("blockers non-empty but loop_status=active; expected blocked")
}

# --- Consistency: open_gaps vs status ---
$gapsLine = (Get-Val $raw 'open_gaps')
$hasGaps = $gapsLine -and ($gapsLine -ne '[]')
if ($hasGaps -and $status -in @('active','completed')) {
  $errors.Add("open_gaps non-empty but loop_status=$status; expected blocked/paused/limit_reached")
}

# --- Consistency: user_decisions_pending vs status ---
$udpLine = (Get-Val $raw 'user_decisions_pending')
$hasUdp = $udpLine -and ($udpLine -ne '[]')
if ($hasUdp -and $status -ne 'blocked') {
  $errors.Add("user_decisions_pending non-empty but loop_status=$status; expected blocked")
}

# --- Consistency: repair_iteration cap ---
$repair = Get-Val $raw 'repair_iteration'
if ($repair) {
  try { $repairN = [int]$repair } catch { $repairN = 0 }
  if ($repairN -gt 2) {
    if (-not (Has $norm 'loop_limit_reached')) {
      $errors.Add("repair_iteration=$repairN exceeds cap 2 but no loop-limit-reached marker in open_gaps")
    }
  }
}

# --- Consistency: dual_mode=cross_model_manual vs subagent_dispatches ---
if ($dualMode -eq 'cross_model_manual') {
  if ((Has $norm 'subagent_dispatches') -and ($norm -match 'subagent_dispatches_.*_plan_b')) {
    $errors.Add("dual_mode=cross_model_manual but subagent_dispatches contains a plan_b entry; cross-model B is transported manually")
  }
}

# --- Consistency: phase=final but active ---
if ($phase -eq 'final' -and $status -eq 'active') {
  $warnings.Add("phase=final but loop_status=active; final phase should complete or block")
}

$ok = $errors.Count -eq 0

if ($Json) {
  $result = [ordered]@{
    path     = $Path
    ok       = $ok
    phase    = $phase
    status   = $status
    dual_mode = $dualMode
    errors   = @($errors)
    warnings = @($warnings)
  }
  $result | ConvertTo-Json -Depth 4
} else {
  if ($ok) { Write-Host "OK: $Path" } else { Write-Host "FAIL: $Path" }
  if ($phase)  { Write-Host "phase: $phase" }
  if ($status) { Write-Host "loop_status: $status" }
  if ($dualMode) { Write-Host "dual_mode: $dualMode" }
  foreach ($e in $errors) { Write-Host "ERROR: $e" }
  foreach ($w in $warnings) { Write-Host "WARNING: $w" }
}

if ($ok) { exit 0 } else { exit 1 }
