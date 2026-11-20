# Input policy and final report confirmation

## Session choice

Before selecting inputs, resolve **new-only** (default/recommended) or **allow-existing**. Remember the answer only in this workflow/session; explicit changes apply going forward. Do not create permanent preference configuration. Bundle this with other unresolved plan choices and preserve already supplied answers.

New-only accepts artifacts from the current collection/snapshot operation, including native-to-XML derivatives of those artifacts. Anchor freshness immediately before that operation and retain the raw-to-XML chain. Converting an old `.coverage` now does **not** make its data new. File modification time alone is insufficient evidence.

Allow-existing lets the user select explicit existing inputs from supplied files/directories or collect new ones. Scan only relevant user-specified locations and present candidates; do not automatically select newest files or merge a directory. Reuse permission is not approval of a final report input list.

## Validate selected files

For supported existing XML, skip build, startup, DLL choice and unused collector checks. Validate directly:

```console
python3 scripts/verify_coverage_xml.py <explicit.xml> --since 0
```

The verifier checks nonempty, complete XML with a supported root (`coverage` or `CoverageSession`); it cannot prove the generating commit or intended module scope. Confirm the corresponding runtime source/version, build scope and test/collection provenance from records or the user. Known mismatches stop. Unknown provenance requires corresponding source/version information or recollection; describe user-supplied provenance as such, not as automatically verified.

For selected native `.coverage`, check the merge tool only when needed and convert into an independent run output, leaving the original intact:

```console
dotnet-coverage merge <selected.coverage> --output-format cobertura --output <derived.xml>
```

Validate the derived XML and original provenance together. For new inputs use the recorded operation start with `--since`; one bad shard stops the report rather than being silently dropped.

## Logical inputs and overlap

A native snapshot and its derived XML represent **one** logical input; pass only the XML to CoverageX. Repeated snapshots without reset are cumulative. Select the intended snapshot; do not automatically merge snapshots from the same cumulative session or silently deduplicate by filename. For multiple inputs, resolve source/session/interval and overlap/merge intent before confirming the list.

The finite runner's `verifiedXml` list contains validated candidates, not a final user-approved list. VSTest may copy a collector's XML into its TRX attachment directory as well as leaving the original. AI should inspect the run/attachment provenance and compare the files, then keep one explicit representative of that logical artifact and explain the copy briefly in the final list. Identical bytes alone do not prove independent test shards are duplicates. Update the consumer's `reportFiles`/CLI input list to the resolved confirmed selection rather than blindly forwarding every candidate; do not rerun collection.

## Final confirmation, every report

Show a compact final list: logical input count, absolute raw and XML paths, format, time, known source/version and scope, session and cumulative interval (or unresolved provenance). Stop on missing required information. Ask the user to confirm this list and generate the report. A directory, permission to reuse, or a general plan approval is not this confirmation.

When the user has already explicitly selected and confirmed the exact final list for this report, continue without asking again. If files or scope change, show the new list and obtain confirmation again. After confirmation call the CLI/MCP once with those verified XML paths; do not rescan a directory or append other files. Host conversation handles this gate; scripts do not manufacture user consent.
