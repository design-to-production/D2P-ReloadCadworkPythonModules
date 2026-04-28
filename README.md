# Hot Reload

![Logo](Media/Images/Logo1024x256.svg)

During cadwork plugin development, changes to imported Python modules only take effect after restarting cadwork. `Hot Reload` let you refresh all modules instantly, no restart needed.

Developed by Design-to-Production : https://www.designtoproduction.com/en/

## Requirements
Developed and tested with cadwork 3d version 2025, build 390.

## Installation

Download the repository and drop the plugin folder `HotReload` in your cadwork APIx64 folder or create a symlink to the APIx64 folder.

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

## Limitations 

- Hot Reload unloads selected modules from `sys.modules`; updated code is imported on the next plugin run.
- If different projects load modules with the same name, one import path can still shadow another.
- In some host-runtime edge cases, long-lived references to old objects may remain; a full cadwork restart is then required.

## License

MIT License — see [LICENSE](LICENSE) for details.



