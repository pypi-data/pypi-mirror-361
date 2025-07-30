import exudyn as exu
from exudyn import SystemContainer
import numpy as np
import exudyn.graphics as graphics
from exudyn.utilities import *

SC = SystemContainer()
from exudyn import *
mbs = SC.AddSystem()

# === User Variables ===
m = 10000.0
k = 1000.0

cRigidBody = mbs.CreateRigidBody(
    referencePosition=[0.0, 0.0, 0.0],
    referenceRotationMatrix=np.array([[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]]),
    initialVelocity=[0.0, 0.0, 0.0],
    initialAngularVelocity=[0.0, 0.0, 0.0],
    initialDisplacement=None,
    initialRotationMatrix=None,
    inertia=exu.utilities.InertiaSphere(mass=1.0, radius=0.1, density=None),
    gravity=[0.0, 0.0, 0.0],
    nodeType=exu.NodeType.RotationEulerParameters,
    graphicsDataList=[graphics.FromSTLfile(fileName='C:/Arbeit/exudynGUI/exudynGUI/exudynGUI/stlFiles/rigidShaft.stl', color=[0.0, 0.0, 1.0, 1.0], verbose=False, density=0.0, scale=1.0, Aoff=[[6.123233995736766e-17, 0.0, 1.0], [0.0, 1.0, 0.0], [-1.0, 0.0, 6.123233995736766e-17]], pOff=[0.0, 0.0, 0.0], invertNormals=True, invertTriangles=True)],
    graphicsDataUserFunction=0,
    drawSize=-1,
    color=[0.5, 0.5, 0.5, 1.0],
    show=True,
    create2D=False,
    returnDict=True
)
cRigidBody_nodeNumber = cRigidBody['nodeNumber']
cRigidBody_bodyNumber = cRigidBody['bodyNumber']
cRigidBody2 = mbs.CreateRigidBody(
    referencePosition=[0.25, 0.0, 0.0],
    referenceRotationMatrix=np.array([[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]]),
    initialVelocity=[0.0, 0.0, 0.0],
    initialAngularVelocity=[0.0, 0.0, 0.0],
    initialDisplacement=None,
    initialRotationMatrix=None,
    inertia=exu.utilities.InertiaSphere(mass=1.0, radius=0.1, density=None),
    gravity=[0.0, 0.0, 0.0],
    nodeType=exu.NodeType.RotationEulerParameters,
    graphicsDataList=[graphics.FromSTLfile(fileName='C:/Arbeit/exudynGUI/exudynGUI/exudynGUI/stlFiles/crossShaft.stl', color=[0.0, 0.0, 0.0, 1.0], verbose=False, density=0.0, scale=1.0, Aoff=[[6.123233995736766e-17, 0.0, 1.0], [0.0, 1.0, 0.0], [-1.0, 0.0, 6.123233995736766e-17]], pOff=[0.0, 0.0, 0.0], invertNormals=True, invertTriangles=True)],
    graphicsDataUserFunction=0,
    drawSize=-1,
    color=[0.5, 0.5, 0.5, 1.0],
    show=True,
    create2D=False,
    returnDict=True
)
cRigidBody2_nodeNumber = cRigidBody2['nodeNumber']
cRigidBody2_bodyNumber = cRigidBody2['bodyNumber']
cRigidBody5 = mbs.CreateRigidBody(
    referencePosition=[0.5, 0.0, 0.0],
    referenceRotationMatrix=np.array([[1.0, 0.0, 0.0], [0.0, 0.0, -1.0], [0.0, 1.0, 0.0]]),
    initialVelocity=[0.0, 0.0, 0.0],
    initialAngularVelocity=[0.0, 0.0, 0.0],
    initialDisplacement=None,
    initialRotationMatrix=None,
    inertia=exu.utilities.InertiaSphere(mass=1.0, radius=0.1, density=None),
    gravity=[0.0, 0.0, 0.0],
    nodeType=exu.NodeType.RotationEulerParameters,
    graphicsDataList=[graphics.FromSTLfile(fileName='C:\\Arbeit\\exudynGUI\\exudynGUI\\exudynGUI\\stlFiles\\rigidShaft.stl', color=[0.5, 0.5, 0.5, 1.0], verbose=False, density=0.0, scale=1.0, Aoff=[[-6.123233995736766e-17, -1.2246467991473532e-16, -1.0], [7.498798913309288e-33, -1.0, 1.2246467991473532e-16], [-1.0, 0.0, 6.123233995736766e-17]], pOff=[0.0, 0.0, 0.0], invertNormals=True, invertTriangles=True)],
    graphicsDataUserFunction=0,
    drawSize=-1,
    color=[0.5, 0.5, 0.5, 1.0],
    show=True,
    create2D=False,
    returnDict=True
)
cRigidBody5_nodeNumber = cRigidBody5['nodeNumber']
cRigidBody5_bodyNumber = cRigidBody5['bodyNumber']
cGround2 = mbs.CreateGround(
    referencePosition=[0.0, 0.0, 0.0],
    referenceRotationMatrix=np.array([[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]]),
    graphicsDataList=[graphics.Basis(origin=[0.0, 0.0, 0.0], rotationMatrix=[[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]], length=0.2, colors=[[1.0, 0.0, 0.0, 1.0],[0.0, 1.0, 0.0, 1.0],[0.0, 0.0, 1.0, 1.0]], headFactor=2.0, headStretch=4.0, nTiles=12)],
    graphicsDataUserFunction=0,
    show=True
)
cGround2_objectNumber = cGround2
cGround2_bodyNumber = cGround2
cRevoluteJoint = mbs.CreateRevoluteJoint(
    bodyNumbers=[cRigidBody2_bodyNumber, cRigidBody5_bodyNumber],
    position=[0.25, 0.0, 0.0],
    axis=[0.0, 0.0, 1.0],
    useGlobalFrame=True,
    show=False,
    axisRadius=0.2,
    axisLength=0.4,
    color=[1.0, 0.0, 1.0, 1.0]
)
cRevoluteJoint_objectNumber = cRevoluteJoint
cRevoluteJoint2 = mbs.CreateRevoluteJoint(
    bodyNumbers=[cRigidBody2_bodyNumber, cRigidBody_bodyNumber],
    position=[0.0, 0.0, 0.0],
    axis=[0.0, 1.0, 0.0],
    useGlobalFrame=False,
    show=True,
    axisRadius=0.02,
    axisLength=0.24,
    color=[1.0, 1.0, 0.0, 1.0]
)
cRevoluteJoint2_objectNumber = cRevoluteJoint2
cTorque = mbs.CreateTorque(
    bodyNumber=cRigidBody_bodyNumber,
    loadVector=[1.0, 0.0, 0.0],
    localPosition=[0.0, 0.0, 0.0],
    bodyFixed=False,
    loadVectorUserFunction=0,
    show=True
)
cTorque_loadNumber = cTorque
cRevoluteJoint3 = mbs.CreateRevoluteJoint(
    bodyNumbers=[cGround2_bodyNumber, cRigidBody_bodyNumber],
    position=[0.0, 0.0, 0.0],
    axis=[1.0, 0.0, 0.0],
    useGlobalFrame=False,
    show=True,
    axisRadius=0.02,
    axisLength=0.22,
    color=[0.0, 1.0, 1.0, 1.0]
)
cRevoluteJoint3_objectNumber = cRevoluteJoint3
cGenericJoint = mbs.CreateGenericJoint(
    bodyNumbers=[3, 0],
    position=[0.0, 0.0, 0.0],
    rotationMatrixAxes=np.array([[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]]),
    constrainedAxes=[1, 0, 0, 0, 0, 0],
    useGlobalFrame=False,
    offsetUserFunction=0,
    offsetUserFunction_t=0,
    show=True,
    axesRadius=0.1,
    axesLength=0.4,
    color=[0.5, 0.5, 0.5, 1.0]
)
cGenericJoint_objectNumber = cGenericJoint
cGenericJoint2 = mbs.CreateGenericJoint(
    bodyNumbers=[2, 3],
    position=[0.0, 0.0, 0.0],
    rotationMatrixAxes=np.array([[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]]),
    constrainedAxes=[0, 1, 1, 0, 0, 0],
    useGlobalFrame=False,
    offsetUserFunction=0,
    offsetUserFunction_t=0,
    show=True,
    axesRadius=0.1,
    axesLength=0.4,
    color=[0.5, 0.5, 0.5, 1.0]
)
cGenericJoint2_objectNumber = cGenericJoint2
lSensorBody = mbs.AddSensor(SensorBody(
    name='Body',
    bodyNumber=cRigidBody2_bodyNumber,
    localPosition=[0.0, 0.0, 0.0],
    writeToFile=True,
    fileName='',
    storeInternal=True,
    outputVariableType=exu.OutputVariableType.AngularAcceleration,
    visualization=VSensorBody(show=True)
))
lSensorBody_sensorNumber = lSensorBody

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