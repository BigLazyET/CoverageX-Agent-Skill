---
name: coveragex-incremental-report
description: Generate fresh .NET coverage XML with dotnet-coverage or dotnet test, verify it, then run CoverageX incremental reports through its CLI or MCP. Use when an AI harness must orchestrate collection before CoverageX; do not use to add collection features to CoverageX itself.
---

# CoverageX Incremental Report

Keep the product boundary explicit: this skill owns coverage collection orchestration; CoverageX only consumes existing XML and generates incremental reports.

## Choose the producer

Offer the user `dotnet-coverage` and `dotnet test`. If they do not choose, use `dotnet-coverage`.

- For `dotnet-coverage`, read [dotnet-coverage.md](references/dotnet-coverage.md).
- For `dotnet test`, read [dotnet-test.md](references/dotnet-test.md).

Do not silently switch producers after a failure.

## Required workflow

1. Resolve the source/target branches, runtime source tree, application or test command, and output directory.
2. Record the collection start time as Unix seconds immediately before collection.
3. Run the selected producer and follow its stopping/interaction rules.
4. Before invoking CoverageX, run:

   ```console
   python3 scripts/verify_coverage_xml.py --since <unix-seconds> <xml-file-or-directory>...
   ```

5. Continue only when the verifier exits zero and returns at least one explicit XML path. Pass only those paths to CoverageX.
6. Read [coveragex.md](references/coveragex.md), select CLI or an already connected MCP server, and run the local or artifact report workflow.
7. Report the producer, session ID when applicable, verified XML paths, CoverageX entry point, and report result/location.

Stop before CoverageX when collection fails, no fresh XML exists, XML parsing fails, the producer prerequisite is absent, or required Git/report inputs are unresolved.

## Permission boundaries

- Missing `dotnet-coverage`: show `dotnet tool install --global dotnet-coverage`, explain that it changes the user's global .NET tools, and ask for approval. Install and verify only after explicit approval.
- Missing `coveragex` when no CoverageX MCP is connected: show `dotnet tool install --global CoverageX.Command`, explain that it changes the user's global .NET tools, and ask for approval. Install and run `coveragex help` only after explicit approval; stop on refusal or either failure.
- Never add coverage packages or edit a target test project without explicit approval.
- Never publish packages, start an indefinite process, access a private repository, or terminate a user's process without applicable authorization.
- A request for a report is not authorization to install tools or modify the target repository.
