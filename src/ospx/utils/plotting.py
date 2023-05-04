# pyright: reportUnnecessaryTypeIgnoreComment=false
import logging
import os
import re
from datetime import datetime as datetime
from pathlib import Path
from typing import Dict, MutableMapping, Union

import matplotlib.pyplot as plt
from matplotlib.figure import Figure

logger = logging.getLogger(__name__)


def create_meta_dict(title: str) -> Dict[str, str]:
    """Create a default of meta dict which can be passed to save_figure().

    Parameters
    ----------
    title : str
        the title of the figure

    Returns
    -------
    Dict[str, str]
        the meta dict
    """
    meta_dict = {
        "Title": title,
        "Author": "VFW",
        "Description": title,
        "Copyright": "VFW",
        "Creation Time": str(datetime.now()),
        "Software": "matplotlib",
        "Disclaimer": "",
        "Warning": "",
        "Source": "",
        "Comment": "",
    }
    return meta_dict


def save_figure(
    fig: Figure,  # type: ignore
    extension: str,
    path: Union[str, os.PathLike[str]],
    title: str,
    meta_dict: MutableMapping[str, str],
):
    """Save a figure object as image file.

    Parameters
    ----------
    fig : Figure
        the Matplotlib figure object
    extension : str
        the file extension. Determines the file format.
    path : Union[str, os.PathLike[str]]
        the folder to save the file in
    title : str
        image title. Will also be used as file name.
    meta_dict : MutableMapping[str, str]
        a dict with additional meta properties. Will be passed as-is to figure.savefig()
    """

    # Make sure path argument is of type Path. If not, cast it to Path type.
    path = path if isinstance(path, Path) else Path(path)

    if not os.path.exists(path):
        logger.info(f"path {path} does not exist, creating")  # 0
        path.mkdir(parents=True, exist_ok=True)

    title_in_file_name = re.sub(r"[\[\]\{\},]+", "", re.sub(r"[\(\)\:\s,]+", "_", title))

    title_string_replacements = [
        ("==", "_eq_"),
        ("!=", "_neq_"),
        (">", "_gt_"),
        ("<", "_lt_"),
        (">=", "_geq_"),
        ("<=", "_leq_"),
        ("+", "_plus_"),
        ("^", "_hat_"),
        ("*", "_ast_"),
        ("|", "_"),
    ]
    for item in title_string_replacements:
        title_in_file_name = title_in_file_name.replace(item[0], item[1])

    # limit overall length to 128 characters
    if len(title_in_file_name) >= 80:
        title_in_file_name = "".join(list(title_in_file_name[:59]) + [".", "."] + list(title_in_file_name[-19:]))

    save_file: str
    if path:
        save_file = str(path / f"{title_in_file_name}.{extension}")
    else:
        save_file = f"{title_in_file_name}.{extension}"

    fig.savefig(  # type: ignore
        save_file,
        orientation="landscape",
        # papertype = 'a4',
        format=extension,
        transparent=False,
        metadata=meta_dict,
    )
    plt.close(fig)  # type: ignore

    return
