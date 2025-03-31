from typing import Protocol
from deepdiff import DeepDiff


class _Source(Protocol):
    source: list[str]


def get_obj_if_in(data: list[_Source], obj: _Source) -> _Source | None:
    for data_obj in data:
        if len(DeepDiff(data_obj, obj, exclude_paths=["source"])) == 0:
            return data_obj
    return None
