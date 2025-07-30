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

lPointGround = mbs.AddNode(NodePointGround(
    name='PointGround',
    referenceCoordinates=[0.0, 0.0, 0.0],
    visualization=VNodePointGround(
        show=True,
        drawSize=-1.0,
        color=[0.0, 0.0, 1.0, 1.0]
    )
))
lPointGround_nodeNumber = lPointGround

lPoint = mbs.AddNode(NodePoint(
    name='Point',
    referenceCoordinates=[0.9999999999999999, 0.0, 0.0],
    initialCoordinates=[0.0, 0.0, 0.0],
    initialVelocities=[0.0, 0.0, 0.0],
    visualization=VNodePoint(
        show=True,
        drawSize=-1.0,
        color=[0.5, 0.5, 0.5, 1.0]
    )
))
lPoint_nodeNumber = lPoint

lMassPoint = mbs.AddObject(ObjectMassPoint(
    name='MassPoint',
    physicsMass=20.0,
    nodeNumber=lPoint_nodeNumber,
    visualization=VObjectMassPoint(
        show=True,
        graphicsData=[exu.graphics.Sphere(point=[0.0, 0.0, 0.0], radius=0.1, color=[0.0, 0.0, 0.0, 1.0], nTiles=8, addEdges=False, edgeColor=[0.0, 0.0, 0.0, 1.0], addFaces=True)]
    )
))
lMassPoint_objectNumber = lMassPoint

lNodeCoordinate = mbs.AddMarker(MarkerNodeCoordinate(
    name='NodeCoordinate',
    nodeNumber=lPointGround_nodeNumber,
    coordinate=0,
    visualization=VMarkerNodeCoordinate(show=True)
))
lNodeCoordinate_markerNumber = lNodeCoordinate

lNodeCoordinate2 = mbs.AddMarker(MarkerNodeCoordinate(
    name='NodeCoordinate2',
    nodeNumber=lPoint_nodeNumber,
    coordinate=0,
    visualization=VMarkerNodeCoordinate(show=True)
))
lNodeCoordinate2_markerNumber = lNodeCoordinate2

lConnectorCoordinateSpringDamper = mbs.AddObject(ObjectConnectorCoordinateSpringDamper(
    name='ConnectorCoordinateSpringDamper',
    markerNumbers=[lNodeCoordinate_markerNumber, lNodeCoordinate2_markerNumber],
    stiffness=40.0,
    damping=10.0,
    offset=0.3,
    activeConnector=True,
    springForceUserFunction=0,
    visualization=VObjectConnectorCoordinateSpringDamper(
        show=True,
        drawSize=-1.0,
        color=[0.0, 1.0, 0.0, 1.0]
    )
))
lConnectorCoordinateSpringDamper_objectNumber = lConnectorCoordinateSpringDamper

lCoordinate = mbs.AddLoad(LoadCoordinate(
    name='Coordinate',
    markerNumber=lNodeCoordinate2_markerNumber,
    load=140.0,
    loadUserFunction=0,
    visualization=VLoadCoordinate(show=True)
))
lCoordinate_loadNumber = lCoordinate

lSensorBody = mbs.AddSensor(SensorBody(
    name='Body3',
    bodyNumber=lMassPoint_objectNumber,
    localPosition=[0.0, 0.0, 0.0],
    writeToFile=True,
    fileName='',
    storeInternal=True,
    outputVariableType=exu.OutputVariableType.Displacement,
    visualization=VSensorBody(show=True)
))
lSensorBody_sensorNumber = lSensorBody

mbs.Assemble()
SC.renderer.Start()
simulationSettings = exu.SimulationSettings()
# Using default simulation settings (no changes detected)

SC.visualizationSettings.general.drawWorldBasis = True
SC.visualizationSettings.interactive.highlightColor = [0.000000e+00, 0.000000e+00, 0.000000e+00, 0.000000e+00]
SC.visualizationSettings.nodes.defaultColor = [1.2200000286102295, 0.20000000298023224, 1.0, 1.0]
SC.visualizationSettings.openGL.faceEdgesColor = [0.2199999988079071, 0.20000000298023224, 0.20000000298023224, 1.0]
SC.visualizationSettings.openGL.light0position = [0.20000000298023224, 10.199999809265137, 10.0, 0.000000e+00]
SC.visualizationSettings.openGL.shadow = 0.5
SC.visualizationSettings.window.alwaysOnTop = True

# Restore view state
renderState = {'centerPoint': [1.09084951877594, 0.25538119673728943, 0.46875],
                'rotationCenterPoint': [0.000000e+00, 0.000000e+00, 0.000000e+00],
                'maxSceneSize': 1.9558806419372559,
                'zoom': 0.7823522686958313
                }
SC.renderer.SetState(renderState)

SC.renderer.DoIdleTasks()
exu.SolveDynamic(mbs, simulationSettings)
SC.renderer.DoIdleTasks()
SC.renderer.Stop()