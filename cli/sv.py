#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from cli import __version__
from cli.common import iter_vault_skills
from cli.import_cmd import apply_import, import_from_url, print_import_summary
from cli.install_cmd import install_skills
from cli.paths import list_ides
from cli.sync_cmd import sync_skills


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="sv",
        description="SkillVault: import, install, and sync Agent Skills across IDEs.",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    sub = parser.add_subparsers(dest="command", required=True)

    p_list = sub.add_parser("list", help="List skills in the vault")
    p_list.set_defaults(func=cmd_list)

    p_install = sub.add_parser("install", help="Install skill(s) into an IDE path")
    p_install.add_argument("skills", nargs="*", help="Skill name(s)")
    p_install.add_argument("--all", action="store_true", help="Install all vault skills")
    p_install.add_argument("--ide", required=True, choices=list_ides(), help="Target IDE")
    p_install.add_argument(
        "--os",
        required=True,
        choices=["linux", "macos", "windows"],
        dest="os_name",
        help="Target OS",
    )
    p_install.add_argument(
        "--scope",
        default="user",
        choices=["user", "project"],
        help="Install scope (default: user)",
    )
    p_install.add_argument(
        "--project-root",
        type=Path,
        default=None,
        help="Project root (required for --scope project)",
    )
    p_install.add_argument("--force", action="store_true", help="Overwrite existing")
    p_install.add_argument(
        "--link",
        action="store_true",
        help="Symlink instead of copy (advanced)",
    )
    p_install.add_argument(
        "--home",
        type=Path,
        default=None,
        help=argparse.SUPPRESS,
    )
    p_install.set_defaults(func=cmd_install)

    p_import = sub.add_parser("import", help="Fetch a public skill URL into cache")
    p_import.add_argument("url", help="GitHub URL or local path")
    p_import.add_argument("--name", help="Local skill name")
    p_import.add_argument("--ref", help="Git ref override")
    p_import.add_argument(
        "--apply",
        action="store_true",
        help="Copy into vault/imported and update registry (raw; prefer AI conversion)",
    )
    p_import.set_defaults(func=cmd_import)

    p_sync = sub.add_parser("sync", help="Re-fetch registered upstream skills")
    p_sync.add_argument("skills", nargs="*", help="Skill name(s)")
    p_sync.add_argument("--all", action="store_true", help="Sync all registry entries")
    p_sync.add_argument(
        "--apply",
        action="store_true",
        help="Apply upstream files into vault/imported",
    )
    p_sync.set_defaults(func=cmd_sync)

    return parser


def cmd_list(_: argparse.Namespace) -> int:
    skills = iter_vault_skills()
    if not skills:
        print("No skills in vault.")
        return 0
    for name, path, origin in skills:
        print(f"{name}\t{origin}\t{path}")
    return 0


def cmd_install(args: argparse.Namespace) -> int:
    paths = install_skills(
        args.skills,
        ide=args.ide,
        os_name=args.os_name,
        scope=args.scope,
        project_root=args.project_root,
        force=args.force,
        link=args.link,
        home_override=args.home,
        all_skills=args.all,
    )
    for path in paths:
        print(f"Installed: {path}")
    return 0


def cmd_import(args: argparse.Namespace) -> int:
    result = import_from_url(
        args.url,
        name=args.name,
        ref=args.ref,
        apply=args.apply,
    )
    print(print_import_summary(result))
    if args.apply:
        if not args.name and result.skill_md:
            # apply_import already ran inside import_from_url when apply=True
            pass
        print(f"Applied to vault/imported/{args.name or '(from frontmatter)'}")
    return 0


def cmd_sync(args: argparse.Namespace) -> int:
    reports = sync_skills(args.skills, all_skills=args.all, apply=args.apply)
    print("\n\n".join(reports))
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except (ValueError, FileNotFoundError, FileExistsError, RuntimeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
