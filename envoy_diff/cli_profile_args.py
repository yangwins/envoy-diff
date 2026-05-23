"""CLI sub-commands for managing named environment profiles."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Optional

from envoy_diff.profiler import (
    DEFAULT_PROFILE_PATH,
    delete_profile,
    list_profiles,
    load_profile,
    save_profile,
)
from envoy_diff.loader import load_from_file, load_from_env


def add_profile_subcommands(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    profile_parser = subparsers.add_parser("profile", help="Manage named environment profiles")
    profile_sub = profile_parser.add_subparsers(dest="profile_cmd", required=True)

    # list
    profile_sub.add_parser("list", help="List saved profiles")

    # save
    save_p = profile_sub.add_parser("save", help="Save an environment as a named profile")
    save_p.add_argument("name", help="Profile name")
    save_p.add_argument("--file", metavar="PATH", help="Load env from file instead of current process")
    save_p.add_argument("--profiles-file", metavar="PATH", default=str(DEFAULT_PROFILE_PATH))

    # show
    show_p = profile_sub.add_parser("show", help="Print a saved profile as JSON")
    show_p.add_argument("name", help="Profile name")
    show_p.add_argument("--profiles-file", metavar="PATH", default=str(DEFAULT_PROFILE_PATH))

    # delete
    del_p = profile_sub.add_parser("delete", help="Delete a saved profile")
    del_p.add_argument("name", help="Profile name")
    del_p.add_argument("--profiles-file", metavar="PATH", default=str(DEFAULT_PROFILE_PATH))


def run_profile_command(args: argparse.Namespace) -> int:
    pfile = Path(args.profiles_file) if hasattr(args, "profiles_file") else DEFAULT_PROFILE_PATH

    if args.profile_cmd == "list":
        names = list_profiles(pfile)
        if not names:
            print("No profiles saved.")
        else:
            for name in names:
                print(name)
        return 0

    if args.profile_cmd == "save":
        env = load_from_file(args.file) if args.file else load_from_env()
        save_profile(args.name, env, pfile)
        print(f"Profile {args.name!r} saved ({len(env)} keys).")
        return 0

    if args.profile_cmd == "show":
        try:
            env = load_profile(args.name, pfile)
        except KeyError as exc:
            print(f"Error: {exc}", file=sys.stderr)
            return 1
        print(json.dumps(env, indent=2))
        return 0

    if args.profile_cmd == "delete":
        existed = delete_profile(args.name, pfile)
        if existed:
            print(f"Profile {args.name!r} deleted.")
            return 0
        print(f"Error: profile {args.name!r} not found.", file=sys.stderr)
        return 1

    return 0
