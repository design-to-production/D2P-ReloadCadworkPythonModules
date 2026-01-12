# ReloadCadworkPythonModules

![Logo](Media/Images/Logo1024x256.svg)

During cadwork plugin development, changes to imported Python modules only take effect after restarting cadwork. This plugin lets you reload all modules instantly—no restart needed.

Developed by Design-to-Production : https://www.designtoproduction.com/en/

## Requirements
Developed and tested with cadwork 3d version 2025, build 390.

## Installation

Download the repository and drop the plugin folder in your cadwork APIx64 folder or create a symlink to the APIx64 folder.

Cadwork guide : https://docs.cadwork.com/projects/cwapi3dpython/en/latest/get_started/ (note, the path for version 2025 is now `...\cadwork\userprofil_2025\3d\API.x64`)

## Usage 

Click on the plugin to refresh all loaded python modules. 

1. Make sure you add the current directory to the system path at the top of your entry point (main python file):
    ```python
    import sys, os
    sys.path.insert(0, os.path.dirname(__file__))
    ```
1. subfolder modules are supported
1. Symlinked modules are supported.

## Limitations 

- The modules are re-imported in order of appearance in the system path which might fail if you have circular import.
- If different projects are loading modules with the same name, the last loaded module will be used by all projects.

## License

MIT License — see [LICENSE](LICENSE) for details.

