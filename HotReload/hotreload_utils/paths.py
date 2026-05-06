from pathlib import Path


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
