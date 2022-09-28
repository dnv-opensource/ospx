# caseDict

## Description

A caseDict is a file in dictIO dict file format used with ospCaseBuilder

A caseDict acts as input for ospCaseBuilder to
* generate an osp-compatible simulation case, consisting of one or multiple fmu's
* trigger subsequent actions, such as writing a statisticsDict and a default watchDict

A caseDict file contains
* generic information about the simulation case and the physical location of the fmu's to be sourced
* information about the components and the names to be used within the simulation
* for each component, a dictionary of settings (e.g. start values and connector names)
* a connection routing between connectors defined in component sub-dictionary

## Elements

| element / key                                     | type      | Description |
| :------------------------------------------------ | :-------- | :---------- |
| #include                                          | string    | include directive. The specified dict file (e.g. a paramDict) will be read and merged into the caseDict |
| _environment                                      | dict      | environment variables needed by ospCaseBuilder at runtime |
| &numsp;libSource                                  | string    | relative or absolute path to the directory where the FMUs are located, i.e. the base folder of an FMU library. It acts as entry point for the FMU search. |
| systemStructure                                   | dict      | complete system structure |
| &numsp;components                                 | dict      | defines all component models used in the simulation |
| &numsp;&numsp;\<COMPONENT>                        | dict      | unique name identifying a component in the simulation |
| &numsp;&numsp;&numsp;connectors                   | dict      | itemization of connectors as defined in the FMU's modelDescription.xml |
| &numsp;&numsp;&numsp;&numsp;\<CONNECTOR>          | dict      | speaking name of a connector, i.e. what it does and where it is mounted |
| &numsp;&numsp;&numsp;&numsp;&numsp;variable       | string    | name of a referenced variable as defined in the FMU file (mutually exclusive with variableGroup)|
| &numsp;&numsp;&numsp;&numsp;&numsp;variableGroup  | string    | name of a referenced VariableGroup as defined in <fmu_name>_OSPModelDescription.xml (mutually exclusive with variable)|
| &numsp;&numsp;&numsp;&numsp;&numsp;type           | string    | type of the connector. Choices: {input, output} |
| &numsp;&numsp;&numsp;initialize                   | dict      | optional initialization, updating the FMU's default settings |
| &numsp;&numsp;&numsp;&numsp;\<VARIABLE>           | dict      | the variable / parameter to be set. Needs to match the name as defined in the FMU file. |
| &numsp;&numsp;&numsp;&numsp;&numsp;causality      | string    | causality of the variable. Choices: {input, output, parameter} |
| &numsp;&numsp;&numsp;&numsp;&numsp;variability    | string    | variability of the variable. Choices: {fixed, calculated, tunable} |
| &numsp;&numsp;&numsp;&numsp;&numsp;start          | float     | initial value the variable shall be set to. |
| &numsp;&numsp;&numsp;fmu                          | string    | relative path to the location of the source FMU (relative to libSource) |
| &numsp;connections                                | dict      | itemization of connections |
| &numsp;&numsp;\<CONNECTION>                       | dict      | speaking name of the connection |
| &numsp;&numsp;&numsp;source                       | dict      | source endpoint of \<CONNECTION> |
| &numsp;&numsp;&numsp;&numsp;component             | string    | name of source \<COMPONENT> |
| &numsp;&numsp;&numsp;&numsp;connector             | string    | name of \<CONNECTOR> at source \<COMPONENT> (mutually exclusive with variable) |
| &numsp;&numsp;&numsp;&numsp;variable              | string    | name of \<VARIABLE> at source \<COMPONENT> (mutually exclusive with connector) |
| &numsp;&numsp;&numsp;target                       | dict      | target endpoint of \<CONNECTION> |
| &numsp;&numsp;&numsp;&numsp;component             | string    | name of target \<COMPONENT> |
| &numsp;&numsp;&numsp;&numsp;connector             | string    | name of \<CONNECTOR> at target \<COMPONENT> (mutually exclusive with variable) |
| &numsp;&numsp;&numsp;&numsp;variable              | string    | name of \<VARIABLE> at target \<COMPONENT> (mutually exclusive with connector) |
| run                                               | dict      | settings for simulation run |
| &numsp;simulation                                 | dict      | additional information about the simulaton. Used for window decoration. |
| &numsp;&numsp;name                                | string    | name of the simulation |
| &numsp;&numsp;startTime                           | float     | start time |
| &numsp;&numsp;stopTime                            | float     | start time |
| &numsp;&numsp;baseStepSize                        | float     | master algorithm step size |
| &numsp;&numsp;algorithm                           | string    | Co-simulation master algorithm (currently 'fixedStep' is supported by OSP) |

## Example

Below example shows a typical caseDict file.

~~~guess
/*---------------------------------*- C++ -*----------------------------------*\
filetype dictionary; coding utf-8; version 0.1; local --; purpose --;
\*----------------------------------------------------------------------------*/
#include 'paramDict'

_environment
{
    libSource                           path/to/a/model/library/on/your/machine;
}
systemStructure
{
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
        subtrahend_to_difference
        {
            source
            {
                component               subtrahend;
                connector               subtrahend_output;
            }
            target
            {
                component               difference;
                connector               difference_input_subtrahend;
            }
        }
        dividend_to_quotient
        {
            source
            {
                component               dividend;
                connector               dividend_output;
            }
            target
            {
                component               quotient;
                connector               quotient_input_dividend;
            }
        }
        difference_to_divisor
        {
            source
            {
                component               difference;
                connector               difference_output;
            }
            target
            {
                component               quotient;
                connector               quotient_input_divisor;
            }
        }
    }
    components
    {
        difference
        {
            connectors
            {
                difference_input_minuend
                {
                    variable            difference.IN1;
                    type                input;
                }
                difference_input_subtrahend
                {
                    variable            difference.IN2;
                    type                input;
                }
                difference_output
                {
                    variable            difference.OUT;
                    type                output;
                }
            }
            fmu                         subfolder/in/your/library/difference.fmu;
        }
        quotient
        {
            connectors
            {
                quotient_input_dividend
                {
                    variable            quotient.IN1;
                    type                input;
                }
                quotient_input_divisor
                {
                    variable            quotient.IN2;
                    type                input;
                }
                quotient_output
                {
                    variable            quotient.OUT;
                    type                output;
                }

            }
            fmu                         subfolder/in/your/library/quotient.fmu;
        }
        minuend
            {
            connectors
            {
                minuend_output
                {
                    variable            constVal.OUT;
                    type                output;
                }
            }
            initialize
            {
                constVal.IN
                {
                    causality           parameter;
                    variability         fixed;
                    start               $minuend;
                }
            }
            fmu                         subfolder/in/your/library/constantVal.fmu;
        }
        subtrahend
        {
            connectors
            {
                subtrahend_output
                {
                    variable            constVal.OUT;
                    type                output;
                }
            }
            initialize
            {
                constVal.IN
                {
                    causality           parameter;
                    variability         fixed;
                    start               $subtrahend;
                }
            }
            fmu                         subfolder/in/your/library/constantVal.fmu;
        }
        dividend
        {
            connectors
            {
                dividend_output
                {
                    variable            constVal.OUT;
                    type                output;
                }
            }
            initialize
            {
                constVal.IN
                {
                    causality           parameter;
                    variability         fixed;
                    start               $dividend;
                }
            }
            fmu                         subfolder/in/your/library/constantVal.fmu;
        }
    }
}
run
{
    simulation
    {
        name                            demoCase;
        startTime                       0;
        stopTime                        10;
        baseStepSize                    0.01;
        algorithm                       fixedStep;
    }
}

~~~
If you aim for just a first inspection of a simulation case, all you need to do is drop all referenced FMUs
into the case's build directory and call ospCaseBuilder with the --inspect option:
```
ospCaseBuilder caseDict --inspect --verbose
```
Inspection works already with a fairly rudimentary caseDict, such as:
~~~guess
/*---------------------------------*- C++ -*----------------------------------*\
filetype dictionary; coding utf-8; version 0.1; local --; purpose --;
\*----------------------------------------------------------------------------*/
_environment
{
    libSource                 path/to/a/model/library/on/your/machine;
}
systemStructure
{
    components
    {
        difference
        {
            fmu             subfolder/in/your/library/difference.fmu;
        }
        quotient
        {
            fmu             subfolder/in/your/library/quotient.fmu;
        }
        minuend
        {
            fmu             subfolder/in/your/library/constantVal.fmu;
        }
        subtrahend
        {
            fmu             subfolder/in/your/library/constantVal.fmu;
        }
        dividend
        {
            fmu             subfolder/in/your/library/constantVal.fmu;
        }
    }
}
run
{
    simulation
    {
        name                  demoCase;
    }
}
~~~