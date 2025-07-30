import os

from bluer_options.help.functions import get_help
from bluer_objects import file, README

from bluer_algo import NAME, VERSION, ICON, REPO_NAME
from bluer_algo.help.functions import help_functions


items = README.Items(
    [
        {
            "name": "image classifier",
            "marquee": "https://github.com/kamangir/assets/raw/main/fruits-365-2025-06-27-97buak/grid.png?raw=true",
            "description": "an image classifier.",
            "url": "./bluer_algo/docs/image-classifier.md",
        }
    ]
)


def build():
    return all(
        README.build(
            items=readme.get("items", []),
            path=os.path.join(file.path(__file__), readme["path"]),
            ICON=ICON,
            NAME=NAME,
            VERSION=VERSION,
            REPO_NAME=REPO_NAME,
            help_function=lambda tokens: get_help(
                tokens,
                help_functions,
                mono=True,
            ),
        )
        for readme in [
            {"items": items, "path": ".."},
            {"path": "docs/image-classifier.md"},
            {"path": "docs/image-classifier-dataset-ingest.md"},
            {"path": "docs/image-classifier-dataset-review.md"},
            {"path": "docs/image-classifier-dataset-sequence.md"},
            {"path": "docs/image-classifier-model-train.md"},
            {"path": "docs/image-classifier-model-prediction.md"},
            # aliases
            {"path": "docs/aliases/image_classifier.md"},
        ]
    )
