import logging
import os
from pathlib import Path
from typing import Union

from dictIO import CppDict, DictReader

from ospx import Graph, OspSimulationCase


__ALL__ = ['OspCaseBuilder']

logger = logging.getLogger(__name__)


class OspCaseBuilder():
    """Builder for OSP-specific configuration files needed to run an OSP (co-)simulation case.
    """

    def __init__(self):
        return

    @staticmethod
    def build(
        case_dict_file: Union[str, os.PathLike[str]],
        inspect: bool = False,
        graph: bool = False,
        clean: bool = False,
    ):
        """Builds the OSP-specific configuration files needed to run an OSP (co-)simulation case.

        Builds following files:
            - OspSystemStructure.xml
            - SystemStructure.ssd
            - Plot.json
            - statisticsDict
            - watchDict

        Parameters
        ----------
        case_dict_file : Union[str, os.PathLike[str]]
            caseDict file. Contains all case-specific information OspCaseBuilder needs to generate the OSP files.
        inspect : bool, optional
            inspect mode. If True, build() reads all properties from the FMUs but does not actually create the OSP case files, by default False
        graph : bool, optional
            if True, creates a dependency graph image using graphviz, by default False
        clean : bool, optional
            if True, cleans up case folder and deletes any formerly created ospx files, e.g. OspSystemStructure.xml .fmu .csv etc.

        Raises
        ------
        FileNotFoundError
            if case_dict_file does not exist
        """

        # Make sure source_file argument is of type Path. If not, cast it to Path type.
        case_dict_file = case_dict_file if isinstance(case_dict_file,
                                                      Path) else Path(case_dict_file)
        if not case_dict_file.exists():
            logger.error(f"OspCaseBuilder: File {case_dict_file} not found.")
            raise FileNotFoundError(case_dict_file)

        if clean:
            case_folder: Path = case_dict_file.resolve().parent
            _clean_case_folder(case_folder)

        logger.info(f'reading {case_dict_file}')    # 0

        case_dict: CppDict = DictReader.read(case_dict_file, comments=False)

        case = OspSimulationCase(case_dict)
        try:
            case.setup()
        except Exception as e:
            logger.exception(e)
            return

        if inspect:
            # inspect and return
            case._inspect()
            return

        # case.write_osp_model_description_xmls()
        case.write_osp_system_structure_xml()
        case.write_system_structure_ssd()

        if 'postProcessing' in case_dict.keys():
            case._write_plot_config_json()

        case.write_statistics_dict()

        if graph:
            Graph.generate_dependency_graph(case)

        case.write_watch_dict()

        return


def _clean_case_folder(case_folder: Path):
    """Cleans up the case folder and deletes any existing ospx files, e.g. modelDescription.xml .fmu .csv etc.
    """
    import re
    from shutil import rmtree

    # specify all files to be deleted (or comment-in / comment-out as needed)
    case_builder_result_files = [
        '*.csv',
        '*.out',
        '*.xml',
        '*.ssd',
        '*.fmu',
        '*callGraph',
        '*.pdf',
        '*.png',                    # 'protect results/*.png'
        'watchDict',
        'statisticsDict',           # 'results',
        'zip',
    ]
    except_list = ['src', '^test_', '_OspModelDescription.xml']
    except_pattern = '(' + '|'.join(except_list) + ')'

    logger.info(f'Clean OSP simulation case folder: {case_folder}')

    for pattern in case_builder_result_files:
        files = list(case_folder.rglob(pattern))

        for file in files:
            if not re.search(except_pattern, str(file)):
                # logger.info("%s in list to clean" % file)
                if file.is_file():
                    # logger.info("file %s cleaned" % file)
                    file.unlink(missing_ok=True)
                else:
                    # logger.info("dir %s removed" % file)
                    rmtree(file)
    return
