from typing import Unpack

import loguru

from liblaf.grapes.logging.filters import make_filter


def jsonl_handler(
    **kwargs: Unpack["loguru.FileHandlerConfig"],
) -> "loguru.FileHandlerConfig":
    kwargs["filter"] = make_filter(kwargs.get("filter"))
    kwargs.setdefault("serialize", True)
    kwargs.setdefault("mode", "w")
    return kwargs
