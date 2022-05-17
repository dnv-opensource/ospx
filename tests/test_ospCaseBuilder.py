from ospx.ospCaseBuilder import OspCaseBuilder
from dictIO.dictParser import DictParser
from pathlib import Path


def test_build():
    # Prepare
    case_dict_file = Path('test_caseDict')
    parsed_case_dict_file = Path(f'parsed.{case_dict_file.name}')
    DictParser.parse(case_dict_file)
    # Execute
    OspCaseBuilder.build(case_dict_file=parsed_case_dict_file)
    # Assert
