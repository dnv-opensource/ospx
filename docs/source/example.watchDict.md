# watchDict file

## Description

A watchDict is a file in C++ dictionary format used with cosim and watchCosim.

A watchDict is suitable for
* monitor the progress of a running cosim simulation
* show a self defined convergence plot on the screen and save the image
* write a statistical summary of the results (as defined in watchDict and as far as the simulation has progressed).

A default watchDict is written during opsCaseBuilder's build process covering all information from the involved fmu's.
The user can opt to reduce and / or adjust the default watchDict's content afterwards manually (or by a user defined tool / process).

## Terms & Definition

| Keyword/Example | Type          | Argument           | Description |
| :-------------- | :------------ | :----------------- | :---------- |
| datasources     | fixed keyword | dictionary         | {all, any, none} names of the involved fmu's |
| FMUNAME         | free choice   | dictionary         | matching the name of any fmu (without file extension) |
| columns         | fixed keyword | list of integers   | columns as they are written in FMUNAME_DATETIME.csv (sub-setting and ordering is free-of-choice)  |
| delimiter       | fixed keyword | string             | the type of delimiter in FMUNAME_DATETIME.csv |
| simulation      | fixed keyword | dictionary         | selected settings of the current simulaton for window decoration |
| name            | fixed keyword | string             | simulation name |
| SIMULATIONNAME  | free choice   | string             | name of the current simulation |

## Related files
* ./watchDict
* results/resultDict
* results/dataFrame.dump
* results/SIMULATIONNAME.png

## Example

![convergence plot example](demoCase.png)

Below example shows the typical structure of a caseDict file.

~~~
/*---------------------------------*- C++ -*----------------------------------*\
filetype dictionary; coding utf-8; version 0.1; local --; purpose --;
\*----------------------------------------------------------------------------*/
datasources
{
    FMUNAME
    {
        columns
        (
            0                 1                 2                 3                 4
        );
    }
}
delimiter                     ,;
simulation
{
    name                      SIMULATIONNAME;
}
~~~
