# CoverageX Incremental Report Skill

An Agent Skill for Codex, Cursor, and compatible AI harnesses. It generates fresh .NET coverage XML with `dotnet-coverage` or `dotnet test`, verifies the XML, then asks CoverageX to produce an incremental coverage report.

Coverage collection belongs to this Skill. CoverageX remains focused on consuming coverage XML and generating incremental analysis and output.

## Install

Download and extract a Release asset, or clone this repository. Copy the complete directory so that `SKILL.md`, `references/`, and `scripts/` stay together.

Codex, user installation:

```bash
mkdir -p ~/.codex/skills/coveragex-incremental-report
cp -R SKILL.md references scripts ~/.codex/skills/coveragex-incremental-report/
```

Codex, project installation:

```bash
mkdir -p .agents/skills/coveragex-incremental-report
cp -R SKILL.md references scripts .agents/skills/coveragex-incremental-report/
```

Cursor, project installation:

```bash
mkdir -p .cursor/skills/coveragex-incremental-report
cp -R SKILL.md references scripts .cursor/skills/coveragex-incremental-report/
```

Restart or reload the AI harness after installation.

## Use

Ask the harness to generate a fresh .NET coverage XML and a CoverageX incremental report. The Skill offers `dotnet-coverage` and `dotnet test`; if no producer is selected, it prefers `dotnet-coverage`.

On first use, the Skill checks prerequisites. It never installs `dotnet-coverage` or `CoverageX.Command` without explicit approval. The CLI is installed from NuGet with:

```bash
dotnet tool install --global CoverageX.Command
```

If an already configured `CoverageX.McpServer` is available, the Skill can use it instead. The Skill does not bundle either NuGet package.

## Releases

Each `v*` tag creates a GitHub Release containing:

- `coveragex-incremental-report-<version>.zip`
- its `SHA256` checksum

The archive always contains one top-level `coveragex-incremental-report/` directory ready to copy into a harness skill directory.

## License

Apache-2.0. See [LICENSE](LICENSE).
