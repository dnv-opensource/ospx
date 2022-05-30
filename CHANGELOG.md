# Changelog

All notable changes to the [ospx] project will be documented in this file.<br>
The changelog format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [Unreleased]

* case dict file format:  Removed 'root' element from '_environment' section, as it is obsolete.

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
[unreleased]: https://github.com/dnv-opensource/ospx/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/dnv-opensource/ospx/compare/v0.0.22...v0.1.0
[0.0.22]: https://github.com/dnv-opensource/ospx/compare/v0.0.17...v0.0.22
[0.0.17]: https://github.com/dnv-opensource/ospx/releases/tag/v0.0.17
[ospx]: https://github.com/dnv-opensource/ospx
