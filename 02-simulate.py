import logging
from importlib import reload

import openmm.unit as openmm_unit
from openmm import LangevinIntegrator, Platform, XmlSerializer
from openmm.app import (
    CheckpointReporter,
    DCDReporter,
    PDBFile,
    Simulation,
    StateDataReporter,
)

reload(logging)

logger = logging.getLogger()
logging.basicConfig(
    filename="paprika.log",
    format="%(asctime)s %(message)s",
    datefmt="%Y-%m-%d %I:%M:%S %p",
    level=logging.INFO,
)

# Init
#properties = {"CudaPrecision": "mixed", "CudaDeviceIndex": "3"}
properties = {"CudaPrecision": "mixed"}
temperature = 298.15 * openmm_unit.kelvin
pressure = 1.01325 * openmm_unit.bar
kT = temperature * openmm_unit.BOLTZMANN_CONSTANT_kB * openmm_unit.AVOGADRO_CONSTANT_NA
dt_therm = 1.0 * openmm_unit.femtoseconds
dt_equil = 2.0 * openmm_unit.femtoseconds
dt_prod = 2.0 * openmm_unit.femtoseconds
therm_steps = 50000    # 0.1 ns
equil_steps = 1000000  # 2 ns
prod_steps = 5000000  # 10 ns
out_freq = 2500

# Open system
pdbfile = PDBFile("system.pdb")
with open("system.xml", "r") as f:
    system = XmlSerializer.deserialize(f.read())

# Minimization and Thermalisation
# --------------------------------------------------------------------#
logger.info("Minimizing and Thermalisation ...")

# Thermostat
integrator = LangevinIntegrator(temperature, 1.0 / openmm_unit.picoseconds, dt_therm)

# Simulation Object
simulation = Simulation(
    pdbfile.topology,
    system,
    integrator,
    Platform.getPlatformByName("CUDA"),
    properties,
)
simulation.context.setPositions(pdbfile.positions)

# Minimize Energy
simulation.minimizeEnergy(
    tolerance=1.0 * openmm_unit.kilojoules_per_mole, maxIterations=5000
)

# Reporters
check_reporter = CheckpointReporter("thermalisation.chk", out_freq * 10)
dcd_reporter = DCDReporter("thermalisation.dcd", out_freq * 10)
state_reporter = StateDataReporter(
    "thermalisation.log",
    out_freq * 10,
    step=True,
    kineticEnergy=True,
    potentialEnergy=True,
    totalEnergy=True,
    temperature=True,
    volume=True,
    speed=True,
    separator=",",
)
simulation.reporters.append(check_reporter)
simulation.reporters.append(dcd_reporter)
simulation.reporters.append(state_reporter)

# MD Step
simulation.step(therm_steps)
simulation.saveState("thermalisation.xml")

# Equilibration
# --------------------------------------------------------------------#
logging.info("Running equilibration ...")

# Thermostat
integrator = LangevinIntegrator(temperature, 1.0 / openmm_unit.picoseconds, dt_equil)

# Simulation object
simulation = Simulation(
    pdbfile.topology,
    system,
    integrator,
    Platform.getPlatformByName("CUDA"),
    properties,
)
simulation.loadState("thermalisation.xml")

# Reporters
check_reporter = CheckpointReporter("equilibration.chk", out_freq * 10)
dcd_reporter = DCDReporter("equilibration.dcd", out_freq * 10)
state_reporter = StateDataReporter(
    "equilibration.log",
    out_freq * 10,
    step=True,
    kineticEnergy=True,
    potentialEnergy=True,
    totalEnergy=True,
    temperature=True,
    volume=True,
    speed=True,
    separator=",",
)
simulation.reporters.append(check_reporter)
simulation.reporters.append(dcd_reporter)
simulation.reporters.append(state_reporter)

# MD step
simulation.step(equil_steps)
simulation.saveState("equilibration.xml")

# Production
# --------------------------------------------------------------------#
logging.info("Running production ...")

# Thermostat
integrator = LangevinIntegrator(temperature, 1.0 / openmm_unit.picoseconds, dt_prod)

# Create simulation object
simulation = Simulation(
    pdbfile.topology,
    system,
    integrator,
    Platform.getPlatformByName("CUDA"),
    properties,
)
simulation.loadState("equilibration.xml")

# Reporters
check_reporter = CheckpointReporter("production.chk", out_freq * 10)
dcd_reporter = DCDReporter("production.dcd", out_freq)
state_reporter = StateDataReporter(
    "production.log",
    out_freq,
    step=True,
    kineticEnergy=True,
    potentialEnergy=True,
    totalEnergy=True,
    temperature=True,
    volume=True,
    speed=True,
    separator=",",
)
simulation.reporters.append(check_reporter)
simulation.reporters.append(dcd_reporter)
simulation.reporters.append(state_reporter)

# MD step
simulation.step(prod_steps)
simulation.saveState("production.xml")
