import uuid
from copy import deepcopy
from microbial_strain_data_model.strain import Source, Strain

from toolbox_microbial_strain_data.util import _Source


def _fix_source_strings(obj_list: list[_Source], removed_source_id: int) -> None:
    # fix all source pointers with new_index > deleted_source_entry_index,
    # because one source got removed, by decrementing the value by 1
    for data_obj in obj_list:
        for i in range(len(data_obj.source)):
            source_id = int(data_obj.source[i].split("/")[-1])
            if source_id > removed_source_id:
                data_obj.source[i] = f"/sources/{source_id-1}"


def split_data_by_source_index(
    orig_micro: Strain, split_source_id: int
) -> tuple[Strain, Strain]:

    if split_source_id >= len(orig_micro.sources):
        raise IndexError(
            f"The source index {split_source_id} is out of range \
maximal index: {len(orig_micro.sources)-1}"
        )

    # get source pointer
    split_source_str = f"/sources/{split_source_id}"

    # define output file
    extracted_data = Strain(
        primaryId=str(uuid.uuid4()),
        organismType=deepcopy(orig_micro.organismType),
        typeStrain=deepcopy(orig_micro.typeStrain),
        taxon=deepcopy(orig_micro.taxon),
        sources=[orig_micro.sources[split_source_id]],
    )

    # iterate over full data set
    for micro_key, micro_value in orig_micro:
        if isinstance(micro_value, list) and micro_value is not orig_micro.sources:
            getattr(extracted_data, micro_key).clear()
            for data_obj in micro_value:
                # extract all data from extraction source
                if split_source_str in data_obj.source:
                    # extract data
                    new_data_obj = deepcopy(data_obj)
                    new_data_obj.source.clear()
                    new_data_obj.source.append("/sources/0")

                    # write extracted obj to output data
                    getattr(extracted_data, micro_key).append(new_data_obj)

                    # delete object if extract source is the only source
                    # else rm source_pointer from source list and update rest
                    if len(data_obj.source) == 1:
                        getattr(orig_micro, micro_key).remove(data_obj)
                    else:
                        data_obj.source.remove(split_source_str)

            _fix_source_strings(micro_value, split_source_id)

    # delete source entry
    del orig_micro.sources[split_source_id]

    return orig_micro, extracted_data


def split_data_by_source_object(
    orig_micro: Strain, split_source: Source
) -> tuple[Strain, Strain]:
    try:
        source_index = orig_micro.sources.index(split_source)
    except ValueError as err:
        err.add_note("Please ensure to use source objects directly from dataset.sources")
        raise

    return split_data_by_source_index(orig_micro, source_index)
