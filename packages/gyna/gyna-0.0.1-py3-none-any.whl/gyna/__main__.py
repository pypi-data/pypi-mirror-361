# -*- encoding: utf-8 -*-
"""Gyna main package."""


import sys
import os
import argparse

from gyna.command import import_command
from gyna.command import iter_command_names
from gyna.command import CommandNotFoundError
from gyna._cli.argparse import ArgparseFormatter
from gyna._cli.argparse import chop_cmdsep


ME_DIR = os.path.dirname(__file__)
PROGNAME = "gyna"


try:
    from gyna import version as _version
except ImportError:
    __version__ = 'dev'
    __revision__ = 'git'
else:
    __version__ = _version.__version__
    __revision__ = _version.__revision__
    del _version


def git_describe():
    import subprocess as sp
    cmd = ["git", '-C', os.fspath(ME_DIR),
           "describe", "--long", "--match", "v*", "--dirty"]
    output = sp.check_output(cmd).decode().strip()
    if output.startswith("v"):
        output = output[1:]
    return output


def get_version():
    if __version__ != 'dev':
        return __version__
    return git_describe()


def git_revision():
    import subprocess as sp
    cmd = ["git", '-C', os.fspath(ME_DIR), "rev-parse", "HEAD"]
    return sp.check_output(cmd).decode().strip()


def get_revision():
    if __revision__ != 'git':
        return __revision__
    return git_revision()


def get_version_string():
    return \
        "gyna {v} "\
        "on python {pyv.major}.{pyv.minor}.{pyv.micro} "\
        "(rev: {rev})"\
        .format(v=get_version(),
                pyv=sys.version_info,
                rev=get_revision())


def mkcli():
    parser = argparse.ArgumentParser(
        prog=PROGNAME,
        description=__doc__,
        formatter_class=ArgparseFormatter,
        add_help=False)
    parser.add_argument(
        "--help",
        dest="show_help",
        action="store_true",
        help="Print help")
    parser.add_argument(
        "--version",
        dest="show_version",
        action="store_true",
        help="Print version number")
    parser.add_argument(
        "subcommand",
        action="store",
        nargs="?",
        help="Name of the sub-command to run")
    return parser


def main(argv):
    cli = mkcli()
    options, rest = cli.parse_known_args(argv[1:])
    if options.show_version:
        print(get_version_string())
        return 0
    if options.subcommand is None:
        cli.print_help()
        print()
        print("sub-commands:")
        for i in iter_command_names():
            print("  ", i)
        return 1
    chop_cmdsep(rest)
    rest = [options.subcommand]+rest
    try:
        subcmd_mod = import_command(options.subcommand)
    except CommandNotFoundError as e:
        print(f"{PROGNAME}: {e}")
        return 1
    return subcmd_mod.main(rest, options)


def sys_main():
    sys.exit(main(sys.argv))


if __name__ == "__main__":
    sys_main()