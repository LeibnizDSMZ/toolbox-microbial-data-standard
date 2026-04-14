from microbial_strain_data_model.strain import Source, Strain

from toolbox_microbial_strain_data.util import get_obj_if_in, _JsonLink


def _merge_object_source(left_obj: _JsonLink, right_obj: _JsonLink) -> None:
    for right_source in right_obj.source:
        if right_source not in left_obj.source:
            left_obj.source.append(right_source)


def _merge_object_related_data(left_obj: _JsonLink, right_obj: _JsonLink) -> None:
    for right_related_data in right_obj.relatedData:
        if right_related_data not in left_obj.relatedData:
            left_obj.relatedData.append(right_related_data)


def _check_constrains(l_mi: Strain, r_mi: Strain) -> bool:
    """Hard constrains, add more if necessary"""

    # check if organism types are equal
    if l_mi.organismType is not r_mi.organismType:
        raise ValueError(
            f"Organism types do not match: {l_mi.organismType}" f" != {r_mi.organismType}"
        )
    return True


def _build_json_link_mapping(
    left_source_list: list[Source],
    right_source_list: list[Source],
    type: str,
) -> dict[str, str]:
    """
    make a dict that has the strings of the right sources link as key, mapping
    to the new string of source link. Counting new index up if source object not
    already included in left list of sources
    """

    left_len = len(left_source_list)
    source_mapping = {}
    n = 0
    for source_obj in right_source_list:
        source_obj_index = right_source_list.index(source_obj)
        if source_obj in left_source_list:
            source_mapping[f"/{type}/{source_obj_index}"] = (
                f"/{type}/{left_source_list.index(source_obj)}"
            )
        else:  # not in left_strain.sources
            source_mapping[f"/{type}/{source_obj_index}"] = f"/{type}/{left_len + n}"
            n += 1
    left_source_list.extend([x for x in right_source_list if x not in left_source_list])
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
        left_strain.sources, right_strain.sources, type="sources"
    )

    # Step 3
    related_data_map = _build_json_link_mapping(
        left_strain.relatedData, right_strain.relatedData, type="relatedData"
    )

    # Step 4
    # merging all lists of objects from right into left and replace source string with
    # the value in dictionary named "source_map" for the old string as key
    for key_right, value_right in right_strain:
        if (
            isinstance(value_right, list)
            and value_right is not right_strain.sources
            and value_right is not right_strain.relatedData
        ):
            for data_obj_right in value_right:
                new_source = []
                for source_str in data_obj_right.source:
                    new_source.append(source_map[source_str])
                data_obj_right.source = new_source

                new_related_data = []

                if hasattr(data_obj_right, "relatedData"):
                    for related_data_str in data_obj_right.relatedData:
                        new_related_data.append(related_data_map[related_data_str])
                    data_obj_right.relatedData = new_related_data

                same_obj = get_obj_if_in(getattr(left_strain, key_right), data_obj_right)
                if same_obj:
                    _merge_object_source(same_obj, data_obj_right)
                    if hasattr(data_obj_right, "relatedData"):
                        _merge_object_related_data(same_obj, data_obj_right)
                else:
                    getattr(left_strain, key_right).append(data_obj_right)

    return left_strain
