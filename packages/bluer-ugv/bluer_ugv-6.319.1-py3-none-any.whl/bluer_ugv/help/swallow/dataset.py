from typing import List

from bluer_options.terminal import show_usage, xtra


def help_combine(
    tokens: List[str],
    mono: bool,
) -> str:
    options = xtra("count=<count>,~download,~recent,~split,upload", mono=mono)

    args = [
        "[--test_ratio 0.1]",
        "[--train_ratio 0.8]",
    ]

    return show_usage(
        [
            "@swallow",
            "dataset",
            "combine",
            f"[{options}]",
            "[-|<object-name>]",
        ]
        + args,
        "combine swallow datasets.",
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
    "combine": help_combine,
    "download": help_download,
    "edit": help_edit,
    "upload": help_upload,
}
