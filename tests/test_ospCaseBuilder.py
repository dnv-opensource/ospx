from ospx import OspCaseBuilder
from dictIO import DictParser
from pathlib import Path
from glob import glob


def test_build():
    # Prepare
    case_dict_file = Path('test_caseDict')
    parsed_case_dict_file = Path(f'parsed.{case_dict_file.name}')
    DictParser.parse(case_dict_file)
    # Execute
    OspCaseBuilder.build(case_dict_file=parsed_case_dict_file)
    # Assert
    # fmu files
    assert Path('constantVal.fmu').exists()
    assert Path('difference.fmu').exists()
    assert Path('quotient.fmu').exists()
    assert not Path('dividend.fmu').exists()
    assert not Path('subtrahend.fmu').exists()
    assert not Path('minuend.fmu').exists()
    # ModelDescription files-> should NOT have been written
    assert not glob('*_ModelDescription.xml')
    # OspModelDescription files
    assert Path('difference_OspModelDescription.xml').exists()
    assert Path('dividend_OspModelDescription.xml').exists()
    assert Path('minuend_OspModelDescription.xml').exists()
    assert Path('quotient_OspModelDescription.xml').exists()
    assert Path('subtrahend_OspModelDescription.xml').exists()
    assert not Path('constantVal_OspModelDescription.xml').exists()
    # SystemStructure files
    assert Path('OspSystemStructure.xml').exists()
    assert Path('SystemStructure.ssd').exists()
    # statisticsDict and watchDict
    assert Path('statisticsDict').exists()
    assert Path('watchDict').exists()


def test_inspect():
    # Prepare
    case_dict_file = Path('test_caseDict')
    parsed_case_dict_file = Path(f'parsed.{case_dict_file.name}')
    DictParser.parse(case_dict_file)
    # Execute
    OspCaseBuilder.build(case_dict_file=parsed_case_dict_file, inspect=True)
    # Assert
