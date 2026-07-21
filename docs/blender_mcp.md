# BlenderMCP with Godot MCP

Use BlenderMCP and Godot MCP in one Codex or Claude Code session to create assets in
Blender, export them into a Godot project, and inspect or run the game through Godot.
Register the servers separately; the client starts each as its own process.

```text
Codex or Claude Code
├── blender MCP ──> BlenderMCP addon on localhost:9876 ──> .blend / .glb
└── godot MCP   ──> local Node server ──> Godot executable ──> project.godot
                                           ↑
                              exported assets from Blender
```

The two MCP servers do not call each other directly. The agent coordinates them through
explicit tool calls and files exported into the Godot project.

## Prerequisites

- Codex or Claude Code with MCP support.
- Blender 3.0 or newer.
- Godot 4 and a project containing `project.godot`.
- Python 3.10 or newer and [`uv`](https://docs.astral.sh/uv/getting-started/installation/)
  for BlenderMCP.
- Node.js 18 or newer and npm for Godot MCP.
- This repository, because its installer owns the curated MCP definitions.

On macOS, install the missing package prerequisites with:

```bash
brew install uv node
```

Confirm that the editor executables are available:

```bash
blender --version
godot --version
node --version
uvx --version
```

If Godot is installed as an application rather than a shell command, its usual macOS
executable is `/Applications/Godot.app/Contents/MacOS/Godot`.

## 1. Install the Blender addon

1. Download `addon.py` from the
   [BlenderMCP repository](https://github.com/ahujasid/blender-mcp/blob/main/addon.py).
2. In Blender, open **Edit > Preferences > Add-ons**.
3. Select **Install from Disk**, choose `addon.py`, and enable **Interface: Blender MCP**.
4. Open a 3D viewport, press **N**, and select the **BlenderMCP** tab.
5. Leave the port at `9876`. Start or connect the server when instructed in the activation
   section below.

Keep the addon version aligned with the MCP package after upgrades. Do not start
`uvx blender-mcp` manually; the MCP client owns that process.

## 2. Build Godot MCP

This repository uses a local source checkout so you can inspect and pin it instead of
launching an unpinned package. Choose a stable directory outside the game project, then build
[`Coding-Solo/godot-mcp`](https://github.com/Coding-Solo/godot-mcp):

```bash
git clone https://github.com/Coding-Solo/godot-mcp.git /absolute/path/to/godot-mcp
cd /absolute/path/to/godot-mcp
npm install
npm run build
test -f build/index.js
```

Record the checkout and Godot executable paths in the shell that will start the MCP
client:

```bash
export GODOT_MCP_PATH="/absolute/path/to/godot-mcp"
export GODOT_BINARY_PATH="$(command -v godot)"
```

If `command -v godot` prints nothing on macOS, use:

```bash
export GODOT_BINARY_PATH="/Applications/Godot.app/Contents/MacOS/Godot"
```

`GODOT_MCP_PATH` and `GODOT_BINARY_PATH` must still be exported when Codex or Claude
Code starts. For terminal clients, add them to your shell profile or export them before
each launch. A client opened from the macOS Dock may not inherit terminal environment
variables; start its CLI from the configured terminal when this happens.

## 3. Register both servers

Choose one client. Registering one MCP does not replace or merge the other.

### Codex

From the Skill Mania repository root:

```bash
./scripts/install-mcp.py --codex --dry-run blender
./scripts/install-mcp.py --codex --dry-run godot

./scripts/install-mcp.py --codex blender
./scripts/install-mcp.py --codex godot
codex mcp list
```

### Claude Code

Use the same scope for both registrations:

```bash
./scripts/install-mcp.py --claude --scope user --dry-run blender
./scripts/install-mcp.py --claude --scope user --dry-run godot

./scripts/install-mcp.py --claude --scope user blender
./scripts/install-mcp.py --claude --scope user godot
claude mcp list
```

The Blender definition pins `blender-mcp==1.6.4`, uses Python 3.11, and disables
upstream telemetry. The Godot definition launches the `build/index.js` file from
`GODOT_MCP_PATH` and passes `GODOT_BINARY_PATH` to it.

## 4. Activate both in one session

Use this startup order:

1. Save the Blender file and the Godot project.
2. Open Blender. In **N > BlenderMCP**, start the addon connection on port `9876`.
3. Export `GODOT_MCP_PATH` and `GODOT_BINARY_PATH` in the terminal.
4. Start Codex or Claude Code from that terminal. Open a new session after first
   registration so the client launches both MCP processes.
5. Check `codex mcp list` or `claude mcp list`. Both `blender` and `godot` should appear.
6. Ask for one read-only operation from each server before making changes.

Suggested verification prompts:

```text
Use only the Blender MCP tools. List the current Blender scene objects and make no changes.
```

```text
Use only the Godot MCP tools. Report the Godot version and inspect the project at
/absolute/path/to/game. Make no changes.
```

Blender and Godot MCP can run together because BlenderMCP uses its own local bridge on
port `9876`, while Godot MCP invokes the configured Godot executable. Run only one MCP
client against the Blender addon at a time: do not keep Codex and Claude Code connected
to the same Blender addon simultaneously.

## 5. Move an asset from Blender to Godot

Use an absolute export path inside the Godot project so both tools refer to the same
file. A practical first task is:

```text
Use Blender MCP to export the selected object as glTF 2.0 to
/absolute/path/to/game/assets/models/robot.glb. Preserve materials, apply transforms,
and do not overwrite an existing file without asking. Then use Godot MCP to inspect the
project, confirm that the asset is visible to Godot, create a test scene that instances
it, and run the scene. Report import or runtime errors without hiding them.
```

Keep editable `.blend` files as source assets and exported `.glb` files as game assets.
For animation work, name actions and clips in Blender before export, then verify the
imported animation names and playback in Godot rather than assuming the export preserved
them.

## Troubleshooting

| Symptom | Check |
| --- | --- |
| `missing prerequisite 'uvx'` | Install `uv`, open a new terminal, and rerun `uvx --version`. |
| `GODOT_MCP_PATH must be exported` | Export both Godot variables before starting the client, not only before registration. |
| `Godot MCP entrypoint not found` | Run `npm install && npm run build` in the checkout and confirm `build/index.js` exists. |
| Godot executable not found | Set `GODOT_BINARY_PATH` to the absolute Godot executable, not the `.app` directory. |
| Blender tools appear but cannot connect | Enable the addon, start its bridge on port `9876`, and close any second MCP client using Blender. |
| One or both tool sets are missing | Confirm both registrations with the client list command, then start a new client session. |
| Exported model has no expected animation | Check Blender action names, glTF export settings, and the imported Godot animation library. |
| A complex operation times out | Save, split the request into smaller modeling/export/import steps, and inspect each result. |

## Safety

BlenderMCP can execute arbitrary Python inside Blender. That code runs with the Blender
process's file and network access. Godot MCP can create scenes and launch projects. Use
both only in trusted workspaces, keep version control or backups, review export targets,
and save before agent-driven changes.

Optional asset-provider features may send prompts, images, or credentials to external
services. Leave Poly Haven, Sketchfab, Hyper3D, and Hunyuan3D integrations disabled unless
you deliberately need and trust them. Never place API keys in prompts or committed MCP
configuration.

## Deactivate or remove

Close the client to stop its stdio MCP processes. Stop the BlenderMCP bridge from the
Blender sidebar when it is no longer needed.

Remove registrations separately:

```bash
codex mcp remove blender
codex mcp remove godot

claude mcp remove --scope user blender
claude mcp remove --scope user godot
```

## Upstream references

- [Codex MCP configuration](https://learn.chatgpt.com/docs/extend/mcp)
- [BlenderMCP installation and addon](https://github.com/ahujasid/blender-mcp)
- [Godot MCP requirements and source build](https://github.com/Coding-Solo/godot-mcp)
- [`uv` installation](https://docs.astral.sh/uv/getting-started/installation/)
