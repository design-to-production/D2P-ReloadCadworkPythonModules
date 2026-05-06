# Hot Reload

![Logo](Media/Images/Logo1024x256.svg)

During cadwork plugin development, changes to imported Python modules only take effect after restarting cadwork. `Hot Reload` let you refresh all modules instantly, no restart needed.

Developed by Design-to-Production : https://www.designtoproduction.com/en/

## Requirements
Developed and tested with cadwork 3d version 2025, build 390.

**`.hotreloadignore`** uses a built-in pattern matcher (Python standard library only; no pip packages).

## Installation

Download the repository and drop the plugin folder `HotReload` in your cadwork APIx64 folder or create a symlink to the API.x64 folder.

Cadwork guide : https://docs.cadwork.com/projects/cwapi3dpython/en/latest/get_started/ (note, the path for version 2025 is now `...\cadwork\userprofil_2025\3d\API.x64`)

## Usage 

After you've made changes in your own python plugin and before running them, run `Hot Reload` instead of restarting cadwork

1. Make sure you add the current directory to the system path at the top of your entry point (main python file):
    ```python
    import sys, os
    sys.path.insert(0, os.path.dirname(__file__))
    ```
1. subfolder modules are supported.
2. submodules outside APIx64 are supported (since 1ac2b14be360e45935e59092277c72e1758e7b5d).
1. Symlinked modules are supported.

## `.hotreloadignore` (optional)

Each plugin folder under `API.x64` may contain a **`.hotreloadignore`** file at its root (next to `plugin_info.xml`). Paths are matched relative to **that plugin folder** (use `/` in patterns even on Windows). Module files that match any rule are **not** unloaded.

This repository’s **`HotReload`** folder ships **`.hotreloadignore`** with `mod:hotreload_utils*` so Hot Reload does not evict its own helper package from `sys.modules` every run (fewer edge cases; edit **`HotReload.py`** itself is still rare—restart cadwork if you change that entry script).

Supported pattern subset (similar to `.gitignore`, not a full clone):

| Syntax | Meaning |
|--------|--------|
| Leading `/` | Match only from the plugin root (not deeper arbitrary prefixes). |
| Trailing `/` | Directory-only: that folder and everything inside it. |
| `*` | Any characters except `/` within one path segment. |
| `?` | One character except `/`. |
| `**` | Across `/` (including “no extra folders”). |
| `**/` | Optional directory prefix (typical use: `**/name.py`). |
| `# …` | Comment line. |
| Lines starting with `!` | Not supported (skipped with a warning). |
| `mod:` prefix | **Module name** glob (`fnmatch`, dotted names). Use for packages **outside** your plugin tree (e.g. `site-packages`). Patterns from **all** `.hotreloadignore` files under `API.x64` are merged. |

Example `API.x64/MyPlugin/.hotreloadignore`:

```gitignore
# third-party tree — keep imported modules as-is
vendor/

# only at plugin root
/generated_constants.py

# any depth under this plugin
**/legacy_stable.py

# keep NumPy / PyClipper loaded (paths are outside this folder — use mod:)
mod:numpy*
mod:pyclipr*
```

## Limitations 

- Hot Reload unloads selected modules from `sys.modules`; updated code is imported on the next plugin run.
- If different projects load modules with the same name, one import path can still shadow another.
- In some host-runtime edge cases, long-lived references to old objects may remain; a full cadwork restart is then required.

## License

MIT License — see [LICENSE](LICENSE) for details.


