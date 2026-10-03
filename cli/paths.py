from __future__ import annotations

import os
from pathlib import Path

from cli.common import ADAPTERS_DIR, load_yaml

SUPPORTED_OS = ("linux", "macos", "windows")
SUPPORTED_SCOPES = ("user", "project")


def load_targets() -> dict:
    return load_yaml(ADAPTERS_DIR / "targets.yaml")


def list_ides() -> list[str]:
    data = load_targets()
    return sorted((data.get("ides") or {}).keys())


def resolve_home(os_name: str, home_override: Path | None = None) -> Path:
    if home_override is not None:
        return home_override.expanduser().resolve()
    # On all supported platforms Path.home() is correct; keep os_name for adapters.
    _ = os_name
    return Path.home().resolve()


def expand_template(
    template: str,
    *,
    os_name: str,
    project_root: Path | None = None,
    home_override: Path | None = None,
) -> Path:
    home = resolve_home(os_name, home_override)
    values = {
        "home": str(home),
        "project_root": str(project_root.resolve()) if project_root else "",
    }
    path = template
    for key, value in values.items():
        path = path.replace("{" + key + "}", value)
    if "{project_root}" in template and not project_root:
        raise ValueError("project_root is required for project scope")
    # Normalize env-style Windows vars if present in custom templates
    path = os.path.expandvars(path)
    return Path(path).expanduser().resolve()


def resolve_install_dir(
    ide: str,
    os_name: str,
    scope: str = "user",
    project_root: Path | None = None,
    home_override: Path | None = None,
) -> Path:
    os_name = os_name.lower()
    scope = scope.lower()
    if os_name not in SUPPORTED_OS:
        raise ValueError(f"Unsupported OS '{os_name}'. Use: {', '.join(SUPPORTED_OS)}")
    if scope not in SUPPORTED_SCOPES:
        raise ValueError(
            f"Unsupported scope '{scope}'. Use: {', '.join(SUPPORTED_SCOPES)}"
        )
    if scope == "project" and project_root is None:
        raise ValueError("--project-root is required when --scope project")
    if scope != "project" and project_root is not None:
        raise ValueError("--project-root is only valid with --scope project")

    data = load_targets()
    ides = data.get("ides") or {}
    if ide not in ides:
        raise ValueError(f"Unknown IDE '{ide}'. Supported: {', '.join(sorted(ides))}")

    template = ((ides[ide].get(scope) or {}).get(os_name))
    if not template:
        raise ValueError(f"No path template for ide={ide} os={os_name} scope={scope}")

    return expand_template(
        template,
        os_name=os_name,
        project_root=project_root,
        home_override=home_override,
    )
