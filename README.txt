This project implements the Firefighter problem as a using Binary Integer programming approach, in both Minizinc and Python's PuLP frameworks.
The goal is to compare performances of the 2 frameworks. Note that the 'COIN-BC' solver was used in both frameworks, to ensure fairness in the comparison test.

Minizinc compiler must be installed on the computer, and the PATH environment variable set up properly.

The following files need to be present and in the same directory:

firefighter_minizinc.py
firefighter_pulp.py
helper.py
firefighter.mzn
pipeline.py

Additionally, the following Python packages must be installed:

numpy
matplotlib
networkx
seaborn
pandas
minizinc
