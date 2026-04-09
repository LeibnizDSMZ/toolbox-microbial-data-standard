from microbial_strain_data_model.strain import Strain
from pathlib import Path


def load_microbial_strain_data(input_file_name: str) -> Strain:
    with Path(input_file_name).open("r") as f_in:
        return Strain.model_validate_json(f_in.read())


def write_microbial_strain_to(strain: Strain, output_file_name: str) -> None:
    Strain.model_validate(strain)
    with Path(output_file_name).open("w") as f_out:
        f_out.write(strain.model_dump_json(indent=2))
