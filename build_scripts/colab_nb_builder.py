#!/bin/env python
# A specific script to be run only in this repository

import json
from pathlib import Path
import logging
import shutil
import textwrap
import argparse

log = logging.getLogger(__name__)


def get_requirements_cell(requirements_path: str | Path) -> dict:
    """turns a requirements.txt into jupyter cell data"""
    with open(requirements_path, "r") as f:
        cell_data = f.readlines()
    for i, line in enumerate(cell_data):
        # Check for comments or empty lines, append !pip install to everything else
        if (len(line.strip()) == 0) or (line.strip()[0] in ["#", "\n"]):
            continue
        cell_data[i] = "!pip install -q " + line

    extra_lines = [
        "# This cell has been automatically inserted from build_scripts/colab_nb_builder.py\n",
        "# It should make this notebook google-colab compatible!\n",
        "\n" "!pip install -q --upgrade pip \n",
    ]

    for i, line in enumerate(extra_lines):
        cell_data.insert(i, line)
    cell_data.append("\n!echo All done! Test below if it works.")

    jupyter_cell = {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": cell_data,  # readlines' output format is the jupyter format
    }
    return jupyter_cell


def get_colab_cell_from_file(cell_name: str | Path, cell_type="code") -> dict:
    """Gets a colab cell from a file

    Parameters
    ----------
    cell_name
        filename to load in as a cell
    cell_type
        Type of cell, ie "code" or "markdown"
    """
    with open(Path(cell_name), "r") as f:
        colab_mkdown_cell = f.readlines()

    jupyter_cell = {
        "cell_type": cell_type,
        "metadata": {},
        "source": colab_mkdown_cell,  # readlines' output format is the jupyter format
    }
    # Extra metadata needed by 'code' type cells that cant be in markdown cells
    if cell_type == "code":
        jupyter_cell["execution_count"] = None
        jupyter_cell["outputs"] = []

    return jupyter_cell


def colabify_notebooks(
    input_notebook_path: str | Path,
    output_notebook_path: str | Path = None,
    requirements_path: str | Path = "requirements.txt",
    colab_cell_path: str | Path = "build_scripts/colab_cells",
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
    colab_cell_path : optional
        the path to where colab cell files are
    """
    normal_nb_path = Path(input_notebook_path)
    if output_notebook_path is None:
        output_notebook_path = Path("colab_notebooks") / (
            normal_nb_path.with_suffix("").name + "_colab.ipynb"
        )

    with open(normal_nb_path, "r") as normal_nb_f:
        notebook_json = json.load(normal_nb_f)

    req_colab_cell = get_requirements_cell(requirements_path)
    cell_files_to_load = [
        ["info_mkd_cell.txt", "markdown"],
        ["grab_data_cell.txt", "code"],
    ]
    cell_fpaths_to_load = [
        [Path(colab_cell_path) / cell_info[0], cell_info[1]] for cell_info in cell_files_to_load
    ]
    other_cells = [
        get_colab_cell_from_file(cell_name=cell_info[0], cell_type=cell_info[1])
        for cell_info in cell_fpaths_to_load
    ]

    notebook_json["cells"].insert(0, req_colab_cell)
    # iterate backwards to insert them in the correct order
    for cell in other_cells[::-1]:
        notebook_json["cells"].insert(0, cell)

    output_notebook_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_notebook_path, "w") as colab_nb_f:
        json.dump(notebook_json, colab_nb_f, indent=1)
    return


def main() -> None:
    """CLI function for this script.

    Notes
    -----
    Run this script from the main directory (ie using `python build_scripts/script_name.py`)
    """
    logging.basicConfig(level=logging.INFO)
    log.info("Starting script")

    parser = argparse.ArgumentParser(
        prog="colabifier",
        description="Adds cells to the top of a jupyter notebook for clab",
    )

    parser.add_argument(
        "-d",
        "--directory",
        help="Input Directory path of jupyter notebooks to operate on",
        default="notebooks",
    )
    parser.add_argument(
        "-o",
        "--output_dir",
        help="Output Directory path of jupyter notebooks to operate on",
        default="notebooks_colab",
    )
    parser.add_argument(
        "-r",
        "--requirements",
        help="requirements file path",
        default="requirements.txt",
    )
    args = parser.parse_args()
    notebooks_fpath = Path(args.directory)
    colab_notebooks_fpath = Path(args.output_dir)
    requirements = args.requirements

    nbs = list(notebooks_fpath.glob("*.ipynb"))
    # Filter notebooks to remove ones that cant have/dont need changes
    nbs_to_convert = [nb for nb in nbs if (nb.name[:2] not in ["00", "01"])]
    # Filter notebooks for ones that need to be copied
    nbs_to_copy = [nb for nb in nbs if (nb.name[:2] in ["01"])]

    log.info(f"Notebooks to copy: {len(nbs_to_copy)}, notebooks to convert: {len(nbs_to_convert)}")
    for old_fpath in nbs_to_copy:
        old_fpath.parent.mkdir(parents=True, exist_ok=True)
        new_fpath = colab_notebooks_fpath / (old_fpath.stem + "_colab.ipynb")
        log.info(f"Copying {old_fpath} to {new_fpath}")
        shutil.copy(old_fpath, new_fpath)

    for old_fpath in nbs_to_convert:
        old_fpath.parent.mkdir(parents=True, exist_ok=True)
        new_fpath = colab_notebooks_fpath / (old_fpath.stem + "_colab.ipynb")
        log.info(f"Colabifying {old_fpath} at {new_fpath}")
        colabify_notebooks(
            old_fpath,
            requirements_path=requirements,
            output_notebook_path=new_fpath,
        )
    log.info("Done! Exiting")
    return


if __name__ == "__main__":
    main()
