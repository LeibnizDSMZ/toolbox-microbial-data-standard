import pytest

from microbial_strain_data_model.classes.actors import Organization
from microbial_strain_data_model.microbe import Microbe

from toolbox_microbial_strain_data import split
from toolbox_microbial_strain_data.io_functions import (
    load_microbial_strain_data,
)


@pytest.fixture
def micro() -> Microbe:
    data = load_microbial_strain_data("./tests/test_files/split_test.json")
    return data


def test_integration_split_object(micro: Microbe) -> None:
    source_dict = {"name": "B", "legalName": "BBBBBBB"}
    extract_source = Organization.model_validate(source_dict)

    micro_purged, micro_extracted = split.split_data_by_source_object(
        micro, extract_source
    )

    assert Microbe.model_validate(micro_purged)
    assert Microbe.model_validate(micro_extracted)

    assert extract_source not in micro_purged.sources
    assert extract_source in micro_extracted.sources

    assert len(micro_purged.sources) == 2
    assert len(micro_extracted.sources) == 1

    assert "/sources/2" not in str(micro_purged.model_dump_json())

    assert "/sources/1" not in str(micro_extracted.model_dump_json())
    assert "/sources/2" not in str(micro_extracted.model_dump_json())


def test_integration_split_object_error(micro: Microbe) -> None:
    org = Organization.model_validate({"legalName": "ZZZZZ", "name": "Z"})
    with pytest.raises(ValueError, match=r"Organization\(name='Z'.*"):
        split.split_data_by_source_object(micro, org)


def test_integration_split_index(micro: Microbe) -> None:
    source_dict = {"name": "B", "legalName": "BBBBBBB"}
    extract_source = Organization.model_validate(source_dict)

    micro_purged, micro_extracted = split.split_data_by_source_index(micro, 1)

    assert Microbe.model_validate(micro_purged)
    assert Microbe.model_validate(micro_extracted)

    assert extract_source not in micro_purged.sources
    assert extract_source in micro_extracted.sources

    assert len(micro_purged.sources) == 2
    assert len(micro_extracted.sources) == 1

    assert "/sources/2" not in str(micro_purged.model_dump_json())

    assert "/sources/1" not in str(micro_extracted.model_dump_json())
    assert "/sources/2" not in str(micro_extracted.model_dump_json())


def test_integration_split_index_error(micro: Microbe) -> None:

    with pytest.raises(
        IndexError, match=r"The source index 3 is out of range maximal index: 2"
    ):
        split.split_data_by_source_index(micro, 3)
