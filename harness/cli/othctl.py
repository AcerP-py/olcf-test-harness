import argparse as ap
import sys

from harness.config import oth_config
from harness.libraries import input_files, regression_test
from harness.libraries.config_file import rgt_config_file
from harness.libraries.output_hub import OutputHub

from .helpers import comma_separated_items


def run(args: ap.Namespace) -> None:
    oh: OutputHub = OutputHub(__name__)

    oh.log_info("reading the harness input file")
    input_file = input_files.rgt_input_file(
        inputfilename=args.input_file,
        runmodecmd=args.mode,
        app_filter=args.app_filter,
        test_filter=args.test_filter,
        logger=oh,
    )
    oh.log_info("completed reading the harness input file")

    if len(input_file.get_tests()) == 0:
        oh.print("No tests were found in the input file. Aborting!")
        sys.exit(0)

    oh.log_info("reading the harness config file")
    try:
        config = rgt_config_file(configfilename=args.config_file, logger=oh)
    except NameError as e:
        oh.log_critical(str(e))
        sys.exit(1)
    oh.log_info("completed reading the harness config file")

    rgt = regression_test.Harness(
        config,
        input_file,
        args.loglevel,
        args.output,
        args.separate_build_stdio,
        args.reuse_first_build,
        args.reuse_build_from_id,
        shuffle=args.shuffle,
    )
    oh.log_info(f"created an instance of the harness: {rgt}")

    oh.log_info("running the harness tasks")
    rgt.run_me()
    oh.log_info("completed running the harness tasks")


def status(args: ap.Namespace) -> None:
    oh: OutputHub = OutputHub(__name__)

    if args.color:
        tbl_str_fmt = "{:<10.10} {:<20.20} {:<20.20} {}{:<9.9}{}"
    else:
        tbl_str_fmt = "{:<10.10} {:<20.20} {:<20.20} {:<9.9}"

    if args.color:
        oh.print(tbl_str_fmt.format("ID", "APPLICATION", "TEST", "", "STATUS", ""))
    else:
        oh.print(tbl_str_fmt.format("ID", "APPLICATION", "TEST", "STATUS"))

    oh.print("=" * 61)

    if args.color:
        oh.print(
            tbl_str_fmt.format(
                "78637645",
                "lammps",
                "n008_ppn8_spce",
                "\033[32m",
                "SUCCEEDED",
                "\033[39m",
            )
        )
        oh.print(
            tbl_str_fmt.format(
                "78694385",
                "osumb",
                "n008_ppn8_alltoall",
                "\033[33m",
                "BUILDING",
                "\033[39m",
            )
        )
        oh.print(
            tbl_str_fmt.format(
                "72766385",
                "cp2k",
                "quantum_combobulations",
                "\033[31m",
                "FAILED",
                "\033[39m",
            )
        )
    else:
        oh.print(
            tbl_str_fmt.format("78637645", "lammps", "n008_ppn8_spce", "SUCCEEDED")
        )
        oh.print(
            tbl_str_fmt.format("78694385", "osumb", "n008_ppn8_alltoall", "BUILDING")
        )
        oh.print(
            tbl_str_fmt.format("72766385", "cp2k", "quantum_combobulations", "FAILED")
        )


def main() -> None:
    # argument parser
    arg_parser: ap.ArgumentParser = ap.ArgumentParser(
        prog="othctl",
        description="OLCF Test Harness CLI driver.",
        epilog="See https://github.com/olcf/olcf-test-harness.git",
        formatter_class=ap.ArgumentDefaultsHelpFormatter,
    )
    arg_parser.add_argument(
        "-l",
        "--log-level",
        default="WARNING",
        type=str,
        choices=("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"),
        required=False,
        help="logging level",
    )
    arg_parser.add_argument(
        "-c",
        "--config-file",
        default=rgt_config_file.get_default_config_file_name(),
        type=str,
        required=False,
        help="machine configuration file",
    )

    # No public type for arg_parser.add_subparsers
    sub_parsers = arg_parser.add_subparsers(
        dest="subcommand", help="harness action"
    )  # TODO: add required=True when Python >= 3.7

    # run subparser
    run_parser: ap.ArgumentParser = sub_parsers.add_parser(
        "run",
        help="run test(s)",
        formatter_class=ap.ArgumentDefaultsHelpFormatter,
    )
    run_parser.add_argument(
        "-i",
        "--input-file",
        default="rgt.input",
        type=str,
        required=False,
        help="input file",
    )
    run_parser.add_argument(
        "--shuffle", action="store_true", help="shuffle the test launch order"
    )
    run_parser.add_argument(
        "-o",
        "--output",
        default="screen",
        type=str,
        choices=("screen", "logfile"),
        required=False,
        help="test output method",
    )
    run_parser.add_argument(
        "-m",
        "--mode",
        nargs="+",
        default=["use_input_file"],
        choices=("checkout", "start", "stop", "status"),
        required=False,
        help="perform checkout, start, stop, or status on application tests listed in the input file",
    )
    run_parser.add_argument(
        "-sb",
        "--separate-build-studio",
        action="store_true",
        required=False,
        help="separate build output into build_out.stderr.txt and build_out.stdout.txt",
    )
    run_parser.add_argument(
        "--reuse-first-build",
        action="store_true",
        required=False,
        help="for re-submittable tests, re-use the first build in the chain",
    )
    run_parser.add_argument(
        "--reuse-build-from-id",
        action="store",
        default=None,
        type=str,
        required=False,
        help="re-use build from specified test ID",
    )
    run_parser.add_argument(
        "--app-filter",
        default=[],
        type=comma_separated_items,
        required=False,
        help="comma-separated list of regular expressions or strings used to select specific applications from the provided input file",
    )
    run_parser.add_argument(
        "--test-filter",
        default=[],
        type=comma_separated_items,
        required=False,
        help="comma-separated list of regular expressions or strings used to select specific tests from the provided input file",
    )

    # status subparser
    status_parser: ap.ArgumentParser = sub_parsers.add_parser(
        "status",
        help="check status of run(s)",
        formatter_class=ap.ArgumentDefaultsHelpFormatter,
    )
    status_parser.add_argument(
        "-id",
        "--run-id",
        action="store",
        type=str,
        required=False,
        help="specific run id to check",
    )
    status_parser.add_argument(
        "--color",
        action="store_true",
        default=False,
        required=False,
        help="print status with color",
    )

    # parse args
    args: ap.Namespace = arg_parser.parse_args()

    # set global config
    oth_config.set("log_level", args.log_level)

    # start harness
    oh: OutputHub = OutputHub(
        __name__,
        log_level=args.log_level,
        log_file="main.log",
        console_log_level=args.log_level,
        file_log_level=args.log_level,
    )
    oh.log_info("starting harness")
    oh.log_info(f"invoked with: '{' '.join(sys.argv[1:])}'")

    # branch to sub-command
    if args.subcommand == "run":
        run(args)
    elif args.subcommand == "status":
        status(args)
    else:
        # TODO: can be removed when the above todo has been done
        raise ValueError("you must specify a valid subcommand - options: (run, status)")

    oh.log_info("ending harness")


if __name__ == "__main__":
    main()
