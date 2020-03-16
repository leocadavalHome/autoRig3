import pymel.core as pm
import autoRig3.tools.controlTools as controlTools
import autoRig3.tools.groupTools as groupTools
import autoRig3.tools.jointTools as jointTools
import autoRig3.tools.attachTools as attatchTools
import autoRig3.tools.vertexWalkTools  as vtxWalk
import logging

logger = logging.getLogger('autoRig')

class Wing:
    def __init__(self, name='wing_sys', distance=500):
        #selecionada a lista de clustes base para posicionar os jnts:
        self.selection = pm.ls(sl=1)
        self.name = name
        self.ikhDrvList = []
        self.ikhNodeList = []
        self.bendList = []
        self.featherNameList = []
        self.baseCoordList = [] # posicao da base de cada pena
        self.baseOrientList = [] # orientacao da base de cada pena
        self.ikhCoordList = [] # posicao do end de cada pena
        self.featherParentGrp = []
        self.curve = None
        self.masterCtrl = None
        self.aimRbbn = None
        self.distance = distance

    def createJointChain(self, baseName, coordList, sufix = '_jnt', parent=None):
        jntList = []

        for e, coord in enumerate(coordList):
            if e < len(coordList)-1:
                name = baseName + sufix
            else:
                name = baseName + '_jnt_end'

            jnt = jointTools.makeJoint(name=name, coords=(coord, (0,0,0), (1,1,1)), connectToLast=1)
            if parent:
                if e == 0:
                    jnt.setParent(parent)

            jntList.append(jnt)

        pm.joint(jntList[0], e=1, oj='xyz', sao='yup')

        pm.select(clear=1)

        return jntList

    def createBend(self, obj, coords, parent=None):
        # bend1
        pm.select(obj)
        bend = pm.nonLinear(type='bend')
        bendTransform = bend[1]
        bendTransform.translate.set(coords[0])
        pm.xform(bendTransform, ro=coords[1], ws=1)
        pm.xform(bendTransform, ro=(0, 0, -90), os=1, r=1)

        bendScale = bendTransform.scaleX.get() * 2
        bendTransform.scale.set(bendScale, bendScale, bendScale)

        bend[0].lowBound.set(0)
        if parent:
            bendTransform.setParent(parent)

        return bend

    def featherSys(self, base, moduleSysGrp):

        sysGrp = groupTools.makeGroup(name=base + '_sys', suffix='', parent=moduleSysGrp)
        sysGrp.v.set(0)
        objToDeform = pm.listConnections(pm.listConnections(pm.listConnections(base.getShape())), t='mesh')[0]
        end = base + '_end'
        baseCoord = pm.xform(base, q=1, rp=1, ws=1)
        self.baseCoordList.append(baseCoord)
        endCoord = pm.xform(end, q=1, rp=1, ws=1)

        featherParentGrp = groupTools.makeGroup(name=base + '_parent_grp', parent=sysGrp, suffix='',
                                        coords=(baseCoord, (0,0,0), (1,1,1)))
        self.featherParentGrp.append(featherParentGrp)
        jointChain = self.createJointChain(base, [baseCoord, endCoord], parent=featherParentGrp)

        jntBase = jointChain[0]
        jntEnd = jointChain[1]

        ikh = pm.ikHandle(n=base + '_ikh', sj=jntBase, ee=jntEnd)[0]
        self.ikhNodeList.append(ikh)
        ikh.poleVectorX.set(0)
        ikh.poleVectorY.set(0)
        ikh.poleVectorZ.set(0)

        objOrient = pm.xform(jointChain[0], q=1, ro=1, ws=1)
        self.baseOrientList.append(objOrient)

        twkGrp = groupTools.makeGroup(name=base+'_twk', parent=moduleSysGrp,
                                        coords=(baseCoord, objOrient, (1,1,1)))
        twkJointChain = self.createJointChain(base+'_twk', [baseCoord, endCoord], parent=twkGrp)

        twkJntBase = twkJointChain[0]
        twkJntBase.v.set(0)
        twkJntEnd = twkJointChain[1]

        twkCtrl = controlTools.cntrlCrv(name=base+'_twk', icone='dropY', lockChannels=['v'], parent=twkGrp,
                              coords=(baseCoord, objOrient, (1,1,1)), size=5)

        twkCtrl.translate >> twkJntBase.translate
        twkCtrl.rotate >> twkJntBase.rotate
        twkCtrl.scale >> twkJntBase.scale

        pm.parentConstraint(jntBase, twkGrp, mo=1)
        pm.scaleConstraint(jntBase, twkGrp, mo=1)

        ikhZero = groupTools.makeGroup(name=base + '_ikh_zero', coords=(baseCoord, objOrient, (1, 1, 1)),
                                         parent=sysGrp, suffix='')

        ikhGrp = groupTools.makeGroup(name=base + '_ikh_grp', coords=(baseCoord, objOrient, (1, 1, 1)),
                                        parent=ikhZero, suffix='')
        self.ikhDrvList.append(ikhGrp)

        pm.xform(ikhZero, t=(self.distance, 0, 0), os=1, r=1)
        ikhPosition = pm.xform(ikhZero, q=1, rp=1, ws=1)

        self.ikhCoordList.append(ikhPosition)
        ikh.setParent(ikhGrp)
        # criando bends:
        nonlinearGrp = groupTools.makeGroup(name=base + '_bend_grp', parent=sysGrp)
        # bend1
        bendX = self.createBend(objToDeform, [baseCoord, objOrient, (1, 1, 1)], nonlinearGrp)
        # bend2
        bendY = self.createBend(objToDeform, [baseCoord, objOrient, (1, 1, 1)], nonlinearGrp)
        pm.xform(bendY, ro=(0, 90, 0), os=1, r=1)
        self.bendList.append([bendX, bendY])

        pm.skinCluster(twkJntBase, objToDeform)

    def ctrlCurve(self, parent=None):

        self.curve = pm.curve(n=self.name+'_curve', d=1, p=self.ikhCoordList)
        if parent:
            self.curve.setParent(parent)
        pm.rebuildCurve(self.curve, s=3, d=3)

        # criando cluster a cada dois cvs
        clusterDrivers = [] # clusters
        curveCtrls = [] # ctrls
        cvsToCluster = []
        poleCoords = []
        drvPtvList = [] # coords de pvt dos tres drivers
        drvOrientList = [] # orientacao dos drivers
        bendCtrlList = []

        index = 0
        curveDrvGrp = groupTools.makeGroup(name=self.name+'_curveDrv', parent=parent)
        curveDrvGrp.v.set(0)
        ctrlGrp = groupTools.makeGroup(name=self.name+'_ctrl', parent=parent)

        # criando ctrl master e parenteando os outros nele:
        masterZeroGrp = groupTools.makeGroup(name=self.name + '_master_zero',
                                               parent=ctrlGrp)
        self.masterCtrl = groupTools.makeGroup(name=self.name + '_master_ctrl', suffix='',
                                               parent=masterZeroGrp)

        masterShape = pm.duplicate(self.curve)[0]
        masterShape.translateZ.set(-25)

        # criando uma rbbn para orientar os pose readers das penas:
        rbbnName = self.name+'_aimRbbn'
        self.aimRbbn = pm.loft(self.curve, masterShape, ch=False, ar=True, d=1, n=rbbnName)[0]
        self.aimRbbn.setParent(parent)
        self.aimRbbn.v.set(0)


        for e, cv in enumerate(self.curve.cv):
            if e == 0 or e == len(self.curve.cv)-1:
                poleCoords.append(vtxWalk.bbox(cv)['globalPvt'])

            cvsToCluster.append(cv)
            for eachSpam in range(2):
                cvsToCluster.append(str(self.aimRbbn.name())+'.cv['+str(eachSpam)+']['+str(e)+']')

            index += 1
            if index == 2:
                cluster = pm.cluster(cvsToCluster, n=self.name+'_'+str((e/2)+1))[1]
                cluster.setParent(curveDrvGrp)
                clusterDrivers.append(cluster)

                index = 0
                cvsToCluster = []

        # ajustando pivos dos clusters das extremidades para os extremos
        pm.xform(clusterDrivers[0], rp=poleCoords[0], ws=1)
        pm.xform(clusterDrivers[2], rp=poleCoords[1], ws=1)

        # criando drv ctrls para a curva
        for e, drv in enumerate(clusterDrivers):
            currentPvt = pm.xform(clusterDrivers[e], rp=1, q=1, ws=1)
            ctrl = controlTools.cntrlCrv(name=self.name+'_'+str(e+1), size=20,
                                         coords=(currentPvt, (0,0,0), (1,1,1)),
                                         parent=ctrlGrp, lockChannels=['v',], color=(.9,.9,0))
            drvPtvList.append(currentPvt)
            curveCtrls.append(ctrl)

        # orientando drv ctrls:
        for i, ctrl in enumerate(curveCtrls):
            target = ctrl.getParent()
            if i == 0:
                source = curveCtrls[1]
                aim = (1,0,0)

            elif i == 1:
                source = curveCtrls[2]
                aim = (1,0,0)

            elif i == 2:
                source = curveCtrls[1]
                aim = (-1,0,0)

            tempConstraint = pm.aimConstraint(source, target, wut='scene', aim=aim, mo=0)
            pm.delete (tempConstraint)
            drvOrientList.append(pm.xform(ctrl, q=1, ro=1, ws=1))

            # contraint do controle para os clusters:

            pm.parentConstraint(ctrl, clusterDrivers[i], mo=1)
            pm.scaleConstraint(ctrl, clusterDrivers[i], mo=1)


        pm.xform(masterZeroGrp, t=drvPtvList[1], ro=drvOrientList[1], ws=1)

        masterShape.setParent(self.masterCtrl)
        pm.makeIdentity(masterShape, t=1, r=1, apply=1)

        pm.parent(masterShape.getShape(), self.masterCtrl, r=1, s=1)
        pm.delete(masterShape)
        self.curve.getShape().template.set(1)

        for ctrl in curveCtrls:
            ctrl.getParent().setParent(self.masterCtrl)


        # ctrls de bend:

        bendCtrl1 = controlTools.cntrlCrv(name=self.name+'_bend1', icone='trianguloZ', size=15, lockChannels=['v'],
                                          coords=(drvPtvList[0], drvOrientList[0], (1,1,1)), parent=ctrlGrp,
                                          color=(0,.1,.5))
        pm.xform(bendCtrl1, t=(0,0,40), ro=(0,90,0), r=1)
        pm.makeIdentity(bendCtrl1, r=1, apply=1)
        bendCtrl1.getParent().setParent(curveCtrls[0])
        bendCtrlList.append(bendCtrl1)

        bendCtrl2 = controlTools.cntrlCrv(name=self.name + '_bend2', icone='trianguloZ', size=15, lockChannels=['v'],
                                          coords=(drvPtvList[2], drvOrientList[2], (1, 1, 1)), parent=ctrlGrp,
                                          color=(0,.1,.5))
        pm.xform(bendCtrl2, t=(0,0,40), ro=(0,-90,0), r=1)
        pm.makeIdentity(bendCtrl2, r=1, apply=1)
        bendCtrl2.getParent().setParent(curveCtrls[2])
        bendCtrlList.append(bendCtrl2)


        return self.masterCtrl, curveCtrls, bendCtrlList

    def getTransform(self, var):
        if type(var) is list:
            transform = pm.ls(var, type='transform')[0]
        else:
            transform = var

        return transform

    def createMotionPath(self, object, curve, uValue, fractionMode=False):

        motionPath = pm.pathAnimation(object, curve, follow=1)
        PyMotionPath = pm.PyNode(motionPath)
        animNode = pm.listConnections(motionPath, t='animCurve')
        pm.delete(animNode)
        PyMotionPath.fractionMode.set(fractionMode)
        PyMotionPath.uValue.set(uValue)
        return PyMotionPath

    def returnClosestPointOnCurve(self, coords=[], curve=None, objList=[]):
        '''
        :param coords: [(x,y,z),(x,y,z)]
        :param objList: lista de objetos a serem extraidas as coordenadas. Essa lista sobrepoe a de coordenadas
        :param curve: curva base
        :return:
        '''
        curve = self.getTransform(curve)

        if objList:
            coords = []
            for obj in objList:
                coord = pm.xform(obj, q=1, rp=1, ws=1)
                coords.append(coord)

        paramList = []

        reader = pm.createNode('nearestPointOnCurve', n='nearestPointOnCurve_reader')
        curve.getShape().local >> reader.inputCurve

        for coord in coords:
            reader.inPosition.set(coord)
            paramList.append(reader.result.parameter.get())

        pm.delete(reader)

        return paramList

    def connectToBendCtrl(self, index, bendCtrls, blendValue):

        for b, bend in enumerate(self.bendList[index]):
            outputCtrl = []
            for e, ctrl in enumerate(bendCtrls):
                bendMultNodeName = self.name+'_bend_'+str(e)+'_'+str(bend)+'_'+str(index)+'_mult'
                bendMultNode = pm.createNode('multDoubleLinear', n=bendMultNodeName)
                if b == 0:
                    ctrl.translateY >> bendMultNode.input1
                elif b == 1:
                    ctrl.translateX >> bendMultNode.input1

                bendMultNode.input2.set(-.25)
                outputCtrl.append(bendMultNode)

            blenderNodeName = self.name+'_bend_'+str(bend)+'_'+str(index)+'_blend'
            blendNode = pm.shadingNode('blendColors', n=blenderNodeName, asUtility=True)
            outputCtrl[1].output >> blendNode.color1R
            outputCtrl[0].output >> blendNode.color2R
            blendNode.outputR >> bend[0].curvature
            blendNode.blender.set(blendValue)

    def createPoseReader(self, index, parent, featherParent):
        baseCoord = self.baseCoordList[index]
        baseOrient = self.baseOrientList[index]
        aimCoord = self.ikhCoordList[index]
        name = self.featherNameList[index]
        ikh = self.ikhNodeList[index]
        ikhDrv = self.ikhDrvList[index]

        readerGrpName = name + '_reader'
        readerBaseLocName = name + '_reader_base_loc'
        readerAimUpLocName = name + '_reader_aim_up_loc'
        readerAimWorldLocName = name + '_reader_aim world_loc'
        readerUpLocName = name + '_reader_upVect_loc'
        readerAimLocName = name + '_reader_target_loc'
        readerMultNegName = name + '_reader_multNeg_md'

        readerGrp = groupTools.makeGroup(name=readerGrpName,
                                           parent=parent, coords=(aimCoord, baseOrient, (1,1,1)))
        readerGrp.v.set(0)

        readerBaseLoc = controlTools.cntrlCrv(icone='null', name=readerBaseLocName, cntrlSulfix='',
                                              parent=readerGrp, coords=(aimCoord, baseOrient, (1,1,1)))

        readerAimUpLoc = controlTools.cntrlCrv(icone='null', name=readerAimUpLocName, cntrlSulfix='', hasZeroGrp=0,
                                               parent=readerBaseLoc, coords=(aimCoord, baseOrient, (1,1,1)))

        readerAimWorldLoc = controlTools.cntrlCrv(icone='null', name=readerAimWorldLocName, cntrlSulfix='',hasZeroGrp=0,
                                               parent=readerAimUpLoc, coords=(aimCoord, baseOrient, (1,1,1)))

        readerUpLoc = controlTools.cntrlCrv(icone='null', name=readerUpLocName, cntrlSulfix='',
                                               parent=readerBaseLoc, coords=(aimCoord, baseOrient, (1,1,1)))

        readerTargetLoc = controlTools.cntrlCrv(icone='null', name=readerAimLocName, cntrlSulfix='',
                                               parent=readerGrp, coords=(baseCoord, baseOrient, (1,1,1)))

        pm.xform(readerUpLoc.getParent(), t=(0,10,0), r=1, os=1)
        pm.aimConstraint(readerTargetLoc, readerAimUpLoc, wuo= readerUpLoc,
                         wut= 'object', u=(0,1,0), aim=(-1,0,0), mo=0)

        pm.aimConstraint(readerTargetLoc, readerAimWorldLoc, wut='scene', u=(0,1,0), aim=(-1,0,0), mo=0)

        pm.parentConstraint(featherParent, readerTargetLoc, mo=1)
        pm.scaleConstraint(featherParent, readerTargetLoc, mo=1)
        foll = attatchTools.hookOnMesh(inputs=[readerGrp, self.aimRbbn], mode=3)
        foll.v.set(0)


        readerMultNeg = pm.createNode('multDoubleLinear', n=readerMultNegName)
        readerAimWorldLoc.rotateX >> readerMultNeg.input1
        readerMultNeg.input2.set(-1)

        readerMultNeg.output >> ikh.twist

        return self

    def orientJoint(self, index, locDrv, parent):
        ikhNode = self.ikhNodeList[index]
        featherParentGrp = self.featherParentGrp[index]

        self.createPoseReader(index, parent, featherParentGrp)

        return locDrv

    def connectCtrls(self, ctrls, parent):
        masterCtrl = ctrls[0]
        drvCtrlList = ctrls[1]
        bendCtrlList = ctrls[2]

        paramList = self.returnClosestPointOnCurve(objList=self.ikhDrvList, curve=self.curve)
        locDrvGrp = groupTools.makeGroup(name=self.name+'_loc_drv', parent=parent)
        locDrvGrp.v.set(0)
        curveMinMaxValue = self.curve.getShape().minMaxValue.get()
        curveSize = curveMinMaxValue[1] - curveMinMaxValue[0]

        locDrvList = []
        for i, each in enumerate(paramList):
            locDrv = controlTools.cntrlCrv(icone='null', name=self.name+'_drv_'+str(i+1)+'_loc',
                                           hasZeroGrp=0, parent=locDrvGrp,
                                           cntrlSulfix='', coords=(self.ikhCoordList[i], (0,0,0), (1,1,1)))
            locDrvList.append(locDrv)
            self.createMotionPath(locDrv, self.curve, each)

            pm.pointConstraint (locDrv, self.ikhNodeList[i], mo=0)

            # construir o reader para extrair rotacao da curva
            self.orientJoint(i, locDrv, parent)

            # bends:
            blendValue = each / curveSize
            self.connectToBendCtrl(i, bendCtrlList, blendValue)


    def constructor(self):
        pm.select(cl=1)

        moduleSysGrp = groupTools.makeGroup(name=self.name, suffix='')

        for base in self.selection:
            self.featherNameList.append(base)
            self.featherSys(base, moduleSysGrp)

        ctrls = self.ctrlCurve(moduleSysGrp)

        self.connectCtrls(ctrls, moduleSysGrp)

        # criar reader para lidar com o twist das penas automaticamente e ainda termos controle individual
        # o grupo sera parenteado em uma curva

#w = Wing(name='R_wing_C_3_sys', distance=500)
#w.constructor()

#Fileira A - Distance 300
#Fileira B - Distance 400
#Fileira C - Distance 500

# rodar por modulo (membro) de modo que temos controles para dividir os bends para dois controles das extremidades
# alem de controles para uma curva pra onde apontam as penas


# connect feathers ctrls
'''
  selecione dois controles proximos de dois sistemas de asa diferentes e rode
  o script vai criar atributos nesses controles para que fiquem proximos ou se 
  mantenham levados inteiramente pelos seus moveall
'''

def connectCtrls():
    ctrls = pm.ls(sl=1)

    masterGrp = groupTools.makeGroup(name='wingCtrlsConnect')
    coordsList = []
    midDrvLocs = []
    holdDrvLocs = []

    mdCtrlsCoord = vtxWalk.bbox(ctrls)['globalPvt']
    middle = controlTools.cntrlCrv(name='wingCtrlsConnect_mid_loc', coords=(mdCtrlsCoord, (0, 0, 0), (1, 1, 1)),
                                   cntrlSulfix='', parent=masterGrp, icone='null')
    tempConstraint = pm.pointConstraint(ctrls[0], ctrls[1], middle, mo=0)
    pm.delete (tempConstraint)
    pm.parentConstraint(ctrls[0].getParent().getParent(), ctrls[1].getParent().getParent(), middle, mo=1,
                        sr=['x', 'y', 'z'])
    pm.aimConstraint(ctrls[0].getParent().getParent(), middle, wut='scene', mo=0)
    orientMiddle = pm.xform(middle, q=1, ro=1, ws=1)

    for ctrl in ctrls:
        coord = vtxWalk.bbox(ctrl)['globalPvt']
        coordsList.append(coordsList)

        midLoc = controlTools.cntrlCrv(name=ctrl+'_mid_drv_loc', coords=(coord, (0,0,0), (1,1,1)),
                                            cntrlSulfix='', parent = middle, icone='null')
        midDrvLocs.append(midLoc)

        holdLoc = controlTools.cntrlCrv(name=ctrl + '_hold_drv_loc', coords=(coord, orientMiddle, (1, 1, 1)),
                                             cntrlSulfix='', parent=masterGrp, icone='null')
        holdDrvLocs.append(holdLoc)
        pm.parentConstraint(ctrl.getParent().getParent(), holdLoc, mo=1)
        pm.addAttr(ctrl, ln='autoConnect', dv=0.8, min=0, max=1, k=1)

        drvPointConstraint = pm.pointConstraint(midLoc, holdLoc, ctrl.getParent(), mo=1)
        #drvOrientConstraint = pm.orientConstraint(middle, holdLoc, ctrl.getParent(), mo=1)

        revNode = pm.createNode('reverse', n='wingCtrlsConnect_rev')
        ctrl.autoConnect >> revNode.inputX
        pm.connectAttr(ctrl.autoConnect, drvPointConstraint + '.' + midLoc + 'W0')
        pm.connectAttr(revNode.outputX, drvPointConstraint + '.' + holdLoc + 'W1')