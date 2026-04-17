from typing import Any, Iterable, Protocol

from deepdiff import DeepHash
from microbial_strain_data_model.strain import RelatedData, Source, Strain
from microbial_strain_data_model.classes.identifier import Identifier, SourceLink
from microbial_strain_data_model.classes.organization import Organization
from microbial_strain_data_model.classes.person import Person
from microbial_strain_data_model.classes.address import Address
from pydantic import EmailStr, HttpUrl
from pydantic_extra_types.country import CountryAlpha2


class _JsonLink(Protocol):
    source: list[str]
    relatedData: list[str]  # noqa: N815


def _identifier_key(obj: list[Identifier]) -> Iterable[str | None | HttpUrl]:
    for ele in obj:
        yield ele.name
        yield ele.value
        yield ele.propertyID
        yield ele.url
        yield ele.logo


def _person_key(obj: list[Person]) -> Iterable[str | None | HttpUrl]:
    for per in obj:
        yield per.name
        yield from _identifier_key(per.identifier)


def _address_key(obj: Address) -> tuple[str | CountryAlpha2 | None, ...]:
    return (
        obj.addressCountry,
        obj.addressCountryIso,
        obj.addressRegion,
        obj.addressLocality,
        obj.postOfficeBoxNumber,
        obj.postalCode,
        obj.streetAddress,
    )


def _organization_key(
    obj: list[Organization],
) -> Iterable[str | None | HttpUrl | EmailStr | CountryAlpha2]:
    for org in obj:
        yield org.name
        yield org.legalName
        yield org.url
        yield org.email
        yield org.logo

        if org.identifier:
            yield from _identifier_key(org.identifier)
        else:
            yield None

        if org.address:
            yield from _address_key(org.address)
        else:
            yield None


def _source_key(
    obj: Source,
) -> tuple[str | None | HttpUrl | EmailStr | CountryAlpha2, ...]:
    return (
        obj.sourceType,
        obj.mode,
        obj.name,
        obj.url,
        obj.datePublished,
        obj.dateRecorded,
        obj.lastUpdate,
        *_identifier_key(obj.identifier),
        *_person_key(obj.author),
        *_organization_key(obj.publisher),
    )


def _related_data_key(obj: RelatedData) -> tuple[str | SourceLink]:
    return (obj.relation, *(src for src in obj.source))


def _merge_object_source(left_obj: _JsonLink, right_obj: _JsonLink) -> Iterable[str]:
    existing = set(left_obj.source)
    for src in right_obj.source:
        if src not in existing:
            yield src
            existing.add(src)


def _merge_object_related_data(
    left_obj: _JsonLink, right_obj: _JsonLink
) -> Iterable[str]:
    existing = set(left_obj.relatedData)
    for right_related_data in right_obj.relatedData:
        if right_related_data not in existing:
            yield right_related_data
            existing.add(right_related_data)


def _check_constrains(l_mi: Strain, r_mi: Strain) -> bool:
    """Hard constrains, add more if necessary"""

    # check if organism types are equal
    if l_mi.organismType is not r_mi.organismType:
        raise ValueError(
            f"Organism types do not match: {l_mi.organismType}" f" != {r_mi.organismType}"
        )
    return True


def _cr_ind(obj: Source | RelatedData) -> tuple[Any, ...]:
    if isinstance(obj, Source):
        return _source_key(obj)
    return _related_data_key(obj)


def _append_left_source[
    T: (Source, RelatedData)
](
    left_source_list: list[T],
    right_source_list: list[T],
    src_type: str,
    source_mapping: dict[str, str],
    /,
) -> Iterable[T]:
    left_len = len(left_source_list)

    left_index = {_cr_ind(obj): ind for ind, obj in enumerate(left_source_list)}
    new_i = 0
    for right_index, source_obj in enumerate(right_source_list):
        left_pos = left_index.get(_cr_ind(source_obj), None)
        if left_pos is not None:
            source_mapping[f"/{src_type}/{right_index}"] = f"/{src_type}/{left_pos}"
        else:
            source_mapping[f"/{src_type}/{right_index}"] = (
                f"/{src_type}/{left_len + new_i}"
            )
            new_i += 1
            yield source_obj


def _build_json_link_mapping[
    T: (Source, RelatedData)
](
    left_source_list: list[T],
    right_source_list: list[T],
    src_type: str,
) -> dict[
    str, str
]:
    """
    make a dict that has the strings of the right sources link as key, mapping
    to the new string of source link. Counting new index up if source object not
    already included in left list of sources
    """
    source_mapping: dict[str, str] = {}
    left_source_list.extend(
        _append_left_source(left_source_list, right_source_list, src_type, source_mapping)
    )
    return source_mapping


def merge_strains(left_strain: Strain, right_strain: Strain) -> Strain:
    """
    Merging two strain objects
    Step 1: Check hard constrains, e.g. organism type must be equal
    Step 2: Make source number mapping and extend source list
    Step 3: Rearrange data and fix source links with new numbers from mapping
    """

    # Step 1
    _check_constrains(left_strain, right_strain)

    # Step2
    source_map = _build_json_link_mapping(
        left_strain.sources, right_strain.sources, "sources"
    )

    # Step 3
    related_data_map = _build_json_link_mapping(
        left_strain.relatedData, right_strain.relatedData, "relatedData"
    )

    # Step 4
    # merging all lists of objects from right into left and replace source string with
    # the value in dictionary named "source_map" for the old string as key
    for key_right in Strain.model_fields.keys():
        if key_right == "sources" or key_right == "relatedData":
            continue
        attr_right = getattr(right_strain, key_right)
        if not isinstance(attr_right, list):
            continue

        attr_left = getattr(left_strain, key_right)
        deep_hash = {
            DeepHash(ele, exclude_paths=["source", "relatedData"])[ele]: ele
            for ele in attr_left
        }
        for data_obj_right in attr_right:
            data_obj_right.source = [source_map[nsr] for nsr in data_obj_right.source]

            if hasattr(data_obj_right, "relatedData"):
                data_obj_right.relatedData = [
                    related_data_map[related_data_str]
                    for related_data_str in data_obj_right.relatedData
                ]
            hash_right = DeepHash(
                data_obj_right, exclude_paths=["source", "relatedData"]
            )[data_obj_right]
            same_obj = deep_hash.get(hash_right, None)
            if same_obj:
                same_obj.source.extend(_merge_object_source(same_obj, data_obj_right))
                if hasattr(data_obj_right, "relatedData"):
                    same_obj.relatedData.extend(
                        _merge_object_related_data(same_obj, data_obj_right)
                    )
            else:
                attr_left.append(data_obj_right)
                deep_hash[hash_right] = data_obj_right

    return left_strain
