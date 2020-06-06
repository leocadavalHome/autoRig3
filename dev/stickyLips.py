import maya.api.OpenMaya as om
import pymel.core as pm
import autoRig3.tools.attachTools as attachTools
import autoRig3.tools.skinTools as skinTools
import autoRig3.modules.baseModule as baseModule
import autoRig3.tools.vertexWalkTools as vtxWalk
import json
import logging

logger = logging.getLogger('autoRig')

class StickyLips(baseModule.BaseModule):
    def __init__(self, name='stickLips'):
        super(StickyLips, self).__init__()

        self.name = name
        self.toExport = ['guideDict', 'name', 'moveallGuideSetup', 'cornersGuideSetup']
        self.guideSulfix = '_guide'
        self.moveallGuideSetup = {'nameTempl': self.name + '_moveall'}
        self.cornersGuideSetup = {'nameTempl': self.name, 'icone': 'null', 'size': .05, 'color': (1, 0, 0)}
        self.guideDict = {'moveall': [(12, 0, 0), (0, 0, 0), (1, 1, 1)],
                          'inCorner': [(10, 0, 2,), (0, 0, 0)], 'outCorner': [(14, 0, 2,), (0, 0, 0)],
                          'upCorner': [(12, 2, 2,), (0, 0, 0)], 'lowCorner': [(12, -2, 2,), (0, 0, 0)],
                          }
        self.mesh = None
        self.L_ctrl = None
        self.R_ctrl = None

    def getDict(self):
        try:
            guideName = self.moveallGuideSetup['nameTempl'] + self.guideSulfix
            self.guideMoveall = pm.PyNode(guideName)

            jsonDict = self.guideMoveall.stickLipsDict.get()
            DictRestored = json.loads(jsonDict)

            self.__dict__.update(**DictRestored)

            self.guideDict['moveall'][0] = self.guideMoveall.getTranslation(space='world').get()
            self.guideDict['moveall'][1] = tuple(self.guideMoveall.getRotation(space='object'))
            self.guideDict['moveall'][2] = tuple(pm.xform(self.guideMoveall, q=True, s=True, ws=True))

            guideName = self.cornersGuideSetup['nameTempl'] + 'InCorner' + self.guideSulfix
            self.inCorner = pm.PyNode(guideName)
            self.guideDict['inCorner'][0] = self.inCorner.getTranslation(space='world').get()
            self.guideDict['inCorner'][1] = tuple(self.inCorner.getRotation(space='object'))

            guideName = self.cornersGuideSetup['nameTempl'] + 'OutCorner' + self.guideSulfix
            self.outCorner = pm.PyNode(guideName)
            self.guideDict['outCorner'][0] = self.outCorner.getTranslation(space='world').get()
            self.guideDict['outCorner'][1] = tuple(self.outCorner.getRotation(space='object'))

            guideName = self.cornersGuideSetup['nameTempl'] + 'UpCorner' + self.guideSulfix
            self.upCorner = pm.PyNode(guideName)
            self.guideDict['upCorner'][0] = self.upCorner.getTranslation(space='world').get()
            self.guideDict['upCorner'][1] = tuple(self.upCorner.getRotation(space='object'))

            guideName = self.cornersGuideSetup['nameTempl'] + 'LowCorner' + self.guideSulfix
            self.lowCorner = pm.PyNode(guideName)
            self.guideDict['lowCorner'][0] = self.lowCorner.getTranslation(space='world').get()
            self.guideDict['lowCorner'][1] = tuple(self.lowCorner.getRotation(space='object'))
        except:
            pass

    def doGuide(self, edgeLoop=None, autoExtremes=True, **kwargs):
        self.edgeLoop = edgeLoop
        self.mesh = pm.ls(self.edgeLoop[0], o=True)[0]

        self.guideMoveall = self.createCntrl('moveallGuide')

        self.inCorner = self.createCntrl(setupName='cornersGuide', nameTempl=self.name + 'InCorner' + self.guideSulfix)
        self.outCorner = self.createCntrl(setupName='cornersGuide', nameTempl=self.name + 'OutCorner' + self.guideSulfix)
        self.upCorner = self.createCntrl(setupName='cornersGuide', nameTempl=self.name + 'UpCorner' + self.guideSulfix)
        self.lowCorner = self.createCntrl(setupName='cornersGuide', nameTempl=self.name + 'LowCorner' + self.guideSulfix)

        if autoExtremes:
            try:
                pts = vtxWalk.getEdgeLoopExtremesPoints(self.edgeLoop)
                inPos = pm.xform(pts[0], q=True, ws=True, t=True)
                outPos = pm.xform(pts[1], q=True, ws=True, t=True)
                upPos = pm.xform(pts[2], q=True, ws=True, t=True)
                lowPos = pm.xform(pts[3], q=True, ws=True, t=True)

                self.guideDict['inCorner'] = [inPos, (0, 0, 0)]
                self.guideDict['outCorner'] = [outPos, (0, 0, 0)]
                self.guideDict['upCorner'] = [upPos, (0, 0, 0)]
                self.guideDict['lowCorner'] = [lowPos, (0, 0, 0)]
            except:
                logger.debug('not possible autoextremes')

        self.setCntrl(self.inCorner, 'inCorner', space='world')
        self.setCntrl(self.outCorner, 'outCorner', space='world')
        self.setCntrl(self.upCorner, 'upCorner', space='world')
        self.setCntrl(self.lowCorner, 'lowCorner', space='world')

        pm.parent(self.inCorner, self.outCorner, self.upCorner, self.lowCorner, self.guideMoveall)

        pm.addAttr(self.guideMoveall, ln='stickLipsDict', dt='string')
        self.guideMoveall.stickLipsDict.set(json.dumps(self.exportDict()))

    def doRig(self, iniOffset=False):
        #grupos
        if pm.objExists(self.name+'stickyLip_sys'):
            pm.delete(self.name+'SkinJxts_grp')

        if pm.objExists(self.name+'DriverJoints_grp'):
            pm.delete(self.name+'DriverJoints_grp')

        if pm.objExists(self.name+'SkinJoints_grp'):
            pm.delete(self.name+'SkinJoints_grp')

        stickLipSysGrp = pm.group(em=True, name=self.name+'stickyLip_sys')
        driverJointsGrp = pm.group(em=True, name=self.name + 'DriverJoints_grp', p=stickLipSysGrp)
        skinJointsGrp = pm.group(em=True, name=self.name + 'SkinJoints_grp', p=stickLipSysGrp)

        ## do joints
        pos = pm.xform(self.upCorner, q=True, ws=True, t=True)
        pm.select(cl=True)
        jntUpper = pm.joint(n='Mid_upper')
        pm.xform(jntUpper, t=pos, ws=True)
        
        pos = pm.xform(self.lowCorner, q=True, ws=True, t=True)
        pm.select(cl=True)
        jntLower = pm.joint(n='Mid_lower')
        pm.xform(jntLower, t=pos, ws=True)

        L_edge = vtxWalk.getLoopByLocators(mesh=self.mesh, loc1=self.upCorner, loc2=self.lowCorner, loc3=self.outCorner)
        L_vertices = vtxWalk.edgeLoopToVextex(L_edge)
        #get corner pos again, because it can be tweaked
        cornerPos = pm.xform(self.outCorner, q=True, ws=True, t=True)
        cornerVertex = vtxWalk.getClosestVertex(mesh=self.mesh, pos=cornerPos)
        cornerIndex = L_vertices.index(cornerVertex)

        def createJointsOnVertices(name=None, verticesList=None):
            jointList = []
            for i, vtx in enumerate(verticesList):
                pm.select(cl=True)
                jnt = pm.joint(n=name + str(i))
                pos = pm.xform(vtx, q=True, t=True, ws=True)
                pm.xform(jnt, t=pos, ws=True)
                jointList.append(jnt)
            return jointList

        L_jointsUp = createJointsOnVertices(name='L_upper', verticesList=L_vertices[1:cornerIndex])
        L_jointsUp.reverse()
        L_jointsLw = createJointsOnVertices(name='L_lower', verticesList=L_vertices[cornerIndex+1:-1])
        
        R_edge = vtxWalk.getLoopByLocators(mesh=self.mesh, loc1=self.upCorner, loc2=self.lowCorner, loc3=self.inCorner)
        R_vertices = vtxWalk.edgeLoopToVextex(R_edge)
        #get corner pos again, because it can be tweaked
        cornerPos = pm.xform(self.inCorner, q=True, ws=True, t=True)
        cornerVertex = vtxWalk.getClosestVertex(mesh=self.mesh, pos=cornerPos)
        cornerIndex = R_vertices.index(cornerVertex)
        
        R_jointsUp = createJointsOnVertices(name='R_upper', verticesList=R_vertices[cornerIndex+1:-1])
        R_jointsLw = createJointsOnVertices(name='R_lower', verticesList=R_vertices[1:cornerIndex])
        R_jointsLw.reverse()

        pm.parent(jntLower, jntUpper, R_jointsLw, R_jointsUp, L_jointsUp, L_jointsLw, driverJointsGrp)

        ## init variaveis
        self.L_ctrl = pm.spaceLocator(n='L_sticky_ctrl')
        self.R_ctrl = pm.spaceLocator(n='R_sticky_ctrl')
        pm.parent(self.L_ctrl, self.R_ctrl, stickLipSysGrp)

        self.L_ctrl.addAttr('sticky', at='float', k=1, dv=0, min=0)
        self.R_ctrl.addAttr('sticky', at='float', k=1, dv=0, min=0)
        self.L_ctrl.addAttr('offset', at='float', k=1, dv=0, min=0)
        self.R_ctrl.addAttr('offset', at='float', k=1, dv=0, min=0)
        self.L_ctrl.addAttr('height', at='float', k=1, dv=0, min=0, max=1)
        self.R_ctrl.addAttr('height', at='float', k=1, dv=0, min=0, max=1)
        self.L_ctrl.addAttr('overshoot', at='float', k=1, dv=0, min=0)

        def stickyPairSetup(name='sticky', upperJnt=None, lowerJnt=None, ctrl1=None, ctrl2=None,
                            stickyMin1=0, stickyMin2=0, stickyMax1=0, stickyMax2=0,
                            iniOffset=False):

            skinJoints=[]

            if hasattr(ctrl1, 'overshoot'):
                overCtrl = ctrl1
            elif hasattr(ctrl2, 'overshoot'):
                overCtrl = ctrl2
            else:
                overCtrl=None

            ##Calcula o centro (usar vetores pra facilitar a conta)
            a = pm.xform(upperJnt, q=True, ws=True, t=True)
            b = pm.xform(lowerJnt, q=True, ws=True, t=True)
            upperPos = om.MVector(a[0], a[1], a[2])
            lowerPos = om.MVector(b[0], b[1], b[2])
            centerPos = (upperPos+lowerPos)/2
        
            #opcao de fazer o offset no centro ou alinhado aos vertices
            if iniOffset:
                upperOffsetPos = (centerPos.x, upperPos.y, centerPos.z)
                lowerOffsetPos = (centerPos.x, lowerPos.y, centerPos.z)
            else:
                upperOffsetPos = (centerPos.x, centerPos.y, centerPos.z)
                lowerOffsetPos = (centerPos.x, centerPos.y, centerPos.z)
        
            #cria os grupos(joints agora)
            pm.select(cl=True)
            upperOffsetJoint = pm.joint(name=name+'Upper_Offset')
            upperDriverJoint = pm.joint(name=name+'Upper_Driver')
        
            pm.xform(upperOffsetJoint, ws=True, t=upperOffsetPos)
            pm.parent(upperOffsetJoint, upperJnt)
        
            pm.select(cl=True)
            lowerOffsetJoint = pm.joint(name=name+'Lower_Offset')
            lowerDriverJoint = pm.joint(name=name+'Lower_Driver')
            pm.xform(lowerOffsetJoint, ws=True, t=lowerOffsetPos)
            pm.parent(lowerOffsetJoint, lowerJnt)
        
            pm.select(cl=True)
            upperOffsetBindJoint = pm.joint(name=name+'UpperSkin_Offset')
            upperBindJoint = pm.joint(name=name+'UpperSkin_jxt')
            pm.xform(upperOffsetBindJoint, ws=True, t=(upperPos.x,upperPos.y,upperPos.z))

            skinJoints.append(upperOffsetBindJoint)

            pm.select(cl=True)
            lowerOffsetBindJoint = pm.joint(name=name+'LowerSkin_Offset')
            lowerBindJoint = pm.joint(name=name+'LowerSkin_jxt')
            pm.xform(lowerOffsetBindJoint, ws=True, t=(lowerPos.x,lowerPos.y,lowerPos.z))

            skinJoints.append(lowerOffsetBindJoint)

            #cria os nodes para o blend de posicao do driver
            upperAddMatrix = pm.createNode('wtAddMatrix')
            upperMultiMatrix = pm.createNode('multMatrix')
            upperDecomposeMatrix = pm.createNode('decomposeMatrix')
            lowerAddMatrix = pm.createNode('wtAddMatrix')
            lowerMultiMatrix = pm.createNode('multMatrix')
            lowerDecomposeMatrix = pm.createNode('decomposeMatrix')
        
            stickyUpperSetRange = pm.createNode('setRange')
            stickyLowerSetRange = pm.createNode('setRange')
            stickyUpperAdd = pm.createNode('addDoubleLinear')
            stickylowerAdd = pm.createNode('addDoubleLinear')
            stickClamp = pm.createNode('clamp')
            stickOffset = pm.createNode('plusMinusAverage')
            stickyReverse = pm.createNode('reverse')
            overshootAddUpper = pm.createNode('addDoubleLinear')
            overshootAddLower = pm.createNode('addDoubleLinear')

            ctrl1.sticky >> stickyUpperSetRange.valueX
            ctrl2.sticky >> stickyUpperSetRange.valueY
            ctrl1.sticky >> stickyLowerSetRange.valueX
            ctrl2.sticky >> stickyLowerSetRange.valueY
            overCtrl.overshoot >> overshootAddLower.input2
            overCtrl.overshoot >> overshootAddUpper.input2

            ctrl1.height >> stickyReverse.inputX
        
            stickyUpperSetRange.minX.set(0)
            ctrl1.height >> stickyUpperSetRange.maxX
            ctrl1.height >> stickyUpperSetRange.maxY
        
            stickyLowerSetRange.minY.set(0)
            stickyReverse.outputX >> stickyLowerSetRange.maxX
            stickyReverse.outputX >> stickyLowerSetRange.maxY
        
            stickyUpperSetRange.oldMinX.set(stickyMin1)
            stickyUpperSetRange.oldMinY.set(stickyMin2)
            stickyLowerSetRange.oldMinX.set(stickyMin1)
            stickyLowerSetRange.oldMinY.set(stickyMin2)

            stickOffset.input2D[0].input2Dx.set(stickyMax1)
            ctrl1.offset >> stickOffset.input2D[1].input2Dx
            stickOffset.output2Dx >> stickyUpperSetRange.oldMaxX
            stickOffset.output2Dx >> stickyLowerSetRange.oldMaxX
        
            stickOffset.input2D[0].input2Dy.set(stickyMax2)
            ctrl2.offset >> stickOffset.input2D[1].input2Dy
            stickOffset.output2Dy >> stickyUpperSetRange.oldMaxY
            stickOffset.output2Dy >> stickyLowerSetRange.oldMaxY
        
            stickyUpperSetRange.outValueX >> stickyUpperAdd.input1
            stickyUpperSetRange.outValueY >> stickyUpperAdd.input2
            stickyUpperAdd.output >> stickClamp.inputR
            ctrl1.height >> stickClamp.maxR
        
            stickyLowerSetRange.outValueX >> stickylowerAdd.input1
            stickyLowerSetRange.outValueY >> stickylowerAdd.input2
            stickylowerAdd.output >> stickClamp.inputG
            stickyReverse.outputX >> stickClamp.maxG

            stickClamp.outputR >> overshootAddUpper.input1
            stickClamp.outputG >> overshootAddLower.input1

            #faz as conexoes para o blend da posicao do driver
            upperOffsetJoint.worldMatrix[0] >> upperAddMatrix.wtMatrix[0].matrixIn
            overshootAddUpper.output >> upperAddMatrix.wtMatrix[0].weightIn
            lowerOffsetJoint.worldMatrix[0] >> upperAddMatrix.wtMatrix[1].matrixIn
            overshootAddUpper.output >> upperAddMatrix.wtMatrix[1].weightIn
            upperOffsetJoint.worldInverseMatrix >> upperMultiMatrix.matrixIn[0]
            upperAddMatrix.matrixSum >> upperMultiMatrix.matrixIn[1]
            upperMultiMatrix.matrixSum >> upperDecomposeMatrix.inputMatrix
            upperDecomposeMatrix.outputTranslate >> upperDriverJoint.translate
        
            upperOffsetJoint.worldMatrix[0] >> lowerAddMatrix.wtMatrix[0].matrixIn
            overshootAddLower.output >> lowerAddMatrix.wtMatrix[0].weightIn
            lowerOffsetJoint.worldMatrix[0] >> lowerAddMatrix.wtMatrix[1].matrixIn
            overshootAddLower.output >> lowerAddMatrix.wtMatrix[1].weightIn
            lowerOffsetJoint.worldInverseMatrix >> lowerMultiMatrix.matrixIn[0]
            lowerAddMatrix.matrixSum >> lowerMultiMatrix.matrixIn[1]
            lowerMultiMatrix.matrixSum >> lowerDecomposeMatrix.inputMatrix
            lowerDecomposeMatrix.outputTranslate >> lowerDriverJoint.translate
        
            upperDriverJoint.translate >> upperBindJoint.translate
            lowerDriverJoint.translate >> lowerBindJoint.translate

            return skinJoints
        stickyMin1 = 0
        stickyMax1 = 20
        stickyMin2 = 20
        stickyMax2 = 40
        total = len(L_jointsUp)
        incr = 20.0 / (total+1)
        skinJoints=[]

        for i, jnts in enumerate(zip(L_jointsUp, L_jointsLw)):
            skinJoints += stickyPairSetup(  name='L_sticky'+str(i),
                                            upperJnt=jnts[0], lowerJnt=jnts[1], ctrl1=self.L_ctrl, ctrl2=self.R_ctrl,
                                            stickyMin1=incr*i, stickyMin2=40-incr*(i+2),
                                            stickyMax1=incr*(i+1), stickyMax2=40-incr*(i+1),
                                            iniOffset=iniOffset)

        skinJoints += stickyPairSetup(  name='mid_sticky',
                                        upperJnt=jntUpper, lowerJnt=jntLower, ctrl1=self.L_ctrl, ctrl2=self.R_ctrl,
                                        stickyMin1=incr * total, stickyMin2=incr * total,
                                        stickyMax1=incr*(total+1), stickyMax2=incr*(total+1),
                                        iniOffset=iniOffset)

        for i, jnts in enumerate(zip(R_jointsUp, R_jointsLw)):
            skinJoints += stickyPairSetup(  name='R_sticky'+str(i),
                                            upperJnt=jnts[0], lowerJnt=jnts[1], ctrl1=self.R_ctrl, ctrl2=self.L_ctrl,
                                            stickyMin1=incr*i, stickyMin2=40-incr*(i+2),
                                            stickyMax1=incr*(i+1), stickyMax2=40-incr*(i+1),
                                            iniOffset=iniOffset)

        pm.parent(skinJoints, skinJointsGrp)
        self.skinJoints = [y[0] for y in [x.getChildren() for x in skinJoints]]

        jointsToAttach=L_jointsUp+L_jointsLw+R_jointsUp+R_jointsLw+[jntUpper, jntLower]
        jointsToAttach.append(self.mesh.getTransform())
        attachTools.hookOnMesh(inputs=jointsToAttach,
                               mode=3,
                               follOn='vzRivet_grp')

    def autoSkin(self, mesh=None, paralelLoopNum=3, holdJoint=None):
        edgeloop1 = vtxWalk.getLoopByLocators(mesh=mesh, loc1=self.inCorner, loc2=self.outCorner, loc3=self.upCorner)
        edgeloop2 = vtxWalk.getLoopByLocators(mesh=mesh, loc1=self.inCorner, loc2=self.outCorner, loc3=self.lowCorner)
        edgeloop=edgeloop1+edgeloop2
        skinCls = skinTools.findSkinCluster(mesh=mesh)

        if not skinCls:
            pm.skinCluster(self.mesh, holdJoint)
            influencesToAdd = self.skinJoints
        else:
            influenceList = pm.skinCluster(skinCls, query=True, influence=True)
            influencesToAdd = [x for x in self.skinJoints if x not in influenceList]

        print influencesToAdd

        pm.skinCluster(skinCls, e=True, ai=influencesToAdd, wt=0)

        vtx = vtxWalk.edgeLoopToVextex(edgeloop)
        pm.skinPercent(skinCls, vtx, resetToDefault=True)

        skinTools.edgeSkin(edgeLoopOriginal=edgeloop, paralelLoopNum=paralelLoopNum)



