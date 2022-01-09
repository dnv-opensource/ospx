# ospx
ospx is an extension package to [farn][farn_docs] supporting the creation of OSP (co-)simulation cases using functional mockup units (FMUs).

ospx supports
* building of case-specific OSP (co-)simulation configuration files
* watching the progress of cosim, and saving final simulation results as a pandas dataframe.

## Installation
```sh
pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ ospx
```
ospx requires the following (sub-)package:
* [dictIO][dictIO_docs]: foundation package, enabling ospx to handle configuration files in C++ dictionary format.

However, dictIO gets installed automatically with ospx.

## Usage Example

ospx provides both an API for use inside Python as well as a CLI for shell execution of core functions.

Reading a caseDict file and building the case-specific OSP (co-)simulation configuration files:
~~~py
from ospx.ospCaseBuilder import OspCaseBuilder

OspCaseBuilder.build('caseDict')
~~~

The above task can also be invoked from the command line, using the 'ospCaseBuilder' command line script installed with ospx:
~~~sh
ospCaseBuilder caseDict
~~~

_For more examples and usage, please refer to [ospx's documentation][ospx_docs] on GitHub Pages._

## File Format
A caseDict is a file in C++ dictionary format used with farn.

_For a documentation of the caseDict file format, see [File Format](fileFormat.md) in [ospx's documentation][ospx_docs] on GitHub Pages._

_For a detailed documentation of the C++ dictionary format used by farn, see [dictIO's documentation][dictIO_docs] on GitHub Pages._

## Development Setup

1. Install [Python 3.9](https://www.python.org/downloads/release/python-399/)

2. git clone the farn repository into your local development directory:

~~~sh
git clone git://github.com/dnv-opensource/ospx.git path/to/your/dev/ospx
~~~

3. In the ospx root folder:

Create a Python virtual environment:
~~~sh
python -m venv .venv
~~~
Activate the virtual environment:
~~~sh
.venv\Scripts\activate
~~~
Update pip and setuptools:
~~~sh
python -m pip install --upgrade pip setuptools
~~~
Install farn's dependencies:
~~~sh
pip install -r requirements.txt
~~~


## Release History

* 0.1.0
    * First release

## Meta

Copyright (c) 2022 [DNV](https://www.dnv.com) [open source](https://github.com/dnv-opensource)

Frank Lumpitzsch – [@LinkedIn](https://www.linkedin.com/in/frank-lumpitzsch-23013196/) – frank.lumpitzsch@dnv.com

Claas Rostock – [@LinkedIn](https://www.linkedin.com/in/claasrostock/?locale=en_US) – claas.rostock@dnv.com

Seunghyeon Yoo – [@LinkedIn](https://www.linkedin.com/in/seunghyeon-yoo-3625173b/) – seunghyeon.yoo@dnv.com

Distributed under the MIT license. See [LICENSE](LICENSE.md) for more information.

[https://github.com/dnv-opensource/ospx](https://github.com/dnv-opensource/ospx)

## Contributing

1. Fork it (<https://github.com/dnv-opensource/ospx/fork>)
2. Create your branch (`git checkout -b fooBar`)
3. Commit your changes (`git commit -am 'Add some fooBar'`)
4. Push to the branch (`git push origin fooBar`)
5. Create a new Pull Request

For your contribution, please make sure you follow the [STYLEGUIDE](STYLEGUIDE.md) before creating the Pull Request.

<!-- Markdown link & img dfn's -->
[dictIO_docs]: https://turbo-adventure-f218cdea.pages.github.io
[ospx_docs]: https://literate-guacamole-9daa57bc.pages.github.io
[farn_docs]: https://crispy-tribble-285142b5.pages.github.io