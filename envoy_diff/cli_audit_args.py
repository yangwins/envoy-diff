"""CLI subcommands for the audit log feature."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from envoy_diff.auditor import clear_audit, load_audit


def add_audit_subcommands(subparsers: argparse._SubParsersAction) -> None:
    """Register 'audit' subcommands onto *subparsers*."""
    audit_parser = subparsers.add_parser("audit", help="Manage the audit log")
    audit_sub = audit_parser.add_subparsers(dest="audit_command")

    # list
    list_parser = audit_sub.add_parser("list", help="Print audit log entries")
    list_parser.add_argument(
        "--directory",
        default=".",
        help="Directory containing the audit log (default: current directory)",
    )
    list_parser.add_argument(
        "--json",
        dest="as_json",
        action="store_true",
        help="Output entries as raw JSON",
    )

    # clear
    clear_parser = audit_sub.add_parser("clear", help="Delete the audit log")
    clear_parser.add_argument(
        "--directory",
        default=".",
        help="Directory containing the audit log (default: current directory)",
    )


def run_audit_command(ns: argparse.Namespace) -> int:
    """Dispatch audit subcommand from parsed namespace. Returns exit code."""
    directory = Path(getattr(ns, "directory", "."))
    command = getattr(ns, "audit_command", None)

    if command == "list":
        entries = load_audit(directory=directory)
        if not entries:
            print("No audit entries found.")
            return 0
        if getattr(ns, "as_json", False):
            print(json.dumps(entries, indent=2))
        else:
            for e in entries:
                import datetime
                ts = datetime.datetime.fromtimestamp(e["timestamp"]).isoformat()
                print(
                    f"[{ts}] {e['operation']} "
                    f"{e['source_a']} vs {e['source_b']} "
                    f"+{e['added']} -{e['removed']} ~{e['changed']}"
                )
        return 0

    if command == "clear":
        clear_audit(directory=directory)
        print("Audit log cleared.")
        return 0

    print("No audit subcommand given. Use 'list' or 'clear'.")
    return 1
