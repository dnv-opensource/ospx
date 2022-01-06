# caseDict

## Description

A caseDict is a file in C++ dictionary format used with ospCaseBuilder

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
| &numsp;root                                       | string    | relative path to the build directory. Use '.' for cwd. |
| systemStructure                                   | dict      | complete system structure |
| &numsp;components                                 | dict      | defines all component models used in the simulation |
| &numsp;&numsp;\<COMPONENT>                        | dict      | unique name identifying a component in the simulation |
| &numsp;&numsp;&numsp;connectors                   | dict      | itemization of connectors as defined in the FMU's modelDescription.xml |
| &numsp;&numsp;&numsp;&numsp;\<CONNECTOR>          | dict      | speaking name of a connector, i.e. what it does and where it is mounted |
| &numsp;&numsp;&numsp;&numsp;&numsp;reference      | string    | internal name of the connector as defined in the FMU file |
| &numsp;&numsp;&numsp;&numsp;&numsp;type           | string    | type of the connector. Choices: {input, output} |
| &numsp;&numsp;&numsp;initialize                   | dict      | optional initialization, updating the FMU's default settings |
| &numsp;&numsp;&numsp;&numsp;\<VARIABLE>           | dict      | the variable / parameter to be set. Needs to match the name as defined in the FMU file. |
| &numsp;&numsp;&numsp;&numsp;&numsp;causality      | string    | causality of the variable. Choices: {input, output, parameter} |
| &numsp;&numsp;&numsp;&numsp;&numsp;start          | float     | initial value the variable shall be set to. |
| &numsp;&numsp;&numsp;&numsp;&numsp;variabliity    | string    | variability of the variable. Choices: {fixed, calculated, tunable} |
| &numsp;&numsp;&numsp;prototype                    | string    | relative path to the location of the source FMU (relative to libSource) |
| &numsp;connections                                | dict      | itemization of connections |
| &numsp;&numsp;\<CONNECTION>                       | dict      | speaking name of the connection |
| &numsp;&numsp;&numsp;source                       | string    | name of source \<COMPONENT> |
| &numsp;&numsp;&numsp;target                       | string    | name of target \<COMPONENT> |
| run                                               | dict      | settings for simulation run |
| &numsp;simulation                                 | dict      | additional information about the simulaton. Used for window decoration. |
| &numsp;&numsp;name                                | string    | name of the simulation |
| &numsp;&numsp;startTime                           | float     | start time |
| &numsp;&numsp;baseStepSize                        | float     | master algorithm step size |

## Example

Below example shows a typical caseDict file.

~~~guess
/*---------------------------------*- C++ -*----------------------------------*\
filetype dictionary; coding utf-8; version 0.1; local --; purpose --;
\*----------------------------------------------------------------------------*/
#include 'paramDict'

_environment
{
    libSource                 'path/to/a/model/library/on/your/machine';
    root                     .;
}
systemStructure
{
    connections
    {
        in_0_to_diff_0
        {
            source                in_0_tx;
            target                diff_0_rx_0;
        }
        in_1_to_diff_0
        {
            source                in_1_tx;
            target                diff_0_rx_1;
        }
        in_2_to_div_0
        {
            source                in_2_tx;
            target                div_0_rx_0;
        }
        diff_0_to_div_0
        {
            source                diff_0_tx;
            target                div_0_rx_1;
        }
    }
    components
    {
        diff_0
        {
            connectors
            {
                diff_0_rx_0
                {
                    reference             difference.IN1;
                    type                  input;
                }
                diff_0_rx_1
                {
                    reference             difference.IN2;
                    type                  input;
                }
                diff_0_tx
                {
                    reference             difference.OUT;
                    type                  input;
                }
            }
            prototype             'subfolder/in/your/library/difference.fmu';
        }
        div_0
        {
            connectors
            {
                div_0_rx_0
                {
                    reference     quotient.IN1;
                    type          input;
                }
                div_0_rx_1
                {
                    reference     quotient.IN2;
                    type          input;
                }
                div_0_tx
                {
                    reference     quotient.OUT;
                    type          input;
                }

            }
            prototype             'subfolder/in/your/library/quotient.fmu';
        }
        in_0
        {
            connectors
            {
                in_0_tx
                {
                    reference     constVal.OUT;
                    type          output;
                }
            }
            initialize
            {
                constVal.IN
                {
                    causality     parameter;
                    start         $in_0;
                    variability   fixed;
                }
            }
            prototype             'subfolder/in/your/library/constantVal.fmu';
        }
        in_1
        {
            connectors
            {
                in_1_tx
                {
                    reference     constVal.OUT;
                    type          output;
                }
            }
            initialize
            {
                constVal.IN
                {
                    causality     parameter;
                    start         $in_1;
                    variability   fixed;
                }
            }
            prototype             'subfolder/in/your/library/constantVal.fmu';
        }
        in_2
        {
            connectors
            {
                in_2_tx
                {
                    reference     constVal.OUT;
                    type          output;
                }
            }
            initialize
            {
                constVal.IN
                {
                    causality     parameter;
                    start         $in_2;
                    variability   fixed;
                }
            }
            prototype             'subfolder/in/your/library/constantVal.fmu';
        }
    }
}
run
{
    simulation
    {
        name                  demoCase;
        startTime             0;
        baseStepSize          0.1;
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
    libSource                 'path/to/a/model/library/on/your/machine';
    root                     .;
}
systemStructure
{
    components
    {
        diff_0
        {
            prototype             'subfolder/in/your/library/difference.fmu';
        }
        div_0
        {
            prototype             'subfolder/in/your/library/quotient.fmu';
        }
        in_0
        {
            prototype             'subfolder/in/your/library/constantVal.fmu';
        }
        in_1
        {
            prototype             'subfolder/in/your/library/constantVal.fmu';
        }
        in_2
        {
            prototype             'subfolder/in/your/library/constantVal.fmu';
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