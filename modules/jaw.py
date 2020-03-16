import pymel.core as pm
import autoRig3.tools.controlTools as controlTools
import autoRig3.tools.jointTools as jointTools
import json
import logging

logger = logging.getLogger('autoRig')

class Jaw:
    def __init__(self, name='jaw'):
        self.guideDict = {'moveall': [(0, 0, 0), (0, 0, 0), (1,1,1)], 'L_corner': [(.31, -0.01, -.1), (0, 0, 0)],
                          'R_corner': [(-.31, -0.01, -.1), (0, 0, 0)], 'pivot': [(0, 0.18, -1.15), (0, 0, 0)],
                          'upperLip': [(0, .15, -.01), (0, 0, 0)], 'jaw': [(0, -0.180, -0.030), (0, 0, 0)],
                          'lowerTeeth': [(0, -.1, -.2), (-90, 0, 0)], 'upperTeeth': [(0, .12, -.2), (90, 0, 0)],
                          'tongue1': [(0, 0, -1.0), (0, 0, 0)], 'tongue2': [(0, 0, -.85), (0, 0, 0)],
                          'tongue3': [(0, 0, -.7), (0, 0, 0)], 'tongue4': [(0, 0, -.55), (0, 0, 0)],
                          'tongue5': [(0, 0, -.40), (0, 0, 0)]}
        self.name = name
        self.toExport = [
                         'name', 'guideDict', 'moveallGuideSetup', 'moveallCtrlSetup', 'L_cornerGuideSetup',
                         'R_cornerGuideSetup',
                         'jawGuideSetup', 'jawCtrlSetup', 'pivotGuideSetup', 'upperLipGuideSetup',
                         'upperTeethGuideSetup', 'upperTeethCtrlSetup',
                         'lowerTeethGuideSetup', 'lowerTeethCtrlSetup'
                         ]
        self.guideSulfix = '_guide'
        self.moveallGuideSetup = {'nameTempl': self.name + 'Moveall', 'icone': 'quadradoZ', 'size': 1, 'color': (1, 0, 0)}
        self.L_cornerGuideSetup = {'nameTempl': 'L_corner', 'icone': 'cubo', 'size': .2, 'color': (32, .7, .17)}
        self.R_cornerGuideSetup = {'nameTempl': 'R_corner', 'icone': 'cubo', 'size': .2, 'color': (32, .7, .17)}
        self.jawGuideSetup = {'nameTempl': 'jaw', 'icone': 'bola', 'size': .2, 'color': (32, .7, .17)}
        self.pivotGuideSetup = {'nameTempl': 'jawPivot', 'icone': 'bola', 'size': .2,'color': (0, 1, 1)}
        self.upperLipGuideSetup = {'nameTempl': 'upperLip', 'icone': 'bola', 'size': .2,'color': (32, .7, .17)}
        self.upperTeethGuideSetup = {'nameTempl': 'upperTeeth', 'icone': 'cubo', 'size': .2 ,'color': (0, 1, 1)}
        self.lowerTeethGuideSetup = {'nameTempl': 'lowerTeeth', 'icone': 'cubo', 'size': .2 ,'color': (0, 1, 1)}

        self.tongue1GuideSetup = {'nameTempl': 'tongue1', 'icone': 'cubo', 'size': .1, 'color': (0, 1, 1)}
        self.tongue2GuideSetup = {'nameTempl': 'tongue2', 'icone': 'cubo', 'size': .1, 'color': (0, 1, 1)}
        self.tongue3GuideSetup = {'nameTempl': 'tongue3', 'icone': 'cubo', 'size': .1, 'color': (0, 1, 1)}
        self.tongue4GuideSetup = {'nameTempl': 'tongue4', 'icone': 'cubo', 'size': .1, 'color': (0, 1, 1)}
        self.tongue5GuideSetup = {'nameTempl': 'tongue5', 'icone': 'cubo', 'size': .1, 'color': (0, 1, 1)}

        self.moveallCtrlSetup = {'nameTempl': self.name + 'MoveAll', 'icone': 'grp', 'size': 1.8, 'color': (1, 1, 0)}
        self.jawCtrlSetup = {'nameTempl': 'jaw', 'icone': 'cubo', 'size': .5,'color': (0, 1, 1)}
        self.upperTeethCtrlSetup = {'nameTempl': 'upperTeeth', 'icone': 'cubo', 'size': .8,'color': (0, 1, 1)}
        self.lowerTeethCtrlSetup = {'nameTempl': 'lowerTeeth', 'icone': 'cubo', 'size': .8,'color': (0, 1, 1)}

        self.tongue1CtrlSetup = {'nameTempl': 'tongue1', 'icone': 'cubo', 'size': .1, 'color': (0, 1, 1)}
        self.tongue2CtrlSetup = {'nameTempl': 'tongue2', 'icone': 'cubo', 'size': .1, 'color': (0, 1, 1)}
        self.tongue3CtrlSetup = {'nameTempl': 'tongue3', 'icone': 'cubo', 'size': .1, 'color': (0, 1, 1)}
        self.tongue4CtrlSetup = {'nameTempl': 'tongue4', 'icone': 'cubo', 'size': .1, 'color': (0, 1, 1)}
        self.tongue5CtrlSetup = {'nameTempl': 'tongue5', 'icone': 'cubo', 'size': .1, 'color': (0, 1, 1)}


    def createCntrl(self, cntrlName):
        displaySetup = self.__dict__[cntrlName+'Setup'].copy()
        cntrlName = displaySetup['nameTempl'] + self.guideSulfix
        if pm.objExists(cntrlName):
            pm.delete(cntrlName)
        guide = controlTools.cntrlCrv(name=cntrlName, hasZeroGrp=False, cntrlSulfix='', hasHandle=True, **displaySetup)
        return guide

    def setCntrl (self, cntrl, posRot, space='object'):
        cntrl.setTranslation(self.guideDict[posRot][0], space=space)
        cntrl.setRotation(self.guideDict[posRot][1], space=space)
        try:
            cntrl.setScale(self.guideDict[posRot][2])
        except:
            pass

    def exportDict(self):
        expDict = {}
        for key in self.toExport:
                expDict[key] = self.__dict__[key]
        return expDict


    def doGuide(self, **kwargs):
        self.__dict__.update(kwargs)

        if pm.objExists('facial_guides_grp'):
            facialGrp = 'facial_guides_grp'
        else:
            facialGrp = pm.group(n='facial_guides_grp', em=True)

        self.guideMoveall = self.createCntrl('moveallGuide')
        self.L_cornerGuide = self.createCntrl('L_cornerGuide')
        self.R_cornerGuide = self.createCntrl('R_cornerGuide')
        self.jawGuide = self.createCntrl('jawGuide')
        self.pivotGuide = self.createCntrl('pivotGuide')
        self.upperLipGuide = self.createCntrl('upperLipGuide')
        self.upperTeethGuide = self.createCntrl('upperTeethGuide')
        self.lowerTeethGuide = self.createCntrl('lowerTeethGuide')

        self.tongue1Guide = self.createCntrl('tongue1Guide')
        self.tongue2Guide = self.createCntrl('tongue2Guide')
        self.tongue3Guide = self.createCntrl('tongue3Guide')
        self.tongue4Guide = self.createCntrl('tongue4Guide')
        self.tongue5Guide = self.createCntrl('tongue5Guide')

        pm.parent(self.L_cornerGuide, self.R_cornerGuide, self.jawGuide, self.upperLipGuide, self.pivotGuide,
                  self.upperTeethGuide, self.lowerTeethGuide,self.tongue1Guide, self.tongue2Guide, self.tongue3Guide,
                  self.tongue4Guide, self.tongue5Guide, self.guideMoveall)


        self.setCntrl(self.L_cornerGuide, 'L_corner')
        self.setCntrl(self.R_cornerGuide, 'R_corner')
        self.setCntrl(self.jawGuide, 'jaw')
        self.setCntrl(self.pivotGuide, 'pivot')
        self.setCntrl(self.upperLipGuide, 'upperLip')
        self.setCntrl(self.upperTeethGuide, 'upperTeeth')
        self.setCntrl(self.lowerTeethGuide, 'lowerTeeth')

        self.setCntrl(self.tongue1Guide, 'tongue1')
        self.setCntrl(self.tongue2Guide, 'tongue2')
        self.setCntrl(self.tongue3Guide, 'tongue3')
        self.setCntrl(self.tongue4Guide, 'tongue4')
        self.setCntrl(self.tongue5Guide, 'tongue5')
        
        self.setCntrl(self.guideMoveall, 'moveall')

        self.R_cornerGuide.template.set(1)

        guide_mdn = pm.createNode('multiplyDivide')
        guide_mdn.input2.input2X.set(-1)

        self.L_cornerGuide.translate >> guide_mdn.input1
        guide_mdn.output >> self.R_cornerGuide.translate
        self.L_cornerGuide.rotate >> self.R_cornerGuide.rotate
        self.L_cornerGuide.scale >> self.R_cornerGuide.scale


        pm.parent(self.guideMoveall, facialGrp)

        pm.addAttr(self.guideMoveall, ln='jawDict', dt='string')
        self.guideMoveall.jawDict.set(json.dumps(self.exportDict()))

    def getDict(self):
        try:
            guideName = self.moveallGuideSetup['nameTempl'] + self.guideSulfix
            self.guideMoveall = pm.PyNode(guideName)

            jsonDict = self.guideMoveall.jawDict.get()
            limbDictRestored = json.loads(jsonDict)

            self.__dict__.update(**limbDictRestored)

            guideName = self.moveallGuideSetup['nameTempl'] + self.guideSulfix
            self.guideMoveall = pm.PyNode(guideName)
            self.guideDict['moveall'][0] = self.guideMoveall.getTranslation(space='world').get()
            self.guideDict['moveall'][1] = tuple(self.guideMoveall.getRotation(space='object'))
            self.guideDict['moveall'][2] = tuple(pm.xform(self.guideMoveall, q=True, s=True, ws=True))

            guideName = self.L_cornerGuideSetup['nameTempl'] + self.guideSulfix
            self.L_cornerGuide = pm.PyNode(guideName)
            self.guideDict['L_corner'][0] = self.L_cornerGuide.getTranslation(space='object').get()
            self.guideDict['L_corner'][1] = tuple(self.L_cornerGuide.getRotation(space='object'))

            guideName = self.R_cornerGuideSetup['nameTempl'] + self.guideSulfix
            self.R_cornerGuide = pm.PyNode(guideName)
            self.guideDict['R_corner'][0] = self.R_cornerGuide.getTranslation(space='object').get()
            self.guideDict['R_corner'][1] = tuple(self.R_cornerGuide.getRotation(space='object'))

            guideName = self.jawGuideSetup['nameTempl'] + self.guideSulfix
            self.jawGuide = pm.PyNode(guideName)
            self.guideDict['jaw'][0] = self.jawGuide.getTranslation(space='object').get()
            self.guideDict['jaw'][1] = tuple(self.jawGuide.getRotation(space='object'))

            guideName = self.pivotGuideSetup['nameTempl'] + self.guideSulfix
            self.pivotGuide = pm.PyNode(guideName)
            self.guideDict['pivot'][0] = self.pivotGuide.getTranslation(space='object').get()
            self.guideDict['pivot'][1] = tuple(self.pivotGuide.getRotation(space='object'))

            guideName = self.upperLipGuideSetup['nameTempl'] + self.guideSulfix
            self.upperLipGuide = pm.PyNode(guideName)
            self.guideDict['upperLip'][0] = self.upperLipGuide.getTranslation(space='object').get()
            self.guideDict['upperLip'][1] = tuple(self.upperLipGuide.getRotation(space='object'))

            guideName = self.upperTeethGuideSetup['nameTempl'] + self.guideSulfix
            self.upperTeethGuide = pm.PyNode(guideName)
            self.guideDict['upperTeeth'][0] = self.upperTeethGuide.getTranslation(space='object').get()
            self.guideDict['upperTeeth'][1] = tuple(self.upperTeethGuide.getRotation(space='object'))

            guideName = self.lowerTeethGuideSetup['nameTempl'] + self.guideSulfix
            self.lowerTeethGuide = pm.PyNode(guideName)
            self.guideDict['lowerTeeth'][0] = self.lowerTeethGuide.getTranslation(space='object').get()
            self.guideDict['lowerTeeth'][1] = tuple(self.lowerTeethGuide.getRotation(space='object'))
            
            
            guideName = self.tongue1GuideSetup['nameTempl'] + self.guideSulfix
            self.tongue1Guide = pm.PyNode(guideName)
            self.guideDict['tongue1'][0] = self.tongue1Guide.getTranslation(space='object').get()
            self.guideDict['tongue1'][1] = tuple(self.tongue1Guide.getRotation(space='object'))
            
            guideName = self.tongue2GuideSetup['nameTempl'] + self.guideSulfix
            self.tongue2Guide = pm.PyNode(guideName)
            self.guideDict['tongue2'][0] = self.tongue2Guide.getTranslation(space='object').get()
            self.guideDict['tongue2'][1] = tuple(self.tongue2Guide.getRotation(space='object'))
            
            guideName = self.tongue3GuideSetup['nameTempl'] + self.guideSulfix
            self.tongue3Guide = pm.PyNode(guideName)
            self.guideDict['tongue3'][0] = self.tongue3Guide.getTranslation(space='object').get()
            self.guideDict['tongue3'][1] = tuple(self.tongue3Guide.getRotation(space='object'))
            
            guideName = self.tongue4GuideSetup['nameTempl'] + self.guideSulfix
            self.tongue4Guide = pm.PyNode(guideName)
            self.guideDict['tongue4'][0] = self.tongue4Guide.getTranslation(space='object').get()
            self.guideDict['tongue4'][1] = tuple(self.tongue4Guide.getRotation(space='object'))
            
            guideName = self.tongue5GuideSetup['nameTempl'] + self.guideSulfix
            self.tongue5Guide = pm.PyNode(guideName)
            self.guideDict['tongue5'][0] = self.tongue5Guide.getTranslation(space='object').get()
            self.guideDict['tongue5'][1] = tuple(self.tongue5Guide.getRotation(space='object'))
        except:
            print('GetDict nao funcionou')

    def doRig(self):

        sufix_skin = 'jxt'
        sufix = 'pivot'

        if not self.guideMoveall:
            self.doGuide()

        if pm.objExists(self.name + '_sys'):
            pm.delete(self.name + '_sys')

        if pm.objExists(self.name + '_constrained'):
            pm.delete (self.name + '_constrained')

        if pm.objExists('head_contrained'):
            head_constrained_grp = 'head_contrained'
        else:
            head_constrained_grp = pm.group(n='head_contrained', em=True)

        moveall = pm.group(n=self.name+'_sys', em=True)

        constrained_grp = pm.group(n=self.name+'_constrained', em=True)
        pm.parent (constrained_grp, head_constrained_grp)

        pm.select(cl=True)
        pivot = pm.xform(self.pivotGuide, q=True, ws=True, t=True)
        jawZero = pm.joint(p=pivot, n='jaw_zero')
        jawJnt = pm.joint(p=pivot, n='jaw_'+ sufix)
        jaw = pm.xform(self.jawGuide, q=True, ws=True, t=True)
        pm.joint(p=jaw, n='jaw_'+sufix_skin)

        pm.select(cl=True)
        L_cornerJnt = pm.joint(p=pivot, n='L_corner_'+sufix)
        L_corner = pm.xform(self.L_cornerGuide, q=True, ws=True, t=True)
        L_cornerTipJnt = pm.joint(p=L_corner, n='L_corner_'+sufix_skin)
        L_ikh = pm.ikHandle(L_cornerJnt, L_cornerTipJnt, sol='ikRPsolver', n=L_cornerJnt+'_ikh')
        pm.select(cl=True)
        L_constraint = pm.parentConstraint(jawZero, jawJnt, L_ikh[0], mo=True)

        pm.select(cl=True)
        R_cornerJnt = pm.joint(p=pivot, n='R_corner_'+sufix)
        R_corner = pm.xform(self.R_cornerGuide, q=True, ws=True, t=True)
        R_cornerTipJnt = pm.joint(p=R_corner, n='R_corner_'+sufix_skin)
        R_ikh = pm.ikHandle(R_cornerJnt, R_cornerTipJnt, sol='ikRPsolver', n=R_cornerJnt+'_ikh')
        R_constraint = pm.parentConstraint(jawZero, jawJnt, R_ikh[0], mo=True)

        pm.select(cl=True)
        upperLipJnt = pm.joint(p=pivot, n='upperLip_'+sufix)
        upperLip = pm.xform(self.upperLipGuide, q=True, ws=True, t=True)
        pm.joint(p=upperLip, n='upperLip_'+sufix_skin)

        pm.select(cl=True)

        tongueJnts = []
        previousJnt = None
        for i in range(1, 6):
            print i
            guide = self.__dict__['tongue'+str(i)+'Guide']
            jnt = jointTools.makeJoint(name='tongue'+str(i), jntSulfix='_jxt', connectToLast=True, obj=guide)
            if previousJnt:
                pm.joint(previousJnt, e=True, zso=True, oj='xyz', sao='yup')

            previousJnt=jnt
            print jnt
            tongueJnts.append(jnt)
        tongueJnts[-1].jointOrientX.set(0)
        tongueJnts[-1].jointOrientY.set(0)
        tongueJnts[-1].jointOrientZ.set(0)
        jointTools.zeroJoints(tongueJnts)

        pm.parent(tongueJnts[0].getParent(), jawJnt)

        previousCtrl=None
        tongueFirstCtrl = None
        print tongueJnts
        for i, jnt in enumerate(tongueJnts):
            print i
            print jnt
            tongueCtrl = controlTools.cntrlCrv(name='tongue'+str(i), obj=jnt, connType='connection', size=.2, icone='cubo')
            if previousCtrl:
                pm.parent(tongueCtrl.getParent(), previousCtrl)
            else:
                tongueFirstCtrl = tongueCtrl
            previousCtrl = tongueCtrl
        print tongueFirstCtrl

        jawCntrl = controlTools.cntrlCrv(name='jaw_ctrl', obj=jawJnt, connType='connection', size=.5, icone='jaw')
        jawCntrl.addAttr('L_cornerFollow', at='float', dv=0.5, k=1)
        jawCntrl.addAttr('R_cornerFollow', at='float', dv=0.5, k=1)

        b = jaw
        a = pivot
        shape = jawCntrl.getShape()
        pm.move(b[0] - a[0], (b[1] - a[1]) - .3, (b[2] - a[2]) + .4, shape.cv, r=True)

        L_reverse = pm.createNode('reverse')
        jawCntrl.L_cornerFollow >> L_reverse.input.inputX
        jawCntrl.L_cornerFollow >> L_constraint.attr(jawZero.name() + 'W0')
        L_reverse.output.outputX >> L_constraint.attr(jawJnt.name() + 'W1')
        jawCntrl.R_cornerFollow >> L_reverse.input.inputY
        jawCntrl.R_cornerFollow >> R_constraint.attr(jawZero.name() + 'W0')
        L_reverse.output.outputY >> R_constraint.attr(jawJnt.name() + 'W1')

        ##
        cond = pm.createNode('condition')
        multiUpLip = pm.createNode('multDoubleLinear')

        jawJnt.rotateX >> cond.firstTerm
        cond.secondTerm.set(0)
        cond.operation.set(4)
        cond.colorIfFalseR.set(0)
        multiUpLip.input2.set(.3)
        jawJnt.rotateX >> multiUpLip.input1
        multiUpLip.output >> cond.colorIfTrue.colorIfTrueR
        cond.outColor.outColorR >> upperLipJnt.rotateX

        self.guideMoveall.visibility.set(False)
        moveall.visibility.set(False)

        #DENTES
        pm.select(cl=True)
        upperTeeth = pm.xform(self.upperTeethGuide, q=True, ws=True, t=True)
        upperTeethJnt = pm.joint(p=upperTeeth, n='upperTeeth_zero')
        upperTeethJxt = pm.joint(n='upperTeeth_'+sufix_skin)

        pm.select(cl=True)
        lowerTeeth = pm.xform(self.lowerTeethGuide, q=True, ws=True, t=True)
        lowerTeethJnt = pm.joint(p=lowerTeeth, n='lowerTeeth_zero')
        lowerTeethJxt = pm.joint(n='lowerTeeth_'+sufix_skin)

        teethUpCtrl = controlTools.cntrlCrv(name='teeth_up_ctrl', obj=upperTeethJxt, connType='connection', size=.5, icone='upTeeth')
        teethDwCtrl = controlTools.cntrlCrv(name='teeth_dw_ctrl', obj=lowerTeethJxt, connType='connection', size=.5, icone='dwTeeth')

        pm.parent(upperTeethJnt, upperLipJnt)
        pm.parent(lowerTeethJnt, jawJnt)
        pm.parent(L_cornerJnt, R_cornerJnt, jawZero, upperLipJnt, L_ikh[0], R_ikh[0], moveall)
        pm.parent(jawCntrl.getParent(), tongueFirstCtrl.getParent(), teethUpCtrl.getParent(), teethDwCtrl.getParent(),
                  constrained_grp)