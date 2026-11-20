---
name: coveragex-incremental-report
description: Prepare .NET coverage with dotnet-coverage or dotnet test, or validate selected existing coverage, then generate a CoverageX incremental report after input confirmation. Use for AI orchestration of coverage and reporting; collection stays outside CoverageX.
---

# CoverageX Incremental Report

This Skill prepares coverage; CoverageX consumes verified XML. Keep collection outside Core.

## Prepare a short plan

Discover the repository/refs, runtime source, entry project and build settings, platform, existing tests/scripts and relevant artifact candidates. Infer facts from project/build evidence rather than asking the user to repeat them. Read [input-policy.md](references/input-policy.md) for input selection and the final confirmation gate.

Combine unresolved choices in one short recommended plan card:

- Input policy: **new-only** (recommended) or **allow-existing**, remembered for this session. Allow-existing adds the option to select files or collect new data; it does not select files automatically.
- For new collection: producer (`dotnet-coverage` by default, or explicitly selected `dotnet test`), application/test command and mode. New static application collection offers inferred business DLLs versus user-specified paths, with the actual inferred list previewed.
- Test plan: execute the user's existing command, or recommend discovered automation. If none is suitable, let the user exercise the application manually.

Preserve explicit choices; do not repeat answered questions. If a choice is unresolved, present native host options or short text options and wait; preselection or timeout is not an answer. Existing-only inputs skip unnecessary build, application startup, DLL selection and collector installation.

## Collect or reuse

- New long-running applications: read [dotnet-coverage.md](references/dotnet-coverage.md). Static and dynamic share collect → exercise → snapshot → merge → verify. Only startup prerequisites/parameters differ.
- Finite VSTest with default Html/options: read [run-report.md](references/run-report.md). Call the runner with **`--entry-point prepare`**, then confirm inputs and invoke the existing consumer separately. Never use its default CLI branch to bypass the gate.
- Explicit `dotnet test`: read [dotnet-test.md](references/dotnet-test.md). Require real successful executed tests.
- Selected existing files: follow [input-policy.md](references/input-policy.md); native `.coverage` needs conversion, supported XML can be verified directly.

Do not silently switch producers/modes, reduce test or DLL scope, or substitute final coverage for a requested snapshot after a failure.

## Confirm inputs and report

Validate the explicit XML and its collection/source/scope provenance. Before **each** report, show the final logical input list with absolute raw/derived paths, format, time, source/session and cumulative interval, then wait for confirmation. Combine file selection and “generate from these files” in one interaction when possible. A confirmed unchanged final list needs no second approval; changed inputs or scope require confirmation again.

Read [coveragex.md](references/coveragex.md) and invoke CLI or an already connected MCP with only that confirmed, verified XML list. Check the actual consumer result before claiming report completion. Return the report link and a concise result; keep tool time separate from waiting for the user.

Stop on failed collection/tests, missing or malformed data, unresolved required Git/source/scope information, or absent final input confirmation.

## Keep the user's context

AI builds matching outputs, starts the agreed collection session, checks readiness and runs agreed automation. Readiness is not business testing. For manual exercise, show the address and one next step: tell AI when testing is done. AI then snapshots, converts and verifies; the user need not remember commands or paths.

Once the selected tests are complete, advance to the requested snapshot; do not replay automation after the user has completed the agreed manual exercise. Recommend additional tests only for a demonstrated gap and obtain the needed choice before running them.

Retain a concise session record: repository/refs, project/build, mode/DLL scope, session ID, address/readiness, input policy, tests/progress, artifacts and pending step. Reuse conversation summaries/helper output; only if necessary write a small session.json in the run directory. Do not add a global state service, permanent preferences or credentials. Reuse this context on follow-up requests and repeated snapshots.

## Permission boundaries

- Missing tools: show the exact global install command (`dotnet tool install --global dotnet-coverage` or `dotnet tool install --global CoverageX.Command`), explain its effect and obtain approval before installation; verify afterwards. Existing XML needs no collector; connected MCP needs no CLI installation.
- Do not add packages or edit a target test project without explicit approval.
- Starting the application through collect is AI's responsibility once the collection plan is authorized. Respect host execution permissions; stop on a port conflict without killing its owner. End only the owned session within agreed cleanup authorization.
- Publishing, private-repository access and unrelated process termination need applicable authorization. A report request does not authorize tool installation or target-project edits.
