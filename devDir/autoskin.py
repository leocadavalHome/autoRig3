import pymel.core as pm
import autoRig3.tools.skinTools as skinTools
import autoRig3.tools.vertexWalkTools as vtxWalk
import copy


skinJoints = pm.ls (sl=True, fl=True) # selecione os joints do eyelid
print skinJoints
edgeLoop = pm.ls (sl=True, fl=True)

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

def autoSkinEdgeLoop(edgeLoop = None, paralelLoops = 5, jointList=None, holdJoint=None):
    mesh = pm.ls(edgeLoop[0], o=True)[0]
    skinCls = findSkinCluster(mesh)

    if not skinCls:
        pm.skinCluster(mesh, holdJoint)
        influencesToAdd = jointList
    else:
        influenceList = pm.skinCluster(skinCls, query=True, influence=True)
        influencesToAdd = [x for x in skinJoints if x not in influenceList]

    pm.skinCluster(skinCls, e=True, ai=influencesToAdd, wt=0)

    vtx = vtxWalk.edgeLoopToVextex(edgeLoop)
    pm.skinPercent(skinCls, vtx, resetToDefault=True)
    skinTools.edgeSkin(edgeLoopOriginal=edgeLoop, paralelLoopNum=5)

