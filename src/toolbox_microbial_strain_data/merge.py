from microbial_strain_data_model.strain import Source, Strain

from toolbox_microbial_strain_data.util import get_obj_if_in, _Source


def _merge_object_source(left_obj: _Source, right_obj: _Source) -> None:
    for right_source in right_obj.source:
        if right_source not in left_obj.source:
            left_obj.source.append(right_source)


def _check_constrains(l_mi: Strain, r_mi: Strain) -> bool:
    """Hard constrains, add more if necessary"""

    # check if organism types are equal
    if l_mi.organismType is not r_mi.organismType:
        raise ValueError(
            f"Organism types do not match: {l_mi.organismType}" f" != {r_mi.organismType}"
        )
    return True


def _build_source_mapping(
    left_source_list: list[Source],
    right_source_list: list[Source],
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
            source_mapping[f"/sources/{source_obj_index}"] = (
                f"/sources/{left_source_list.index(source_obj)}"
            )
        else:  # not in left_microbe.sources
            source_mapping[f"/sources/{source_obj_index}"] = f"/sources/{left_len + n}"
            n += 1
    left_source_list.extend([x for x in right_source_list if x not in left_source_list])
    return source_mapping


def merge_microbes(left_microbe: Strain, right_microbe: Strain) -> Strain:
    """
    Merging two microbe objects
    Step 1: Check hard constrains, e.g. organism type must be equal
    Step 2: Make source number mapping and extend source list
    Step 3: Rearrange data and fix source links with new numbers from mapping
    """

    # Step 1
    _check_constrains(left_microbe, right_microbe)

    # Step2
    source_map = _build_source_mapping(left_microbe.sources, right_microbe.sources)

    # Step 3
    # merging all lists of objects from right into left and replace source string with
    # the value in dictionary named "source_map" for the old string as key
    for key_right, value_right in right_microbe:
        if isinstance(value_right, list) and value_right is not right_microbe.sources:
            for data_obj_right in value_right:
                new_source = []
                for source_str in data_obj_right.source:
                    new_source.append(source_map[source_str])
                data_obj_right.source = new_source

                same_obj = get_obj_if_in(getattr(left_microbe, key_right), data_obj_right)
                if same_obj:
                    _merge_object_source(same_obj, data_obj_right)
                else:
                    getattr(left_microbe, key_right).append(data_obj_right)

    return left_microbe
