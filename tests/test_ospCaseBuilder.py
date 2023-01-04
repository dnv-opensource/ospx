from pathlib import Path

from dictIO import DictParser

from ospx import OspCaseBuilder


def test_build():
    # sourcery skip: extract-duplicate-method
    # Prepare
    case_dict_file = Path("test_caseDict_simple")
    parsed_case_dict_file = Path(f"parsed.{case_dict_file.name}")
    _ = DictParser.parse(case_dict_file)
    # Execute
    OspCaseBuilder.build(case_dict_file=parsed_case_dict_file)
    # Assert
    # fmu files
    assert not Path("constantVal.fmu").exists()
    assert not Path("difference.fmu").exists()
    assert not Path("quotient.fmu").exists()
    assert not Path("dividend.fmu").exists()
    assert not Path("subtrahend.fmu").exists()
    assert not Path("minuend.fmu").exists()
    # ModelDescription files-> should NOT have been written
    assert not Path("constantVal_ModelDescription.xml").exists()
    assert not Path("difference_ModelDescription.xml").exists()
    assert not Path("quotient_ModelDescription.xml").exists()
    assert not Path("dividend_ModelDescription.xml").exists()
    assert not Path("subtrahend_ModelDescription.xml").exists()
    assert not Path("minuend_ModelDescription.xml").exists()
    # OspModelDescription files
    assert not Path("constantVal_OspModelDescription.xml").exists()
    assert not Path("difference_OspModelDescription.xml").exists()
    assert not Path("quotient_OspModelDescription.xml").exists()
    assert not Path("dividend_OspModelDescription.xml").exists()
    assert not Path("subtrahend_OspModelDescription.xml").exists()
    assert not Path("minuend_OspModelDescription.xml").exists()
    # SystemStructure files
    assert Path("OspSystemStructure.xml").exists()
    assert Path("SystemStructure.ssd").exists()
    # statisticsDict and watchDict
    assert Path("statisticsDict").exists()
    assert Path("watchDict").exists()


def test_inspect():
    # Prepare
    case_dict_file = Path("test_caseDict")
    parsed_case_dict_file = Path(f"parsed.{case_dict_file.name}")
    _ = DictParser.parse(case_dict_file)
    # Execute
    OspCaseBuilder.build(case_dict_file=parsed_case_dict_file, inspect=True)
    # Assert
