# Changelog

All notable changes to the [ospx] project will be documented in this file.<br>
The changelog format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [Unreleased]

* --


## [0.2.5] - 2022-12-01

### Changed

* variable.py: get_fmi_data_type():
    * Removed the elif branch 'isinstance(arg, Sequence)'. <br>
      It caused problems as it falsely returned the FMI type 'Enumeration' also for strings. <br>
      The respective elif branch is for the time being commented out. <br>
      However, a proper solution is needed as soon as xs:enumeration is used in an OSP case. <br>
      The problem is registered as [Issue #5](https://github.com/dnv-opensource/ospx/issues/5)
* Code formatting: Changed from yapf to black
* STYLEGUIDE.md : Adjusted to match black formatting
* VS Code settings: Updated to use black as formatter
* requirements.txt: Updated dependencies to their most recent versions
* GitHub actions (yml files): Updated following actions to their most recent versions:
    * checkout@v1 -> checkout@v3
    * setup-python@v2 -> setup-python@v4
    * cache@v2 -> cache@v3

### Added

* watchCosim: Added commandline option --scale <br>
    (allows to scale the generated images by a factor)
* Added sourcery configuration (.sourcery.yaml)
* Added py.typed file into the package root folder and included it setup.cfg as package_data


## [0.2.4] - 2022-11-08

### Changed

* Renamed module systemStructure.py to system.py <br>
  Accordingly, renamed also class SystemStructure to System.

* Renamed some attributes in FMU class

* dependencies:
    * upgraded to dictIO >= 0.2.2  (now supporting references and expressions in JSON dicts)

### Added

* \tests: Added spring_mass_damper example

* \tests: Added test_fmu.py

### Solved

* watchCosim.py : Added try-except statements to catch TypeErrors and ValueErrors when trying to plot non-numerical variables (i.e. String or None)



## [0.2.3] - 2022-10-05

### Solved

* Importer:<br>
    * Corrected a bug in OspSystemStructureImporter, where multiple connections between two components would not be imported (but only the last one survived). Now, also more than one connection in between two components are imported correctly.
    * OspSystemStructureImporter now resolves the type of initial values. I.e. If an initial value in OspSystemStructure is denoted as literal '1' but with Type 'Real', then this initial value will be imported not as integer 1 but as float 1.0


## [0.2.2] - 2022-10-05

### Solved

* Connection:<br>
    Corrected a bug in Connection.is_variable_connection() and Connection.is_variable_group_connection() which led to Variable Connections not being resolved.


## [0.2.1] - 2022-10-01

### Changed

* OspSimulationCase:<br>
    Changed setup(): FMU files get no longer copied into the case folder by default but stay where they are (i.e. in the library).<br>
    Only if an FMU is not reachable by a relative path from the case folder, the FMU will get copied into the case folder.


* dependencies:
    * upgraded to dictIO >= 0.2.0


## [0.2.0] - 2022-09-28

### Solved

* importer.py: <br>
  Relative paths to libSource and FMUs are now properly resolved, relative to the target directory the OSPSystemStructure.xml is imported into (= folder in which the caseDict is created).
  For libSource, by default the absolute path will be entered. This makes the caseDict insensitive when moved or copied into other (case) folders.

### Changed

* OSPModelDescription.xml: <br>
  The handling of OSPModelDescription.xml files has changed:
    * no OSPModelDescription.xml files get written by default
    * existing OSPModelDescription.xml files will be kept

* dependencies:
    * upgraded to dictIO >= 0.1.2

### Added

* OSPSystemStructure.xml:
    * Added support for VariableGroups and VariableGroupConnections (as defined in OSP-IS). <br>
      importSystemStructure is now also able to import OSPSystemStructure.xml files that use Connections of OSP-IS type  'VariableGroupConnection'.

    * Added support for <Simulator> stepSize attribute: <br>
      If a \<Simulator\> element in OSPSystemStructure.xml explicitely defines the stepSize attribute, and if the value given for a \<Simulator\>'s stepSize inside OSPSystemStructure.xml differs from the default stepSize defined in the FMU's ModelDescription.xml, then the stepSize defined in OSPSystemStructure.xml prevails and will also explicitely be included in the OSPSystemStructure.xml file written by ospCaseBuilder.



## [0.1.2] - 2022-08-19

### Changed

* variable.py:
    * variable.start -> added type casting to setter property ensuring an already defined data_type of the variable is not altered when a new start value is set.

* watchCosim.py
    * put watchCosim in working state after time stepping, before changing over to individual data frames
    * move *.csv files finally into folder /results

* Protect png's in result folder from being deleted

* ospCaseBuilder CLI:
    * inspect mode (--inspect) now adds to the results the attributes of the DefaultExperiment element from the FMU's modelDescription.xml

* plotting.py:
    * added further exceptions for non-word characters in title strings

* dependencies:
    * ospx now uses dictIO v0.1.1

## [0.1.1] - 2022-05-30

### Changed

* case dict file format:  Removed 'root' element from '_environment' section, as it is obsolete.

### Fixed

* relative paths in the 'fmu' element led to a FileNotFound error. This is fixed now.

## [0.1.0] - 2022-05-28

### Changed

* Major refactoring, introducing classes for the main elements such as FMU, Component, SystemStructure etc.
* Simplified imports from namespace ospx. Example:
    * Old (<= v0.0.22):
        ~~~py
        from ospx.ospCaseBuilder import OspCaseBuilder
        ~~~
    * New:
        ~~~py
        from ospx import OspCaseBuilder
        ~~~
* Use new simplified imports from namespace dictIO (using updated version of dictIO package)
* Two changes were introduced in the case dict file format:
    1. Connector element: key 'reference' changed to 'variable':<br>
        * Old (<= v0.0.22):
            ~~~cpp
            connectors
            {
                difference_input_minuend
                {
                    reference             difference.IN1;
                    type                  input;
                }
            ~~~
        * New:
            ~~~cpp
            connectors
            {
                difference_input_minuend
                {
                    variable            difference.IN1;
                    type                input;
                }
            ~~~
    2. Connection element: source and target changed from single strings to fully qualified endpoints, providing not only the connector but also the component the connector or variable belongs to:
        * Old (<= v0.0.22):
            ~~~cpp
            connections
            {
                minuend_to_difference
                {
                    source                minuend_output;
                    target                difference_input_minuend;
                }
            ~~~
        * New:
            ~~~cpp
            connections
            {
                minuend_to_difference
                {
                    source
                    {
                        component               minuend;
                        connector               minuend_output;
                    }
                    target
                    {
                        component               difference;
                        connector               difference_input_minuend;
                    }
                }
            ~~~
        * Instead of connector, alternatively also a variable can be referenced in source / target endpoint. Example:
            ~~~cpp
            connections
            {
                minuend_to_difference
                {
                    source
                    {
                        component               minuend;
                        variable                constVal.OUT;
                    }
                    target
                    {
                        component               difference;
                        variable                difference.IN1;
                    }
                }
            ~~~


## [0.0.22] - 2022-05-09

* First public release

## [0.0.17] - 2022-02-14

### Added

* Added support for Python 3.10

<!-- Markdown link & img dfn's -->
[unreleased]: https://github.com/dnv-opensource/ospx/compare/v0.2.5...HEAD
[0.2.5]: https://github.com/dnv-opensource/ospx/compare/v0.2.4...v0.2.5
[0.2.4]: https://github.com/dnv-opensource/ospx/compare/v0.2.3...v0.2.4
[0.2.3]: https://github.com/dnv-opensource/ospx/compare/v0.2.2...v0.2.3
[0.2.2]: https://github.com/dnv-opensource/ospx/compare/v0.2.1...v0.2.2
[0.2.1]: https://github.com/dnv-opensource/ospx/compare/v0.2.0...v0.2.1
[0.2.0]: https://github.com/dnv-opensource/ospx/compare/v0.1.1...v0.2.0
[0.1.2]: https://github.com/dnv-opensource/ospx/compare/v0.1.1...v0.1.2
[0.1.1]: https://github.com/dnv-opensource/ospx/compare/v0.1.0...v0.1.1
[0.1.0]: https://github.com/dnv-opensource/ospx/compare/v0.0.22...v0.1.0
[0.0.22]: https://github.com/dnv-opensource/ospx/compare/v0.0.17...v0.0.22
[0.0.17]: https://github.com/dnv-opensource/ospx/releases/tag/v0.0.17
[ospx]: https://github.com/dnv-opensource/ospx
