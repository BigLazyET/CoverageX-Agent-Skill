# dotnet-coverage producer

Use this path when selected by the user or when no producer was selected.

## Preconditions

1. Check `dotnet-coverage --version`.
2. If missing, present `dotnet tool install --global dotnet-coverage` and request permission. After approval, run it and verify `dotnet-coverage --version`; otherwise stop.
3. Detect OS, version, and architecture. Compare them with the [Microsoft codecoverage support matrix](https://github.com/microsoft/codecoverage/blob/main/docs/supported-os.md#supported-os-versions). Dynamic instrumentation is supported on Windows x64/x86/Arm64; Alpine 3.15+, CentOS 8+, Debian 10+, Fedora 33+, OpenSUSE 15+, Oracle Linux 7+, RHEL 7+, SLES 12 SP+, and Ubuntu 18.04+ on x64; and macOS 10.15+ on x64. Treat every matrix row marked unsupported, an older version, or an unlisted/best-effort host as unavailable for this workflow. State that only `dotnet test` remains; do not silently switch or enable static instrumentation.
4. On supported macOS/Linux hosts, require `libxml2`; on Alpine 3.18+, also require `libintl`. Stop with dependency guidance if a requirement is missing because Dynamic instrumentation may otherwise yield an empty report.

## Interactive command-mode collection

Generate a unique session ID. Start the application with command mode, not server mode:

```console
dotnet-coverage collect --session-id <session-id> --output-format cobertura --output <final.xml> <application-command> <arguments...>
```

For example:

```console
dotnet-coverage collect --session-id coveragex-<unique-id> --output-format cobertura --output artifacts/coverage/final.xml dotnet run --project src/WebApi/WebApi.csproj
```

Run this in a persistent foreground terminal. Never add `--server-mode`. Wait until the output shows the session ID and the application is ready, then tell the user to exercise the application through Swagger, Apifox, or their normal client.

## Snapshots

While the command-mode session is active, the user may request repeated snapshots:

```console
dotnet-coverage snapshot <session-id> --output <snapshot.coverage>
dotnet-coverage merge --output <snapshot.cobertura.xml> --output-format cobertura <snapshot.coverage>
```

The documented `snapshot` command has no output-format option, so treat its output as native coverage data and convert it explicitly before passing it to the XML verifier. Do not assume an `.xml` extension changes the format.

Use `--reset` only when the user wants the next snapshot to exclude earlier hits.

When the user is finished, request/confirm process termination as appropriate. `dotnet-coverage shutdown <session-id>` addresses a collection session; preserve the final Cobertura output and verify it before running CoverageX.

Official command reference: [dotnet-coverage](https://learn.microsoft.com/dotnet/core/additional-tools/dotnet-coverage).
