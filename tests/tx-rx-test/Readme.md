## send -- receive -- test simulation for ospCaseBuilder

### Step 1 Run inspect

Run

```ospCaseBuilder.py inspectFirstDict --inspect```

in current folder and note console output.

### Step 2 Run generate simulation

Step into tx-test and execute

```ospCaseBuilder.py tx-testDict```

and / or step into rx-test and execute

```ospCaseBuilder.py rx-testDict```

respectively,

to generate a working sender simulation and
a working receiver simulation.

### Step 3 (optional) prepare network settings

* shut-off zScaler
* open ports 32001 and 32002 for incoming and outgoing connections in windows firewall app

### Step 4 (optional) run the simulation(s)

Open two console windows.

For each source software modules
* _cmd
* _dev
* OSP/cosim-0.5.0

and development module

* modelVerification/latest

For each navigate to generator folder and

for each run cosim for 95 seconds,

using command:


```cosim run OspSystemStructure.xml -b 0 -d 95 --real-time --log-level=debug```
