#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from cli import __version__
from cli.common import KNOWN_CATEGORIES, iter_vault_skills, validate_category
from cli.import_cmd import apply_import, import_from_url, print_import_summary
from cli.install_cmd import install_skills
from cli.paths import list_ides
from cli.ide_sync import compare_vault_to_ide, format_ide_sync_report
from cli.security_scan import scan_tree, write_reports
from cli.sync_cmd import sync_skills
from cli.watch_security_sources import (
    format_security_sources,
    watch_security_sources,
    write_security_json,
)
from cli.watch_upstream import format_upstream_watch, watch_upstream, write_upstream_json


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="sv",
        description="SkillVault: import, install, and sync Agent Skills across IDEs.",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    sub = parser.add_subparsers(dest="command", required=True)

    p_list = sub.add_parser("list", help="List skills in the vault")
    p_list.add_argument(
        "--category",
        metavar="CAT",
        help=(
            "Filter by taxonomy category (see docs/taxonomy.md). "
            f"Known: {', '.join(sorted(KNOWN_CATEGORIES))}"
        ),
    )
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
        "--category",
        default="inbox",
        help="Category under vault/imported when using --apply (default: inbox)",
    )
    p_import.add_argument(
        "--apply",
        action="store_true",
        help="Copy into vault/imported and update registry (raw; prefer AI conversion)",
    )
    p_import.add_argument(
        "--accept-security-risks",
        action="store_true",
        help="Allow --apply when security verdict is FAIL (Gate B must document acceptance)",
    )
    p_import.set_defaults(func=cmd_import)

    p_scan = sub.add_parser(
        "security-scan",
        help="Scan a skill directory or import cache for security findings",
    )
    p_scan.add_argument(
        "path",
        type=Path,
        help="Path to skill root (contains SKILL.md) or import cache dir",
    )
    p_scan.set_defaults(func=cmd_security_scan)

    p_doctor = sub.add_parser(
        "doctor",
        help="Vault↔IDE presence report (pending / orphan / in_sync by name)",
    )
    p_doctor.add_argument("--ide", required=True, choices=list_ides(), help="Target IDE")
    p_doctor.add_argument(
        "--os",
        required=True,
        choices=["linux", "macos", "windows"],
        dest="os_name",
        help="Host OS",
    )
    p_doctor.add_argument(
        "--scope",
        default="user",
        choices=["user", "project"],
        help="Scope (default: user)",
    )
    p_doctor.add_argument(
        "--project-root",
        type=Path,
        default=None,
        help="Project root when --scope project",
    )
    p_doctor.add_argument(
        "--home",
        type=Path,
        default=None,
        help=argparse.SUPPRESS,
    )
    p_doctor.set_defaults(func=cmd_doctor)

    p_sync = sub.add_parser(
        "sync",
        help="Re-fetch upstream registry skills and diff vs vault/imported",
    )
    p_sync.add_argument("skills", nargs="*", help="Upstream skill name(s) to re-fetch")
    p_sync.add_argument(
        "--all",
        action="store_true",
        help="Re-fetch all registry upstream entries",
    )
    p_sync.add_argument(
        "--apply",
        action="store_true",
        help="Apply upstream files into vault/imported",
    )
    p_sync.add_argument(
        "--accept-security-risks",
        action="store_true",
        help=(
            "Allow --apply when security verdict is FAIL "
            "(Gate B must document acceptance)"
        ),
    )
    # Deprecated: use `sv doctor` for vault↔IDE presence
    p_sync.add_argument(
        "--ide",
        choices=list_ides(),
        help=argparse.SUPPRESS,
    )
    p_sync.add_argument(
        "--os",
        choices=["linux", "macos", "windows"],
        dest="os_name",
        help=argparse.SUPPRESS,
    )
    p_sync.add_argument(
        "--scope",
        default="user",
        choices=["user", "project"],
        help=argparse.SUPPRESS,
    )
    p_sync.add_argument(
        "--project-root",
        type=Path,
        default=None,
        help=argparse.SUPPRESS,
    )
    p_sync.add_argument(
        "--home",
        type=Path,
        default=None,
        help=argparse.SUPPRESS,
    )
    p_sync.set_defaults(func=cmd_sync)

    p_watch = sub.add_parser(
        "watch",
        help="Scheduled watch helpers: upstream drift or security rule sources",
    )
    watch_sub = p_watch.add_subparsers(dest="watch_cmd", required=True)
    p_watch_up = watch_sub.add_parser(
        "upstream", help="Compare registry upstream vs vault/imported (no --apply)"
    )
    p_watch_up.add_argument(
        "--json-out",
        type=Path,
        default=None,
        help="Write machine-readable report JSON",
    )
    p_watch_up.set_defaults(func=cmd_watch_upstream)
    p_watch_sec = watch_sub.add_parser(
        "security-sources",
        help="Fingerprint pinned security rule sources (no auto-edit)",
    )
    p_watch_sec.add_argument(
        "--json-out",
        type=Path,
        default=None,
        help="Write machine-readable report JSON",
    )
    p_watch_sec.set_defaults(func=cmd_watch_security_sources)

    return parser


def cmd_list(args: argparse.Namespace) -> int:
    skills = iter_vault_skills()
    category = getattr(args, "category", None)
    if category:
        validate_category(category)
        skills = [s for s in skills if s[3] == category]
        if not skills:
            tip = ""
            if category not in KNOWN_CATEGORIES:
                tip = (
                    f" Note: '{category}' is not in the known taxonomy set "
                    f"({', '.join(sorted(KNOWN_CATEGORIES))})."
                )
            print(f"No skills matching category '{category}'.{tip}")
            return 0
    if not skills:
        print("No skills in vault.")
        return 0
    print("name\tcategory\torigin\tpath")
    for name, path, origin, cat in skills:
        print(f"{name}\t{cat}\t{origin}\t{path}")
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
    if args.apply:
        validate_category(args.category)
    result = import_from_url(
        args.url,
        name=args.name,
        ref=args.ref,
        apply=args.apply,
        accept_security_risks=args.accept_security_risks,
        category=args.category,
    )
    print(print_import_summary(result))
    if args.apply:
        if not args.name and result.skill_md:
            # apply_import already ran inside import_from_url when apply=True
            pass
        print(
            f"Applied to vault/imported/{args.category}/"
            f"{args.name or '(from frontmatter)'}"
        )
    return 0


def cmd_security_scan(args: argparse.Namespace) -> int:
    root = args.path.expanduser().resolve()
    if not root.exists():
        raise FileNotFoundError(f"Path not found: {root}")
    report = scan_tree(root)
    json_path, md_path = write_reports(root, report)
    print(f"Verdict: {report.verdict}")
    print(
        f"Counts: critical={report.counts.get('critical', 0)} "
        f"warn={report.counts.get('warn', 0)} info={report.counts.get('info', 0)}"
    )
    print(f"Report: {md_path}")
    print(f"JSON: {json_path}")
    return 0 if report.verdict != "FAIL" else 2


def cmd_watch_upstream(args: argparse.Namespace) -> int:
    report = watch_upstream(all_skills=True)
    print(format_upstream_watch(report))
    if args.json_out:
        write_upstream_json(args.json_out, report)
        print(f"JSON: {args.json_out}")
    return 2 if report.has_drift else 0


def cmd_watch_security_sources(args: argparse.Namespace) -> int:
    report = watch_security_sources()
    print(format_security_sources(report))
    if args.json_out:
        write_security_json(args.json_out, report)
        print(f"JSON: {args.json_out}")
    return 2 if report.has_changes else 0


def _run_doctor(args: argparse.Namespace) -> int:
    if args.scope == "project" and args.project_root is None:
        raise ValueError("--project-root is required when --scope project")
    report = compare_vault_to_ide(
        ide=args.ide,
        os_name=args.os_name,
        scope=args.scope,
        project_root=args.project_root,
        home_override=args.home,
    )
    print(format_ide_sync_report(report))
    return 0


def cmd_doctor(args: argparse.Namespace) -> int:
    return _run_doctor(args)


def cmd_sync(args: argparse.Namespace) -> int:
    ide_mode = args.ide is not None or args.os_name is not None
    upstream_mode = bool(args.skills) or args.all or args.apply

    if ide_mode and upstream_mode:
        raise ValueError(
            "Use either `sv doctor --ide/--os` or upstream `sv sync` "
            "(skill names / --all), not both."
        )
    if ide_mode:
        if not args.ide or not args.os_name:
            raise ValueError("deprecated vault↔IDE mode requires both --ide and --os")
        print(
            "warning: `sv sync --ide/--os` is deprecated; use "
            f"`sv doctor --ide {args.ide} --os {args.os_name}` instead.",
            file=sys.stderr,
        )
        return _run_doctor(args)

    if not upstream_mode:
        raise ValueError(
            "Specify skill names or --all for upstream re-fetch. "
            "For vault↔IDE presence, use `sv doctor --ide <ide> --os <os>`."
        )
    reports = sync_skills(
        args.skills,
        all_skills=args.all,
        apply=args.apply,
        accept_security_risks=args.accept_security_risks,
    )
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
