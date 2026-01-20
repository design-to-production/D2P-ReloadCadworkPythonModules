# reload_all/reload_all.py
import sys
import importlib
from pathlib import Path


def is_subpath(child: Path, parent: Path) -> bool:
    """Check if child is under parent, handling symlinks by checking both paths."""
    # Check using original paths (preserves symlinks)
    try:
        child.relative_to(parent)
        return True
    except ValueError:
        pass
    
    # Check using resolved paths (follows symlinks)
    try:
        child.resolve().relative_to(parent.resolve())
        return True
    except ValueError:
        pass
    
    return False


def ReloadAllModules():
    """
    Reload all Python modules that are currently loaded and located 
    in the Cadwork API.x64 directory.
    """
    # Get the API.x64 base directory
    api_base = Path(__file__).parent.parent
    
    print(f"HotReload - Reloading modules from: {api_base}")
    
    # Find all modules that are:
    # 1. Currently imported (in sys.modules)
    # 2. Located within the API.x64 folder
    # 3. Not __main__ (the currently executing script)
    modules_to_reload = []
    
    for module_name, module in list(sys.modules.items()):
        # Skip __main__ and None modules
        if module is None or module_name == '__main__':
            continue
            
        # Get module file path
        try:
            module_file = getattr(module, '__file__', None)
            if module_file is None:
                continue
                
            module_path = Path(module_file)
            
            # Check if module is within API.x64 folder (handles symlinks)
            if is_subpath(module_path, api_base):
                modules_to_reload.append((module_name, module))
                
        except (AttributeError, TypeError):
            continue
    
    # Reload each module
    reloaded_count = 0
    failed_count = 0
    
    for module_name, module in modules_to_reload:
        try:
            importlib.reload(module)
            print(f"HotReload - Reloaded: {module_name}")
            reloaded_count += 1
        except Exception as e:
            print(f"HotReload - Failed to reload {module_name}: {e}")
            failed_count += 1
    
    print(f"\nHotReload - Reload complete: {reloaded_count} successful, {failed_count} failed")


if __name__ == "__main__":
    ReloadAllModules()