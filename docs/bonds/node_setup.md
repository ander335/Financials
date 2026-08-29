# Shared Node Runtime and Spreadsheet Modules

## Installed configuration

A user-wide runtime has been installed outside the repository at:

```text
C:\Users\user\AppData\Local\FinancialsNodeRuntime
```

Installed components:

| Component | Version | Location |
|---|---:|---|
| Node.js | 24.19.0 | `C:\Users\user\AppData\Local\FinancialsNodeRuntime\node.exe` |
| `@oai/artifact-tool` | 2.8.52 | `C:\Users\user\AppData\Local\FinancialsNodeRuntime\node_modules\@oai\artifact-tool` |
| `@oai/walnut` | 0.1.245 | Bundled under `@oai/artifact-tool\node_modules` |
| `skia-canvas` | 3.0.6 | Bundled under `@oai/artifact-tool\node_modules` |

Two user environment variables were created:

```text
FINANCIALS_NODE_RUNTIME=C:\Users\user\AppData\Local\FinancialsNodeRuntime
FINANCIALS_NODE_MODULES=C:\Users\user\AppData\Local\FinancialsNodeRuntime\node_modules
```

Open a new terminal after changing user environment variables. No `node_modules` directory or package-manager metadata is required inside `G:\projects\Financials`.

## Why the package is copied instead of installed from npm

`@oai/artifact-tool` is marked as a private package and is supplied with the Codex spreadsheet runtime. It should not be assumed to exist in the public npm registry. The safe reproducible installation method is to copy the complete package directory, including its bundled native and JavaScript dependencies, from the Codex runtime to the shared user location.

Do not run `npm install -g @oai/artifact-tool` unless an authorized private registry has been configured separately.

## Reinstall or update procedure

Run the following in PowerShell after Codex has supplied or updated its spreadsheet runtime:

```powershell
$sourceRoot = "$env:USERPROFILE\.cache\codex-runtimes\codex-primary-runtime\dependencies\node"
$runtimeRoot = "$env:LOCALAPPDATA\FinancialsNodeRuntime"
$moduleRoot = Join-Path $runtimeRoot "node_modules"
$scopeRoot = Join-Path $moduleRoot "@oai"

New-Item -ItemType Directory -Force -Path $scopeRoot | Out-Null
Copy-Item -LiteralPath (Join-Path $sourceRoot "bin\node.exe") -Destination (Join-Path $runtimeRoot "node.exe") -Force
Copy-Item -LiteralPath (Join-Path $sourceRoot "node_modules\@oai\artifact-tool") -Destination $scopeRoot -Recurse -Force

[Environment]::SetEnvironmentVariable("FINANCIALS_NODE_RUNTIME", $runtimeRoot, "User")
[Environment]::SetEnvironmentVariable("FINANCIALS_NODE_MODULES", $moduleRoot, "User")
```

Before an update, close processes that may be using `node.exe` or native modules. If a version must be rolled back, restore the previous shared runtime directory from a backup rather than mixing files from different package versions.

## Import pattern for repository scripts

Node ESM does not reliably resolve globally installed packages by name. Scripts should dynamically import the module from the shared path instead of creating a project-local junction:

```javascript
import path from "node:path";
import { pathToFileURL } from "node:url";

const moduleRoot = process.env.FINANCIALS_NODE_MODULES;
if (!moduleRoot) {
  throw new Error("FINANCIALS_NODE_MODULES is not set; open a new terminal or set it for this process.");
}

const artifactToolUrl = pathToFileURL(
  path.join(moduleRoot, "@oai", "artifact-tool", "dist", "artifact_tool.mjs"),
).href;

const { FileBlob, SpreadsheetFile } = await import(artifactToolUrl);
```

Run the script with:

```powershell
& "$env:FINANCIALS_NODE_RUNTIME\node.exe" .\scripts\your_script.mjs
```

If the current terminal was open before installation, initialize its process variables once:

```powershell
$env:FINANCIALS_NODE_RUNTIME = [Environment]::GetEnvironmentVariable("FINANCIALS_NODE_RUNTIME", "User")
$env:FINANCIALS_NODE_MODULES = [Environment]::GetEnvironmentVariable("FINANCIALS_NODE_MODULES", "User")
```

## Verification

Check the installed versions:

```powershell
& "$env:FINANCIALS_NODE_RUNTIME\node.exe" --version
Get-Content -Raw "$env:FINANCIALS_NODE_MODULES\@oai\artifact-tool\package.json" |
  ConvertFrom-Json |
  Select-Object name, version
```

Test the module import:

```powershell
& "$env:FINANCIALS_NODE_RUNTIME\node.exe" --input-type=module -e `
  'const root=process.env.FINANCIALS_NODE_MODULES.replaceAll("\\","/"); const m=await import(`file:///${root}/@oai/artifact-tool/dist/artifact_tool.mjs`); console.log(Boolean(m.FileBlob && m.SpreadsheetFile));'
```

The expected result is `true`.

## Troubleshooting

- **Environment variable is empty:** open a new terminal or load the user-level value into the current process as shown above.
- **Module import fails after an update:** recopy the complete `@oai/artifact-tool` directory; do not copy only `dist/` because native and transitive dependencies are required.
- **Native rendering error:** confirm that `skia-canvas` and its files are present under the package's own `node_modules` directory.
- **Wrong package version:** inspect `package.json` in the shared location and update the entire package atomically.
- **Project-local `node_modules` reappears:** remove it only after confirming it was created for this shared-module workaround and contains no user-managed dependencies. Repository scripts should use the dynamic-import pattern above.
