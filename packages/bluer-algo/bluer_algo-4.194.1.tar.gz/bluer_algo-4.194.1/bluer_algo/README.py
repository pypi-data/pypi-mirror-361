import os

from bluer_objects import file, README

from bluer_algo import NAME, VERSION, ICON, REPO_NAME


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
        )
        for readme in [
            {"items": items, "path": ".."},
            {"path": "docs/image-classifier.md"},
            {"path": "docs/image-classifier-dataset-ingest.md"},
            {"path": "docs/image-classifier-dataset-review.md"},
            {"path": "docs/image-classifier-model-train.md"},
            {"path": "docs/image-classifier-model-prediction.md"},
        ]
    )
