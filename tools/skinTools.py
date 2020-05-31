import cPickle as pickle
import pymel.core as pm
import os.path
import os
import copy
import maya.mel as mel
import logging
import autoRig3.tools.vertexWalkTools as vtxWalk

logger = logging.getLogger('autoRig')


def selectSkinJoints():
    sel = pm.ls (sl=True)
    if sel:
        objShp = sel[0].getShape()
        setList = objShp.inputs(t='objectSet')
        for st in setList:
            x= st.inputs (t='skinCluster')
            if not x==[]:
                skinCls=x
        if skinCls:
            jnts = skinCls[0].inputs (t='joint')
            pm.select (jnts)
        else:
            print 'ERRO: objeto nao tem skin'
    else:
        print 'ERRO:nenhum objeto selecionado'

def findSkinCluster(mesh):
    skinclusterList = []
    skinCls = None
    for each in pm.listHistory(mesh, pdo=True, il=2):
        if type(each) == pm.nodetypes.SkinCluster:
            skinclusterList.append(each)
    try:
        skinCls = skinclusterList[0]
    except:
        pass

    return skinCls

def saveSkinning(path, meshes=None):
    logger.debug('init save skin')
    if meshes:
        dataDict = getSkinClusterInfluence(meshes)
        with open(path, 'wb') as handle:
            pickle.dump(dataDict, handle, protocol=pickle.HIGHEST_PROTOCOL)
        logger.debug('skin saving ok!')
    else:
        logger.debug('no skinCluster found!!')

def getSkinClusterInfluence(meshes):
    dataDict = {}

    for msh in meshes:
        skincluster = findSkinCluster(msh)
        influenceData = {}
        for infl in skincluster.getInfluence():
            vtxList = []
            getData = skincluster.getPointsAffectedByInfluence(infl)
            if getData[0] and getData[1]:
                for vtx, wgt in zip(getData[0][0], getData[1]):
                    vtxList.append((vtx.currentItemIndex(), wgt))
                influenceData[infl.name()] = vtxList
        dataDict[msh.name()] = influenceData
    return dataDict

def loadSkinning(path):
    with open(path, 'rb') as handle:
        fileData = pickle.load(handle)

    for msh, dataDict in fileData.iteritems():
        mshAndJnts = dataDict.keys()
        mshAndJnts.append(msh)

        skinCls = findSkinCluster(msh)
        if skinCls:
            for eachJnt in mshAndJnts:
                pm.skinCluster(skinCls, edit=True, ai=eachJnt, lw=True)

        else:
            skinCls = pm.skinCluster(mshAndJnts, tsb=True, tst=False)

        skinCls.setNormalizeWeights(0)
        pm.skinPercent(skinCls, msh, nrm=False, prw=100)

        jointDict = {}
        for storedJoint in dataDict:
            try:
                jnt = pm.PyNode(storedJoint)
            except pm.MayaNodeError:
                logger.debug('nao achou jnt: %s' % jnt)
            jointDict[storedJoint] = skinCls.indexForInfluenceObject(jnt)

        for infl in dataDict:
            for vtx in dataDict[infl]:
                pm.setAttr(skinCls.name() + '.weightList[' + str(vtx[0]) + '].weights[' + str(jointDict[infl]) + ']',
                           vtx[1])
        skinCls.setNormalizeWeights(1)
        logger.debug('skin loading ok!')

def resetSkin():
    mel.eval('source findRelatedSkinCluster.mel');
    mel.eval('source generateChannelMenu.mel');

    sel = pm.ls(sl=1)
    if not sel: return

    for obj in sel:
        skinCluster = mel.eval('findRelatedSkinCluster ' + obj)
        if skinCluster:
            jointsDic = {}
            matrixConn = pm.ls(pm.listConnections(skinCluster + '.matrix', connections=True), long=True)
            if matrixConn:
                for i, j in enumerate(matrixConn):
                    if i % 2:
                        jointsDic[j] = matrixConn[i - 1]

            for j in jointsDic:
                try:
                    m = pm.getAttr(j + '.worldInverseMatrix')
                    bindPre = jointsDic[j].replace('matrix', 'bindPreMatrix')
                    pm.connecttAttr(j + '.worldInverseMatrix', bindPre)
                    mel.eval('CBdeleteConnection ' + bindPre + ';')
                except:
                    pass

def mirrorSkin(type):
    sel = pm.ls(sl=1)
    if not sel: return

    # normal Maya mirror
    if type == 0:
        if len(sel) > 2:
            print 'Error! Please select one or two objects at most.'
            return
        else:
            mel.eval('MirrorSkinWeights')
    # multi mirror individual
    elif type == 1:
        for obj in sel:
            skinCluster = mel.eval('findRelatedSkinCluster ' + obj)
            if skinCluster:
                mel.eval('MirrorSkinWeights')
            else:
                print '"' + obj + '" does not have a skinCluster to mirror... skipping.'

def mirrorSkinOptions():
    mel.eval('MirrorSkinWeightsOptions')

def selectSkinInfluences():
    sel = pm.ls(sl=1)
    if not sel: return

    infSet = set()

    for obj in sel:
        res = pm.skinCluster(obj, query=True, influence=True)
        if res: infSet = infSet.union(set(res))

    if infSet: pm.select(list(infSet))

def copySkinRUI():
    sel = pm.ls(sl=1)
    if sel:
        source = sel[0]
        dest = sel[1:]

        for d in dest:
            pm.copySkinWeights(source, d, noMirror=True, surfaceAssociation='closestPoint',
                                 influenceAssociation='oneToOne')

        pm.select(sel[1:])
        mel.eval('removeUnusedInfluences')

def transferSkin():
    sel = pm.ls(sl=1)
    if len(sel) > 1:
        source = sel[0]
        dest = sel[1:]

        infs = pm.skinCluster(source, query=True, influence=True)
        if not infs:
            print 'Source object "' + source + '" does not have influences attached!'
        else:
            for d in dest:
                pm.select(infs, d)
                pm.skinCluster(toSelectedBones=1, normalizeWeights=1, rui=0)
            pm.select(source, dest)
            copySkinRUI()

    else:
        print 'Please select at least ONE source object and ONE destination object.'

def getParalelEdges(edge=None, exclude=None):
    mesh = pm.ls(edge, o=True)[0]
    index = edge.index()
    temp = edge.connectedFaces()
    faces = pm.ls(temp, fl=True)

    paralelEdges = []
    for face in faces:
        faceEdges = face.getEdges()
        if len(faceEdges) == 4:
            faceIndex = faceEdges.index(index) + 2
            if faceIndex > 3:
                faceIndex -= 4
            outEdge = mesh.e[faceEdges[faceIndex]]
            if outEdge not in exclude:
                paralelEdges.append(outEdge)
    return paralelEdges

def edgeSkin(edgeLoopOriginal = None, paralelLoopNum = 5):
    if not edgeLoopOriginal:
        edgeLoopOriginal = pm.ls(sl=True, fl=True)

    loopList = []

    mesh = pm.ls(edgeLoopOriginal[0], o=True)[0]
    skinCls = findSkinCluster(mesh)
    influenceList = pm.skinCluster(skinCls, q=True, inf=True)

    edgeLoop = copy.copy(edgeLoopOriginal)
    excludeLoop = copy.copy(edgeLoopOriginal)

    for i in range(paralelLoopNum):
        paralelEdgeLoop = []
        for edge in edgeLoop:
            paralelEdges = getParalelEdges(edge=edge, exclude=excludeLoop)

            paralelEdgeLoop += paralelEdges

        edgeLoop = paralelEdgeLoop

        loopList.append(paralelEdgeLoop)
        excludeLoop += paralelEdgeLoop

    for indice in range(len(edgeLoopOriginal)):
        vtx = edgeLoopOriginal[indice].connectedVertices()

        for v in vtx:
            weightsList = pm.skinPercent (skinCls, v, q=True, v=True)
            maxWeight = 0
            maxInfluence = None

            for influence, weight in zip(influenceList, weightsList):
                if weight > maxWeight:
                    maxWeight = weight
                    maxInfluence = influence


            pm.skinPercent(skinCls, v, tv=(maxInfluence, 1))
            oppositeVtx = [x for x in vtx if x != v][0]

            vConnected = v.connectedVertices ()

            vConnected = pm.ls([x for x in vConnected if x != oppositeVtx], fl=True)

            for level in range(paralelLoopNum):
                vtxParalel = pm.ls (loopList[level][indice * 2].connectedVertices() \
                             + loopList[level][indice * 2 + 1].connectedVertices(), fl=True)

                vConnectedParalel = [x for x in vConnected if x in vtxParalel]
                vConnected = pm.ls ([x.connectedVertices () for x in vConnectedParalel], fl=True)

                if len(vConnectedParalel)>2:
                    print 'erro pontos com mais de 2 conexoes!!'
                    break

                for c in vConnectedParalel:
                    pm.skinPercent(skinCls, c, tv=(maxInfluence, 1))
                    pm.skinPercent(skinCls, c, tv=(maxInfluence, 1))

def loadngSkinToolPlugin():
    logger.debug ('loading ng...')
    if pm.pluginInfo ('ngSkinTools.mll', name=True, query=True, loaded=True):
        return True
    ver = pm.about (v=True)
    pluginPath = os.path.join(os.path.dirname(__file__), 'ng', ver)

    if os.environ.has_key ('MAYA_PLUGIN_PATH'):
        os.environ['MAYA_PLUGIN_PATH'] += ';' + pluginPath + ';'
    else:
        os.environ['MAYA_PLUGIN_PATH'] = pluginPath + ';'

    try:
        pm.loadPlugin (os.path.join (pluginPath, 'ngSkinTools.mll'))
        logger.debug ('ngPlugin ok')
    except:
        logger.debug ('Nao achou plugin ng!!!')