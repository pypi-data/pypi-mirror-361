import os
from bluer_options.env import load_config, load_env, get_env

load_env(__name__)
load_config(__name__)


BLUER_BEAST_MODEL = get_env("BLUER_BEAST_MODEL")

BLUER_UGV_CAMERA_PERIOD = get_env("BLUER_UGV_CAMERA_PERIOD", 3)

BLUER_UGV_MOUSEPAD_ENABLED = get_env("BLUER_UGV_MOUSEPAD_ENABLED", 0)

BLUER_UGV_SWALLOW_DATASET_LIST = get_env("BLUER_UGV_SWALLOW_DATASET_LIST", "")
