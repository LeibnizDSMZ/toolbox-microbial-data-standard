from typing import Protocol
from deepdiff import DeepDiff


class _JsonLink(Protocol):
    source: list[str]
    relatedData: list[str]  # noqa: N815


def get_obj_if_in(data: list[_JsonLink], obj: _JsonLink) -> _JsonLink | None:
    for data_obj in data:
        if len(DeepDiff(data_obj, obj, exclude_paths=["source", "relatedData"])) == 0:
            return data_obj
    return None
