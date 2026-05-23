"""CLI sub-commands for managing and checking environment variable pins."""
from __future__ import annotations

import argparse
import sys
from typing import List

from envoy_diff.loader import load_from_env, load_from_file
from envoy_diff.pinner import check_pins, load_pins, save_pin, remove_pin


def add_pin_subcommands(subparsers: argparse._SubParsersAction) -> None:  # noqa: SLF001
    pin_parser = subparsers.add_parser("pin", help="Manage and check environment pins")
    pin_sub = pin_parser.add_subparsers(dest="pin_command", required=True)

    # pin set KEY VALUE
    set_p = pin_sub.add_parser("set", help="Pin a key to an expected value")
    set_p.add_argument("key", help="Environment variable name")
    set_p.add_argument("value", help="Expected value")
    set_p.add_argument("--dir", default=".", dest="directory", help="Pins directory")

    # pin remove KEY
    rm_p = pin_sub.add_parser("remove", help="Remove a pin")
    rm_p.add_argument("key", help="Environment variable name")
    rm_p.add_argument("--dir", default=".", dest="directory", help="Pins directory")

    # pin list
    ls_p = pin_sub.add_parser("list", help="List all pins")
    ls_p.add_argument("--dir", default=".", dest="directory", help="Pins directory")

    # pin check [--file FILE | uses live env]
    chk_p = pin_sub.add_parser("check", help="Check an environment against pins")
    chk_p.add_argument("--file", default=None, help="Env file to check (JSON or .env)")
    chk_p.add_argument("--dir", default=".", dest="directory", help="Pins directory")


def run_pin_command(args: argparse.Namespace, out=sys.stdout, err=sys.stderr) -> int:
    cmd = args.pin_command

    if cmd == "set":
        save_pin(args.key, args.value, args.directory)
        out.write(f"Pinned {args.key} = {args.value!r}\n")
        return 0

    if cmd == "remove":
        existed = remove_pin(args.key, args.directory)
        if existed:
            out.write(f"Removed pin for {args.key}\n")
        else:
            err.write(f"No pin found for {args.key}\n")
        return 0 if existed else 1

    if cmd == "list":
        pins = load_pins(args.directory)
        if not pins:
            out.write("No pins defined.\n")
        else:
            for key, value in sorted(pins.items()):
                out.write(f"{key}={value}\n")
        return 0

    if cmd == "check":
        env = load_from_file(args.file) if args.file else load_from_env()
        pins = load_pins(args.directory)
        result = check_pins(env, pins)
        if result.passed:
            out.write("All pins passed.\n")
            return 0
        else:
            err.write(f"{len(result.violations)} pin violation(s):\n")
            for v in result.violations:
                actual_display = repr(v.actual) if v.actual is not None else "<missing>"
                err.write(f"  {v.key}: expected {v.expected!r}, got {actual_display}\n")
            return 1

    err.write(f"Unknown pin sub-command: {cmd}\n")
    return 2
