from __future__ import annotations

import argparse
import json
from pathlib import Path

from .bootstrap import render_bootstrap
from .cloud import cloud_pull, cloud_push, cloud_save, cloud_status
from .config import load_config
from .curator import curate_apply, scan_status
from .inbox import add_inbox_note
from .registry import register_agent, render_members
from .setup import setup_workspace
from .sync import install_marker, sync_apply, sync_dry_run
from .triggers import classify_trigger


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="agent-memory",
        description="agent memory hub: shared memory infrastructure for multi-agent workflows",
    )
    parser.add_argument("--root", default=".", help="Workspace root")
    subparsers = parser.add_subparsers(dest="command")

    trigger = subparsers.add_parser("trigger", help="Classify memory intent")
    trigger.add_argument("text")

    setup = subparsers.add_parser("setup", help="Initialize a private agent memory hub workspace")
    setup.add_argument("--workspace", default="my-agent-memory")
    setup.add_argument("--machine", action="append", dest="machines", default=[])
    setup.add_argument("--adapter", action="append", dest="adapters", default=[])
    setup.add_argument("--force", action="store_true")

    inbox = subparsers.add_parser("inbox-add", help="Write a shared-memory inbox note")
    inbox.add_argument("--machine", required=True)
    inbox.add_argument("--agent", required=True)
    inbox.add_argument("--type", required=True)
    inbox.add_argument("--scope", default="global")
    inbox.add_argument("--priority", default="normal")
    inbox.add_argument("--fact", required=True)
    inbox.add_argument("--why", required=True)
    inbox.add_argument("--evidence", required=True)
    inbox.add_argument("--destination", required=True)

    register = subparsers.add_parser("register-agent", help="Register a machine/agent pair")
    register.add_argument("--machine", required=True)
    register.add_argument("--agent", required=True)
    register.add_argument("--adapter", default="")
    register.add_argument("--primary-memory", required=True)
    register.add_argument("--skill-target", default="")

    subparsers.add_parser("members", help="Show registered agents")

    bootstrap = subparsers.add_parser("bootstrap", help="Render an agent cold-start contract")
    bootstrap.add_argument("--machine", required=True)
    bootstrap.add_argument("--agent", required=True)

    subparsers.add_parser("status", help="Show inbox and curator status")
    subparsers.add_parser("curate-dry-run", help="Validate pending notes without merging")
    curate = subparsers.add_parser("curate-apply", help="Merge clean pending notes into canonical memory")
    curate.add_argument("--machine", required=True)
    curate.add_argument("--agent", required=True)

    cloud_status_parser = subparsers.add_parser("cloud-status", help="Check Git remote readiness")
    cloud_status_parser.add_argument("--remote", default="origin")
    cloud_pull_parser = subparsers.add_parser("cloud-pull", help="Fast-forward pull latest shared state")
    cloud_pull_parser.add_argument("--remote", default="origin")
    cloud_pull_parser.add_argument("--branch", default=None)
    cloud_save_parser = subparsers.add_parser("cloud-save", help="Commit shared memory state only")
    cloud_save_parser.add_argument("--message", required=True)
    cloud_save_parser.add_argument("--remote", default="origin")
    cloud_push_parser = subparsers.add_parser("cloud-push", help="Push committed shared state")
    cloud_push_parser.add_argument("--remote", default="origin")
    cloud_push_parser.add_argument("--branch", default=None)

    sync = subparsers.add_parser("sync", help="Sync canonical shared memory into an agent memory file")
    sync.add_argument("--machine", required=True)
    sync.add_argument("--agent", required=True)
    sync.add_argument("--home", default=str(Path.home()))
    sync_mode = sync.add_mutually_exclusive_group(required=True)
    sync_mode.add_argument("--dry-run", action="store_true")
    sync_mode.add_argument("--install-marker", action="store_true")
    sync_mode.add_argument("--apply", action="store_true")

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    root = Path(args.root).resolve()

    if args.command == "trigger":
        try:
            config = load_config(root)
        except FileNotFoundError:
            config = None
        print(classify_trigger(args.text, config=config))
        return 0

    if args.command == "setup":
        result = setup_workspace(
            root,
            workspace=args.workspace,
            machines=args.machines or ["laptop"],
            adapters=args.adapters or ["codex"],
            force=args.force,
        )
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0

    if args.command == "inbox-add":
        try:
            note = add_inbox_note(
                root,
                machine=args.machine,
                agent=args.agent,
                note_type=args.type,
                scope=args.scope,
                priority=args.priority,
                fact=args.fact,
                why=args.why,
                evidence=args.evidence,
                suggested_destination=args.destination,
            )
        except ValueError as exc:
            print(str(exc))
            return 2
        print(f"inbox note created: {note['path'].relative_to(root)}")
        return 0

    if args.command == "register-agent":
        record = register_agent(
            root,
            machine=args.machine,
            agent=args.agent,
            adapter=args.adapter,
            primary_memory=args.primary_memory,
            skill_target=args.skill_target,
        )
        print(json.dumps(record, ensure_ascii=False, indent=2))
        return 0

    if args.command == "members":
        print(render_members(root))
        return 0

    if args.command == "bootstrap":
        try:
            print(render_bootstrap(root, machine=args.machine, agent=args.agent))
        except ValueError as exc:
            print(str(exc))
            return 2
        return 0

    if args.command in ("status", "curate-dry-run"):
        status = scan_status(root)
        print(json.dumps(status, ensure_ascii=False, indent=2))
        if args.command == "curate-dry-run" and (status["secret_blocked_notes"] or status["invalid_notes"]):
            return 2
        return 0

    if args.command == "curate-apply":
        result = curate_apply(root, machine=args.machine, agent=args.agent)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0

    if args.command == "cloud-status":
        result = cloud_status(root, remote=args.remote)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0 if result["status"] == "ready" else 2

    if args.command == "cloud-pull":
        result = cloud_pull(root, remote=args.remote, branch=args.branch)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0 if result["status"] == "up_to_date" else 2

    if args.command == "cloud-save":
        result = cloud_save(root, message=args.message, remote=args.remote)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0 if result["status"] in ("committed", "no_change") else 2

    if args.command == "cloud-push":
        result = cloud_push(root, remote=args.remote, branch=args.branch)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0 if result["status"] == "pushed" else 2

    if args.command == "sync":
        home = Path(args.home).expanduser().resolve()
        try:
            if args.dry_run:
                result = sync_dry_run(root, home=home, machine=args.machine, agent=args.agent)
            elif args.install_marker:
                result = install_marker(root, home=home, machine=args.machine, agent=args.agent)
            else:
                result = sync_apply(root, home=home, machine=args.machine, agent=args.agent)
        except (FileNotFoundError, ValueError) as exc:
            print(str(exc))
            return 2
        print(json.dumps(result, ensure_ascii=False, indent=2))
        blocked_statuses = {"unsafe_target", "missing_marker", "missing_target"}
        return 2 if result["status"] in blocked_statuses else 0

    parser.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
