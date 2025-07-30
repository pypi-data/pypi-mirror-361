import exudyn as exu
from exudyn import SystemContainer
import numpy as np
import exudyn.graphics as graphics
from exudyn.utilities import *

SC = SystemContainer()
mbs = SC.AddSystem()

# === User Variables ===
m = 10000.0
k = 1000.0

cGround = mbs.CreateGround(
    referencePosition=[0.0, 0.0, 0.0],
    referenceRotationMatrix=np.array([[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]]),
    graphicsDataList=[graphics.CheckerBoard(point=[0, 0, 0], normal=[0, 0, 1], size=1, color=[0.7, 0.7, 0.7, 1.0], alternatingColor=[0.85, 0.85, 0.85, 1.0], nTiles=10)],
    graphicsDataUserFunction=0,
    show=True
)
cGround_objectNumber = cGround
cGround_bodyNumber = cGround
cMassPoint = mbs.CreateMassPoint(
    referencePosition=[0.0, 0.0, 0.5],
    initialDisplacement=[0.0, 0.0, 0.0],
    initialVelocity=[0.0, 0.0, 0.0],
    physicsMass=1.0,
    gravity=[0.0, 0.0, -9.81],
    graphicsDataList=[graphics.Brick(centerPoint=[0, 0, 0], size=[0.2, 0.2, 0.1], color=[1.0, 0.0, 1.0, 1.0], addNormals=False, addEdges=False, edgeColor=[0.0, 0.0, 0.0, 1.0], addFaces=True, roundness=0, nTiles=12)],
    drawSize=-1.0,
    color=[0.5, 0.5, 0.5, 1.0],
    show=True,
    create2D=False,
    returnDict=True
)
cMassPoint_nodeNumber = cMassPoint['nodeNumber']
cMassPoint_bodyNumber = cMassPoint['bodyNumber']
cSpringDamper = mbs.CreateSpringDamper(
    bodyNumbers=[cGround_bodyNumber, cMassPoint_bodyNumber],
    localPosition0=[0.0, 0.0, 0.0],
    localPosition1=[0.0, 0.0, 0.0],
    referenceLength=None,
    stiffness=100.0,
    damping=10,
    force=0.0,
    velocityOffset=0.0,
    springForceUserFunction=0,
    show=True,
    drawSize=-1.0,
    color=[1.0, 0.0, 1.0, 1.0],
    bodyOrNodeList=[None, None],
    bodyList=[None, None]
)
cSpringDamper_objectNumber = cSpringDamper

mbs.Assemble()
# mbs.SolveDynamic()  # Uncomment to run simulation

simulationSettings = exu.SimulationSettings()
simulationSettings.solutionSettings.solutionWritePeriod = 5e-3
simulationSettings.solutionSettings.sensorsWritePeriod = 5e-3
simulationSettings.timeIntegration.numberOfSteps = 1000
simulationSettings.timeIntegration.endTime = 1.0
simulationSettings.displayComputationTime = True
simulationSettings.timeIntegration.verboseMode = 1
simulationSettings.timeIntegration.generalizedAlpha.spectralRadius = 1

exu.StartRenderer()
mbs.WaitForUserToContinue()
exu.SolveDynamic(mbs, simulationSettings)
mbs.WaitForUserToContinue()
exu.StopRenderer()