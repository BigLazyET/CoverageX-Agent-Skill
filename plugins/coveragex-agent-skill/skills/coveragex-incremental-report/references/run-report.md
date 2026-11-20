# Finite VSTest report runner

Use `scripts/run_report.py` after reading the selected producer's prerequisites. It accepts an existing `.csproj`, `.sln`, or `.slnx` with VSTest tests; it does not install tools, add packages, select fewer tests, or run an interactive server. Verify the repository's test framework, coverage integration and the producer's OS/version/native dependencies first. Other test platforms and custom report filters/types use the regular workflow.

For the user-selected `dotnet test` and an **already installed** collector:

```console
python3 scripts/run_report.py --source-directory <repo> --source <feature> --target <main> --project <tests.csproj> --producer dotnet-test --collector "XPlat Code Coverage" --output-directory <artifacts> --entry-point prepare
```

Use the collector actually present, including its format settings (for example `Code Coverage;Format=cobertura`). For existing Coverlet MSBuild integration, replace `--collector ...` with `--coverlet-msbuild`. Do not infer that a collector exists from these examples.

For the selected/default `dotnet-coverage`, on a supported host:

```console
python3 scripts/run_report.py --source-directory <repo> --source <feature> --target <main> --project <tests.csproj> --producer dotnet-coverage --output-directory <artifacts> --entry-point prepare
```

This collects the finite `dotnet test --no-build --no-restore` process directly into final Cobertura XML. It uses a unique collection session and does not need snapshot/merge. It does not implement static instrumentation or change platform support.

Options `--configuration` (default Debug), `--framework`, and `--runtime` are forwarded consistently to build and test. The runner never skips the first matching build based on an old DLL. `--runtime-branch` defaults to source and must match the checked-out branch; source and target must resolve locally. No clone, fetch or checkout occurs.

The output parent receives a new `run-*` directory for each invocation. In the Skill, always select `--entry-point prepare`: it does not require/invoke CoverageX and returns `status=ready-for-input-confirmation`, `verifiedXml` and `arguments`. `success=true` means preparation succeeded, not that a report exists. Show the final list using [input-policy.md](input-policy.md), wait for confirmation, then invoke the existing CLI or connected MCP with those exact inputs. Do not rerun the producer after confirmation.

For standalone, already-confirmed usage, default CLI mode remains compatible and runs `coveragex lreport` using only verified explicit XML paths and Html. `--coveragex <executable>` can select a local CLI launcher. Tool output goes to stderr; stdout contains one final JSON object with `success`, `producer`, `timingsMs`, actual `commits`, `verifiedXml` and report paths. Nonzero exit means stop; `failedStage` identifies the stage. Test count must be positive and failed test counters are rejected. No stale coverage is reused.

## Already connected MCP

The Skill uses `prepare` and confirms the final inputs before calling the connected tool. Standalone, already-confirmed integrations may still use `--entry-point mcp`. The runner does not require or invoke a CoverageX CLI. A successful `status: ready-for-mcp` means collection and verification are done, **not that a report exists**. After final input confirmation, call the connected local report tool (`GenerateLocalIncrementalReport`, using its actual exposed tool name) once with the returned `arguments`, then inspect that result and report its location. Keep MCP time separate from the runner's collection total.

## Timings

`preflight`, `build`, `producer`, `test-results`, `verify`, `report` (CLI only), and `total` use a monotonic clock and milliseconds. `producer` includes test execution, collection and final XML export; it does not pretend to measure those internals separately. Compare the same tests, framework, configuration and source commits, separating cold and warm runs.
