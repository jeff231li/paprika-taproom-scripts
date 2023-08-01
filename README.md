# paprika-taproom-scripts
A repository that contains scripts to generate APR files from Taproom repository in pAPRika

There are three files in the repository:
* [01-generate_system.ipynb](01-generate_system.ipynb) -- Jupyter Notebook that generates the APR windows for a given host-guest pair.
* [02-simulate.py](02-simulate.py) -- OpenMM simulation script you run for each window.
* [03-analysis.ipynb](03-analysis.ipynb) -- Jupyter Notebook that analyzes the APR simulations and extracts the binding free energy.
