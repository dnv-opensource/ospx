# Changelog

All notable changes to the [ospx] project will be documented in this file.<br>
The changelog format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [Unreleased]

### Dependencies
* Updated to ruff>=0.11.0  (from ruff>=0.9.2)
* Updated to pyright>=1.1.396  (from pyright>=1.1.392)
* Updated to sourcery>=1.35  (from sourcery>=1.31)
* Updated to types-lxml>=2025.3  (from types-lxml>=2024.12)
* Updated to pre-commit>=4.1  (from pre-commit>=4.0)
* Updated to mypy>=1.15  (from mypy>=1.14)

### Changed
* Do not run code quality checks in nightly builds
* Included uv.lock file in version control


## [0.3.1] - 2025-01-18

### Added
* Added support for Python 3.13
* Added CITATION.cff
* pyproject.toml : Added keywords

### Solved
* Resolved issues raised by `ruff` 0.9.2

### Dependencies
* Updated to ruff>=0.9.2  (from ruff>=0.6.3)
* Updated to pyright>=1.1.392  (from pyright>=1.1.378)
* Updated to sourcery>=1.31  (from sourcery>=1.22)
* Updated to lxml>=5.3  (from lxml>=5.2)
* Updated to types-lxml>=2024.12  (from types-lxml>=2024.4)
* Updated to matplotlib>=3.10  (from matplotlib>=3.9)
* Updated to dictIO>=0.4.1  (from dictIO>=0.4.0)
* Updated to Sphinx>=8.1  (from Sphinx>=8.0)
* Updated to sphinx-argparse-cli>=1.19  (from sphinx-argparse-cli>=1.17)
* Updated to sphinx-autodoc-typehints>=3.0  (from sphinx-autodoc-typehints>=2.2)
* Updated to mypy>=1.14  (from mypy>=1.11.1)
* Updated to setup-uv@v5  (from setup-uv@v2)
* Updated to jupyter>=1.1  (from jupyter>=1.0)
* Updated to pytest-cov>=6.0  (from pytest-cov>=5.0)
* Updated to pre-commit>=4.0  (from pre-commit>=3.8)
* numpy: As Python 3.13 requires numpy 2.x, made minimum required numpy version in pyproject.toml dependent on Python version:
  * "numpy>=1.26; python_version < '3.13'",
  * "numpy>=2.2; python_version >= '3.13'",


## [0.3.0] - 2024-11-11

### Breaking changes
* The code has been adapted to [dictIO][dictIO_docs] 0.4.0 <br>
  [dictIO][dictIO_docs] 0.4.0 introduced some breaking changes. With the current release 0.3.0 of ospx, the code base has been adapted to these in changes. <br>
  The most prominent change being that class `dictIO.CppDict` has been replaced by class `dictIO.SDict`.

### Changed
* Changed from `pip`/`tox` to `uv` as package manager
* README.md : Completely rewrote section "Development Setup", introducing `uv` as package manager.
* Changed publishing workflow to use OpenID Connect (Trusted Publisher Management) when publishing to PyPI
* Updated copyright statement
* VS Code settings: Turned off automatic venv activation
* Replaced black formatter with ruff formatter

### Solved
* Sphinx documentation: Resolved issue that documentation of class members was generated twice.

### Added
* Sphinx documentation: Added extension to support Markdown-based diagrams created with Mermaid.
* Added `mypy` as static type checker (in addition to `pyright`)

### GitHub workflows
* (all workflows): Adapted to use `uv` as package manager
* _test_future.yml : updated Python version to 3.13.0-alpha - 3.13.0
* _test_future.yml : updated name of test job to 'test313'

### Dependencies
* Updated to dictIO>=0.4.0  (from dictIO>=0.3.4)
* Updated to ruff>=0.6.3  (from ruff==0.4.2)
* Updated to pyright>=1.1.378  (from pyright==1.1.360)
* Updated to sourcery>=1.22  (from sourcery==1.16)
* Updated to pytest>=8.3  (from pytest>=8.2)
* Updated to Sphinx>=8.0  (from Sphinx>=7.3)
* Updated to sphinx-argparse-cli>=1.17  (from sphinx-argparse-cli>=1.16)
* Updated to myst-parser>=4.0  (from myst-parser>=3.0)
* Updated to furo>=2024.8  (from furo>=2024.5)
* updated to setup-python@v5  (from setup-python@v4)
* updated to actions-gh-pages@v4  (from actions-gh-pages@v3)
* updated to upload-artifact@v4  (from upload-artifact@v3)
* Updated to download-artifact@v4  (from download-artifact@v3)
* updated to checkout@v4  (from checkout@v3)


## [0.2.14] - 2024-05-22

### Dependencies
* updated to ruff==0.4.2  (from ruff==0.2.1)
* updated to pyright==1.1.360  (from pyright==1.1.350)
* updated to sourcery==1.16  (from sourcery==1.15)
* updated to lxml>=5.2  (from lxml>=5.1)
* updated to types-lxml>=2024.4  (from types-lxml>=5.1)
* updated to pytest>=8.2  (from pytest>=7.4)
* updated to pytest-cov>=5.0  (from pytest-cov>=4.1)
* updated to Sphinx>=7.3  (from Sphinx>=7.2)
* updated to sphinx-argparse-cli>=1.15  (from sphinx-argparse-cli>=1.11)
* updated to myst-parser>=3.0  (from myst-parser>=2.0)
* updated to furo>=2024.4  (from furo>=2023.9.10)
* updated to numpy>=1.26,<2.0  (from numpy>=1.26)
* updated to matplotlib>=3.9  (from matplotlib>=3.8)
* updated to dictIO>=0.3.4  (from dictIO>=0.3.1)
* removed black

### Changed
* replaced black formatter with ruff formatter
* Changed publishing workflow to use OpenID Connect (Trusted Publisher Management) when publishing to PyPI
* Updated copyright statement
* VS Code settings: Turned off automatic venv activation


## [0.2.13] - 2024-02-21

### Added
* README.md : Under `Development Setup`, added a step to install current package in "editable" mode, using the pip install -e option.
This removes the need to manually add /src to the PythonPath environment variable in order for debugging and tests to work.

### Removed
* VS Code settings: Removed the setting which added the /src folder to PythonPath. This is no longer necessary. Installing the project itself as a package in "editable" mode, using the pip install -e option, solves the issue and removes the need to manually add /src to the PythonPath environment variable.

### Changed
* Moved all project configuration from setup.cfg to pyproject.toml
* Moved all tox configuration from setup.cfg to tox.ini.
* Moved pytest configuration from pyproject.toml to pytest.ini
* Deleted setup.cfg

### Dependencies
* updated to black[jupyter]==24.1  (from black[jupyter]==23.12)
* updated to version: '==24.1'  (from version: '==23.12')
* updated to ruff==0.2.1  (from ruff==0.1.8)
* updated to pyright==1.1.350  (from pyright==1.1.338)
* updated to sourcery==1.15  (from sourcery==1.14)
* updated to lxml>=5.1  (from lxml>=4.9)
* updated to pandas>=2.2  (from pandas>=2.1)


## [0.2.12] - 2024-01-09

Maintenance Release

### Dependencies

* Updated to dictIO>=0.3.1  (from dictIO>=0.2.9)
* Updated other dependencies to latest versions


## [0.2.11] - 2023-09-25

### Dependencies

* Updated dependencies to latest versions


## [0.2.10] - 2023-06-22

### Changed

* Modularized GitHub workflows
* Changed default Python version in GitHub workflows from 3.10 to 3.11

### Dependencies

* updated to dictIO>=0.2.8
* requirements-dev.txt: Updated dependencies to latest versions


## [0.2.9] - 2023-05-04

### Changed

* dependencies: updated dependencies to latest versions


## [0.2.8] - 2023-01-11

### Changed

* Added missing DocStrings for public classes, methods and functions
* Changed links to package documentation to open README.html, not the default index page
* data classes: changed initialisation of mutable types to use default_factory
* ruff: added rule-set "B" (flake8-bugbear)

### Dependencies

* updated to dictIO>=0.2.6


## [0.2.7] - 2023-01-04

### Changed

* Linter: Migrated from flake8 to ruff. <br>
  (Added ruff; removed flake8 and isort)
* Adjusted GitHub CI workflow accordingly. <br>
  (Added ruff job; removed flake8 and isort jobs)
* VS Code settings: Adjusted Pylance configuration

### Added

* Added a batch file 'qa.bat' in root folder to ease local execution of code quality checks

### Dependencies

* updated to dictIO>=0.2.5


## [0.2.6] - 2022-12-12

### Changed

* Moved dev-only dependencies from requirements.txt to requirements-dev.txt
* ospx/`__init__`.py and ospx/fmi/`__init__`.py : ensured that imported symbols get also exported <br>
  (added "as" clause -> "from x import y as y" instead of only "from x import y")
* Configured code quality tools flake8, black, isort, pyright
* Improved code quality, resolving all warnings and errors flagged by the configured code quality tools
  (flake8, black, isort, pyright, sourcery)

### Added

* Added GitHub workflow 'main.yml' for continuous integration (runs all CI tasks except Sphinx)
    * format checks: black, isort
    * lint check: flake8, flake8-bugbear
    * type check: pyright
    * test: uses tox to run pytest on {Windows, Linux, MacOS} with {py39, py310}
    * publish: publishing to PyPI (runs only on push of new tag vx.x.x, and after all other jobs succeeded)
    * merge_to_release_branch: merge tagged commit to release branch (runs after publish)

### Dependencies

* updated to dictIO>=0.2.4


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
[unreleased]: https://github.com/dnv-opensource/ospx/compare/v0.3.1...HEAD
[0.3.1]: https://github.com/dnv-opensource/ospx/compare/v0.3.0...v0.3.1
[0.3.0]: https://github.com/dnv-opensource/ospx/compare/v0.2.14...v0.3.0
[0.2.14]: https://github.com/dnv-opensource/ospx/compare/v0.2.13...v0.2.14
[0.2.13]: https://github.com/dnv-opensource/ospx/compare/v0.2.12...v0.2.13
[0.2.12]: https://github.com/dnv-opensource/ospx/compare/v0.2.11...v0.2.12
[0.2.11]: https://github.com/dnv-opensource/ospx/compare/v0.2.10...v0.2.11
[0.2.10]: https://github.com/dnv-opensource/ospx/compare/v0.2.9...v0.2.10
[0.2.9]: https://github.com/dnv-opensource/ospx/compare/v0.2.8...v0.2.9
[0.2.8]: https://github.com/dnv-opensource/ospx/compare/v0.2.7...v0.2.8
[0.2.7]: https://github.com/dnv-opensource/ospx/compare/v0.2.6...v0.2.7
[0.2.6]: https://github.com/dnv-opensource/ospx/compare/v0.2.5...v0.2.6
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

<!-- Markdown link & img dfn's -->
[dictIO_docs]: https://dnv-opensource.github.io/dictIO/README.html
