# dotnet test producer

Use this path only when the user selects it.

## Test prerequisite

Inspect solution/project files for actual test projects and framework/adapter references, then list tests with the repository's supported command when practical. Evidence may include `Microsoft.NET.Test.Sdk`, MSTest, NUnit, xUnit, or Microsoft.Testing.Platform configuration.

If no test project or discoverable tests exist, state that `dotnet test` cannot start coverage collection for this solution/directory and stop. A successful build with zero executed tests is not coverage success.

## Reuse existing coverage integration

Use the integration already present in the target repository:

- Collector example:

  ```console
  dotnet test <solution-or-test-project> --collect "XPlat Code Coverage" --results-directory <output-directory>
  ```

- MSBuild/Coverlet example:

  ```console
  dotnet test <solution-or-test-project> -p:CollectCoverage=true -p:CoverletOutputFormat=cobertura -p:CoverletOutput=<output-path>
  ```

Do not guess that either integration exists. Do not add packages or edit project files unless the user explicitly approves that separate change.

Require a successful test run with executed tests, then validate the newly created XML. Random GUID result directories are acceptable because the verifier returns explicit paths.
