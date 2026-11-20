"""Exercise finite pipeline boundaries without installing or invoking .NET tools."""

import os
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import run_report


class PipelineTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.repo = Path(self.temporary.name)
        (self.repo / "Tests.csproj").write_text("<Project />")
        self.calls = []
        self.executed = 2
        self.failed = False
        self.xml = "<coverage />"
        self.stale = False
        self.fail_command = None

    def args(self, *extra):
        return run_report.parser().parse_args([
            "--source-directory", str(self.repo), "--source", "feature", "--target", "main",
            "--project", "Tests.csproj", "--producer", "dotnet-test", "--collector", "XPlat Code Coverage",
            "--output-directory", str(self.repo / "outputs with spaces"), *extra])

    def subprocess(self, argv, **kwargs):
        self.calls.append(argv)
        output = ""
        code = 0
        if argv[0] == "git":
            output = str(self.repo) if "--show-toplevel" in argv else "feature" if "symbolic-ref" in argv else "commit-sha"
        elif "build" in argv:
            code = 1 if self.fail_command == "build" else 0
        elif "test" in argv:
            directory = Path(argv[argv.index("--results-directory") + 1])
            (directory / "test.trx").write_text(
                f'<TestRun xmlns="urn:test"><ResultSummary><Counters executed="{self.executed}" '
                f'failed="{int(self.failed)}" /></ResultSummary></TestRun>')
            coverage = directory / "coverage.xml"
            coverage.write_text(self.xml)
            if self.stale:
                os.utime(coverage, (1, 1))
            code = 1 if self.fail_command == "producer" else 0
        elif "lreport" in argv:
            directory = Path(argv[argv.index("--report-directory") + 1])
            directory.mkdir()
            (directory / "index.html").write_text("report")
        return subprocess.CompletedProcess(argv, code, stdout=output, stderr="")

    def run_pipeline(self, args):
        with patch.object(run_report.subprocess, "run", side_effect=self.subprocess), \
             patch.object(run_report.shutil, "which", side_effect=lambda name: None if name == "missing-cli" else name), \
             patch.object(run_report.platform, "machine", return_value="x86_64"):
            return run_report.run(args)

    def test_build_once_and_report_only_verified_paths(self):
        result = self.run_pipeline(self.args("--framework", "net8.0", "--configuration", "Release"))
        self.assertTrue(result["success"], result)
        self.assertEqual(sum("build" in call for call in self.calls), 1)
        tests = next(call for call in self.calls if "test" in call)
        self.assertIn("--no-build", tests)
        self.assertIn("--no-restore", tests)
        self.assertIn("Release", tests)
        report = next(call for call in self.calls if "lreport" in call)
        self.assertEqual(report[report.index("--report-input-files") + 1], ";".join(result["verifiedXml"]))
        self.assertNotIn("--report-input-directories", report)
        self.assertTrue(Path(result["entryReportPath"]).is_file())
        self.assertGreaterEqual(result["timingsMs"]["total"], result["timingsMs"]["build"])

    def test_mcp_handoff_does_not_require_cli_or_claim_report_created(self):
        result = self.run_pipeline(self.args("--entry-point", "mcp", "--coveragex", "missing-cli"))
        self.assertTrue(result["success"], result)
        self.assertEqual(result["status"], "ready-for-mcp")
        self.assertEqual(result["arguments"]["reportFiles"], result["verifiedXml"])
        self.assertNotIn("entryReportPath", result)
        self.assertFalse(any("lreport" in call for call in self.calls))

    def test_reject_zero_failed_stale_or_malformed_inputs_before_report(self):
        for setting, value, stage in (("executed", 0, "test-results"), ("failed", True, "test-results"),
                                      ("stale", True, "verify"), ("xml", "<coverage>", "verify")):
            with self.subTest(setting=setting):
                self.setUp_state()
                setattr(self, setting, value)
                result = self.run_pipeline(self.args())
                self.assertFalse(result["success"])
                self.assertEqual(result["failedStage"], stage)
                self.assertFalse(any("lreport" in call for call in self.calls))

    def setUp_state(self):
        self.calls = []
        self.executed, self.failed, self.stale, self.xml = 2, False, False, "<coverage />"

    def test_failed_command_stops_following_stages(self):
        for stage in ("build", "producer"):
            with self.subTest(stage=stage):
                self.calls = []
                self.fail_command = stage
                result = self.run_pipeline(self.args())
                self.assertFalse(result["success"])
                self.assertEqual(result["failedStage"], stage)
                self.assertFalse(any("lreport" in call for call in self.calls))

    def test_dynamic_unsupported_platform_stops_before_build(self):
        args = self.args()
        args.producer, args.collector = "dotnet-coverage", None
        with patch.object(run_report.platform, "machine", return_value="arm64"), \
             patch.object(run_report.sys, "platform", "darwin"), \
             patch.object(run_report.shutil, "which", return_value="tool"):
            result = run_report.run(args)
        self.assertFalse(result["success"])
        self.assertEqual(result["failedStage"], "preflight")
        self.assertNotIn("runDirectory", result)

    def test_finite_dotnet_coverage_uses_final_xml_without_snapshot(self):
        args = self.args()
        args.producer, args.collector = "dotnet-coverage", None
        result = self.run_pipeline(args)
        self.assertTrue(result["success"], result)
        producer = next(call for call in self.calls if call[0] == "dotnet-coverage")
        self.assertIn("--no-build", producer)
        self.assertIn("--session-id", producer)
        self.assertEqual(producer[producer.index("--output-format") + 1], "cobertura")
        self.assertFalse(any("snapshot" in call or "merge" in call for call in self.calls))

    def test_msbuild_integration_and_isolated_output(self):
        args = self.args()
        args.collector, args.coverlet_msbuild = None, True
        first = self.run_pipeline(args)
        second = self.run_pipeline(args)
        self.assertTrue(first["success"] and second["success"])
        self.assertNotEqual(first["runDirectory"], second["runDirectory"])
        tests = next(call for call in self.calls if "test" in call)
        self.assertIn("-p:CollectCoverage=true", tests)

    def test_missing_cli_fails_before_build(self):
        result = self.run_pipeline(self.args("--coveragex", "missing-cli"))
        self.assertFalse(result["success"])
        self.assertEqual(result["failedStage"], "preflight")
        self.assertFalse(any("build" in call for call in self.calls))


if __name__ == "__main__":
    unittest.main()
