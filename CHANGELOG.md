# Changelog

All notable changes to the [ospx] project will be documented in this file.<br>
The changelog format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [Unreleased]

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
[unreleased]: https://github.com/dnv-opensource/ospx/compare/v0.1.2...HEAD
[0.1.2]: https://github.com/dnv-opensource/ospx/compare/v0.1.1...v0.1.2
[0.1.1]: https://github.com/dnv-opensource/ospx/compare/v0.1.0...v0.1.1
[0.1.0]: https://github.com/dnv-opensource/ospx/compare/v0.0.22...v0.1.0
[0.0.22]: https://github.com/dnv-opensource/ospx/compare/v0.0.17...v0.0.22
[0.0.17]: https://github.com/dnv-opensource/ospx/releases/tag/v0.0.17
[ospx]: https://github.com/dnv-opensource/ospx
