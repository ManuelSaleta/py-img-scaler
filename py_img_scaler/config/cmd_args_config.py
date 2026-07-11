import argparse
from pathlib import Path
from typing import NamedTuple


class CmdArgument(NamedTuple):
    """Simple data structure to hold command line argument details."""

    short: str
    long: str
    desc: str


project_desc = "py_img_scaler: A cross-platform AI upscaling utility to upscale images to a higher resolution."

predefined_command_line_args = [
    CmdArgument(
        short="-s",
        long="--source",
        desc="Path to the source directory containing input images. (Overrides config default)",
    ),
    CmdArgument(
        short="-d",
        long="--destination",
        desc="Path to the destination directory for upscaled outputs. (Overrides config default)",
    ),
    CmdArgument(
        short="-m",
        long="--model",
        desc="Specify the AI model to use for upscaling. values 0,1,2 - 0 is the smallest and most performant model, 2 is the largest and most accurate model, but will be slower and most powerful (Overrides config default)",
    ),
]


def validate_args(args):
    """Validate the provided command line arguments."""
    if args.source and not Path(args.source).is_dir():
        raise ValueError(
            f"Source directory '{args.source}' does not exist or is not a directory."
        )
    if args.destination and not Path(args.destination).is_dir():
        raise ValueError(
            f"Destination directory '{args.destination}' does not exist or is not a directory."
        )
    if args.model and args.model not in ["0", "1", "2"]:
        raise ValueError(
            f"Model '{args.model}' is invalid. Choose from 0, 1, or 2. 0 being least resource intensive model."
        )


def get_parsed_args():
    """Parse and return command line arguments."""
    # Parser setup for command line arguments

    parser = argparse.ArgumentParser(description=project_desc)

    for arg in predefined_command_line_args:
        parser.add_argument(arg.short, arg.long, help=arg.desc)

    args = parser.parse_args()
    validate_args(args)
    return args
