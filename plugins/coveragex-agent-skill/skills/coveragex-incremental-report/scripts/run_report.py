#!/usr/bin/env python3
"""Build once, collect finite VSTest coverage, and prepare inputs or report locally."""

from __future__ import annotations

import argparse
import json
import platform
import shutil
import subprocess
import sys
import tempfile
import time
import uuid
import xml.etree.ElementTree as ET
from pathlib import Path

from verify_coverage_xml import verify


def executed_tests(directory: Path) -> int:
    count = 0
    for path in directory.rglob("*.trx"):
        counters = ET.parse(path).find(".//{*}Counters")
        if counters is None:
            raise ValueError("TRX has no test counters")
        count += int(counters.get("executed", "0"))
        if any(int(counters.get(key, "0")) for key in ("failed", "error", "timeout", "aborted")):
            raise ValueError("TRX contains failed tests")
    if count == 0:
        raise ValueError("No executed tests; fresh coverage requires a successful test run")
    return count


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    result.add_argument("--source-directory", type=Path, required=True)
    result.add_argument("--source", required=True)
    result.add_argument("--target", required=True)
    result.add_argument("--runtime-branch")
    result.add_argument("--project", type=Path, required=True, help="Existing VSTest project or solution")
    result.add_argument("--producer", choices=("dotnet-coverage", "dotnet-test"), default="dotnet-coverage")
    integration = result.add_mutually_exclusive_group()
    integration.add_argument("--collector", help="Already installed collector name, including format settings")
    integration.add_argument("--coverlet-msbuild", action="store_true", help="Use existing coverlet.msbuild integration")
    result.add_argument("--configuration", default="Debug")
    result.add_argument("--framework")
    result.add_argument("--runtime")
    result.add_argument("--output-directory", type=Path, required=True, help="Parent for a new, isolated run directory")
    result.add_argument("--entry-point", choices=("prepare", "cli", "mcp"), default="cli")
    result.add_argument("--coveragex", default="coveragex", help="CLI executable; used only with entry-point cli")
    return result


def run(args: argparse.Namespace) -> dict:
    result = {"success": False, "producer": args.producer, "timingsMs": {}}
    started = time.monotonic()
    stage = "preflight"

    def command(argv: list[str], *, capture: bool = False) -> str:
        completed = subprocess.run(argv, cwd=repo, text=True, stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE if capture else subprocess.STDOUT)
        if not capture and completed.stdout:
            print(completed.stdout, file=sys.stderr, end="")
        if completed.returncode:
            raise ValueError(f"{stage} command failed (exit {completed.returncode})")
        return completed.stdout.strip()

    def timed(name: str, action):
        nonlocal stage
        stage = name
        begin = time.monotonic()
        try:
            return action()
        finally:
            result["timingsMs"][name] = round((time.monotonic() - begin) * 1000, 3)

    repo = args.source_directory.resolve()
    try:
        def preflight():
            if not repo.is_dir():
                raise ValueError("source-directory does not exist")
            for tool in ("git", "dotnet"):
                if not shutil.which(tool):
                    raise ValueError(f"Missing tool: {tool}; install separately with approval")
            if args.producer == "dotnet-test" and not (args.collector or args.coverlet_msbuild):
                raise ValueError("dotnet-test requires an explicitly selected existing coverage integration")
            if args.producer == "dotnet-coverage":
                if args.collector or args.coverlet_msbuild:
                    raise ValueError("Collector/MSBuild options require producer dotnet-test")
                machine = platform.machine().lower()
                supported = (sys.platform == "win32" and machine in ("amd64", "x86", "arm64")) or (
                    sys.platform in ("darwin", "linux") and machine in ("x86_64", "amd64"))
                if not supported:
                    raise ValueError("Dynamic instrumentation is unsupported on this OS/architecture; do not switch producer automatically")
                if not shutil.which("dotnet-coverage"):
                    raise ValueError("Missing dotnet-coverage; install separately with approval")
            if args.entry_point == "cli" and not shutil.which(args.coveragex):
                raise ValueError("Missing CoverageX CLI; use connected MCP or install separately with approval")
            if Path(command(["git", "rev-parse", "--show-toplevel"], capture=True)).resolve() != repo:
                raise ValueError("source-directory must be the Git working tree root")
            branch = command(["git", "symbolic-ref", "--short", "HEAD"], capture=True)
            if branch != (args.runtime_branch or args.source):
                raise ValueError("Current branch must match runtime-branch (defaults to source)")
            result["commits"] = {ref: command(["git", "rev-parse", "--verify", "--end-of-options", ref + "^{commit}"], capture=True)
                                 for ref in dict.fromkeys((args.source, args.target, branch))}
            project = args.project if args.project.is_absolute() else repo / args.project
            if not project.is_file() or project.suffix.lower() not in (".csproj", ".sln", ".slnx"):
                raise ValueError("project must be an existing VSTest project or solution file")
            return project.resolve()

        project = timed("preflight", preflight)
        output = args.output_directory.resolve()
        output.mkdir(parents=True, exist_ok=True)
        run_directory = Path(tempfile.mkdtemp(prefix="run-", dir=output))
        result["runDirectory"] = str(run_directory)
        build_options = ["--configuration", args.configuration]
        if args.framework:
            build_options += ["--framework", args.framework]
        if args.runtime:
            build_options += ["--runtime", args.runtime]
        timed("build", lambda: command(["dotnet", "build", str(project), *build_options]))
        tests = ["dotnet", "test", str(project), *build_options, "--no-build", "--no-restore",
                 "--logger", "trx", "--results-directory", str(run_directory)]
        if args.producer == "dotnet-test":
            if args.collector:
                tests += ["--collect", args.collector]
            else:
                tests += ["-p:CollectCoverage=true", "-p:CoverletOutputFormat=cobertura",
                          f"-p:CoverletOutput={run_directory}/"]
            producer = tests
        else:
            session = "coveragex-" + uuid.uuid4().hex
            result["sessionId"] = session
            producer = ["dotnet-coverage", "collect", "--session-id", session, "--output-format", "cobertura",
                        "--output", str(run_directory / "coverage.xml"), *tests]
        since = time.time()
        timed("producer", lambda: command(producer))
        result["executedTests"] = timed("test-results", lambda: executed_tests(run_directory))
        files = timed("verify", lambda: verify([run_directory], since))
        result["verifiedXml"] = files
        report = {"source": args.source, "target": args.target, "sourceDirectory": str(repo),
                  "runtimeBranch": args.runtime_branch or args.source, "reportFiles": files,
                  "reportDirectory": str(run_directory / "report"), "reportTypes": ["Html"]}
        if args.entry_point == "prepare":
            result.update(success=True, status="ready-for-input-confirmation", arguments=report)
        elif args.entry_point == "mcp":
            result.update(success=True, status="ready-for-mcp", mcpTool="GenerateLocalIncrementalReport", arguments=report)
        else:
            timed("report", lambda: command([args.coveragex, "lreport", "--source", args.source, "--target", args.target,
                  "--runtime-branch", report["runtimeBranch"], "--source-directory", str(repo),
                  "--report-input-files", ";".join(files), "--report-directory", report["reportDirectory"], "--report-type", "Html"]))
            entry = Path(report["reportDirectory"]) / "index.html"
            if not entry.is_file():
                raise ValueError("CoverageX produced no Html report")
            result.update(success=True, status="reported", reportDirectory=report["reportDirectory"], entryReportPath=str(entry))
    except (OSError, ValueError, ET.ParseError, KeyboardInterrupt) as exc:
        result.update(failedStage=stage, error=str(exc) or "Interrupted")
    finally:
        result["timingsMs"]["total"] = round((time.monotonic() - started) * 1000, 3)
    return result


if __name__ == "__main__":
    outcome = run(parser().parse_args())
    print(json.dumps(outcome))
    raise SystemExit(0 if outcome["success"] else 1)
