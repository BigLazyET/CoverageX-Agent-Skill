# dotnet-coverage application collection

## Startup prerequisites and mode

Check installed `dotnet-coverage --version`; installation needs separate approval. Detect OS/version/architecture and check the current [Microsoft support matrix](https://github.com/microsoft/codecoverage/blob/main/docs/supported-os.md#supported-os-versions) and [command reference](https://learn.microsoft.com/dotnet/core/additional-tools/dotnet-coverage).

Respect the selected mode. When unspecified, retain dynamic as the default on supported hosts. Dynamic managed instrumentation supports Windows x64/x86/Arm64, supported Linux x64 and macOS x64; require documented OS minimums and native dependencies (`libxml2` on macOS/Linux, also `libintl` on Alpine 3.18+). Unlisted/unsupported dynamic hosts are not dynamically supported. If managed static instrumentation is available there (for example macOS ARM64), explain/select static **before startup**, rather than refusing collect/snapshot entirely. Do not silently change mode after a failure. Native modules are outside this workflow.

### Static DLL scope

AI discovers the entry project, actual build configuration/TFM/runtime and business project dependencies. Use MSBuild/project output metadata, deployment assets and actual runtime-loading paths; account for custom AssemblyName/OutputPath and multiple TFMs. Do not construct DLL names solely from project names, instrument all third-party/system DLLs, or choose only changed modules.

Preview inferred **absolute** DLL paths with project/build scope and offer “use inferred list” or “specify one/multiple DLLs” unless the user already explicitly chose inference or supplied paths. Wait for an unresolved choice; combine it with input/test choices where possible. Build matching outputs when required, then resolve/validate the final paths and matching symbols. Clarify ambiguity, missing files or mismatched source/build instead of guessing.

Use the actual application-loaded copies. For Material's SampleApi → SampleLibrary reference, both DLLs come from SampleApi's output directory, not each project's separate bin directory. A user's intentional narrower scope must also narrow the report scope explicitly; do not claim complete coverage with omitted modules. Static instrumentation may alter authorized build outputs; do not promise automatic restoration after abnormal termination.

## Start once, then share the lifecycle

AI builds once with matching settings, then runs the freshly built entry DLL, retaining application arguments. Never infer freshness from a DLL's existence. Check known ports first and do not terminate their owners. Start an authorized unique command-mode session in a persistent host terminal/process (no `--server-mode`).

Dynamic:

```console
dotnet-coverage collect --session-id <id> --output-format cobertura --output <run/final.xml> dotnet <fresh-entry.dll> <app-args...>
```

Static differs only by explicit matching module parameters:

```console
dotnet-coverage collect --session-id <id> --include-files <absolute-entry.dll> --include-files <absolute-business-library.dll> --output-format cobertura --output <run/final.xml> dotnet <fresh-entry.dll> <app-args...>
```

Pass each `--include-files` separately; correctly quote paths with spaces. Keep the session ID, mode and DLL scope. AI checks process/readiness/health, then runs agreed existing business automation and checks success, or gives the manual user the URL and asks them to signal completion. Startup/health alone is not business testing. Failed tests are reported and not presented as successful exercise.

Inspect automation before recommending it: an end-to-end demo that starts its own collector or generates a report is not a request-only test script for this active session. Do not run it to bypass input confirmation or create a second session; recommend suitable existing request/tests or manual exercise instead.

If only useful request commands embedded inside such a demo exist, AI may prepare a request-only plan from them, label it as extracted preparation rather than an existing standalone test script, and resolve the test choice in the plan card. After an agreed manual exercise is done, proceed to snapshot without replaying those requests or making the user reconfirm the test plan.

For **finite VSTest** instead, use [run-report.md](run-report.md). Its dynamic-only platform guard does not govern this static application path; finite final XML remains distinct from an interactive snapshot.

## Snapshot and report, repeatedly

After business exercise, AI records the snapshot start time and uses new explicit paths:

```console
dotnet-coverage snapshot <id> --output <run/snapshot-N.coverage>
dotnet-coverage merge <run/snapshot-N.coverage> --output-format cobertura --output <run/snapshot-N.xml>
python3 scripts/verify_coverage_xml.py <run/snapshot-N.xml> --since <snapshot-start-unix-seconds>
```

Snapshot has **no output-format** option. Its native output requires merge; naming it `.xml` does not convert it. Verify the operation succeeded and the raw/derived lineage is current. Follow [input-policy.md](input-policy.md): confirm the final logical inputs before each report, then consume only explicit verified XML.

Snapshot does not shut down the application. Default snapshots are cumulative; do not reset or automatically merge them. Use `--reset` only when explicitly requested, recording the interval. Retain context so subsequent requests do not repeat setup or DLL questions.

When finished, shut down only the owned session with applicable cleanup authorization: `dotnet-coverage shutdown <id>`. A successful explicit shutdown can yield child exit 137/143; accept those only with confirmed successful shutdown and valid expected output. Do not repeat normal shutdown from cleanup. Preserve final output but do not substitute it for a requested snapshot or automatically add it to report inputs.
