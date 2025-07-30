import argparse

from blueness import module
from blueness.argparse.generic import sys_exit

from bluer_algo import NAME
from bluer_algo.image_classifier.dataset.review import review
from bluer_algo.logger import logger

NAME = module.name(__file__, NAME)

parser = argparse.ArgumentParser(NAME)
parser.add_argument(
    "task",
    type=str,
    help="review",
)
parser.add_argument(
    "--object_name",
    type=str,
)
args = parser.parse_args()

success = False
if args.task == "review":
    success = review(object_name=args.object_name)
else:
    success = None

sys_exit(logger, NAME, args.task, success)
