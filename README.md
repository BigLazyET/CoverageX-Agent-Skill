# CoverageX Agent Skill

CoverageX Agent Skill collects running .NET business applications with `dotnet-coverage`, or validates selected existing coverage, then generates an incremental report after the user confirms its inputs. It does not run unit/integration test projects or provide arbitrary automation-command execution.

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

Codex stores Marketplace plugins in the current user's plugin cache, so this is a user-level installation available across projects. A trusted project can override whether the plugin is enabled in `.codex/config.toml`:

```toml
[plugins."coveragex-agent-skill@coveragex"]
enabled = true
```

## Cursor

Open Cursor Marketplace, choose **Add Marketplace from GitHub Repository**, and enter:

```text
https://github.com/BigLazyET/CoverageX-Agent-Skill
```

Install `coveragex-agent-skill` from the imported marketplace, then reload Cursor.

When installing, Cursor lets you choose the scope:

- **User** makes the plugin available across your projects.
- **Project** limits it to the current project.

## Install with the Skills CLI

The third-party [`skills`](https://github.com/vercel-labs/skills) CLI can install the Skill directly from this Git repository without adding the Marketplace.

Project-level installation is the default. Run this from the project that should use the Skill:

```bash
npx skills@latest add BigLazyET/CoverageX-Agent-Skill \
  --skill coveragex-incremental-report \
  --agent codex cursor
```

Codex and Cursor share the project-level `.agents/skills/` location, so one installed copy works for both.

For a user-level installation available across projects, add `--global`:

```bash
npx skills@latest add BigLazyET/CoverageX-Agent-Skill \
  --skill coveragex-incremental-report \
  --agent codex cursor \
  --global
```

At user scope, the CLI installs the Skill into each agent's global Skill location (`~/.codex/skills/` and `~/.cursor/skills/`).

## Manual fallback

The canonical Skill is stored at:

```text
plugins/coveragex-agent-skill/skills/coveragex-incremental-report/
```

Copy that complete directory to `~/.codex/skills/`, `.agents/skills/`, or `.cursor/skills/` when marketplace installation is unavailable.

- `~/.codex/skills/` and `~/.cursor/skills/` are user-level locations.
- `.agents/skills/` and `.cursor/skills/` inside a project are project-level locations.

## Use

Ask the harness for a CoverageX incremental report. The canonical contract is [SKILL.md](plugins/coveragex-agent-skill/skills/coveragex-incremental-report/SKILL.md): current-run inputs by default, one final XML-list confirmation before each report, and the same collect → user/external business exercise → snapshot → merge flow for static and dynamic startup. After confirmation the host calls the CLI or an already connected MCP server. Existing files are accepted by supported format and validity, independently of the user's generating tool.

The Skill does not install `dotnet-coverage` or `CoverageX.Command` without explicit approval, and it does not bundle either CoverageX NuGet package.

## Releases

Each `v*` tag creates a GitHub Release containing the complete dual-marketplace repository as `coveragex-agent-skill-<version>.zip` plus its SHA256 checksum.

## License

Apache-2.0. See [LICENSE](LICENSE).
