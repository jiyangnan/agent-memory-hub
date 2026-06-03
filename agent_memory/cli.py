from __future__ import annotations

import argparse
import json
from pathlib import Path

from .config import load_config
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

    parser.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

