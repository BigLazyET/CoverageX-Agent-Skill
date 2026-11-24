---
name: coveragex-incremental-report
description: Collect running .NET business application coverage with dotnet-coverage, or validate selected existing coverage files, then generate a CoverageX incremental report after input confirmation.
---

# CoverageX Incremental Report

This Skill prepares coverage; CoverageX consumes verified XML. Keep collection outside Core.

## Prepare a short plan

Discover the repository/refs, runtime source, executable business entry project and build settings, platform, application address and relevant artifact candidates. Infer facts from project/build evidence rather than asking the user to repeat them. Read [input-policy.md](references/input-policy.md) for input selection and the final confirmation gate.

Combine unresolved choices in one short recommended plan card:

- Input policy: **new-only** (recommended) or **allow-existing**, remembered for this session. Allow-existing adds the option to select files or collect new data; it does not select files automatically.
- For new collection: `dotnet-coverage` mode, business entry application and arguments. Static collection offers inferred business DLLs versus user-specified paths, with the actual inferred list previewed.
- Business exercise: user operation or external HTTP/UI automation against the running application. AI may prepare and execute authorized request-only actions; do not discover or execute unit/integration test projects or offer arbitrary automation-command execution.

Preserve explicit choices; do not repeat answered questions. If a choice is unresolved, present native host options or short text options and wait; preselection or timeout is not an answer. Existing-only inputs skip unnecessary build, application startup, DLL selection and collector installation.

## Collect or reuse

- New long-running applications: read [dotnet-coverage.md](references/dotnet-coverage.md). Static and dynamic share collect → exercise → snapshot → merge → verify. Only startup prerequisites/parameters differ.
- Selected existing files: follow [input-policy.md](references/input-policy.md); native `.coverage` needs conversion, supported XML can be verified directly.

Use only `dotnet-coverage` for active collection. Do not switch to a test-project runner or another collector, silently change mode, reduce agreed business/DLL scope, or substitute final coverage for a requested snapshot after a failure. SDK build, Git comparison and CoverageX reporting keep their separate roles.

## Confirm inputs and report

Validate the explicit XML and its collection/source/scope provenance. Before **each** report, show the final logical input list with absolute raw/derived paths, format, time, source/session and cumulative interval, then wait for confirmation. Combine file selection and “generate from these files” in one interaction when possible. A confirmed unchanged final list needs no second approval; changed inputs or scope require confirmation again.

Read [coveragex.md](references/coveragex.md) and invoke CLI or an already connected MCP with only that confirmed, verified XML list. Check the actual consumer result before claiming report completion. Return the report link and a concise result; keep tool time separate from waiting for the user.

Stop on failed collection, missing or malformed data, unresolved required Git/source/scope information, or absent final input confirmation. Supported existing files are not restricted by the user's generating tool.

## Keep the user's context

AI builds matching outputs, starts the agreed collection session and checks readiness. Show the address and one next step: tell AI when business operation is done. Readiness is not business coverage. AI then snapshots, converts and verifies; the user need not remember commands or paths.

Once the user confirms business exercise is complete, advance to the requested snapshot; do not replay requests after completed manual exercise. Prepare additional business requests only for a demonstrated gap and obtain the needed choice before executing them.

Retain a concise session record: repository/refs, project/build, mode/DLL scope, session ID, address/readiness, input policy, business exercise/progress, artifacts and pending step. Reuse conversation summaries; only if necessary write a small session.json in the run directory. Do not add a global state service, permanent preferences or credentials. Reuse this context on follow-up requests and repeated snapshots.

## Permission boundaries

- Missing tools: show the exact global install command (`dotnet tool install --global dotnet-coverage` or `dotnet tool install --global CoverageX.Command`), explain its effect and obtain approval before installation; verify afterwards. Existing XML needs no collector; connected MCP needs no CLI installation.
- Do not add packages or edit the user's target project without explicit approval.
- Starting the application through collect is AI's responsibility once the collection plan is authorized. Respect host execution permissions; stop on a port conflict without killing its owner. End only the owned session within agreed cleanup authorization.
- Publishing, private-repository access and unrelated process termination need applicable authorization. A report request does not authorize tool installation or target-project edits.
