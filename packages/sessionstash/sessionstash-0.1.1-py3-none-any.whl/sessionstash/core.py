from __future__ import annotations

"""Core helpers for saving and loading Python workspaces."""

import inspect
from types import ModuleType
from pathlib import Path
import dill

__all__ = ["save_workspace", "load_workspace"]

# Built‑in names plus heavy / unserialisable objects to skip by default.
_DEFAULT_EXCLUDE: set[str] = set(dir(__builtins__)) | {
    "dill",
    "inspect",
    "ModuleType",
    "Path",
}


def _collect_serialisable(namespace: dict[str, object]) -> dict[str, object]:
    """Return only pickle‑able items from *namespace*."""
    serialisable: dict[str, object] = {}
    for name, obj in namespace.items():
        if (
            name.startswith("_")
            or name in _DEFAULT_EXCLUDE
            or isinstance(obj, ModuleType)
            or inspect.ismodule(obj)
        ):
            continue
        serialisable[name] = obj
    return serialisable


def save_workspace(
    path: str | Path,
    namespace: dict[str, object] | None = None,
) -> None:
    """Serialize *namespace* (defaults to the caller's local scope) to *path* using dill."""
    path = Path(path)
    if namespace is None:
        # Go back 1 frame to get the caller's locals
        frame = inspect.currentframe()
        if frame and frame.f_back:
            namespace = frame.f_back.f_locals
        else:  # Fallback for weird environments
            namespace = locals()

    path.write_bytes(dill.dumps(_collect_serialisable(namespace)))
    print(f"✅ Workspace saved → {path}")


def load_workspace(
    path: str | Path,
    namespace: dict[str, object] | None = None,
) -> None:
    """Deserialize objects from *path* into *namespace* (defaults to the caller's ``globals()``)."""
    path = Path(path)
    if namespace is None:
        # Go back 1 frame to get the caller's globals
        frame = inspect.currentframe()
        if frame and frame.f_back:
            namespace = frame.f_back.f_globals
        else:  # Fallback for weird environments
            namespace = globals()

    loaded_data = dill.loads(path.read_bytes())
    namespace.update(loaded_data)
    print(f"✅ Workspace restored ← {path} ({len(loaded_data)} objects)")
