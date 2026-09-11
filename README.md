# CoverageX Agent Skill

CoverageX Agent Skill generates fresh .NET coverage XML with `dotnet-coverage` or `dotnet test`, verifies it, then asks CoverageX to produce an incremental coverage report.

Coverage collection belongs to this Skill. CoverageX remains focused on consuming coverage XML and generating incremental analysis and output.

See [Marketplace and plugin layout](docs/marketplace-layout.md) for the roles of the Codex and Cursor manifests and why both platforms share one canonical Skill.

## Codex

In Codex, add this repository as a plugin marketplace:

```text
https://github.com/BigLazyET/CoverageX-Agent-Skill
```

Then install `coveragex-agent-skill` from the `coveragex` marketplace and start a new thread so Codex discovers the Skill.

For the Codex CLI, clone the repository and add its local path before installing the plugin:

```bash
git clone https://github.com/BigLazyET/CoverageX-Agent-Skill.git
codex plugin marketplace add ./CoverageX-Agent-Skill
codex plugin add coveragex-agent-skill@coveragex
```

## Cursor

Open Cursor Marketplace, choose **Add Marketplace from GitHub Repository**, and enter:

```text
https://github.com/BigLazyET/CoverageX-Agent-Skill
```

Install `coveragex-agent-skill` from the imported marketplace, then reload Cursor.

## Manual fallback

The canonical Skill is stored at:

```text
plugins/coveragex-agent-skill/skills/coveragex-incremental-report/
```

Copy that complete directory to `~/.codex/skills/`, `.agents/skills/`, or `.cursor/skills/` when marketplace installation is unavailable.

## Use

Ask the harness to generate fresh .NET coverage XML and a CoverageX incremental report. The Skill offers `dotnet-coverage` and `dotnet test`; if no producer is selected, it prefers `dotnet-coverage`.

On first use, the Skill checks prerequisites. It never installs `dotnet-coverage` or `CoverageX.Command` without explicit approval. It can use an already configured `CoverageX.McpServer`, but does not bundle either CoverageX NuGet package.

## Releases

Each `v*` tag creates a GitHub Release containing the complete dual-marketplace repository as `coveragex-agent-skill-<version>.zip` plus its SHA256 checksum.

## License

Apache-2.0. See [LICENSE](LICENSE).
