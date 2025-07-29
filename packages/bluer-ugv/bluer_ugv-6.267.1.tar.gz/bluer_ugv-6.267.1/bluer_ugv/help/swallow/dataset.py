from typing import List

from bluer_options.terminal import show_usage, xtra


def help_collect(
    tokens: List[str],
    mono: bool,
) -> str:
    options = xtra("count=<count>,~download,update_metadata,upload", mono=mono)

    return show_usage(
        [
            "@swallow",
            "dataset",
            "collect",
            f"[{options}]",
            "[-|<object-name>]",
        ],
        "collect the swallow dataset.",
        mono=mono,
    )


def help_download(
    tokens: List[str],
    mono: bool,
) -> str:
    options = xtra("~metadata", mono=mono)

    return show_usage(
        [
            "@swallow",
            "dataset",
            "download",
            f"[{options}]",
        ],
        "download the swallow dataset.",
        mono=mono,
    )


def help_edit(
    tokens: List[str],
    mono: bool,
) -> str:
    options = xtra("~download", mono=mono)

    return show_usage(
        [
            "@swallow",
            "dataset",
            "edit",
            f"[{options}]",
        ],
        "edit the swallow dataset.",
        mono=mono,
    )


def help_upload(
    tokens: List[str],
    mono: bool,
) -> str:
    options = xtra("~metadata", mono=mono)

    return show_usage(
        [
            "@swallow",
            "dataset",
            "upload",
            f"[{options}]",
        ],
        "upload the swallow dataset.",
        mono=mono,
    )


help_functions = {
    "collect": help_collect,
    "download": help_download,
    "edit": help_edit,
    "upload": help_upload,
}
