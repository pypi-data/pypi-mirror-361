import copy
import pandas as pd
from typing import Dict, Tuple, List
import numpy as np

from bluer_options import string
from bluer_objects import objects, file
from bluer_objects.metadata import post_to_object
from bluer_objects.logger.image import log_image_grid
from bluer_objects.metadata import get_from_object

from bluer_algo.host import signature
from bluer_algo.logger import logger


class ImageClassifierDataset:
    def __init__(
        self,
        dict_of_classes: Dict = {},
        object_name: str = "",
    ):
        self.list_of_subsets = ["train", "test", "eval"]

        self.df = pd.DataFrame(
            columns=[
                "filename",
                "class_index",
                "subset",
            ]
        )

        self.dict_of_classes = dict_of_classes.copy()

        self.object_name = object_name

        self.shape = []

    def add(
        self,
        filename: str,
        class_index: int,
        subset: str = "train",
        log: bool = False,
    ) -> bool:
        filename = file.name_and_extension(filename)

        self.df.loc[len(self.df)] = {
            "filename": filename,
            "class_index": class_index,
            "subset": subset,
        }

        if log:
            logger.info(
                "{} += {} : {}/{}".format(
                    self.__class__.__name__,
                    filename,
                    subset,
                    self.dict_of_classes[class_index],
                )
            )

        if self.shape:
            return True

        success, image = file.load_image(
            objects.path_of(
                object_name=self.object_name,
                filename=filename,
            )
        )
        if not success:
            return False

        self.shape = list(image.shape)
        logger.info(
            "shape: {}".format(
                string.pretty_shape(self.shape),
            )
        )

        return True

    def as_str(self, what="subsets") -> str:
        count = self.count

        if what == "classes":
            return "{} class(es): {}".format(
                self.class_count,
                ", ".join(
                    [
                        "{}: {} [%{:.1f}]".format(
                            self.dict_of_classes[class_index],
                            class_count,
                            class_count / count * 100,
                        )
                        for class_index, class_count in self.dict_of_class_counts.items()
                    ]
                ),
            )

        if what == "subsets":
            return "{} subset(s): {}".format(
                len(self.list_of_subsets),
                ", ".join(
                    [
                        "{}: {} [%{:.1f}]".format(
                            subset, subset_count, subset_count / count * 100
                        )
                        for subset, subset_count in self.dict_of_subsets.items()
                    ]
                ),
            )

        return f"{what} not found."

    @property
    def class_count(self) -> int:
        return len(self.dict_of_classes)

    @property
    def count(self) -> int:
        return len(self.df)

    @property
    def dict_of_class_counts(self) -> Dict[int, int]:
        return {
            class_index: self.df[self.df["class_index"] == class_index].shape[0]
            for class_index in self.dict_of_classes.keys()
        }

    @property
    def dict_of_subsets(self) -> Dict[str, int]:
        return {
            subset_name: self.df[self.df["subset"] == subset_name].shape[0]
            for subset_name in self.list_of_subsets
        }

    @staticmethod
    def load(
        object_name: str,
        log: bool = True,
    ) -> Tuple[bool, "ImageClassifierDataset"]:
        dataset = ImageClassifierDataset(object_name=object_name)

        logger.info(
            "loading {} from {} ...".format(
                dataset.__class__.__name__,
                object_name,
            )
        )

        success, dataset.df = file.load_dataframe(
            objects.path_of(
                object_name=object_name,
                filename="metadata.csv",
            ),
            log=log,
        )
        if not success:
            return False, dataset

        metadata = get_from_object(
            object_name=object_name,
            key="dataset",
        )

        for thing in ["classes", "shape"]:
            if thing not in metadata:
                logger.error(f"{thing} not found.")
                return False, dataset

        dataset.dict_of_classes = metadata["classes"]
        dataset.shape = metadata["shape"]

        if not dataset.log_image_grid(log=log):
            return False, dataset

        logger.info(dataset.as_str("subsets"))
        logger.info(dataset.as_str("classes"))
        logger.info("shape: {}".format(string.pretty_shape(dataset.shape)))

        return True, dataset

    def log_image_grid(
        self,
        log: bool = True,
        verbose: bool = False,
    ) -> bool:
        df = self.df.copy()

        df["title"] = df.apply(
            lambda row: "#{}: {} @ {}".format(
                row["class_index"],
                self.dict_of_classes[row["class_index"]],
                row["subset"],
            ),
            axis=1,
        )

        return log_image_grid(
            df,
            objects.path_of(
                object_name=self.object_name,
                filename="grid.png",
            ),
            shuffle=True,
            header=[
                f"count: {self.count}",
                self.as_str("subsets"),
                self.as_str("classes"),
            ],
            footer=signature(),
            log=log,
            verbose=verbose,
            relative_path=True,
        )

    def sample(self, subset: str = "test") -> Tuple[bool, int, np.ndarray]:
        test_row = self.df[self.df["subset"] == subset].sample(n=1)

        success, image = file.load_image(
            objects.path_of(
                object_name=self.object_name,
                filename=test_row["filename"].values[0],
            )
        )
        if not success:
            return success, 0, np.array([])

        class_index = test_row["class_index"].values[0]
        return True, int(class_index), image

    def save(
        self,
        metadata: Dict = {},
        log: bool = True,
    ) -> bool:
        logger.info(self.as_str("subsets"))
        logger.info(self.as_str("classes"))

        metadata_ = copy.deepcopy(metadata)
        metadata_["classes"] = self.dict_of_classes
        metadata_["class_count"] = self.class_count
        metadata_["count"] = self.count
        metadata_["subsets"] = self.dict_of_subsets
        metadata_["shape"] = self.shape

        if not file.save_csv(
            objects.path_of(
                object_name=self.object_name,
                filename="metadata.csv",
            ),
            self.df,
            log=log,
        ):
            return False

        if not post_to_object(
            object_name=self.object_name,
            key="dataset",
            value=metadata_,
        ):
            return False

        if not self.log_image_grid(log=log):
            return False

        logger.info(
            "{} x {} record(s) -> {}".format(
                self.count,
                string.pretty_shape(self.shape),
                self.object_name,
            )
        )

        return True

    def signature(self) -> List[str]:
        return [
            f"{self.count} record(s)",
            self.as_str("subsets"),
            self.as_str("classes"),
            "shape: {}".format(string.pretty_shape(self.shape)),
        ]
