#!/bin/env python

import json
from pathlib import Path
import argparse
import logging

log = logging.getLogger(__name__)


def get_requirements_cell(requirements_path: str | Path) -> dict:
    """turns a requirements.txt into jupyter cell data"""
    with open(requirements_path, "r") as f:
        cell_data = f.readlines()
    for i, line in enumerate(cell_data):
        # Check for comments or empty lines, append !pip install to everything else
        if (len(line.strip()) == 0) or (line.strip()[0] in ["#", "\n"]):
            continue
        cell_data[i] = "!pip install " + line

    extra_lines = [
        "# This cell has been automatically inserted from build/google_colab_cell.py\n",
        "# It should make this notebook google-colab compatible!\n",
        "\n" "!pip install --upgrade pip \n",
    ]

    for i, line in enumerate(extra_lines):
        cell_data.insert(i, line)

    jupyter_cell = {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": cell_data,  # readlines' output format is the jupyter format
    }
    return jupyter_cell


def colabify_notebooks(
    input_notebook_path: str | Path,
    output_notebook_path: str | Path = None,
    requirements_path: str | Path = "requirements.txt",
) -> None:
    """Adds cell(s) to a jupyter notebook for it to work in google colab

    Parameters
    ----------
    input_notebook_path
        the notebook you want to use as a template
    output_notebook_path : optional
        the path to where you wish to save the notebook.
        If left out this will be in colab_notebooks/name_colab.ipynb
    requirements_path : optional
        the path to the requirements file to be inserted
    """
    normal_nb_path = Path(input_notebook_path)
    if output_notebook_path is None:
        output_notebook_path = Path("colab_notebooks") / (
            normal_nb_path.with_suffix("").name + "_colab.ipynb"
        )

    with open(normal_nb_path, "r") as normal_nb_f:
        notebook_json = json.load(normal_nb_f)

    colab_cell = get_requirements_cell(requirements_path)
    notebook_json["cells"].insert(0, colab_cell)

    output_notebook_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_notebook_path, "w") as colab_nb_f:
        json.dump(notebook_json, colab_nb_f, indent=1)
    return


# TODO DELME
colabify_notebooks("notebooks/2_Analysing_Patient_Data.ipynb")


def main():
    """CLI function for this script"""
    logging.basicConfig(level=logging.INFO)
    log.info("Starting CLI script")

    parser = argparse.ArgumentParser(
        prog="colabifier",
        description="Adds a cell to the top of a jupyter notebook for clab",
    )
    parser.add_argument(
        "-f",
        "--fpath",
        help="File path of a single jupyter notebook to operate on",
        default=None,
    )
    parser.add_argument(
        "-d",
        "--directory",
        help="Input Directory path of jupyter notebooks to operate on",
        default=None,
    )
    parser.add_argument(
        "-o",
        "--output_dir",
        help="Output Directory path of jupyter notebooks to operate on",
        default=None,
    )
    parser.add_argument(
        "-r",
        "--requirements",
        help="requirements file path",
        default="requirements.txt",
    )
    args = parser.parse_args()
    fpath = args.fpath
    directory = args.directory
    requirements = args.requirements
    # Sanity check
    no_inputs = (fpath is None) and (directory is None)
    too_many_inputs = (fpath is not None) and (directory is not None)
    if no_inputs or too_many_inputs:
        raise ValueError("Need only one of fpath or directory")
    log.info("CLI loaded. Starting processing")

    if fpath:
        log.info(f"Single file input {fpath}, colabifying")
        colabify_notebooks(fpath, requirements_path=requirements)
    elif directory:
        # TODO make file glob below be case insensitive
        files = list(Path(directory).glob("*.ipynb"))
        log.info(f"Directory input: {directory}, colabifying {len(files)} ipynb files")
        for file in files:
            log.info(f"Processing file {file}")
            colabify_notebooks(file, requirements_path=requirements)
    log.info("Done! Exiting")
    return


if __name__ == "__main__":
    main()
