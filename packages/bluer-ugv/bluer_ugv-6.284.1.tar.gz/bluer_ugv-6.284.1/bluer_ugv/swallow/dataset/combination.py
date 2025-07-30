from typing import List
from tqdm import tqdm

from blueness import module
from bluer_options.logger import log_list
from bluer_objects import storage
from bluer_objects.metadata import get_from_object
from bluer_objects.storage.policies import DownloadPolicy

from bluer_ugv import NAME
from bluer_ugv import env
from bluer_algo.image_classifier.dataset.dataset import ImageClassifierDataset
from bluer_ugv.logger import logger

NAME = module.name(__file__, NAME)


def combine(
    object_name: str,
    count: int = -1,
    download: bool = True,
    log: bool = True,
    verbose: bool = False,
) -> bool:
    logger.info(
        "{}.combine({}{}) -> {}".format(
            NAME,
            "all" if count == -1 else f"count={count}",
            ",download" if download else "",
            object_name,
        )
    )

    list_of_dataset_object_names: List[str] = get_from_object(
        object_name=env.BLUER_UGV_SWALLOW_DATASET_LIST,
        key="dataset-list",
        default=[],
        download=download,
    )
    if count != -1:
        list_of_dataset_object_names = list_of_dataset_object_names[:count]
    log_list(
        logger,
        "combining",
        list_of_dataset_object_names,
        "dataset(s)",
        itemize=True,
    )

    if download:
        for dataset_object_name in tqdm(list_of_dataset_object_names):
            logger.info(f"downloading {dataset_object_name} ...")
            if not storage.download(
                dataset_object_name,
                policy=DownloadPolicy.DOESNT_EXIST,
                log=verbose,
            ):
                return False

    success, list_of_datasets = ImageClassifierDataset.load_list(
        list_of_dataset_object_names,
        log=log,
    )
    if not success:
        return success

    success, dataset = ImageClassifierDataset.combine(
        list_of_datasets,
        object_name=object_name,
    )
    if not success:
        return success

    return dataset.save(
        metadata={
            "contains": list_of_dataset_object_names,
        },
        log=True,
    )
