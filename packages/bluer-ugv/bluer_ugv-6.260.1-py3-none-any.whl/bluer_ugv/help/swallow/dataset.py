from typing import List

from bluer_options.terminal import show_usage, xtra


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
        "download swallow dataset.",
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
        "edit swallow dataset.",
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
        "upload swallow dataset.",
        mono=mono,
    )


help_functions = {
    "download": help_download,
    "edit": help_edit,
    "upload": help_upload,
}
