# reload_all/reload_all.py
import sys
import importlib
from pathlib import Path
from typing import Optional


def _module_fs_path(module) -> Optional[Path]:
    """Filesystem path from __file__ or spec.origin (namespace / missing -> None)."""
    fp = getattr(module, "__file__", None)
    if fp:
        return Path(fp)
    spec = getattr(module, "__spec__", None)
    if spec is None or not spec.origin or spec.origin == "namespace":
        return None
    return Path(spec.origin)


def is_subpath(child: Path, parent: Path) -> bool:
    """True if child is under parent (logical path or resolved)."""
    try:
        child.relative_to(parent)
        return True
    except ValueError:
        pass
    try:
        child.resolve().relative_to(parent.resolve())
        return True
    except ValueError:
        pass
    return False


def _embedded_runtime_root() -> Path:
    """Directory tree of the Cadwork / embedded Python install (stdlib, DLLs)."""
    return Path(sys.base_prefix).resolve()


def _reload_candidate(module, module_path: Optional[Path], api_base: Path) -> bool:
    """
    True if the module can be reloaded from disk.

    - Under API.x64 (deployed plugins), or
    - Any .py/.pyd with a path outside sys.base_prefix (e.g. cadwork_oo from a
      Git checkout on sys.path while biskupcltplanner lives under Public).

    Skips built-in/frozen, namespace-only, and stdlib under base_prefix.
    """
    spec = getattr(module, "__spec__", None)
    if spec is not None and spec.origin in ("built-in", "frozen"):
        return False
    if module_path is None:
        return False
    ps = str(module_path)
    if ps in ("built-in", "frozen") or ps.startswith("<"):
        return False
    if is_subpath(module_path, api_base):
        return True
    try:
        if is_subpath(module_path.resolve(), _embedded_runtime_root()):
            return False
    except OSError:
        pass
    return True


def ReloadAllModules():
    """
    Reload loaded plugin/project modules: under API.x64, or on disk outside
    the embedded Python tree (sys.base_prefix) so sibling repos (e.g.
    cadwork_oo from Git) reload together with code under Public/API.x64.
    """
    api_base = Path(__file__).parent.parent
    print(f"HotReload - Reloading modules from: {api_base}")

    modules_to_reload = []
    for module_name, module in list(sys.modules.items()):
        if module is None or module_name == "__main__":
            continue
        try:
            module_path = _module_fs_path(module)
            if not _reload_candidate(module, module_path, api_base):
                continue
            modules_to_reload.append((module_name, module))
        except (AttributeError, TypeError, ValueError):
            continue

    modules_to_reload.sort(key=lambda item: (-item[0].count("."), item[0]))

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
