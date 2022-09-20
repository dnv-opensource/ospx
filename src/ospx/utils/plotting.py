import logging
import os
import re
from typing import Union
from datetime import datetime
from pathlib import Path


logger = logging.getLogger(__name__)


def create_meta_dict(title):
    # sourcery skip: inline-immediately-returned-variable
    meta_dict = {
        'Title': title,
        'Author': 'VFW',
        'Description': title,
        'Copyright': 'VFW',
        'Creation Time': str(datetime.now()),
        'Software': 'matplotlib',
        'Disclaimer': '',
        'Warning': '',
        'Source': '',
        'Comment': ''
    }
    return meta_dict


def save_figure(plt, fig, extension, path: Union[str, os.PathLike[str]], title: str, meta_dict):

    # Make sure path argument is of type Path. If not, cast it to Path type.
    path = path if isinstance(path, Path) else Path(path)

    if not os.path.exists(path):
        logger.info(f'path {path} does not exist, creating')    # 0
        path.mkdir(parents=True, exist_ok=True)

    title_in_file_name = re.sub(r'[\[\]\{\},]+', '', re.sub(r'[\(\)\:\s,]+', '_', title))

    title_string_replacements = [
        ('==', '_eq_'),
        ('!=', '_neq_'),
        ('>', '_gt_'),
        ('<', '_lt_'),
        ('>=', '_geq_'),
        ('<=', '_leq_'),
        ('+', '_plus_'),
        ('^', '_hat_'),
        ('*', '_ast_'),
        ('|', '_')
    ]
    for item in title_string_replacements:
        title_in_file_name = title_in_file_name.replace(item[0], item[1])

    if path:
        save_file = Path() / path / f'{title_in_file_name}.{extension}'
    else:
        save_file = f'{title_in_file_name}.{extension}'

    fig.savefig(
        save_file,
        orientation='landscape',
        # papertype = 'a4',
        format=extension,
        transparent=False,
        metadata=meta_dict,
    )
    plt.close(fig)

    return
