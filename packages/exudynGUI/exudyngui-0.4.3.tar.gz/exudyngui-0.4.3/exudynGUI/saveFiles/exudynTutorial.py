import exudyn as exu
from exudyn import SystemContainer
import numpy as np
from exudyn.utilities import *

SC = SystemContainer()
from exudyn import *
mbs = SC.AddSystem()

# === User Variables ===
L = 0.5
mass = 1.6
spring = 400
damper = 8
f = 80
u0 = 0.08
v0 = 1
x0 = 0.2

lPoint = mbs.AddNode(NodePoint(
    name='Point',
    referenceCoordinates=[L,0,0],
    initialCoordinates=[u0,0,0],
    initialVelocities=[v0,0,0],
    visualization=VNodePoint(
        show=True,
        drawSize=-1.0,
        color=[0.0, 1.0, 0.0, 1.0]
    )
))
lPoint_nodeNumber = lPoint
lPointGround = mbs.AddNode(NodePointGround(
    name='PointGround',
    referenceCoordinates=[0.0, 0.0, 0.0],
    visualization=VNodePointGround(
        show=True,
        drawSize=-1.0,
        color=[0.0, 0.0, 0.0, 1.0]
    )
))
lPointGround_nodeNumber = lPointGround
lMassPoint = mbs.AddObject(ObjectMassPoint(
    name='MassPoint',
    physicsMass=mass,
    nodeNumber=lPoint_nodeNumber,
    visualization=VObjectMassPoint(
        show=True,
        graphicsData=[exu.graphics.Sphere(point=[0.0, 0.0, 0.0], radius=0.1, color=[0.0, 0.0, 1.0, 1.0], nTiles=8, addEdges=False, edgeColor=[0.0, 0.0, 0.0, 1.0], addFaces=True)]
    )
))
lMassPoint_objectNumber = lMassPoint
lgroundMarker = mbs.AddMarker(MarkerNodeCoordinate(
    name='groundMarker',
    nodeNumber=lPointGround_nodeNumber,
    coordinate=0,
    visualization=VMarkerNodeCoordinate(show=True)
))
lgroundMarker_markerNumber = lgroundMarker
lnodeMarker = mbs.AddMarker(MarkerNodeCoordinate(
    name='nodeMarker',
    nodeNumber=lPoint_nodeNumber,
    coordinate=0,
    visualization=VMarkerNodeCoordinate(show=True)
))
lnodeMarker_markerNumber = lnodeMarker
lConnectorCoordinateSpringDamper = mbs.AddObject(ObjectConnectorCoordinateSpringDamper(
    name='ConnectorCoordinateSpringDamper',
    markerNumbers=[lgroundMarker_markerNumber, lnodeMarker_markerNumber],
    stiffness=spring,
    damping=damper,
    offset=0.0,
    activeConnector=True,
    springForceUserFunction=0,
    visualization=VObjectConnectorCoordinateSpringDamper(
        show=True,
        drawSize=-1.0,
        color=[0.0, 1.0, 1.0, 1.0]
    )
))
lConnectorCoordinateSpringDamper_objectNumber = lConnectorCoordinateSpringDamper
lCoordinate = mbs.AddLoad(LoadCoordinate(
    name='Coordinate',
    markerNumber=lnodeMarker_markerNumber,
    load=f,
    loadUserFunction=0,
    visualization=VLoadCoordinate(show=True)
))
lCoordinate_loadNumber = lCoordinate
lSensorObject = mbs.AddSensor(SensorObject(
    name='sensorObjectSD',
    objectNumber=lConnectorCoordinateSpringDamper_objectNumber,
    writeToFile=True,
    fileName='',
    storeInternal=True,
    outputVariableType=exu.OutputVariableType.Force,
    visualization=VSensorObject(show=True)
))
lSensorObject_sensorNumber = lSensorObject

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