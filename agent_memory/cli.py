from __future__ import annotations

import argparse
import json
from pathlib import Path

from .bootstrap import render_bootstrap
from .config import load_config
from .inbox import add_inbox_note
from .registry import register_agent, render_members
from .setup import setup_workspace
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

    parser.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
