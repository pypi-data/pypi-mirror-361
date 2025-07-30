import argparse as ap
import logging
import sys

from .query_user_interval import cli_entrypoint


main_parser = ap.ArgumentParser(
    description="`fractal-slurm-tools-user-interval` command-line interface",
    allow_abbrev=False,
)

main_parser.add_argument(
    "--fractal-backend-url",
    type=str,
    required=True,
)
main_parser.add_argument(
    "--user-email",
    type=str,
    required=True,
)
main_parser.add_argument(
    "--base-output-folder",
    type=str,
    help="Base folder for output files.",
    required=True,
)

main_parser.add_argument(
    "--year",
    type=int,
    required=True,
)
main_parser.add_argument(
    "--month",
    type=int,
    required=True,
)


main_parser.add_argument(
    "--verbose",
    help="If set, use DEBUG as a logging level.",
    action="store_true",
)


def _parse_arguments(sys_argv: list[str] | None = None) -> ap.Namespace:
    """
    Parse `sys.argv` or custom CLI arguments.

    Arguments:
        sys_argv: If set, overrides `sys.argv` (useful for testing).
    """
    if sys_argv is None:
        sys_argv = sys.argv[:]
    args = main_parser.parse_args(sys_argv[1:])
    return args


def main():
    args = _parse_arguments()

    fmt = "%(asctime)s; %(levelname)s; %(message)s"
    if args.verbose:
        logging.basicConfig(level=logging.DEBUG, format=fmt)
    else:
        logging.basicConfig(level=logging.INFO, format=fmt)
    from . import __VERSION__

    logging.debug(f"fractal-slurm-tools-user-interval version: {__VERSION__}")
    logging.debug(f"{args=}")

    cli_entrypoint(
        fractal_backend_url=args.fractal_backend_url,
        user_email=args.user_email,
        year=args.year,
        month=args.month,
        base_output_folder=args.base_output_folder,
    )
