import os

from bluer_options.help.functions import get_help
from bluer_objects import file, README

from bluer_ugv import NAME, VERSION, ICON, REPO_NAME
from bluer_ugv.help.functions import help_functions
from bluer_ugv.swallow.README import items as swallow_items


items = README.Items(
    [
        {
            "name": "bluer_swallow",
            "marquee": "https://github.com/kamangir/assets2/blob/main/bluer-swallow/20250701_2206342_1.gif?raw=true",
            "description": "based on power wheels.",
            "url": "./bluer_ugv/docs/bluer_swallow",
        },
        {
            "name": "bluer-fire",
            "marquee": "https://github.com/kamangir/assets/blob/main/bluer-ugv/bluer-fire.png?raw=true",
            "description": "based on a used car.",
            "url": "./bluer_ugv/docs/bluer_fire",
        },
        {
            "name": "bluer-beast",
            "marquee": "https://github.com/waveshareteam/ugv_rpi/raw/main/media/UGV-Rover-details-23.jpg",
            "description": "based on [UGV Beast PI ROS2](https://www.waveshare.com/wiki/UGV_Beast_PI_ROS2).",
            "url": "./bluer_ugv/docs/bluer_beast",
        },
    ]
)


def build():
    return all(
        README.build(
            items=readme.get("items", []),
            path=os.path.join(file.path(__file__), readme["path"]),
            cols=readme.get("cols", 3),
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
            {
                "items": items,
                "path": "..",
            },
            {"path": "docs/bluer_beast"},
            {"path": "docs/bluer_fire"},
            {
                "items": swallow_items,
                "path": "docs/bluer_swallow",
            },
            {"path": "docs/bluer_swallow/analog"},
            {"path": "docs/bluer_swallow/digital"},
            {"path": "docs/bluer_swallow/digital/parts.md"},
            {"path": "docs/bluer_swallow/digital/terraform.md"},
            {"path": "docs/bluer_swallow/digital/steering-over-current-detection.md"},
            {"path": "docs/bluer_swallow/digital/rpi-pinout.md"},
            {"path": "docs/bluer_swallow/digital/operation.md"},
            {"path": "docs/bluer_swallow/digital/dataset"},
            {"path": "docs/bluer_swallow/digital/dataset/generation.md"},
            {"path": "docs/bluer_swallow/digital/dataset/combination.md"},
            {"path": "docs/bluer_swallow/digital/dataset/review.md"},
            {"path": "docs/bluer_swallow/digital/training.md"},
            # aliases
            {"path": "docs/aliases/swallow.md"},
        ]
    )
