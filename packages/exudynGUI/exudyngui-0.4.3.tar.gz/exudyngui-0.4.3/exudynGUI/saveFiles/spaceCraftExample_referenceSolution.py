#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#
# Details:  Spacecraft Example for EXUDYN workshop at ECCOMAS Multibody 2025
#           Innsbruck; This is the reference solution.
# Authors:  Johannes Gerstmayr and Sebastian Weyrer
# Date:     2025-07-13
#
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

import exudyn as exu
import exudyn.graphics as graphics
from exudyn.utilities import *
from exudyn.FEM import *

import time
import numpy as np
from math import pi

print('EXUDYN version:', exu.config.Version())

#++++++++++++++++++++++++++++++++++++++++++++++++++
# some general definitions
y0 = 0.5                                # [m] initial height of space craft
phi0 = pi/8                             # initial rotation of space craft
g = -1.62                               # [m/s^2] gravitational acceleration on the moon
feetSphereRadius = 0.05                 # [m] radius of the sphere that is at the end of the feet
planetRadius = 1e3                      # [m] radius of the planet (used for SphereSphere Contact)
contactStiffness = 1e5                  # [N/m^2] contact stiffness between space craft and planet surface
contactDamping = 1e3                    # [Ns/m] contact damping between space craft and planet surface
dynamicFriction = 0.001                 # friction factor for the SphereSphereContact
stiffnessProportionalDamping = 0.02     # [s] stiffness proportional damping (Rayleigh Damping) added to the floating coordinates
restitutionCoefficient = 0.5            # restitution coefficient for the SphereSphereContact
stlFileName = 'spaceCraftGraphics'      # STL file that contains the visualization of the spacecraft
meshFileName = 'spaceCraftMesh'         # Mesh file that is used for the flexible simulation
useSolutionViewer = True                # use the solution viewer if you want to have a closer look at your simulation
simulateFlexibleBody = False            # set this True if you also want to simulate the flexible body

#++++++++++++++++++++++++++++++++++++++++++++++++++
# EXUDYN initializations
SC = exu.SystemContainer()
mbs = SC.AddSystem()
simulationSettings = exu.SimulationSettings()

#%% PART 1: set up the RIGID body model of the space craft
if not simulateFlexibleBody:
    # TODO 1) Create the ground object
    # -> Add your code below
    oGround = mbs.CreateGround(referencePosition=[0, 0, 0], graphicsDataList=[graphics.CheckerBoard(normal=[0, 1, 0], size=20)])
    
    # TODO 2) Define the parameters of the rigid body
    # -> Add your code below
    inertiaSpaceCraft = np.array([[76.62, 0., 0.],
                                  [0., 21.6, 0.],
                                  [0., 0., 76.62]])
    pCOM = np.array([0., 0.71, 0.])
    rigidBodyInertia = RigidBodyInertia(mass=105.77, inertiaTensor=inertiaSpaceCraft, com=pCOM, inertiaTensorAtCOM=False)
    print(rigidBodyInertia)
    
    # TODO 3) Make the visualization for the rigid body object
    # -> Add your code below
    gSpaceCraft = graphics.FromSTLfileASCII(fileName=stlFileName + '.stl', color=color4orange)
    # gSpaceCraft = graphics.AddEdgesAndSmoothenNormals(gSpaceCraft, addEdges=False) # for faster execution comment this line
    
    # TODO 3) Create the rigid body object
    # -> Add your code below
    bSpaceCraft = mbs.CreateRigidBody(inertia=rigidBodyInertia,
                                      initialDisplacement=[0, y0, 0],
                                      initialRotationMatrix=RotationMatrixZ(phi0),
                                      gravity=[0, g, 0],
                                      graphicsDataList=[gSpaceCraft])
    
    # TODO 5) Create the contact between ground and feet
    # -> Add your code below
    feetPositionsList = [[0.55, 0.05, 0.55],
                         [-0.55, 0.05, 0.55],
                         [-0.55, 0.05, -0.55],
                         [0.55, 0.05, -0.55]]
    



    for i in range(4):
        mbs.CreateSphereSphereContact(bodyNumbers=[oGround, bSpaceCraft],
                                      localPosition0=[0, -planetRadius, 0],
                                      localPosition1=feetPositionsList[i],
                                      spheresRadii=[planetRadius, feetSphereRadius],
                                      restitutionCoefficient=restitutionCoefficient,
                                      contactStiffness=contactStiffness, contactDamping=contactDamping,
                                      dynamicFriction=dynamicFriction)

#%% PART 2: set up the FLEXIBLE body model of the space craft
else:
    mbs.Reset()
    oGround = mbs.CreateGround(referencePosition=[0, 0, 0], graphicsDataList=[graphics.CheckerBoard(normal=[0, 1, 0], size=20)])
    # TODO 1) Load the handed-out mesh to EXUDYN's FEM interface
    # -> Add your code below
    fem = FEMinterface()
    fem.LoadFromFile(meshFileName, mode='PKL')
    
    # TODO 2) Get the boundary nodes that are already defined (for Hurty Craig-Bempton (HCB) Modes)
    # -> Add your code below
    # get boundary nodes and weights (defined with the occ wrapper)
    boundaryNodesList = []
    boundaryWeightsList = []
    for nodeSet in fem.nodeSets:
        boundaryNodesList += [nodeSet['NodeNumbers']]
        boundaryWeightsList += [nodeSet['NodeWeights']]
    
    # TODO 3) Compute the HCB Modes
    # -> Add your code below
    print('Start computing HCB modes')
    start_time = time.time()
    fem.ComputeHurtyCraigBamptonModes(boundaryNodesList=boundaryNodesList, 
                                      nEigenModes=16, # number of eigen modes in addition to STATIC modes
                                      useSparseSolver=True,
                                      excludeRigidBodyMotion=True,
                                      computationMode=HCBstaticModeSelection.RBE2)
    print('HCB modes needed %.3f seconds of computation time' % (time.time() - start_time))
        
    # TODO 4) Add Floating Frame of Reference Formulation (FFRF) object
    # -> Add your code below
    cms = ObjectFFRFreducedOrderInterface(fem)
    objFFRF = cms.AddObjectFFRFreducedOrder(mbs, positionRef=[0, y0, 0],
                                            rotationMatrixRef=RotationMatrixZ(phi0), # rotation w.r.t. reference position
                                            stiffnessProportionalDamping=stiffnessProportionalDamping,
                                            gravity=[0, g, 0])
    
    # TODO 5) Add MarkerSuperElementRigid to the FFRF object, so that we can add Connectors, ...
    # -> Add your code below
    boundaryMarkerList = []
    for i, nodeSet in enumerate(boundaryNodesList):
        weights = boundaryWeightsList[i]
        marker = mbs.AddMarker(MarkerSuperElementRigid(bodyNumber=objFFRF['oFFRFreducedOrder'], 
                                                       meshNodeNumbers=np.array(nodeSet), # these are the meshNodenumbers
                                                       weightingFactors=weights))
        boundaryMarkerList += [marker]
    
    # TODO 6) Add SphereSphere Contact using the MarkerSuperElementRigid
    # -> Add your code below
    mGround = mbs.AddMarker(MarkerBodyRigid(bodyNumber=oGround, localPosition=[0, -planetRadius, 0]))
    for marker in boundaryMarkerList:
        nGeneric = mbs.AddNode(NodeGenericData(numberOfDataCoordinates=4, initialCoordinates=[0]*4))
        mbs.AddObject(ObjectContactSphereSphere(markerNumbers=[mGround, marker],
                                                nodeNumber=nGeneric, spheresRadii=[planetRadius, feetSphereRadius],
                                                restitutionCoefficient=restitutionCoefficient,
                                                contactStiffness=contactStiffness, contactDamping=contactDamping,
                                                dynamicFriction=dynamicFriction))
    
# %% some special visualization and solver settings for the flexible body simulation
    # visualization settings
    SC.visualizationSettings.contour.outputVariable = exu.OutputVariableType.DisplacementLocal
    SC.visualizationSettings.contour.outputVariableComponent = -1 # norm
    # solver settings
    simulationSettings.linearSolverType = exu.LinearSolverType.EigenSparse
    simulationSettings.timeIntegration.discontinuous.useRecommendedStepSize = False # for testing

#%% do simulation (implicit dynamic simulation) (WYSWYS - What You See is What You Simulate)
mbs.Assemble() 
h = 1e-3    # [s] step size of simulation
tEnd = 10   # [s] duration of simulation

#++++++++++++++++++++++++++++++++++++++++++++++++++
# general visualization settings
SC.visualizationSettings.nodes.show = False
SC.visualizationSettings.markers.show = True
SC.visualizationSettings.markers.drawSimplified = True
SC.visualizationSettings.openGL.light0position = [0, 10, 1, 1]
SC.visualizationSettings.openGL.shadow = 0.25

#++++++++++++++++++++++++++++++++++++++++++++++++++
# simulation settings
simulationSettings.timeIntegration.numberOfSteps = int(tEnd/h)
simulationSettings.timeIntegration.endTime = tEnd
simulationSettings.solutionSettings.writeSolutionToFile = True
simulationSettings.timeIntegration.newton.useModifiedNewton = True
simulationSettings.displayComputationTime = True

#++++++++++++++++++++++++++++++++++++++++++++++++++
SC.renderer.Start()
# set render state
renderState = {'centerPoint': [0, 1, 0],
                'rotationCenterPoint': [0, 0, 0], 
                'maxSceneSize': 15, 
                'zoom':2.5}
SC.renderer.SetState(renderState)
SC.renderer.DoIdleTasks()
mbs.SolveDynamic(simulationSettings=simulationSettings)
SC.renderer.DoIdleTasks()
SC.renderer.Stop() # safely close rendering window!
    
#++++++++++++++++++++++++++++++++++++++++++++++++++
if useSolutionViewer:
    mbs.SolutionViewer()
