# caseDict file

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

## Terms & Definition

| Keyword/Example       | Type              | Argument                     | Description |
| :---------------------| :---------------- | :--------------------------- | :---------- |
| #include              | include directive | string                       | the included dict file will be read and merged into the parent dict|
| _environment          | fixed keyword     | dictionary                   | definitions about the environment |
|   libSource           | fixed keyword     | relativ/absolute path string | entry point for fmu search |
|   root                | fixed keyword     | relativ path string          | build directory |
| systemStructure       | fixed keyword     | dictionary                   | complete system structure |
|   components          | fixed keyword     | dictionary                   | complete set of components (building blocks) |
|     COMPONENTNAME     | free choice       | dictionary                   | matching the name of any fmu (without file extension) |
|       connectors      | fixed keyword     | dictionary                   | itemization of connectors from fmu's modelDescription.xml |
|         CONNECTORNAME | free choice       | dictionary                   | speaking name of the connector, i.e. what it does and where it is mounted |
|           component   | fixed keyword     | string                       | obsolete (herited from former structure) |
|           reference   | fixed keyword     | string                       | internal representation (name) of the connector in the regarding fmu |
|           type        | fixed keyword     | string, choice               | input\|output |
|       initialize      | fixec keyword     | dictionary                   | optional initialization, updating fmu's default settings |
|         VARIABLENAME  | defined choice    | dictionary                   | the variable/parameter to be set, name is defined in the fmu file |
|           causality   | defined choice    | string                       | choice wether input\|output\|parameter |
|           start       | free choice       | double                       | value or reference/formula to be included |
|           variabliity | fixed keyword     | string                       | choice wether fixed\|calculated\|tunable |
|       prototype       | fixed value       | relative path string         | pointing to the location of the source fmu on the file system |
| connections           | fixed keyword     | dictionary                   | itemization of connections from the simulation setup |
|   CONNECTIONNAME      | fixed keyword     | dictionary                   | speaking name of the connection |
|     source            | fixed keyword     | string                       | COMPONENTNAME of the incoming connection |
|     target            | fixed keyword     | string                       | COMPONENTNAME of the outgoing connection |
| run                   | fixed keyword     | dictionary                   | div. global settings |
|   simulation          | fixed keyword     | dictionary                   | some settings of the current simulaton for window decoration |
|     name              | fixed keyword     | string                       | simulation name |
|     startTime         | fixed keyword     | double                       | start time |
|     baseStepSize      | fixed keyword     | double                       | basic step size of simulators communication steps |

## Example

Below example shows the typical structure of a caseDict file.

~~~
/*---------------------------------*- C++ -*----------------------------------*\
filetype dictionary; coding utf-8; version 0.1; local --; purpose --;
\*----------------------------------------------------------------------------*/
#include '.\paramDict'

_environment
{
    libSource                 'C:\Path\to\a\model\library\on\your\machine';
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
                    component             diff_0;
                    reference             difference.IN1;
                    type                  input;
                }
                diff_0_rx_1
                {
                    component             diff_0;
                    reference             difference.IN2;
                    type                  input;
                }
                diff_0_tx
                {
                    component             diff_0;
                    reference             difference.OUT;
                    type                  input;
                }
            }
            prototype             subfolder\in\your\library\difference.fmu;
        }
        div_0
        {
            connectors
            {
                div_0_rx_0
                {
                    component     div_0;
                    reference     quotient.IN1;
                    type          input;
                }
                div_0_rx_1
                {
                    component     div_0;
                    reference     quotient.IN2;
                    type          input;
                }
                div_0_tx
                {
                    component     div_0;
                    reference     quotient.OUT;
                    type          input;
                }

            }
            prototype             subfolder\in\your\library\quotient.fmu;
        }
        in_0
            {
            connectors
            {
                in_0_tx
                {
                    component     in_0;
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
            prototype             subfolder\in\your\library\constantVal.fmu;
        }
        in_1
        {
            connectors
            {
                in_1_tx
                {
                    component     in_1;
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
            prototype             subfolder\in\your\library\constantVal.fmu;
        }
        in_2
        {
            connectors
            {
                in_2_tx
                {
                    component     in_2;
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
            prototype             subfolder\in\your\library\constantVal.fmu;
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
