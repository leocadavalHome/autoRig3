import pymel.core as pm
import maya.api.OpenMaya as om
import copy
import operator
import logging
import copy

logger = logging.getLogger('autoRig')

def vtxWalking():
    '''
        walk:
        selecionar o edge loop da mesh base

        criar uma curva a partir da selecao de edge
        um sistema de motion path sai criando locators espacados na curva
        crio uma nova curva a partir dos locators, essa vai ser a base do guide

    :return:
    '''

    edgeList = pm.ls(sl=1, fl=1)
    print '############################################ ', edgeList
    vtxListOrig = {}
    pairVtxEdge = []  # guarda pares de vertices que compoem as edges

    vtxWidthOrdered = {}
    vtxWidthToCenterOrdered = {}
    vtxHeightOrdered = {}

    vtxListOrdinary = []
    vtxListOrdinaryIndex = []
    vtxListOrdinaryCoord = []

    vtxPoleList = []  # list com vertices top, bttm, left, right

    for e, edge in enumerate(edgeList):
        vertConvert = pm.polyListComponentConversion(edge.name(), fe=True, tv=True)
        vtxListTemp = pm.ls(vertConvert, fl=1)  # lista com os vertices de cada edge do loop

        # print edge
        pairVtxEdge.append(vtxListTemp)
        for vertice in vtxListTemp:
            vertIndex = int(vertice.split('[')[1][:-1])  # identificamos o indice do vertice
            vtxListOrig.update({vertIndex: vertice})  # adicionamos numa lista onde nao se repete indices
            # identificando qual eh o vertice central superior:
            currentbBbox = bbox(vertice)
            vtxWidth = currentbBbox['width']
            vtxHeight = currentbBbox['height']

            if vtxWidth < 0:
                vtxWidthToCenter = vtxWidth * -1  # todos os valores do eixo x eh positivo para encontrarmos o mais prox de zero
                # print 'current neg position: ', vtxWidth, ' _ ', vtxHeight
            else:
                vtxWidthToCenter = vtxWidth

            vtxWidthToCenterOrdered.update({vertIndex: vtxWidthToCenter})
            vtxWidthOrdered.update({vertIndex: vtxWidth})
            vtxHeightOrdered.update({vertIndex: vtxHeight})

    # comparando nos dois eixos x
    sorted_widthToCenterVtx = sorted(vtxWidthToCenterOrdered.items(), key=operator.itemgetter(1))
    sorted_widthVtx = sorted(vtxWidthOrdered.items(), key=operator.itemgetter(1))

    # identificar qual dos dois vertices esta mais acima

    if vtxHeightOrdered[sorted_widthToCenterVtx[0][0]] > vtxHeightOrdered[sorted_widthToCenterVtx[1][0]]:
        topVtx = vtxListOrig[sorted_widthToCenterVtx[0][0]]
        bttmVtx = vtxListOrig[sorted_widthToCenterVtx[1][0]]
    else:
        topVtx = vtxListOrig[sorted_widthToCenterVtx[1][0]]
        bttmVtx = vtxListOrig[sorted_widthToCenterVtx[0][0]]

    vtxPoleList.append(topVtx)
    vtxPoleList.append(bttmVtx)
    vtxListOrdinary.append(topVtx)

    leftVtx = vtxListOrig[sorted_widthVtx[-1][0]]
    vtxPoleList.append(leftVtx)
    RigthVtx = vtxListOrig[sorted_widthVtx[0][0]]
    vtxPoleList.append(RigthVtx)

    # encontrando o vertice a direita do primeiro
    # encontrando quais os vertices ao lado do primeiro e deixando na lista nearVtxList
    nearVtxList = []

    for pair in pairVtxEdge:
        if topVtx in pair:
            tempPair = list(pair)
            tempPair.remove(topVtx)
            nearVtxList.append(tempPair[0])

    # identificando qual dos dois vertices eh o da direita:

    tempVtxBox = None
    tempVtx = None
    for eachVtx in nearVtxList:
        currentBbox = bbox(eachVtx)['width']
        if not tempVtxBox and not tempVtx:
            tempVtxBox = currentBbox
            tempVtx = eachVtx

        if currentBbox > tempVtxBox:
            leftNearVtx = eachVtx
        else:
            leftNearVtx = tempVtx

    vtxListOrdinary.append(leftNearVtx)

    # ordenando os demais vertices:
    for i in range(len(pairVtxEdge) - 2):
        pairOptions = []
        for pairSet in pairVtxEdge:
            if vtxListOrdinary[-1] in pairSet:
                pairOptions.append(pairSet)

        for option in pairOptions:
            if option[0] in vtxListOrdinary and option[1] in vtxListOrdinary:
                pairOptions.remove(option)

        tempPair = list(pairOptions[0])
        tempPair.remove(vtxListOrdinary[-1])
        nextPair = tempPair[0]

        vtxListOrdinary.append(nextPair)

    # lista de coordenadas dos vertices do loop:
    for vtx in vtxListOrdinary:
        vtxIndex = vtx.split('[')[1][:-1]

        coord = bbox(vtx)

        #tempLoc = rigFunctions.cntrlCrv(name=vtx + 'temp', icone='null', cntrlSulfix='_loc')
        #tempLoc.setTranslation((coord['width'], coord['height'], coord['deph']), 'world')
        coordSet = ((coord['width'], coord['height'], coord['deph']))
        vtxListOrdinaryCoord.append(coordSet)
        vtxListOrdinaryIndex.append(vtxIndex)

    print vtxListOrdinary
    print vtxListOrdinaryCoord
    print vtxListOrdinaryIndex
    print vtxPoleList

    return {'vtxNameList': vtxListOrdinary,        # retorna lista com nome da cada vtx na ordem
            'vtxCoordList': vtxListOrdinaryCoord,  # retorna lista com coordenadas dos vtx na ordem
            'vtxIndexList': vtxListOrdinaryIndex,  # retorna lista com indices dos vtx na ordem
            'vtxPolesList': vtxPoleList            # retorna lista com nomes dos vtx dos polos [top, bttm, left, rigth]
            }

def getClosestVertex(mesh=None, pos=[0, 0, 0]):
    """
    Returns the closest vertex from the given position

    :param mesh: polygon mesh
    :param pos: position
    :return: vertex
    """
    #se o mesh eh uma instancia do pymel, pega somente o nome
    if isinstance(mesh, basestring):
        mayaMeshName = mesh
    else:
        mayaMeshName = mesh.name()

    mVector = om.MVector(pos)

    selectionList = om.MSelectionList()
    selectionList.add(mayaMeshName)
    dPath = selectionList.getDagPath(0)
    mMesh = om.MFnMesh(dPath)

    # getting closest face ID
    ID = mMesh.getClosestPoint(om.MPoint(mVector), space=om.MSpace.kWorld)[1]
    # face's vertices list
    list = pm.ls(pm.polyListComponentConversion(mayaMeshName+'.f['+str(ID)+']', ff=True, tv=True), flatten=True)

    #setting vertex [0] as the closest one
    d = mVector - om.MVector(pm.xform(list[0], t=True, ws=True, q=True))
    # using distance squared to compare distance
    smallestDist2 = d.x*d.x+d[1]*d[1]+d[2]*d[2]
    closest = list[0]

    #iterating from vertex [1]
    for i in range(1, len(list)):
        d = mVector - om.MVector(pm.xform(list[i], t=True, ws=True, q=True))
        d2 = d.x*d.x+d[1]*d[1]+d[2]*d[2]
        if d2 < smallestDist2:
            smallestDist2=d2
            closest = list[i]
    return closest

def getEdgeLoopExtremesPoints(edgeLoop):
    """
    returns the extreme vertices of an edgeloop

    :param edgeLoop:
    :return: vertex list: [left extreme, right extreme, upper extreme, lower extreme]
    """

    vertexList = []
    for x in edgeLoop:
        cv = x.connectedVertices()
        for v in cv:
            if v not in vertexList:
                vertexList.append(v)
    maxX = None
    maxY = None
    minX = None
    minY = None
    upPos = None
    lowPos = None
    inPos = None
    outPos = None

    for x in vertexList:
        pos = x.getPosition(space='world')
        if maxX is None or pos[0] > maxX:
            maxX = pos[0]
            outPos = x
        if maxY is None or pos[1] > maxY:
            maxY = pos[1]
            upPos = x
        if minX is None or pos[0] < minX:
            minX = pos[0]
            inPos = x
        if minY is None or pos[1] < minY:
            minY = pos[1]
            lowPos = x
    return inPos, outPos, upPos, lowPos

def edgeLoopSort(edgeLoop, vertStart, vertEnd=None):
    """
    Sort an edgelooop list, dividing it at vertStart and vertEnd vertices

    :param edgeLoop: list of edges
    :param vertStart: vertex
    :param vertEnd: vertex
    :return: sorted edgeloop list, first half, second half
    """
    extremesVertices = []
    edgeLoopSorted = []
    edgeCurrent = None
    count = 0
    hasNext = True
    firstHalf = []
    secondHalf = []

    for e in edgeLoop:
        for vxt in e.connectedVertices():
            valency = len(vxt.connectedEdges())
            if valency > 4:
                extremesVertices.append(vxt)
    if extremesVertices:
        vertexCurrent = extremesVertices[0]
        cutVertex = vertStart
    else:
        vertexCurrent = vertStart
        cutVertex = vertEnd

    while hasNext:
        connEdges = [x for x in vertexCurrent.connectedEdges() if
                     x in edgeLoop and x != edgeCurrent and x not in edgeLoopSorted]
        if connEdges:
            edgeCurrent = connEdges[0]
            vertexCurrent = [x for x in edgeCurrent.connectedVertices() if x != vertexCurrent][0]
            edgeLoopSorted.append(edgeCurrent)
            if cutVertex and vertexCurrent == cutVertex:
                firstHalf = copy.copy(edgeLoopSorted)
        else:
            hasNext = False

        count += 1
        if count > 100:
            print 'deu break'
            break

    if cutVertex:
        try:
            secondHalf = [x for x in edgeLoopSorted if x not in firstHalf]
        except:
            pass

    return [edgeLoopSorted, firstHalf, secondHalf]

def getLoopByLocators(mesh=None, loc1=None, loc2=None, loc3=None):
    '''
    Evaluates the mesh to find the edgeloop passing through the locators

    :param mesh: polygon mesh
    :param loc1: locator, start vertex
    :param loc2: locator, end vertex
    :param loc3: locator, edgeloop pass through this vertex
    :return:  list of edges
    '''

    foundSegment = None

    pos1 = pm.xform(loc1, q=True, ws=True, t=True)
    pos2 = pm.xform(loc2, q=True, ws=True, t=True)
    pos3 = pm.xform(loc3, q=True, ws=True, t=True)

    closest1 = getClosestVertex(mesh.name(), pos=pos1)
    closest2 = getClosestVertex(mesh.name(), pos=pos2)
    closest3 = getClosestVertex(mesh.name(), pos=pos3)

    pm.select(closest1)
    edges = closest1.connectedEdges()

    foundLoop=None
    for e in edges:
        edgeloop = pm.polySelect(mesh, edgeLoop=e.index(), edgeBorder=e.index())
        vertexLoop = pm.ls(pm.polyListComponentConversion(fe=True, tv=True), fl=True)
        if closest2 in vertexLoop and closest3 in vertexLoop:
            foundLoop = vertexLoop

    if foundLoop:
        foundEdgeloop = []
        for vtx in foundLoop:
            edges = vtx.connectedEdges()
            for e in edges:
                conVtxs = e.connectedVertices()
                if conVtxs[0] in foundLoop and conVtxs[1] in foundLoop:
                    foundEdgeloop.append(e)

        sortedEdgeloop = edgeLoopSort(foundEdgeloop, closest1, closest2)
        rev = False
        foundSegment = None
        for i in range(1, 3):
            pm.select(sortedEdgeloop[i])
            vertexLoop = pm.ls(pm.polyListComponentConversion(fe=True, tv=True), fl=True)
            if closest3 in vertexLoop:
                foundSegment = sortedEdgeloop[i]

    pm.select(cl=True)
    return foundSegment

def getParalelEdgeloops(edgeloop=None, paralelNumber=1):
    """
    return list n of paralel edgesloops

    :param edgeloop:
    :param paralelNumber:
    :return:
    """

    def getNextEdgeRing(edge, edgeRing=None):
        if not edgeRing:
            mesh = pm.PyNode(edge.name().split('.')[0])
            edgeRing = [pm.PyNode(x) for x in pm.polySelect(mesh, edgeRing=edge.index(), ns=True, ass=True)]
        all = []
        checked = [edge]
        conn = edge.connectedEdges()
        for e in conn:
            temp = e.connectedEdges()
            for x in temp:
                all.append(x)
        inRing = list(set([x for x in all if x in edgeRing and x not in checked]))
        return inRing

    allRing = []
    checked = [x for x in edgeloop]
    allRingVtx = []

    for i in range(paralelNumber):
        print i
        nextRing = []
        nextRingVxt = []
        for e in edgeloop:
            ring = getNextEdgeRing(e)
            for x in ring:
                if x not in checked:
                    nextRing.append(x)
                    checked.append(x)
                    connectVxts = x.connectedVertices()
                    for v in connectVxts:
                        if v not in nextRingVxt:
                            nextRingVxt.append(v)
        edgeloop = nextRing
        allRing.append(nextRing)
        allRingVtx.append(nextRingVxt)

    return allRingVtx

def edgeLoopToVextex(edgeLoop):
    vxtLoop=[]
    for e in edgeLoop:
        connectVxts = e.connectedVertices()
        for v in connectVxts:
            if v not in vxtLoop:
                vxtLoop.append(v)

    connectedEdges = vxtLoop[0].connectedEdges()
    inEdgeLoop = [x for x in connectedEdges if x in edgeLoop]
    if len(inEdgeLoop) > 1:
        temp = copy.copy(vxtLoop[0])
        temp1 = copy.copy(vxtLoop[1])
        vxtLoop[0] = temp1
        vxtLoop[1] = temp

    return vxtLoop

##PROTOTIPO DE ANALISE DE GEOMETRIA
def doLoc(name, pos):
    loc = pm.spaceLocator(n=name)
    loc.localScaleX.set(0.05)
    loc.localScaleY.set(0.05)
    loc.localScaleZ.set(0.05)
    pm.xform(loc, t=pos, wd=True)
    return loc

def intersectEdgePlane(planePoint, planeNormal, A, B):
    u = B - A
    w = (A - planePoint) * -1
    D = planeNormal * u
    N = planeNormal * w
    if abs(D) < 0.001:
        if N == 0:
            return None
        else:
            return None
    SI = N / D
    if (SI < 0 or SI > 1):
        return 0
    I = A + SI * u
    return I

def calcMidPoint(planeLoc, geo):
    originalSelect = pm.ls(sl=True)
    sel = om.MSelectionList()
    sel.add(planeLoc)
    dag = sel.getDagPath(0)
    planeTransform = om.MFnTransform(dag)
    planePoint = om.MVector(planeTransform.translation(om.MSpace.kWorld))
    planeNormal = om.MVector.kZaxisVector * planeTransform.transformation().asMatrix()

    sel = om.MSelectionList()
    sel.add(geo)
    dag = sel.getDagPath(0)

    mesh = om.MFnMesh(dag)
    edgeIt = om.MItMeshEdge(dag)
    polygonIt = om.MItMeshPolygon(dag)

    intesectList = {}
    while not edgeIt.isDone():
        vtxA = mesh.getPoint(edgeIt.vertexId(0), om.MSpace.kWorld)
        vtxB = mesh.getPoint(edgeIt.vertexId(1), om.MSpace.kWorld)
        A = om.MVector(vtxA)
        B = om.MVector(vtxB)

        result = intersectEdgePlane(planePoint, planeNormal, A, B)
        onBoudary = edgeIt.onBoundary()

        if result:
            # doLoc ('center1', result)
            intesectList[edgeIt.index()] = [result, onBoudary]

        edgeIt.next()

    if intesectList == {}:
        return

    allSortedEdges = []
    sortedEdges = []
    edgeIt.reset()
    remainedEdges = intesectList.keys()
    count = len(remainedEdges)
    boundary = [x for x in remainedEdges if intesectList[x][1] == True]
    if boundary:
        i = boundary[0]
        isClosed = False
    else:
        i = remainedEdges[0]
        isClosed = True

    while not count == 0:
        sortedEdges.append(i)
        remainedEdges.remove(i)
        edgeIt.setIndex(i)
        connectedFaces = edgeIt.getConnectedFaces()
        nextEdge = []
        for f in connectedFaces:
            polygonIt.setIndex(f)
            connectedEdges = polygonIt.getEdges()
            a = [x for x in connectedEdges if x in remainedEdges]
            if a:
                i = a[0]
                nextEdge.append(i)

        if nextEdge:
            i = nextEdge[0]
        else:
            allSortedEdges.append([sortedEdges, isClosed])
            if remainedEdges:
                boundary = [x for x in remainedEdges if intesectList[x][1] == True]
                if boundary:
                    i = boundary[0]
                    isClosed = False
                else:
                    i = remainedEdges[0]
                    isClosed = True
            sortedEdges = []
        count -= 1

    for loop in allSortedEdges:
        maxD = -100000.0
        minD = 100000.0
        minIndex = 0
        maxIndex = 0
        for vtx in loop[0]:
            vtxPoint = om.MVector(intesectList[vtx][0])
            if maxD < vtxPoint.length():
                maxD = vtxPoint.length()
                maxIndex = vtx

            if minD > vtxPoint.length():
                minD = vtxPoint.length()
                minIndex = vtx

        p1 = om.MVector(intesectList[maxIndex][0])
        p2 = om.MVector(intesectList[minIndex][0])
        c = (p1 + p2) / 2

        d = om.MVector(planePoint - c)

        distTreshold = .5

        if d.length() < distTreshold:
            v1 = om.MVector(p1 - c)
            v2 = v1 ^ planeNormal
            p3 = c + v2.normal() * v2.length()
            p4 = c - v2.normal() * v2.length()
            crv = pm.curve(n='clipCurve', d=1, p=(p1, p3, p2, p4, p1), k=(0, 1, 2, 3, 4))
            loc = doLoc('center1', c)
            pm.color(crv, rgb=(1, 0, 0))
            pm.color(loc, rgb=(0, 1, 0))
            pm.select(originalSelect)

def sjobMidPoint():
    cen = pm.ls('clipCurve*', 'center*')
    pm.delete(cen)
    geos = ['pSphere1Shape', 'pSphere2Shape']
    for g in geos:
        calcMidPoint('locator1', g)

def bbox(obj):
    coords = {}
    bboxVtx = pm.exactWorldBoundingBox(obj)

    coords['minX'] = bboxVtx[0]
    coords['minY'] = bboxVtx[1]
    coords['minZ'] = bboxVtx[2]
    coords['maxX'] = bboxVtx[3]
    coords['maxY'] = bboxVtx[4]
    coords['maxZ'] = bboxVtx[5]

    if coords['minX'] == coords['maxX']:
        coords['width'] = coords['minX']
        globalPvtX = coords['minX']
    else:
        coords['width'] = coords['maxX'] - coords['minX']
        globalPvtX = coords['maxX'] - (coords['width'] /2 )

    if coords['minY'] == coords['maxY']:
        coords['height'] = coords['minY']
        globalPvtY = coords['minY']
    else:
        coords['height'] = coords['maxY'] - coords['minY']
        globalPvtY = coords['maxY'] - (coords['height'] /2 )

    if coords['minZ'] == coords['maxZ']:
        coords['deph'] = coords['minZ']
        globalPvtZ = coords['minZ']
    else:
        coords['deph'] = coords['maxZ'] - coords['minZ']
        globalPvtZ = coords['maxZ'] - (coords['deph'] /2 )

    coords['globalPvt'] = tuple([globalPvtX, globalPvtY, globalPvtZ])

    return coords