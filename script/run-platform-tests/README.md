# How to run platform tests

1. Clone the appropriate `regrid-wrapper` branch on Gaea-C6 or Ursa.
1. `cd <clone directory>/script/run-platform-tests`
1. Update `env-run-platform-tests.sh` with correct paths and experiment configuration. _Note: There are a couple "clean" flags in the environment script. Be sure you want those enabled!_
1. `bash run-platform-tests.sh 2>&1 | tee out.run-platform-tests.sh`