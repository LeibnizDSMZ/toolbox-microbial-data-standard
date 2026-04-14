import pytest

from toolbox_microbial_strain_data import merge
from toolbox_microbial_strain_data.io_functions import (
    load_microbial_strain_data,
)

from microbial_strain_data_model.classes.source import Source, SourceType, CurationMode


def test_integration_merge() -> None:
    micro_left = load_microbial_strain_data("./tests/test_files/merge_test_a.json")
    assert len(micro_left.sources) == 2
    assert len(micro_left.relatedData) == 2
    micro_right = load_microbial_strain_data("./tests/test_files/merge_test_b.json")
    assert len(micro_right.sources) == 2
    assert len(micro_right.relatedData) == 2
    mm = merge.merge_strains(micro_left, micro_right)
    assert len(mm.sources) == 3
    assert len(mm.relatedData) == 3


def test_unit_build_source_mapping() -> None:
    list_a = [
        Source(
            sourceType=SourceType("literature"),
            mode=CurationMode("automated"),
            name="A literature",
        ),
        Source(
            sourceType=SourceType("website"),
            mode=CurationMode("automated"),
            name="A Person",
        ),
        Source(
            sourceType=SourceType("dataset"),
            mode=CurationMode("automated"),
            name="A Organisation",
        ),
    ]
    list_b = [
        Source(
            sourceType=SourceType("literature"),
            mode=CurationMode("automated"),
            name="B literature",
        ),
        Source(
            sourceType=SourceType("website"),
            mode=CurationMode("automated"),
            name="A Person",
        ),
        Source(
            sourceType=SourceType("dataset"),
            mode=CurationMode("automated"),
            name="B Organisation",
        ),
    ]

    # mapping includes for str from list_b the new strings for merged result
    mapping = merge._build_json_link_mapping(list_a, list_b, type="sources")

    assert isinstance(mapping, dict)
    assert len(mapping.keys()) == 3
    assert mapping["/sources/0"] == "/sources/3"  # first element list_b
    assert mapping["/sources/1"] == "/sources/1"  # second element list_b
    assert mapping["/sources/2"] == "/sources/4"  # third element list_b


def test_unit_check_constrains() -> None:
    micro_left = load_microbial_strain_data("./tests/test_files/merge_test_a.json")
    assert len(micro_left.sources) == 2
    micro_right = load_microbial_strain_data("./tests/test_files/merge_test_b.json")
    assert len(micro_right.sources) == 2
    assert merge._check_constrains(micro_left, micro_right)


def test_value_error() -> None:
    micro_left = load_microbial_strain_data("./tests/test_files/merge_test_a.json")
    micro_fungi = load_microbial_strain_data("./tests/test_files/minimal_fungi.json")
    with pytest.raises(ValueError, match=r".*"):
        merge._check_constrains(micro_left, micro_fungi)
