from typing import List

from bluer_options.timer import Timer
from bluer_options import string
from bluer_options import host
from bluer_objects.metadata import post_to_object, get_from_object
from bluer_algo.image_classifier.dataset.dataset import ImageClassifierDataset
from bluer_sbc.imager.camera import instance as camera

from bluer_ugv.swallow.session.classical.keyboard import ClassicalKeyboard
from bluer_ugv.swallow.session.classical.leds import ClassicalLeds
from bluer_ugv import env
from bluer_ugv.logger import logger


class ClassicalCamera:
    def __init__(
        self,
        keyboard: ClassicalKeyboard,
        leds: ClassicalLeds,
        object_name: str,
    ):
        self.timer = Timer(
            period=env.BLUER_UGV_CAMERA_PERIOD,
            name=self.__class__.__name__,
        )

        self.keyboard = keyboard
        self.leds = leds

        self.object_name = object_name

        self.dict_of_classes = {
            0: "no_action",
            1: "left",
            2: "right",
        }

        self.dataset = ImageClassifierDataset(
            dict_of_classes=self.dict_of_classes,
            object_name=self.object_name,
        )

        logger.info(
            "{}: period={}".format(
                self.__class__.__name__,
                string.pretty_duration(env.BLUER_UGV_CAMERA_PERIOD),
            )
        )

    def initialize(self) -> bool:
        return camera.open(log=True)

    def cleanup(self):
        camera.close(log=True)

        self.dataset.save(
            metadata={
                "source": host.get_name(),
            },
            log=True,
        )

        dataset_list: List[str] = get_from_object(
            object_name=env.BLUER_UGV_SWALLOW_DATASET_LIST,
            key="dataset-list",
            default=[],
            download=True,
        )
        dataset_list.append(self.object_name)
        if not post_to_object(
            object_name=env.BLUER_UGV_SWALLOW_DATASET_LIST,
            key="dataset-list",
            value=dataset_list,
            upload=True,
            verbose=True,
        ):
            logger.error("failed to add object to dataset list.")

    def update(self) -> bool:
        if not self.keyboard.train_mode:
            return True
        if not any(
            [
                self.timer.tick(),
                self.keyboard.last_key != "",
            ]
        ):
            return True

        self.leds.leds["red"]["state"] = not self.leds.leds["red"]["state"]

        filename = "{}.png".format(
            string.pretty_date(
                as_filename=True,
                unique=True,
            )
        )

        success, _ = camera.capture(
            close_after=False,
            open_before=False,
            object_name=self.object_name,
            filename=filename,
            log=True,
        )
        if not success:
            return success

        logger.info(f"self.keyboard.last_key: {self.keyboard.last_key}")

        if not self.dataset.add(
            filename=filename,
            class_index=(
                0
                if self.keyboard.last_key == ""
                else 1 if self.keyboard.last_key == "a" else 2
            ),
            log=True,
        ):
            return False

        self.timer.reset()

        return True
