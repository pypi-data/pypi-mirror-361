import argparse

from blueness import module
from blueness.argparse.generic import sys_exit

from bluer_ugv import NAME
from bluer_ugv.swallow.dataset.combination import combine
from bluer_ugv.logger import logger

NAME = module.name(__file__, NAME)

parser = argparse.ArgumentParser(NAME)
parser.add_argument(
    "task",
    type=str,
    help="combine",
)
parser.add_argument(
    "--count",
    type=int,
    default=-1,
)
parser.add_argument(
    "--download",
    type=int,
    default=1,
    help="0 | 1",
)
parser.add_argument(
    "--object_name",
    type=str,
)
args = parser.parse_args()

success = False
if args.task == "combine":
    success = combine(
        object_name=args.object_name,
        count=args.count,
        download=args.download == 1,
    )
else:
    success = None
sys_exit(logger, NAME, args.task, success)
