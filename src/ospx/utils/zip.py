import logging
import os
import re
from pathlib import Path
from shutil import copyfile
from tempfile import mkstemp
from zipfile import ZIP_DEFLATED, ZipFile

logger = logging.getLogger(__name__)


def read_file_content_from_zip(zip_file: Path, file_name: str) -> str | None:
    """Read a single file.

    Belongs to zip functions
    """
    file_handle, temp_name = mkstemp(dir=zip_file.parent)
    file_content = None
    try:
        with ZipFile(zip_file, "r") as zip_read:
            for item in zip_read.infolist():
                if re.search(file_name, item.filename):
                    file_content = str(zip_read.read(item.filename).decode("utf-8"))
                    break
    except Exception:
        logger.exception("misc.zip.read_file_content_from_zip failed")
    finally:
        os.close(file_handle)
        Path(temp_name).unlink(missing_ok=True)
    return file_content


def rename_file_in_zip(zip_file: Path, file_name: str, new_file_name: str) -> ZipFile | None:
    """Rename files.

    Belongs to zip functions.
    """
    file_handle, temp_name = mkstemp(dir=zip_file.parent)
    updated_zip_file = None
    try:
        with ZipFile(zip_file, "r") as zip_read, ZipFile(temp_name, "w") as zip_write:
            for item in zip_read.infolist():
                if item.filename != file_name:
                    data = zip_read.read(item.filename)
                else:
                    data = zip_read.read(item.filename)
                    item.filename = new_file_name
                zip_write.writestr(item, data)
        _ = copyfile(temp_name, zip_file)

        updated_zip_file = ZipFile(zip_file, mode="a")

    except Exception:
        logger.exception("misc.zip.rename_file_in_zip failed")
    finally:
        os.close(file_handle)
        Path(temp_name).unlink(missing_ok=True)

    return updated_zip_file


def remove_files_from_zip(zip_file: Path, *file_names: str) -> ZipFile | None:
    """Remove files.

    Belongs to zip functions.
    """
    file_handle, temp_name = mkstemp(dir=zip_file.parent)
    updated_zip_file = None
    try:
        with ZipFile(zip_file, "r") as zip_read, ZipFile(temp_name, "w") as zip_write:
            for item in zip_read.infolist():
                if item.filename not in file_names:
                    data = zip_read.read(item.filename)
                    zip_write.writestr(item, data)

        _ = copyfile(temp_name, zip_file)

        updated_zip_file = ZipFile(zip_file, mode="a")

    except Exception:
        logger.exception("misc.zip.remove_files_from_zip failed")

    finally:
        os.close(file_handle)
        Path(temp_name).unlink(missing_ok=True)

    return updated_zip_file


def add_file_content_to_zip(zip_file: Path, file_name: str, file_content: str) -> ZipFile | None:
    """Add a single file and its ascii content.

    Belongs to zip functions.
    """
    file_handle, temp_name = mkstemp(dir=zip_file.parent)
    updated_zip_file = None
    try:
        with ZipFile(zip_file, "a") as zip_write:
            zip_write.writestr(file_name, file_content, compress_type=ZIP_DEFLATED)

        updated_zip_file = ZipFile(zip_file, mode="a")

    except Exception:
        logger.exception("misc.zip.add_file_content_to_zip failed")
    finally:
        os.close(file_handle)
        Path(temp_name).unlink(missing_ok=True)

    return updated_zip_file


def substitute_text_in_zip(
    zip_file: Path, file_name_pattern: str = "", subst: tuple[str, str] = ("", "")
) -> ZipFile | None:
    """Substitute a given string in all files matching the passed file name pattern.

    Belongs to zip functions.
    """
    file_handle, temp_name = mkstemp(dir=zip_file.parent)
    updated_zip_file = None
    try:
        with ZipFile(zip_file, "r") as zip_read, ZipFile(temp_name, "w") as zip_write:
            zip_write.comment = zip_read.comment  # preserve the comment
            for item in zip_read.infolist():
                if not re.search(file_name_pattern, item.filename):
                    zip_write.writestr(item, zip_read.read(item.filename))
                else:
                    temp = zip_read.read(item.filename)
                    source = (re.findall(subst[0], str(temp)))[0]
                    if not str(source):
                        logger.warning(f'substitution source is empty:\'{" ".join(source)}\'')
                    temp = temp.replace(bytes(source, "utf-8"), bytes(subst[1], "utf-8"))
                    zip_write.writestr(item, temp)

        updated_zip_file = ZipFile(zip_file, mode="a")

    except Exception:
        logger.exception("misc.zip.substitute_text_in_zip failed")
    finally:
        os.close(file_handle)
        Path(temp_name).unlink(missing_ok=True)

    return updated_zip_file


def update_file_content_in_zip(zip_file: Path, file_name: str, file_content: str) -> ZipFile | None:
    """Update the ascii content of a single file.

    Belongs to zip functions.
    """
    file_handle, temp_name = mkstemp(dir=zip_file.parent)
    updated_zip_file = None
    try:
        with ZipFile(zip_file, "r") as zip_read, ZipFile(temp_name, "w") as zip_write:
            zip_write.comment = zip_read.comment  # preserve the comment
            for item in zip_read.infolist():
                if item.filename != file_name:
                    zip_write.writestr(item, zip_read.read(item.filename))

        with ZipFile(zip_file, mode="a", compression=ZIP_DEFLATED) as zf:
            # zf.writestr(contentFile, '<?xml version="1.0" encoding="UTF-8"?>\n'+data.decode('utf-8'))  # noqa: ERA001
            zf.writestr(file_name, file_content)

        updated_zip_file = ZipFile(zip_file, mode="a")

    except Exception:
        logger.exception("misc.zip.update_file_content_in_zip failed")
    finally:
        os.close(file_handle)
        Path(temp_name).unlink(missing_ok=True)

    return updated_zip_file
