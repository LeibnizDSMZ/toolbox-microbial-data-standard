from microbial_strain_data_model.microbe import Microbe
from pathlib import Path


def load_microbial_strain_data(input_file_name: str) -> Microbe:
    with Path(input_file_name).open("r") as f_in:
        return Microbe.model_validate_json(f_in.read())


def write_microbial_strain_to(microbe: Microbe, output_file_name: str) -> None:
    Microbe.model_validate(microbe)
    with Path(output_file_name).open("w") as f_out:
        f_out.write(microbe.model_dump_json(indent=2))
