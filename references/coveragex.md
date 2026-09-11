# CoverageX consumer

CoverageX consumes verified XML; it does not generate it.

## Select the entry point

Prefer an already connected `CoverageX.McpServer` when its tools are available. Otherwise check for the `coveragex` CLI.

If the CLI is missing:

1. Show `dotnet tool install --global CoverageX.Command` and explain that it changes the user's global .NET Tool state.
2. Ask for explicit approval. A report request alone is not approval.
3. If approved, run the shown command, then run `coveragex help`.
4. Continue only when installation and verification both succeed. Stop if the user refuses or either command fails.

Do not install the CLI when MCP is already available, install both entry points by default, or modify MCP host configuration without separate authorization.

## Local source tree

Use local mode when the runtime source tree is the existing Git working tree:

```console
coveragex lreport --source <source> --target <target> --source-directory <repo> --runtime-branch <runtime-branch> --report-input-files <file1;file2>
```

MCP equivalent: `GenerateLocalIncrementalReport` with `source`, `target`, `sourceDirectory`, `runtimeBranch`, and `reportFiles`.

## Managed/artifact source tree

Use artifact mode when CoverageX must prepare or reuse a managed runtime source tree:

```console
coveragex areport --source <source> --target <target> --runtime-branch <runtime-branch> --repository-url <url> --report-input-files <file1;file2>
```

MCP equivalent: `GenerateArtifactIncrementalReport` with the corresponding camelCase fields. Use `noPull` only with an explicit existing `sourceDirectory`.

## Invariants

- Pass only XML paths returned by `verify_coverage_xml.py`.
- `source`, `target`, and `runtimeBranch` refer to committed branch tips; CoverageX does not analyze uncommitted changes.
- Do not put repository credentials in logs or command summaries.
- Preserve user-selected report types, filters, history directory, title, and tag.
