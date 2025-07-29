

from typing import (
    Annotated, 
    Any,
    # ByteString,
    # Callable,
    # Container,
    Callable,
    Dict,
    # Generic,
    # IO,
    # Iterable,
    # Iterator,
    List,
    Literal,
    # Mapping,
    # NoReturn,
    # Optional,
    overload,
    # Sequence,
    # Sized,
    # SupportsComplex,
    # SupportsFloat,
    # SupportsInt,
    # Text,
    Tuple, #for Tuple[int, int]
    # Type,
    TypeVar,
    Union,
)
from numpy.typing import ArrayLike, NDArray
from enum import Enum
import numpy as np



T1 = TypeVar("T1", bound=int)
T2 = TypeVar("T2", bound=int)

Shape = Tuple
Shape1D = Shape[T1]
Shape2D = Shape[T1, T2]



import exudyn
from exudyn import (ObjectIndex, NodeIndex, MarkerIndex, LoadIndex, SensorIndex)






@overload
def Help() -> None: ...
@overload
def RequireVersion(requiredVersionString: str) -> None: ...
@overload
def SetWriteToFile(filename: str, flagWriteToFile=True, flagAppend=False, flagFlushAlways=False) -> None: ...
@overload
def Print() -> None: ...
@overload
def InvalidIndex() -> int: ...
__version__:str
variables:dict
sys:dict


class OutputVariableType(Enum):
    _None = int
    Distance = int
    Position = int
    Displacement = int
    DisplacementLocal = int
    Velocity = int
    VelocityLocal = int
    Acceleration = int
    AccelerationLocal = int
    RotationMatrix = int
    Rotation = int
    AngularVelocity = int
    AngularVelocityLocal = int
    AngularAcceleration = int
    AngularAccelerationLocal = int
    CoordinatesTotal = int
    Coordinates = int
    Coordinates_t = int
    Coordinates_tt = int
    SlidingCoordinate = int
    Director1 = int
    Director2 = int
    Director3 = int
    Force = int
    ForceLocal = int
    Torque = int
    TorqueLocal = int
    StrainLocal = int
    StressLocal = int
    CurvatureLocal = int
    ConstraintEquation = int


class ConfigurationType(Enum):
    _None = int
    Initial = int
    Current = int
    Reference = int
    StartOfStep = int
    Visualization = int
    EndOfEnumList = int


class ItemType(Enum):
    _None = int
    Node = int
    Object = int
    Marker = int
    Load = int
    Sensor = int


class NodeType(Enum):
    _None = int
    Ground = int
    Position2D = int
    Orientation2D = int
    Point2DSlope1 = int
    Position = int
    Orientation = int
    RigidBody = int
    RotationEulerParameters = int
    RotationRxyz = int
    RotationRotationVector = int
    LieGroupWithDirectUpdate = int
    GenericODE2 = int
    GenericODE1 = int
    GenericAE = int
    GenericData = int
    PointSlope1 = int
    PointSlope12 = int
    PointSlope23 = int


class JointType(Enum):
    _None = int
    RevoluteX = int
    RevoluteY = int
    RevoluteZ = int
    PrismaticX = int
    PrismaticY = int
    PrismaticZ = int


class DynamicSolverType(Enum):
    GeneralizedAlpha = int
    TrapezoidalIndex2 = int
    ExplicitEuler = int
    ExplicitMidpoint = int
    RK33 = int
    RK44 = int
    RK67 = int
    ODE23 = int
    DOPRI5 = int
    DVERK6 = int
    VelocityVerlet = int


class CrossSectionType(Enum):
    Polygon = int
    Circular = int


class KeyCode(Enum):
    SPACE = int
    ENTER = int
    TAB = int
    BACKSPACE = int
    RIGHT = int
    LEFT = int
    DOWN = int
    UP = int
    F1 = int
    F2 = int
    F3 = int
    F4 = int
    F5 = int
    F6 = int
    F7 = int
    F8 = int
    F9 = int
    F10 = int


class LinearSolverType(Enum):
    _None = int
    EXUdense = int
    EigenSparse = int
    EigenSparseSymmetric = int
    EigenDense = int


class ContactTypeIndex(Enum):
    IndexSpheresMarkerBased = int
    IndexANCFCable2D = int
    IndexTrigsRigidBodyBased = int
    IndexEndOfEnumList = int


class MatrixContainer:
    @overload
    def Initialize(self, numberOfRows: int, numberOfColumns: int, useDenseMatrix: bool=True) -> None: ...
    @overload
    def SetWithDenseMatrix(self, pyArray, useDenseMatrix=False, factor=1.) -> None: ...
    @overload
    def SetWithSparseMatrix(self, sparseMatrix: Any, numberOfRows: int=invalid (-1), numberOfColumns: int=invalid (-1), useDenseMatrix: bool=False, factor: float=1.) -> None: ...
    @overload
    def AddSparseMatrix(self, sparseMatrix: Any, factor: float=1.) -> None: ...
    @overload
    def GetPythonObject(self) -> Union[dict,ArrayLike]: ...
    @overload
    def Convert2DenseMatrix(self) -> ArrayLike: ...
    @overload
    def UseDenseMatrix(self) -> bool: ...
    @overload
    def SetAllZero(self) -> None: ...
    @overload
    def SetWithSparseMatrixCSR(self, numberOfRowsInit: int, numberOfColumnsInit: int, pyArrayCSR: Any, useDenseMatrix: bool=False, factor: float=1.) -> None: ...


class GraphicsMaterialList:
    @overload
    def Reset(self) -> None: ...
    @overload
    def Append(self, material: Any) -> int: ...
    @overload
    def New(self) -> VSettingsMaterial: ...
    @overload
    def Set(self, indexOrName: int, material: Any) -> None: ...
    @overload
    def Get(self, indexOrName: int) -> None: ...
    @overload
    def GetDict(self, indexOrName: int) -> None: ...


class Vector3DList:
    @overload
    def Append(self, pyArray: [float,float,float]) -> None: ...
    @overload
    def GetPythonObject(self) -> List[[float,float,float]]: ...


class Vector2DList:
    @overload
    def Append(self, pyArray: [float,float]) -> None: ...
    @overload
    def GetPythonObject(self) -> List[[float,float]]: ...


class Vector6DList:
    @overload
    def Append(self, pyArray: [float,float,float,float,float,float]) -> None: ...
    @overload
    def GetPythonObject(self) -> List[[float,float,float,float,float,float]]: ...


class Matrix3DList:
    @overload
    def Append(self, pyArray: NDArray[Shape2D[3,3], float]) -> None: ...
    @overload
    def GetPythonObject(self) -> List[NDArray[Shape2D[3,3], float]]: ...


class Matrix6DList:
    @overload
    def Append(self, pyArray: NDArray[Shape2D[6,6], float]) -> None: ...
    @overload
    def GetPythonObject(self) -> List[NDArray[Shape2D[6,6], float]]: ...


class BeamSection:
    dampingMatrix: ArrayLike
    inertia: ArrayLike
    massPerLength: float
    stiffnessMatrix: ArrayLike


class BeamSectionGeometry:
    crossSectionRadiusY: float
    crossSectionRadiusZ: float
    crossSectionType: CrossSectionType
    polygonalPoints: Vector2DList


class SolutionSettings:
    appendToFile: bool
    binarySolutionFile: bool
    coordinatesSolutionFileName: str
    exportAccelerations: bool
    exportAlgebraicCoordinates: bool
    exportDataCoordinates: bool
    exportODE1Velocities: bool
    exportVelocities: bool
    flushFilesDOF: int
    flushFilesImmediately: bool
    outputPrecision: int
    recordImagesInterval: float
    restartFileName: str
    restartWritePeriod: float
    sensorsAppendToFile: bool
    sensorsStoreAndWriteFiles: bool
    sensorsWriteFileFooter: bool
    sensorsWriteFileHeader: bool
    sensorsWritePeriod: float
    solutionInformation: str
    solutionWritePeriod: float
    solverInformationFileName: str
    writeFileFooter: bool
    writeFileHeader: bool
    writeInitialValues: bool
    writeRestartFile: bool
    writeSolutionToFile: bool


class NumericalDifferentiationSettings:
    addReferenceCoordinatesToEpsilon: bool
    doSystemWideDifferentiation: bool
    forAE: bool
    forODE2: bool
    forODE2connectors: bool
    jacobianConnectorDerivative: bool
    minimumCoordinateSize: float
    relativeEpsilon: float


class DiscontinuousSettings:
    ignoreMaxIterations: bool
    iterationTolerance: float
    maxIterations: int
    useRecommendedStepSize: bool


class NewtonSettings:
    numericalDifferentiation: NumericalDifferentiationSettings
    absoluteTolerance: float
    adaptInitialResidual: bool
    maximumSolutionNorm: float
    maxIterations: int
    maxModifiedNewtonIterations: int
    maxModifiedNewtonRestartIterations: int
    modifiedNewtonContractivity: float
    modifiedNewtonJacUpdatePerStep: bool
    newtonResidualMode: int
    relativeTolerance: float
    useModifiedNewton: bool
    useNewtonSolver: bool
    weightTolerancePerCoordinate: bool


class GeneralizedAlphaSettings:
    computeInitialAccelerations: bool
    lieGroupAddTangentOperator: bool
    lieGroupSimplifiedKinematicRelations: bool
    newmarkBeta: float
    newmarkGamma: float
    resetAccelerations: bool
    spectralRadius: float
    useIndex2Constraints: bool
    useNewmark: bool


class ExplicitIntegrationSettings:
    computeEndOfStepAccelerations: bool
    computeMassMatrixInversePerBody: bool
    dynamicSolverType: DynamicSolverType
    eliminateConstraints: bool
    useLieGroupIntegration: bool


class TimeIntegrationSettings:
    discontinuous: DiscontinuousSettings
    explicitIntegration: ExplicitIntegrationSettings
    generalizedAlpha: GeneralizedAlphaSettings
    newton: NewtonSettings
    absoluteTolerance: float
    adaptiveStep: bool
    adaptiveStepDecrease: float
    adaptiveStepIncrease: float
    adaptiveStepRecoveryIterations: int
    adaptiveStepRecoverySteps: int
    automaticStepSize: bool
    computeLoadsJacobian: int
    endTime: float
    initialStepSize: float
    minimumStepSize: float
    numberOfSteps: float
    realtimeFactor: float
    realtimeWaitMicroseconds: int
    relativeTolerance: float
    reuseConstantMassMatrix: bool
    simulateInRealtime: bool
    startTime: float
    stepInformation: int
    stepSizeMaxIncrease: float
    stepSizeSafety: float
    verboseMode: int
    verboseModeFile: int


class StaticSolverSettings:
    discontinuous: DiscontinuousSettings
    newton: NewtonSettings
    adaptiveStep: bool
    adaptiveStepDecrease: float
    adaptiveStepIncrease: float
    adaptiveStepRecoveryIterations: int
    adaptiveStepRecoverySteps: int
    computeLoadsJacobian: bool
    constrainODE1coordinates: bool
    loadStepDuration: float
    loadStepGeometric: bool
    loadStepGeometricRange: float
    loadStepStart: float
    minimumStepSize: float
    numberOfLoadSteps: int
    stabilizerODE2term: float
    stepInformation: int
    useLoadFactor: bool
    verboseMode: int
    verboseModeFile: int


class LinearSolverSettings:
    ignoreSingularJacobian: bool
    pivotThreshold: float
    reuseAnalyzedPattern: bool
    showCausingItems: bool


class Parallel:
    multithreadedLLimitJacobians: int
    multithreadedLLimitLoads: int
    multithreadedLLimitMassMatrices: int
    multithreadedLLimitResiduals: int
    numberOfThreads: int
    taskSplitMinItems: int
    taskSplitTasksPerThread: int
    useLoadBalancing: bool


class SimulationSettings:
    linearSolverSettings: LinearSolverSettings
    parallel: Parallel
    solutionSettings: SolutionSettings
    staticSolver: StaticSolverSettings
    timeIntegration: TimeIntegrationSettings
    cleanUpMemory: bool
    displayComputationTime: bool
    displayGlobalTimers: bool
    displayStatistics: bool
    linearSolverType: LinearSolverType
    outputPrecision: int
    pauseAfterEachStep: bool


class VSettingsGeneral:
    autoFitScene: bool
    axesTiling: int
    backgroundColor: Tuple[float,float,float,float]
    backgroundColorBottom: Tuple[float,float,float,float]
    circleTiling: int
    coordinateSystemSize: float
    cylinderTiling: int
    drawCoordinateSystem: bool
    drawWorldBasis: bool
    graphicsUpdateInterval: float
    linuxDisplayScaleFactor: float
    minSceneSize: float
    pointSize: float
    rendererPrecision: int
    renderWindowString: str
    showComputationInfo: bool
    showHelpOnStartup: int
    showSolutionInformation: bool
    showSolverInformation: bool
    showSolverTime: bool
    sphereTiling: int
    textAlwaysInFront: bool
    textColor: Tuple[float,float,float,float]
    textHasBackground: bool
    textOffsetFactor: float
    textSize: float
    threadSafeGraphicsUpdate: bool
    useBitmapText: bool
    useGradientBackground: bool
    useMultiThreadedRendering: bool
    useWindowsDisplayScaleFactor: bool
    worldBasisSize: float


class VSettingsContour:
    alphaTransparency: float
    automaticRange: bool
    colorBarPrecision: int
    colorBarTiling: int
    maxValue: float
    minValue: float
    nodesColored: bool
    outputVariable: OutputVariableType
    outputVariableComponent: int
    reduceRange: bool
    rigidBodiesColored: bool
    showColorBar: bool


class VSettingsNodes:
    basisSize: float
    defaultColor: Tuple[float,float,float,float]
    defaultSize: float
    drawNodesAsPoint: bool
    show: bool
    showBasis: bool
    showNodalSlopes: int
    showNumbers: bool
    tiling: int


class VSettingsBeams:
    axialTiling: int
    crossSectionFilled: bool
    crossSectionTiling: int
    drawVertical: bool
    drawVerticalColor: Tuple[float,float,float,float]
    drawVerticalFactor: float
    drawVerticalLines: bool
    drawVerticalOffset: float
    drawVerticalValues: bool
    reducedAxialInterploation: bool


class VSettingsKinematicTree:
    frameSize: float
    showCOMframes: bool
    showFramesNumbers: bool
    showJointFrames: bool


class VSettingsBodies:
    beams: VSettingsBeams
    kinematicTree: VSettingsKinematicTree
    defaultColor: Tuple[float,float,float,float]
    defaultSize: Tuple[float,float,float]
    deformationScaleFactor: float
    show: bool
    showNumbers: bool


class VSettingsConnectors:
    contactPointsDefaultSize: float
    defaultColor: Tuple[float,float,float,float]
    defaultSize: float
    jointAxesLength: float
    jointAxesRadius: float
    show: bool
    showContact: bool
    showJointAxes: bool
    showNumbers: bool
    springNumberOfWindings: int


class VSettingsMarkers:
    defaultColor: Tuple[float,float,float,float]
    defaultSize: float
    drawSimplified: bool
    show: bool
    showNumbers: bool


class VSettingsLoads:
    defaultColor: Tuple[float,float,float,float]
    defaultRadius: float
    defaultSize: float
    drawSimplified: bool
    drawWithUserFunction: bool
    fixedLoadSize: bool
    loadSizeFactor: float
    show: bool
    showNumbers: bool


class VSettingsTraces:
    lineWidth: float
    listOfPositionSensors: ArrayIndex
    listOfTriadSensors: ArrayIndex
    listOfVectorSensors: ArrayIndex
    positionsShowEvery: int
    sensorsMbsNumber: int
    showCurrent: bool
    showFuture: bool
    showPast: bool
    showPositionTrace: bool
    showTriads: bool
    showVectors: bool
    timeSpan: float
    traceColors: ArrayFloat
    triadSize: float
    triadsShowEvery: int
    vectorScaling: float
    vectorsShowEvery: int


class VSettingsSensors:
    traces: VSettingsTraces
    defaultColor: Tuple[float,float,float,float]
    defaultSize: float
    drawSimplified: bool
    show: bool
    showNumbers: bool


class VSettingsContact:
    colorBoundingBoxes: Tuple[float,float,float,float]
    colorSearchTree: Tuple[float,float,float,float]
    colorSpheres: Tuple[float,float,float,float]
    colorTori: Tuple[float,float,float,float]
    colorTriangles: Tuple[float,float,float,float]
    contactForcesFactor: float
    contactPointsDefaultSize: float
    showBoundingBoxes: bool
    showContactForces: bool
    showContactForcesValues: bool
    showSearchTree: bool
    showSearchTreeCells: bool
    showSpheres: bool
    showTori: bool
    showTriangles: bool
    tilingCurves: int
    tilingSpheres: int


class VSettingsWindow:
    alwaysOnTop: bool
    ignoreKeys: bool
    keyPressUserFunction: Any
    limitWindowToScreenSize: bool
    maximize: bool
    reallyQuitTimeLimit: float
    renderWindowSize: Tuple[int,int]
    @overload
    def ResetKeyPressUserFunction() -> None: ...
    showMouseCoordinates: bool
    showWindow: bool
    startupTimeout: int


class VSettingsDialogs:
    alphaTransparency: float
    alwaysTopmost: bool
    fontScalingMacOS: float
    multiThreadedDialogs: bool
    openTreeView: bool


class VSettingsMaterial:
    alpha: float
    baseColor: Tuple[float,float,float]
    emission: Tuple[float,float,float]
    ior: float
    name: str
    reflectivity: float
    shininess: float
    specular: Tuple[float,float,float]


class VSettingsRaytracer:
    material0: VSettingsMaterial
    material1: VSettingsMaterial
    material2: VSettingsMaterial
    material3: VSettingsMaterial
    material4: VSettingsMaterial
    material5: VSettingsMaterial
    material6: VSettingsMaterial
    material7: VSettingsMaterial
    material8: VSettingsMaterial
    material9: VSettingsMaterial
    ambientLightColor: Tuple[float,float,float,float]
    backgroundColorReflections: Tuple[float,float,float,float]
    enable: bool
    globalFogColor: Tuple[float,float,float,float]
    globalFogDensity: float
    imageSizeFactor: int
    keepWindowActive: bool
    lightRadius: float
    lightRadiusVariations: int
    maxReflectionDepth: int
    maxTransparencyDepth: int
    numberOfThreads: int
    searchTreeFactor: int
    tilesPerThread: int
    verbose: bool
    zBiasLines: float
    zOffsetCamera: float


class VSettingsOpenGL:
    clippingPlaneColor: Tuple[float,float,float,float]
    clippingPlaneDistance: float
    clippingPlaneNormal: Tuple[float,float,float]
    depthSorting: bool
    drawFaceNormals: bool
    drawNormalsLength: float
    drawVertexNormals: bool
    enableLight0: bool
    enableLight1: bool
    enableLighting: bool
    faceEdgesColor: Tuple[float,float,float,float]
    facesTransparent: bool
    faceTransparencyGlobal: float
    initialCenterPoint: Tuple[float,float,float]
    initialMaxSceneSize: float
    initialModelRotation: ArrayLike
    initialZoom: float
    light0ambient: float
    light0constantAttenuation: float
    light0diffuse: float
    light0linearAttenuation: float
    light0position: Tuple[float,float,float,float]
    light0quadraticAttenuation: float
    light0specular: float
    light1ambient: float
    light1constantAttenuation: float
    light1diffuse: float
    light1linearAttenuation: float
    light1position: Tuple[float,float,float,float]
    light1quadraticAttenuation: float
    light1specular: float
    lightModelAmbient: Tuple[float,float,float,float]
    lightModelLocalViewer: bool
    lightModelTwoSide: bool
    lightPositionsInCameraFrame: bool
    lineSmooth: bool
    lineWidth: float
    materialAmbientAndDiffuse: Tuple[float,float,float,float]
    materialShininess: float
    materialSpecular: Tuple[float,float,float,float]
    multiSampling: int
    perspective: float
    polygonOffset: float
    shadeModelSmooth: bool
    shadow: float
    shadowPolygonOffset: float
    showFaceEdges: bool
    showFaces: bool
    showLines: bool
    showMeshEdges: bool
    showMeshFaces: bool
    textLineSmooth: bool
    textLineWidth: float


class VSettingsExportImages:
    heightAlignment: int
    saveImageAsTextCircles: bool
    saveImageAsTextLines: bool
    saveImageAsTextTexts: bool
    saveImageAsTextTriangles: bool
    saveImageFileCounter: int
    saveImageFileName: str
    saveImageFormat: str
    saveImageSingleFile: bool
    saveImageTimeOut: int
    widthAlignment: int


class VSettingsOpenVR:
    actionManifestFileName: str
    enable: bool
    logLevel: int
    showCompanionWindow: bool


class VSettingsInteractive:
    openVR: VSettingsOpenVR
    highlightColor: Tuple[float,float,float,float]
    highlightItemIndex: int
    highlightItemType: ItemType
    highlightMbsNumber: int
    highlightOtherColor: Tuple[float,float,float,float]
    joystickScaleRotation: float
    joystickScaleTranslation: float
    keypressRotationStep: float
    keypressTranslationStep: float
    lockModelView: bool
    mouseMoveRotationFactor: float
    pauseWithSpacebar: bool
    selectionHighlights: bool
    selectionLeftMouse: bool
    selectionLeftMouseItemTypes: int
    selectionRightMouse: bool
    selectionRightMouseGraphicsData: bool
    trackMarker: int
    trackMarkerMbsNumber: int
    trackMarkerOrientation: Tuple[float,float,float]
    trackMarkerPosition: Tuple[float,float,float]
    useJoystickInput: bool
    zoomStepFactor: float


class VisualizationSettings:
    bodies: VSettingsBodies
    connectors: VSettingsConnectors
    contact: VSettingsContact
    contour: VSettingsContour
    dialogs: VSettingsDialogs
    exportImages: VSettingsExportImages
    general: VSettingsGeneral
    interactive: VSettingsInteractive
    loads: VSettingsLoads
    markers: VSettingsMarkers
    nodes: VSettingsNodes
    openGL: VSettingsOpenGL
    raytracer: VSettingsRaytracer
    sensors: VSettingsSensors
    window: VSettingsWindow


class CSolverTimer:
    AERHS: float
    errorEstimator: float
    factorization: float
    integrationFormula: float
    jacobianAE: float
    jacobianODE1: float
    jacobianODE2: float
    jacobianODE2_t: float
    massMatrix: float
    newtonIncrement: float
    ODE1RHS: float
    ODE2RHS: float
    overhead: float
    postNewton: float
    python: float
    reactionForces: float
    realtimeIdleCPU: float
    @overload
    def Reset(useSolverTimer) -> None: ...
    @overload
    def StartTimer(value) -> None: ...
    @overload
    def StopTimer(value) -> None: ...
    @overload
    def Sum() -> float: ...
    @overload
    def ToString() -> str: ...
    total: float
    totalJacobian: float
    useTimer: bool
    visualization: float
    writeSolution: float


class SolverIterationData:
    adaptiveStep: bool
    automaticStepSize: bool
    automaticStepSizeError: float
    currentStepIndex: int
    currentStepSize: float
    currentTime: float
    discontinuousIteration: int
    discontinuousIterationsCount: int
    endTime: float
    initialStepSize: float
    lastStepSize: float
    maxStepSize: float
    minStepSize: float
    newtonJacobiCount: int
    newtonSteps: int
    newtonStepsCount: int
    numberOfSteps: int
    recommendedStepSize: float
    rejectedAutomaticStepSizeSteps: int
    rejectedModifiedNewtonSteps: int
    startTime: float
    @overload
    def ToString() -> str: ...


class SolverConvergenceData:
    contractivity: float
    discontinuousIterationError: float
    discontinuousIterationSuccessful: bool
    errorCoordinateFactor: float
    @overload
    def InitializeData() -> None: ...
    jacobianUpdateRequested: bool
    lastResidual: float
    linearSolverCausingRow: int
    linearSolverFailed: bool
    massMatrixNotInvertible: bool
    newtonConverged: bool
    newtonSolutionDiverged: bool
    residual: float
    stepReductionFailed: bool
    stopNewton: bool


class SolverOutputData:
    cpuLastTimePrinted: float
    cpuStartTime: float
    finishedSuccessfully: bool
    initializationSuccessful: bool
    @overload
    def InitializeData() -> None: ...
    lastDiscontinuousIterationsCount: int
    lastImageRecorded: float
    lastNewtonJacobiCount: int
    lastNewtonStepsCount: int
    lastSensorsWritten: float
    lastSolutionWritten: float
    lastVerboseStepIndex: int
    multiThreadingMode: int
    numberOfThreadsUsed: int
    stepInformation: int
    verboseMode: int
    verboseModeFile: int
    writeToSolutionFile: bool
    writeToSolverFile: bool


class MainSolverStatic:
    conv: SolverConvergenceData
    it: SolverIterationData
    newton: NewtonSettings
    output: SolverOutputData
    timer: CSolverTimer
    @overload
    def CheckInitialized(mainSystem) -> bool: ...
    @overload
    def ComputeAlgebraicEquations(mainSystem, velocityLevel=False) -> None: ...
    @overload
    def ComputeJacobianAE(mainSystem, scalarFactor_ODE2=1., scalarFactor_ODE2_t=0., scalarFactor_ODE1=1., velocityLevel=False) -> None: ...
    @overload
    def ComputeJacobianODE1RHS(mainSystem, scalarFactor_ODE2=1., scalarFactor_ODE2_t=0., scalarFactor_ODE1=1.) -> None: ...
    @overload
    def ComputeJacobianODE2RHS(mainSystem, scalarFactor_ODE2=1., scalarFactor_ODE2_t=0., scalarFactor_ODE1=1., computeLoadsJacobian=0) -> None: ...
    @overload
    def ComputeLoadFactor(simulationSettings) -> float: ...
    @overload
    def ComputeMassMatrix(mainSystem, scalarFactor=1.) -> None: ...
    @overload
    def ComputeNewtonJacobian(mainSystem, simulationSettings) -> None: ...
    @overload
    def ComputeNewtonResidual(mainSystem, simulationSettings) -> float: ...
    @overload
    def ComputeNewtonUpdate(mainSystem, simulationSettings, initial=True) -> None: ...
    @overload
    def ComputeODE2RHS(mainSystem) -> None: ...
    @overload
    def DiscontinuousIteration(mainSystem, simulationSettings) -> bool: ...
    @overload
    def FinalizeSolver(mainSystem, simulationSettings) -> None: ...
    @overload
    def FinishStep(mainSystem, simulationSettings) -> None: ...
    @overload
    def GetAEsize() -> int: ...
    @overload
    def GetDataSize() -> int: ...
    @overload
    def GetErrorString() -> str: ...
    @overload
    def GetNewtonSolution() -> ArrayLike: ...
    @overload
    def GetODE1size() -> int: ...
    @overload
    def GetODE2size() -> int: ...
    @overload
    def GetSimulationEndTime(simulationSettings) -> float: ...
    @overload
    def GetSolverName() -> str: ...
    @overload
    def GetSystemJacobian() -> ArrayLike: ...
    @overload
    def GetSystemMassMatrix() -> ArrayLike: ...
    @overload
    def GetSystemResidual() -> ArrayLike: ...
    @overload
    def HasAutomaticStepSizeControl(mainSystem, simulationSettings) -> bool: ...
    @overload
    def IncreaseStepSize(mainSystem, simulationSettings) -> None: ...
    @overload
    def InitializeSolver(mainSystem, simulationSettings) -> bool: ...
    @overload
    def InitializeSolverData(mainSystem, simulationSettings) -> None: ...
    @overload
    def InitializeSolverInitialConditions(mainSystem, simulationSettings) -> None: ...
    @overload
    def InitializeSolverOutput(mainSystem, simulationSettings) -> None: ...
    @overload
    def InitializeSolverPreChecks(mainSystem, simulationSettings) -> bool: ...
    @overload
    def InitializeStep(mainSystem, simulationSettings) -> None: ...
    @overload
    def IsStaticSolver() -> bool: ...
    @overload
    def IsVerboseCheck(level) -> bool: ...
    loadStepGeometricFactor: float
    @overload
    def Newton(mainSystem, simulationSettings) -> bool: ...
    @overload
    def PostInitializeSolverSpecific(mainSystem, simulationSettings) -> None: ...
    @overload
    def PreInitializeSolverSpecific(mainSystem, simulationSettings) -> None: ...
    @overload
    def ReduceStepSize(mainSystem, simulationSettings, severity) -> bool: ...
    @overload
    def SetSystemJacobian(systemJacobian) -> None: ...
    @overload
    def SetSystemMassMatrix(systemMassMatrix) -> None: ...
    @overload
    def SetSystemResidual(systemResidual) -> None: ...
    @overload
    def SolveSteps(mainSystem, simulationSettings) -> bool: ...
    @overload
    def SolveSystem(mainSystem, simulationSettings) -> bool: ...
    @overload
    def UpdateCurrentTime(mainSystem, simulationSettings) -> None: ...
    @overload
    def VerboseWrite(level, str) -> None: ...
    @overload
    def WriteCoordinatesToFile(mainSystem, simulationSettings) -> None: ...
    @overload
    def WriteSolutionFileHeader(mainSystem, simulationSettings) -> None: ...


class MainSolverImplicitSecondOrder:
    conv: SolverConvergenceData
    it: SolverIterationData
    newton: NewtonSettings
    output: SolverOutputData
    timer: CSolverTimer
    alphaF: float
    alphaM: float
    @overload
    def CheckInitialized(mainSystem) -> bool: ...
    @overload
    def ComputeAlgebraicEquations(mainSystem, velocityLevel=False) -> None: ...
    @overload
    def ComputeJacobianAE(mainSystem, scalarFactor_ODE2=1., scalarFactor_ODE2_t=0., scalarFactor_ODE1=1., velocityLevel=False) -> None: ...
    @overload
    def ComputeJacobianODE1RHS(mainSystem, scalarFactor_ODE2=1., scalarFactor_ODE2_t=0., scalarFactor_ODE1=1.) -> None: ...
    @overload
    def ComputeJacobianODE2RHS(mainSystem, scalarFactor_ODE2=1., scalarFactor_ODE2_t=0., scalarFactor_ODE1=1., computeLoadsJacobian=0) -> None: ...
    @overload
    def ComputeLoadFactor(simulationSettings) -> float: ...
    @overload
    def ComputeMassMatrix(mainSystem, scalarFactor=1.) -> None: ...
    @overload
    def ComputeNewtonJacobian(mainSystem, simulationSettings) -> None: ...
    @overload
    def ComputeNewtonResidual(mainSystem, simulationSettings) -> float: ...
    @overload
    def ComputeNewtonUpdate(mainSystem, simulationSettings, initial=True) -> None: ...
    @overload
    def ComputeODE1RHS(mainSystem) -> None: ...
    @overload
    def ComputeODE2RHS(mainSystem) -> None: ...
    @overload
    def DiscontinuousIteration(mainSystem, simulationSettings) -> bool: ...
    factJacAlgorithmic: float
    @overload
    def FinalizeSolver(mainSystem, simulationSettings) -> None: ...
    @overload
    def FinishStep(mainSystem, simulationSettings) -> None: ...
    @overload
    def GetAAlgorithmic() -> ArrayLike: ...
    @overload
    def GetAEsize() -> int: ...
    @overload
    def GetDataSize() -> int: ...
    @overload
    def GetErrorString() -> str: ...
    @overload
    def GetNewtonSolution() -> ArrayLike: ...
    @overload
    def GetODE1size() -> int: ...
    @overload
    def GetODE2size() -> int: ...
    @overload
    def GetSimulationEndTime(simulationSettings) -> float: ...
    @overload
    def GetSolverName() -> str: ...
    @overload
    def GetStartOfStepStateAAlgorithmic() -> ArrayLike: ...
    @overload
    def GetSystemJacobian() -> ArrayLike: ...
    @overload
    def GetSystemMassMatrix() -> ArrayLike: ...
    @overload
    def GetSystemResidual() -> ArrayLike: ...
    @overload
    def HasAutomaticStepSizeControl(mainSystem, simulationSettings) -> bool: ...
    @overload
    def IncreaseStepSize(mainSystem, simulationSettings) -> None: ...
    @overload
    def InitializeSolver(mainSystem, simulationSettings) -> bool: ...
    @overload
    def InitializeSolverData(mainSystem, simulationSettings) -> None: ...
    @overload
    def InitializeSolverInitialConditions(mainSystem, simulationSettings) -> None: ...
    @overload
    def InitializeSolverOutput(mainSystem, simulationSettings) -> None: ...
    @overload
    def InitializeSolverPreChecks(mainSystem, simulationSettings) -> bool: ...
    @overload
    def InitializeStep(mainSystem, simulationSettings) -> None: ...
    @overload
    def IsStaticSolver() -> bool: ...
    @overload
    def IsVerboseCheck(level) -> bool: ...
    newmarkBeta: float
    newmarkGamma: float
    @overload
    def Newton(mainSystem, simulationSettings) -> bool: ...
    @overload
    def PostInitializeSolverSpecific(mainSystem, simulationSettings) -> None: ...
    @overload
    def PostNewton(mainSystem, simulationSettings) -> float: ...
    @overload
    def PreInitializeSolverSpecific(mainSystem, simulationSettings) -> None: ...
    @overload
    def ReduceStepSize(mainSystem, simulationSettings, severity) -> bool: ...
    @overload
    def SetSystemJacobian(systemJacobian) -> None: ...
    @overload
    def SetSystemMassMatrix(systemMassMatrix) -> None: ...
    @overload
    def SetSystemResidual(systemResidual) -> None: ...
    @overload
    def SetUserFunctionComputeNewtonJacobian(mainSystem, userFunction) -> None: ...
    @overload
    def SetUserFunctionComputeNewtonResidual(mainSystem, userFunction) -> None: ...
    @overload
    def SetUserFunctionComputeNewtonUpdate(mainSystem, userFunction) -> None: ...
    @overload
    def SetUserFunctionDiscontinuousIteration(mainSystem, userFunction) -> None: ...
    @overload
    def SetUserFunctionFinishStep(mainSystem, userFunction) -> None: ...
    @overload
    def SetUserFunctionInitializeStep(mainSystem, userFunction) -> None: ...
    @overload
    def SetUserFunctionNewton(mainSystem, userFunction) -> None: ...
    @overload
    def SetUserFunctionPostNewton(mainSystem, userFunction) -> None: ...
    @overload
    def SetUserFunctionUpdateCurrentTime(mainSystem, userFunction) -> None: ...
    @overload
    def SolveSteps(mainSystem, simulationSettings) -> bool: ...
    @overload
    def SolveSystem(mainSystem, simulationSettings) -> bool: ...
    spectralRadius: float
    @overload
    def UpdateCurrentTime(mainSystem, simulationSettings) -> None: ...
    @overload
    def VerboseWrite(level, str) -> None: ...
    @overload
    def WriteCoordinatesToFile(mainSystem, simulationSettings) -> None: ...
    @overload
    def WriteSolutionFileHeader(mainSystem, simulationSettings) -> None: ...


class MainSolverExplicit:
    conv: SolverConvergenceData
    it: SolverIterationData
    output: SolverOutputData
    timer: CSolverTimer
    @overload
    def ComputeLoadFactor(simulationSettings) -> float: ...
    @overload
    def ComputeMassMatrix(mainSystem, scalarFactor=1.) -> None: ...
    @overload
    def ComputeNewtonJacobian(mainSystem, simulationSettings) -> None: ...
    @overload
    def ComputeNewtonResidual(mainSystem, simulationSettings) -> float: ...
    @overload
    def ComputeNewtonUpdate(mainSystem, simulationSettings, initial=True) -> None: ...
    @overload
    def ComputeODE1RHS(mainSystem) -> None: ...
    @overload
    def ComputeODE2RHS(mainSystem) -> None: ...
    @overload
    def DiscontinuousIteration(mainSystem, simulationSettings) -> bool: ...
    @overload
    def FinalizeSolver(mainSystem, simulationSettings) -> None: ...
    @overload
    def FinishStep(mainSystem, simulationSettings) -> None: ...
    @overload
    def GetAEsize() -> int: ...
    @overload
    def GetDataSize() -> int: ...
    @overload
    def GetErrorString() -> str: ...
    @overload
    def GetMethodOrder() -> int: ...
    @overload
    def GetNumberOfStages() -> int: ...
    @overload
    def GetODE1size() -> int: ...
    @overload
    def GetODE2size() -> int: ...
    @overload
    def GetSimulationEndTime(simulationSettings) -> float: ...
    @overload
    def GetSolverName() -> str: ...
    @overload
    def GetSystemMassMatrix() -> ArrayLike: ...
    @overload
    def GetSystemResidual() -> ArrayLike: ...
    @overload
    def HasAutomaticStepSizeControl(mainSystem, simulationSettings) -> bool: ...
    @overload
    def IncreaseStepSize(mainSystem, simulationSettings) -> None: ...
    @overload
    def InitializeSolver(mainSystem, simulationSettings) -> bool: ...
    @overload
    def InitializeSolverData(mainSystem, simulationSettings) -> None: ...
    @overload
    def InitializeSolverInitialConditions(mainSystem, simulationSettings) -> None: ...
    @overload
    def InitializeSolverOutput(mainSystem, simulationSettings) -> None: ...
    @overload
    def InitializeSolverPreChecks(mainSystem, simulationSettings) -> bool: ...
    @overload
    def InitializeStep(mainSystem, simulationSettings) -> None: ...
    @overload
    def IsStaticSolver() -> bool: ...
    @overload
    def IsVerboseCheck(level) -> bool: ...
    @overload
    def Newton(mainSystem, simulationSettings) -> bool: ...
    @overload
    def PostInitializeSolverSpecific(mainSystem, simulationSettings) -> None: ...
    @overload
    def PreInitializeSolverSpecific(mainSystem, simulationSettings) -> None: ...
    @overload
    def ReduceStepSize(mainSystem, simulationSettings, severity) -> bool: ...
    @overload
    def SetSystemMassMatrix(systemMassMatrix) -> None: ...
    @overload
    def SetSystemResidual(systemResidual) -> None: ...
    @overload
    def SolveSteps(mainSystem, simulationSettings) -> bool: ...
    @overload
    def SolveSystem(mainSystem, simulationSettings) -> bool: ...
    @overload
    def UpdateCurrentTime(mainSystem, simulationSettings) -> None: ...
    @overload
    def VerboseWrite(level, str) -> None: ...
    @overload
    def WriteCoordinatesToFile(mainSystem, simulationSettings) -> None: ...
    @overload
    def WriteSolutionFileHeader(mainSystem, simulationSettings) -> None: ...


class VisuGeneralContact:
    @overload
    def Reset(self) -> None: ...


class GeneralContact:
    @overload
    def GetPythonObject(self) -> dict: ...
    @overload
    def Reset(self, freeMemory=True) -> None: ...
    isActive:bool
    verboseMode:int
    visualization:VisuGeneralContact
    resetSearchTreeInterval:int
    sphereSphereContact:bool
    sphereSphereFrictionRecycle:bool
    minRelDistanceSpheresTriangles:float
    frictionProportionalZone:float
    excludeOverlappingTrigSphereContacts:bool
    excludeDuplicatedTrigSphereContactPoints:bool
    computeExactStaticTriangleBins:bool
    computeContactForces:bool
    ancfCableUseExactMethod:bool
    ancfCableNumberOfContactSegments:int
    ancfCableMeasuringSegments:int
    parallelTaskSplit:int
    parallelTaskSplitBoundingBoxes:int
    parallelTaskSplitThreshold:int
    parallelTaskSplitBoundingBoxesThreshold:int
    @overload
    def SetFrictionPairings(self, frictionPairings: ArrayLike) -> None: ...
    @overload
    def SetFrictionProportionalZone(self, frictionProportionalZone: float) -> None: ...
    @overload
    def SetSearchTreeCellSize(self, numberOfCells: [int,int,int]) -> None: ...
    @overload
    def SetSearchTreeBox(self, pMin: [float,float,float], pMax: [float,float,float]) -> None: ...
    @overload
    def AddSphereWithMarker(self, markerIndex: MarkerIndex, radius: float, contactStiffness: float, contactDamping: float, frictionMaterialIndex: int) -> int: ...
    @overload
    def AddANCFCable(self, objectIndex: ObjectIndex, halfHeight: float, contactStiffness: float, contactDamping: float, frictionMaterialIndex: int) -> int: ...
    @overload
    def AddTrianglesRigidBodyBased(self, rigidBodyMarkerIndex: MarkerIndex, contactStiffness: float, contactDamping: float, frictionMaterialIndex: int, pointList: List[[float,float,float]], triangleList: List[[int,int,int]], staticTriangles: bool=False) -> int: ...
    @overload
    def GetItemsInBox(self, pMin: [float,float,float], pMax: [float,float,float]) -> Union[dict,bool]: ...
    @overload
    def GetSphereMarkerBased(self, localIndex: int, addData: bool=False) -> dict: ...
    @overload
    def SetSphereMarkerBased(self, localIndex: int, contactStiffness: float=-1., contactDamping: float=-1., radius: float=-1., frictionMaterialIndex: int=-1) -> None: ...
    @overload
    def GetTriangleRigidBodyBased(self, localIndex: int) -> dict: ...
    @overload
    def SetTriangleRigidBodyBased(self, localIndex: int, points: NDArray[Shape2D[3,3], float], contactRigidBodyIndex: int=-1) -> None: ...
    @overload
    def ShortestDistanceAlongLine(self, pStart: [float,float,float]=[0,0,0], direction: [float,float,float]=[1,0,0], minDistance: float=-1e-7, maxDistance: float=1e7, asDictionary: bool=False, cylinderRadius: float=0, typeIndex: ContactTypeIndex=Contact.IndexEndOfEnumList) -> Union[dict,float]: ...
    @overload
    def UpdateContacts(self, mainSystem: MainSystem) -> None: ...
    @overload
    def GetActiveContacts(self, typeIndex: ContactTypeIndex, itemIndex: int) -> List[int]: ...
    @overload
    def GetSystemODE2RhsContactForces(self, copy: bool=False) -> List[float]: ...


class SystemData:
    @overload
    def NumberOfLoads(self) -> int: ...
    @overload
    def NumberOfMarkers(self) -> int: ...
    @overload
    def NumberOfNodes(self) -> int: ...
    @overload
    def NumberOfObjects(self) -> int: ...
    @overload
    def NumberOfSensors(self) -> int: ...
    @overload
    def ODE2Size(self, configurationType: ConfigurationType=ConfigurationType.Current) -> int: ...
    @overload
    def ODE1Size(self, configurationType: ConfigurationType=ConfigurationType.Current) -> int: ...
    @overload
    def AEsize(self, configurationType: ConfigurationType=ConfigurationType.Current) -> int: ...
    @overload
    def DataSize(self, configurationType: ConfigurationType=ConfigurationType.Current) -> int: ...
    @overload
    def SystemSize(self, configurationType: ConfigurationType=ConfigurationType.Current) -> int: ...
    @overload
    def GetTime(self, configurationType: ConfigurationType=ConfigurationType.Current) -> float: ...
    @overload
    def SetTime(self, newTime: float, configurationType: ConfigurationType=ConfigurationType.Current) -> None: ...
    @overload
    def AddODE2LoadDependencies(self, loadNumber: float, globalODE2coordinates: List[int]) -> None: ...
    @overload
    def Info(self) -> None: ...
    @overload
    def InfoLTG(self) -> None: ...
    @overload
    def GetODE2CoordinatesTotal(self, configuration: ConfigurationType=ConfigurationType.Current) -> List[float]: ...
    @overload
    def GetODE2Coordinates(self, configuration: ConfigurationType=ConfigurationType.Current, copy: bool=True) -> List[float]: ...
    @overload
    def SetODE2Coordinates(self, coordinates: List[float], configuration: ConfigurationType=ConfigurationType.Current) -> None: ...
    @overload
    def GetODE2Coordinates_t(self, configuration: ConfigurationType=ConfigurationType.Current, copy: bool=True) -> List[float]: ...
    @overload
    def SetODE2Coordinates_t(self, coordinates: List[float], configuration: ConfigurationType=ConfigurationType.Current) -> None: ...
    @overload
    def GetODE2Coordinates_tt(self, configuration: ConfigurationType=ConfigurationType.Current, copy: bool=True) -> List[float]: ...
    @overload
    def SetODE2Coordinates_tt(self, coordinates: List[float], configuration: ConfigurationType=ConfigurationType.Current) -> None: ...
    @overload
    def GetODE1Coordinates(self, configuration: ConfigurationType=ConfigurationType.Current, copy: bool=True) -> List[float]: ...
    @overload
    def SetODE1Coordinates(self, coordinates: List[float], configuration: ConfigurationType=ConfigurationType.Current) -> None: ...
    @overload
    def GetODE1Coordinates_t(self, configuration: ConfigurationType=ConfigurationType.Current, copy: bool=True) -> List[float]: ...
    @overload
    def SetODE1Coordinates_t(self, coordinates: List[float], configuration: ConfigurationType=ConfigurationType.Current) -> None: ...
    @overload
    def GetAECoordinates(self, configuration: ConfigurationType=ConfigurationType.Current, copy: bool=True) -> List[float]: ...
    @overload
    def SetAECoordinates(self, coordinates: List[float], configuration: ConfigurationType=ConfigurationType.Current) -> None: ...
    @overload
    def GetDataCoordinates(self, configuration: ConfigurationType=ConfigurationType.Current, copy: bool=True) -> List[float]: ...
    @overload
    def SetDataCoordinates(self, coordinates: List[float], configuration: ConfigurationType=ConfigurationType.Current) -> None: ...
    @overload
    def GetSystemState(self, configuration: ConfigurationType=ConfigurationType.Current) -> List[List[float]]: ...
    @overload
    def SetSystemState(self, systemStateList: List[List[float]], configuration: ConfigurationType=ConfigurationType.Current) -> None: ...
    @overload
    def GetSystemStateDict(self, configuration: ConfigurationType=ConfigurationType.Current, reference: bool=False) -> Dict[List[float]]: ...
    @overload
    def GetObjectLTGODE2(self, objectNumber: int) -> List[int]: ...
    @overload
    def GetObjectLTGODE1(self, objectNumber: int) -> List[int]: ...
    @overload
    def GetObjectLTGAE(self, objectNumber: int) -> List[int]: ...
    @overload
    def GetObjectLTGData(self, objectNumber: int) -> List[int]: ...
    @overload
    def GetNodeLTGODE2(self, nodeNumber: int) -> List[int]: ...
    @overload
    def GetNodeLTGODE1(self, nodeNumber: int) -> List[int]: ...
    @overload
    def GetNodeLTGAE(self, nodeNumber: int) -> List[int]: ...
    @overload
    def GetNodeLTGData(self, nodeNumber: int) -> List[int]: ...


class MainSystem:
    @overload
    def Assemble(self) -> None: ...
    @overload
    def AssembleCoordinates(self) -> None: ...
    @overload
    def AssembleLTGLists(self) -> None: ...
    @overload
    def AssembleInitializeSystemCoordinates(self) -> None: ...
    @overload
    def AssembleSystemInitialize(self) -> None: ...
    @overload
    def Reset(self) -> None: ...
    @overload
    def GetSystemContainer(self) -> SystemContainer: ...
    @overload
    def SendRedrawSignal(self) -> None: ...
    @overload
    def GetRenderEngineStopFlag(self) -> bool: ...
    @overload
    def SetRenderEngineStopFlag(self, stopFlag: bool) -> None: ...
    @overload
    def ActivateRendering(self, flag: bool=True) -> None: ...
    @overload
    def SetPreStepUserFunction(self, value: Callable[[MainSystem, float],bool]) -> None: ...
    @overload
    def GetPreStepUserFunction(self, asDict: bool=False) -> Callable[[MainSystem, float],bool]: ...
    @overload
    def SetPostStepUserFunction(self, value: Callable[[MainSystem, float],bool]) -> None: ...
    @overload
    def GetPostStepUserFunction(self, asDict: bool=False) -> Callable[[MainSystem, float],bool]: ...
    @overload
    def SetPostNewtonUserFunction(self, value: Callable[[MainSystem, float],[float,float]]) -> None: ...
    @overload
    def GetPostNewtonUserFunction(self, asDict: bool=False) -> Callable[[MainSystem, float],bool]: ...
    @overload
    def SetPreNewtonResidualUserFunction(self, value: Callable[[MainSystem, float, int, int],None]) -> None: ...
    @overload
    def GetPreNewtonResidualUserFunction(self, asDict: bool=False) -> Callable[[MainSystem, float, int, int],None]: ...
    @overload
    def SetSystemJacobianUserFunction(self, value: Callable[[MainSystem, float, float, float, float],Any]) -> None: ...
    @overload
    def GetSystemJacobianUserFunction(self, asDict: bool=False) -> Callable[[MainSystem, float, float, float, float],Any]: ...
    @overload
    def AddGeneralContact(self) -> GeneralContact: ...
    @overload
    def GetGeneralContact(self, generalContactNumber: int) -> GeneralContact: ...
    @overload
    def DeleteGeneralContact(self, generalContactNumber: int) -> None: ...
    @overload
    def NumberOfGeneralContacts(self) -> int: ...
    @overload
    def GetAvailableFactoryItems(self) -> dict: ...
    @overload
    def GetDictionary(self) -> dict: ...
    @overload
    def SetDictionary(self, systemDict: dict) -> None: ...
    systemIsConsistent:bool
    interactiveMode:bool
    variables:dict
    sys:dict
    solverSignalJacobianUpdate:bool
    systemData:SystemData
    @overload
    def AddNode(self, pyObject: Any) -> NodeIndex: ...
    @overload
    def DeleteNode(self, nodeNumber, suppressWarnings=False) -> None: ...
    @overload
    def GetNodeNumber(self, nodeName: str) -> NodeIndex: ...
    @overload
    def GetNode(self, nodeNumber: NodeIndex) -> dict: ...
    @overload
    def ModifyNode(self, nodeNumber: NodeIndex, nodeDict: dict) -> None: ...
    @overload
    def GetNodeDefaults(self, typeName: str) -> dict: ...
    @overload
    def GetNodeOutput(self, nodeNumber: NodeIndex, variableType: OutputVariableType, configuration: ConfigurationType=ConfigurationType.Current) -> List[float]: ...
    @overload
    def GetNodeODE2Index(self, nodeNumber: NodeIndex) -> int: ...
    @overload
    def GetNodeODE1Index(self, nodeNumber: NodeIndex) -> int: ...
    @overload
    def GetNodeAEIndex(self, nodeNumber: NodeIndex) -> int: ...
    @overload
    def GetNodeParameter(self, nodeNumber: NodeIndex, parameterName: str) -> Any: ...
    @overload
    def SetNodeParameter(self, nodeNumber: NodeIndex, parameterName: str, value: Any) -> None: ...
    @overload
    def AddObject(self, pyObject: Any) -> ObjectIndex: ...
    @overload
    def DeleteObject(self, objectNumber: ObjectIndex, deleteDependentItems: bool=True, suppressWarnings: bool=False) -> None: ...
    @overload
    def GetObjectNumber(self, objectName: str) -> ObjectIndex: ...
    @overload
    def GetObject(self, objectNumber: ObjectIndex, addGraphicsData: bool=False) -> dict: ...
    @overload
    def ModifyObject(self, objectNumber: ObjectIndex, objectDict: dict) -> None: ...
    @overload
    def GetObjectDefaults(self, typeName: str) -> dict: ...
    @overload
    def GetObjectOutput(self, objectNumber: ObjectIndex, variableType: OutputVariableType, configuration: ConfigurationType=ConfigurationType.Current) -> List[float]: ...
    @overload
    def GetObjectOutputBody(self, objectNumber: ObjectIndex, variableType: OutputVariableType, localPosition: [float,float,float]=[0,0,0], configuration: ConfigurationType=ConfigurationType.Current) -> List[float]: ...
    @overload
    def GetObjectOutputSuperElement(self, objectNumber: ObjectIndex, variableType: OutputVariableType, meshNodeNumber: int, configuration: ConfigurationType=ConfigurationType.Current) -> List[float]: ...
    @overload
    def GetObjectParameter(self, objectNumber: ObjectIndex, parameterName: str) -> Any: ...
    @overload
    def SetObjectParameter(self, objectNumber: ObjectIndex, parameterName: str, value: Any) -> None: ...
    @overload
    def AddMarker(self, pyObject: Any) -> MarkerIndex: ...
    @overload
    def DeleteMarker(self, markerNumber: MarkerIndex, suppressWarnings: bool=False) -> None: ...
    @overload
    def GetMarkerNumber(self, markerName: str) -> MarkerIndex: ...
    @overload
    def GetMarker(self, markerNumber: MarkerIndex) -> dict: ...
    @overload
    def ModifyMarker(self, markerNumber: MarkerIndex, markerDict: dict) -> None: ...
    @overload
    def GetMarkerDefaults(self, typeName: str) -> dict: ...
    @overload
    def GetMarkerParameter(self, markerNumber: MarkerIndex, parameterName: str) -> Any: ...
    @overload
    def SetMarkerParameter(self, markerNumber: MarkerIndex, parameterName: str, value: Any) -> None: ...
    @overload
    def GetMarkerOutput(self, markerNumber: MarkerIndex, variableType: OutputVariableType, configuration: ConfigurationType=ConfigurationType.Current) -> List[float]: ...
    @overload
    def AddLoad(self, pyObject: Any) -> LoadIndex: ...
    @overload
    def DeleteLoad(self, loadNumber: LoadIndex, deleteDependentMarkers: bool=True, suppressWarnings: bool=False) -> None: ...
    @overload
    def GetLoadNumber(self, loadName: str) -> LoadIndex: ...
    @overload
    def GetLoad(self, loadNumber: LoadIndex) -> dict: ...
    @overload
    def ModifyLoad(self, loadNumber: LoadIndex, loadDict: dict) -> None: ...
    @overload
    def GetLoadDefaults(self, typeName: str) -> dict: ...
    @overload
    def GetLoadValues(self, loadNumber: LoadIndex) -> List[float]: ...
    @overload
    def GetLoadParameter(self, loadNumber: LoadIndex, parameterName: str) -> Any: ...
    @overload
    def SetLoadParameter(self, loadNumber: LoadIndex, parameterName: str, value: Any) -> None: ...
    @overload
    def AddSensor(self, pyObject: Any) -> SensorIndex: ...
    @overload
    def DeleteSensor(self, sensorNumber, suppressWarnings=False) -> None: ...
    @overload
    def GetSensorNumber(self, sensorName: str) -> SensorIndex: ...
    @overload
    def GetSensor(self, sensorNumber: SensorIndex) -> dict: ...
    @overload
    def ModifySensor(self, sensorNumber: SensorIndex, sensorDict: dict) -> None: ...
    @overload
    def GetSensorDefaults(self, typeName: str) -> dict: ...
    @overload
    def GetSensorValues(self, sensorNumber: SensorIndex, configuration: ConfigurationType=ConfigurationType.Current) -> List[float]: ...
    @overload
    def GetSensorStoredData(self, sensorNumber: SensorIndex) -> ArrayLike: ...
    @overload
    def GetSensorParameter(self, sensorNumber: SensorIndex, parameterName: str) -> Any: ...
    @overload
    def SetSensorParameter(self, sensorNumber: SensorIndex, parameterName: str, value: Any) -> None: ...

    @overload
    def SolutionViewer(self, solution=None, rowIncrement=1, timeout=0.04, runOnStart=True, runMode=2, fontSize=12, title='', checkRenderEngineStopFlag=True) -> None: ...

    @overload
    def CreateGround(self, name='', referencePosition=[0.,0.,0.], referenceRotationMatrix=np.eye(3), graphicsDataList=[], graphicsDataUserFunction=0, show=True) -> ObjectIndex: ...

    @overload
    def CreateMassPoint(self, name='', referencePosition=[0.,0.,0.], initialDisplacement=[0.,0.,0.], initialVelocity=[0.,0.,0.], physicsMass=0, gravity=[0.,0.,0.], graphicsDataList=[], drawSize=-1, color=[-1.,-1.,-1.,-1.], show=True, create2D=False, returnDict=False) -> Union[dict, ObjectIndex]: ...

    @overload
    def CreateRigidBody(self, name='', referencePosition=[0.,0.,0.], referenceRotationMatrix=np.eye(3), initialVelocity=[0.,0.,0.], initialAngularVelocity=[0.,0.,0.], initialDisplacement=None, initialRotationMatrix=None, inertia=None, gravity=[0.,0.,0.], nodeType=exudyn.NodeType.RotationEulerParameters, graphicsDataList=[], graphicsDataUserFunction=0, drawSize=-1, color=[-1.,-1.,-1.,-1.], show=True, create2D=False, returnDict=False) -> Union[dict, ObjectIndex]: ...

    @overload
    def CreateSpringDamper(self, name='', bodyNumbers=[None, None], localPosition0=[0.,0.,0.], localPosition1=[0.,0.,0.], referenceLength=None, stiffness=0., damping=0., force=0., velocityOffset=0., springForceUserFunction=0, bodyOrNodeList=[None, None], bodyList=[None, None], show=True, drawSize=-1, color=exudyn.graphics.color.default) -> ObjectIndex: ...

    @overload
    def CreateCartesianSpringDamper(self, name='', bodyNumbers=[None, None], localPosition0=[0.,0.,0.], localPosition1=[0.,0.,0.], stiffness=[0.,0.,0.], damping=[0.,0.,0.], offset=[0.,0.,0.], springForceUserFunction=0, bodyOrNodeList=[None, None], bodyList=[None, None], show=True, drawSize=-1, color=exudyn.graphics.color.default) -> ObjectIndex: ...

    @overload
    def CreateRigidBodySpringDamper(self, name='', bodyNumbers=[None, None], localPosition0=[0.,0.,0.], localPosition1=[0.,0.,0.], stiffness=np.zeros((6,6)), damping=np.zeros((6,6)), offset=[0.,0.,0.,0.,0.,0.], rotationMatrixJoint=np.eye(3), useGlobalFrame=True, intrinsicFormulation=True, springForceTorqueUserFunction=0, postNewtonStepUserFunction=0, bodyOrNodeList=[None, None], bodyList=[None, None], show=True, drawSize=-1, color=exudyn.graphics.color.default) -> ObjectIndex: ...

    @overload
    def CreateTorsionalSpringDamper(self, name='', bodyNumbers=[None, None], position=[0.,0.,0.], axis=[0.,0.,0.], stiffness=0., damping=0., offset=0., velocityOffset=0., torque=0., useGlobalFrame=True, springTorqueUserFunction=0, unlimitedRotations=True, show=True, drawSize=-1, color=exudyn.graphics.color.default) -> ObjectIndex: ...

    @overload
    def CreateRevoluteJoint(self, name='', bodyNumbers=[None, None], position=[], axis=[], useGlobalFrame=True, show=True, axisRadius=0.1, axisLength=0.4, color=exudyn.graphics.color.default) -> ObjectIndex: ...

    @overload
    def CreatePrismaticJoint(self, name='', bodyNumbers=[None, None], position=[], axis=[], useGlobalFrame=True, show=True, axisRadius=0.1, axisLength=0.4, color=exudyn.graphics.color.default) -> ObjectIndex: ...

    @overload
    def CreateSphericalJoint(self, name='', bodyNumbers=[None, None], position=[], constrainedAxes=[1,1,1], useGlobalFrame=True, show=True, jointRadius=0.1, color=exudyn.graphics.color.default) -> ObjectIndex: ...

    @overload
    def CreateGenericJoint(self, name='', bodyNumbers=[None, None], position=[], rotationMatrixAxes=np.eye(3), constrainedAxes=[1,1,1, 1,1,1], useGlobalFrame=True, offsetUserFunction=0, offsetUserFunction_t=0, show=True, axesRadius=0.1, axesLength=0.4, color=exudyn.graphics.color.default) -> ObjectIndex: ...

    @overload
    def CreateDistanceConstraint(self, name='', bodyNumbers=[None, None], localPosition0=[0.,0.,0.], localPosition1=[0.,0.,0.], distance=None, bodyOrNodeList=[None, None], bodyList=[None, None], show=True, drawSize=-1., color=exudyn.graphics.color.default) -> ObjectIndex: ...

    @overload
    def CreateCoordinateConstraint(self, name='', bodyNumbers=[None, None], coordinates=[None, None], offset=0., factorValue1=1., velocityLevel=False, offsetUserFunction=0, offsetUserFunction_t=0, show=True, drawSize=-1., color=exudyn.graphics.color.default) -> ObjectIndex: ...

    @overload
    def CreateRollingDisc(self, name='', bodyNumbers=[None, None], axisPosition=[], axisVector=[1,0,0], discRadius=0., planePosition=[0,0,0], planeNormal=[0,0,1], constrainedAxes=[1,1,1], activeConnector=True, show=True, discWidth=0.1, color=exudyn.graphics.color.default) -> ObjectIndex: ...

    @overload
    def CreateRollingDiscPenalty(self, name='', bodyNumbers=[None, None], axisPosition=[], axisVector=[1,0,0], discRadius=0., planePosition=[0,0,0], planeNormal=[0,0,1], contactStiffness=0., contactDamping=0., dryFriction=[0,0], dryFrictionAngle=0., dryFrictionProportionalZone=0., viscousFriction=[0,0], rollingFrictionViscous=0., useLinearProportionalZone=False, activeConnector=True, show=True, discWidth=0.1, color=exudyn.graphics.color.default) -> ObjectIndex: ...

    @overload
    def CreateSphereSphereContact(self, name='', bodyNumbers=[None, None], localPosition0=[0.,0.,0.], localPosition1=[0.,0.,0.], spheresRadii=[-1,-1], isHollowSphere1=False, dynamicFriction=0., frictionProportionalZone=1e-3, contactStiffness=0., contactDamping=0., contactStiffnessExponent=1, constantPullOffForce=0, contactPlasticityRatio=0, adhesionCoefficient=0, adhesionExponent=1, restitutionCoefficient=1, minimumImpactVelocity=0, impactModel=0, dataInitialCoordinates=[0,0,0,0], activeConnector=True, bodyOrNodeList=[None, None], show=False, color=exudyn.graphics.color.default) -> ObjectIndex: ...

    @overload
    def CreateSphereQuadContact(self, name='', bodyNumbers=[None, None], localPosition0=[0.,0.,0.], radiusSphere=0, quadPoints=exudyn.Vector3DList([[0,0,0],[1,0,0],[1,1,0],[0,1,0]]), includeEdges=15, dynamicFriction=0., frictionProportionalZone=1e-3, contactStiffness=0., contactDamping=0., contactStiffnessExponent=1, restitutionCoefficient=1, minimumImpactVelocity=0, impactModel=0, dataInitialCoordinates=[0,0,0,0], activeConnector=True, bodyOrNodeList=[None, None], localPosition1=[0.,0.,0.], show=False, color=exudyn.graphics.color.default) -> dict containing oContact0 and oContact1 with ObjectIndex of each contact object: ...

    @overload
    def CreateSphereTriangleContact(self, name='', bodyNumbers=[None, None], localPosition0=[0.,0.,0.], radiusSphere=0, trianglePoints=exudyn.Vector3DList([[0,0,0],[1,0,0],[0,1,0]]), includeEdges=7, dynamicFriction=0., frictionProportionalZone=1e-3, contactStiffness=0., contactDamping=0., contactStiffnessExponent=1, restitutionCoefficient=1, minimumImpactVelocity=0, impactModel=0, dataInitialCoordinates=[0,0,0,0], activeConnector=True, bodyOrNodeList=[None, None], localPosition1=[0.,0.,0.], show=False, color=exudyn.graphics.color.default) -> ObjectIndex: ...

    @overload
    def CreateKinematicTree(self, name='', listOfTreeLinks=[], referenceCoordinates=None, initialCoordinates=None, initialCoordinates_t=None, gravity=[0.,0.,0.], baseOffset=[0.,0.,0.], linkForces=None, linkTorques=None, jointForceVector=None, jointPositionOffsetVector=None, jointVelocityOffsetVector=None, forceUserFunction=0, jointRadius=0.05, jointWidth=0.12, colors=exudyn.graphics.color.default, colorsJoints=exudyn.graphics.color.default, baseGraphicsDataList=None, linkRoundness=0.2, show=True) -> ObjectIndex: ...

    @overload
    def CreateForce(self, name='', bodyNumber=None, loadVector=[0.,0.,0.], localPosition=[0.,0.,0.], bodyFixed=False, loadVectorUserFunction=0, show=True) -> LoadIndex: ...

    @overload
    def CreateTorque(self, name='', bodyNumber=None, loadVector=[0.,0.,0.], localPosition=[0.,0.,0.], bodyFixed=False, loadVectorUserFunction=0, show=True) -> LoadIndex: ...

    @overload
    def PlotSensor(self, sensorNumbers=[], components=0, xLabel='time (s)', yLabel=None, labels=[], colorCodeOffset=0, newFigure=True, closeAll=False, componentsX=[], title='', figureName='', fontSize=16, colors=[], lineStyles=[], lineWidths=[], markerStyles=[], markerSizes=[], markerDensity=0.08, rangeX=[], rangeY=[], majorTicksX=10, majorTicksY=10, offsets=[], factors=[], subPlot=[], sizeInches=[6.4,4.8], fileName='', useXYZcomponents=True, **kwargs) -> [Any, Any, Any, Any]: ...

    @overload
    def SolveStatic(self, simulationSettings=exudyn.SimulationSettings(), updateInitialValues=False, storeSolver=True, showHints=False, showCausingItems=True, autoAssemble=True) -> bool: ...

    @overload
    def SolveDynamic(self, simulationSettings=exudyn.SimulationSettings(), solverType=exudyn.DynamicSolverType.GeneralizedAlpha, updateInitialValues=False, storeSolver=True, showHints=False, showCausingItems=True, autoAssemble=True) -> bool: ...

    @overload
    def ComputeLinearizedSystem(self, simulationSettings=exudyn.SimulationSettings(), projectIntoConstraintNullspace=False, singularValuesTolerance=1e-12, returnConstraintJacobian=False, returnConstraintNullspace=False, autoAssemble=True) -> [ArrayLike, ArrayLike, ArrayLike]: ...

    @overload
    def ComputeODE2Eigenvalues(self, simulationSettings=exudyn.SimulationSettings(), useSparseSolver=False, numberOfEigenvalues=0, constrainedCoordinates=[], convert2Frequencies=False, useAbsoluteValues=True, computeComplexEigenvalues=False, ignoreAlgebraicEquations=False, singularValuesTolerance=1e-12, autoAssemble=True) -> [ArrayLike, ArrayLike]: ...

    @overload
    def ComputeSystemDegreeOfFreedom(self, simulationSettings=exudyn.SimulationSettings(), threshold=1e-12, verbose=False, useSVD=False, autoAssemble=True) -> dict: ...

    @overload
    def CreateDistanceSensorGeometry(self, meshPoints, meshTrigs, rigidBodyMarkerIndex, searchTreeCellSize=[8,8,8]) -> int: ...

    @overload
    def CreateDistanceSensor(self, generalContactIndex, positionOrMarker, dirSensor, minDistance=-1e7, maxDistance=1e7, cylinderRadius=0, selectedTypeIndex=exudyn.ContactTypeIndex.IndexEndOfEnumList, storeInternal=False, fileName='', measureVelocity=False, addGraphicsObject=False, drawDisplaced=True, color=exudyn.graphics.color.red) -> SensorIndex: ...

    @overload
    def DrawSystemGraph(self, showLoads=True, showSensors=True, useItemNames=False, useItemTypes=False, addItemTypeNames=True, multiLine=True, fontSizeFactor=1., layoutDistanceFactor=3., layoutIterations=100, showLegend=True, tightLayout=True) -> [Any, Any, Any]: ...


class Renderer:
    @overload
    def Start(self, verbose=0) -> bool: ...
    @overload
    def Stop(self) -> None: ...
    @overload
    def IsActive(self) -> bool: ...
    @overload
    def Attach(self) -> bool: ...
    @overload
    def Detach(self) -> bool: ...
    @overload
    def DoIdleTasks(self, waitSeconds: float=-1., printPauseMessage: bool=True) -> bool: ...
    @overload
    def ZoomAll(self) -> None: ...
    @overload
    def RedrawAndSaveImage(self) -> None: ...
    @overload
    def SendRedrawSignal(self) -> None: ...
    @overload
    def GetRenderCount(self) -> bool: ...
    @overload
    def GetState(self) -> dict: ...
    @overload
    def SetState(self, renderState: dict, waitForRendererFullStartup: bool=True) -> None: ...
    @overload
    def GetMouseCoordinates(self, useOpenGLcoordinates: bool=False) -> [float,float]: ...
    @overload
    def GetItemSelection(self, resetSelection: bool=True) -> [int,int,int,float]: ...
    materials:GraphicsMaterialList


class SystemContainer:
    @overload
    def Reset(self) -> None: ...
    @overload
    def AddSystem(self) -> MainSystem: ...
    @overload
    def Append(self, mainSystem: MainSystem) -> int: ...
    @overload
    def NumberOfSystems(self) -> int: ...
    @overload
    def GetSystem(self, systemNumber: int) -> MainSystem: ...
    visualizationSettings:VisualizationSettings
    @overload
    def GetDictionary(self) -> dict: ...
    @overload
    def SetDictionary(self, systemDict: dict) -> None: ...
    renderer:Renderer
    visualizationSettings:VisualizationSettings

