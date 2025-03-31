from toolbox_microbial_strain_data.io_functions import load_microbial_strain_data


def test_read_file() -> None:
    micro = load_microbial_strain_data("./tests/test_files/merge_test_a.json")
    assert micro.organismType == "Bacteria"
