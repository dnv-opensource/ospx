import os
import re
from tempfile import mkstemp
from zipfile import ZipFile, ZIP_DEFLATED
from pathlib import Path
from typing import Sequence, Union
import logging

from shutil import copyfile

logger = logging.getLogger(__name__)


def read_file_content_from_zip(zip_file: Path, file_name: str) -> Union[str, None]:
    '''
    belongs to zip functions
    read a single file
    '''
    file_handle, temp_name = mkstemp(dir=zip_file.parent)
    file_content = None
    try:
        with ZipFile(zip_file, 'r') as zip_read:
            for item in zip_read.infolist():
                if re.search(file_name, item.filename):
                    file_content = str(zip_read.read(item.filename).decode('utf-8'))
                    break
    except Exception:
        logger.exception('misc.zip.read_file_content_from_zip failed')
    finally:
        os.close(file_handle)
        os.remove(temp_name)
    return file_content


def rename_file_in_zip(zip_file: Path, file_name: str, new_file_name: str) -> Union[ZipFile, None]:
    '''
    belongs to zip functions
    rename files
    '''
    file_handle, temp_name = mkstemp(dir=zip_file.parent)
    updated_zip_file = None
    try:
        with ZipFile(zip_file, 'r') as zip_read:
            with ZipFile(temp_name, 'w') as zip_write:
                for item in zip_read.infolist():
                    if item.filename != file_name:
                        data = zip_read.read(item.filename)
                    else:
                        data = zip_read.read(item.filename)
                        item.filename = new_file_name
                    zip_write.writestr(item, data)
        copyfile(temp_name, zip_file)

        updated_zip_file = ZipFile(zip_file, mode='a')

    except Exception:
        logger.exception('misc.zip.rename_file_in_zip failed')
    finally:
        os.close(file_handle)
        os.remove(temp_name)

    return updated_zip_file


def remove_files_from_zip(zip_file: Path, *file_names: str) -> Union[ZipFile, None]:
    '''
    belongs to zip functions
    remove files
    '''
    file_handle, temp_name = mkstemp(dir=zip_file.parent)
    updated_zip_file = None
    try:
        with ZipFile(zip_file, 'r') as zip_read:
            with ZipFile(temp_name, 'w') as zip_write:
                for item in zip_read.infolist():
                    if item.filename not in file_names:
                        data = zip_read.read(item.filename)
                        zip_write.writestr(item, data)

        copyfile(temp_name, zip_file)

        updated_zip_file = ZipFile(zip_file, mode='a')

    except Exception:
        logger.exception('misc.zip.remove_files_from_zip failed')

    finally:
        os.close(file_handle)
        os.remove(temp_name)

    return updated_zip_file


def add_file_content_to_zip(zip_file: Path, file_name: str, file_content: str) -> Union[ZipFile, None]:
    '''
    belongs to zip functions
    does add a single file and its ascii content
    '''
    file_handle, temp_name = mkstemp(dir=zip_file.parent)
    updated_zip_file = None
    try:
        with ZipFile(zip_file, 'a') as zip_write:
            zip_write.writestr(file_name, file_content, compress_type=ZIP_DEFLATED)

        updated_zip_file = ZipFile(zip_file, mode='a')

    except Exception:
        logger.exception('misc.zip.add_file_content_to_zip failed')
    finally:
        os.close(file_handle)
        os.remove(temp_name)

    return updated_zip_file


def substitute_text_in_zip(zip_file: Path, file_name_pattern: str = '', subst: Sequence[str] = ('', '')) -> Union[ZipFile, None]:

    file_handle, temp_name = mkstemp(dir=zip_file.parent)
    updated_zip_file = None
    try:
        with ZipFile(zip_file, 'r') as zip_read:
            with ZipFile(temp_name, 'w') as zip_write:
                zip_write.comment = zip_read.comment  # preserve the comment
                for item in zip_read.infolist():

                    if not re.search(file_name_pattern, item.filename):
                        zip_write.writestr(item, zip_read.read(item.filename))
                    else:
                        temp = zip_read.read(item.filename)
                        source = (re.findall(subst[0], str(temp)))[0]
                        if len(str(source)) == 0:
                            logger.warning(f'substitution source is empty:\'{" ".join(source)}\'')
                        temp = temp.replace(bytes(source, 'utf-8'), bytes(subst[1], 'utf-8'))
                        zip_write.writestr(item, temp)

        updated_zip_file = ZipFile(zip_file, mode='a')

    except Exception:
        logger.exception('misc.zip.substitute_text_in_zip failed')
    finally:
        os.close(file_handle)
        os.remove(temp_name)

    return updated_zip_file


def update_file_content_in_zip(zip_file: Path, file_name: str, file_content: str) -> Union[ZipFile, None]:

    file_handle, temp_name = mkstemp(dir=zip_file.parent)
    updated_zip_file = None
    try:
        with ZipFile(zip_file, 'r') as zip_read:
            with ZipFile(temp_name, 'w') as zip_write:
                zip_write.comment = zip_read.comment  # preserve the comment
                for item in zip_read.infolist():
                    if item.filename != file_name:
                        zip_write.writestr(item, zip_read.read(item.filename))

        with ZipFile(zip_file, mode='a', compression=ZIP_DEFLATED) as zf:
            # zf.writestr(contentFile, '<?xml version="1.0" encoding="UTF-8"?>\n'+data.decode('utf-8'))
            zf.writestr(file_name, file_content)

        updated_zip_file = ZipFile(zip_file, mode='a')

    except Exception:
        logger.exception('misc.zip.update_file_content_in_zip failed')
    finally:
        os.close(file_handle)
        os.remove(temp_name)

    return updated_zip_file
