import pymel.core as pm
import autoRig3.tools.rigFunctions as rigFunctions

# j=Jaw(name='jaw')
# j.doGuide()
# j.getGuideFromScene()
# j.doRig()

class Jaw:
    def __init__(self, name='jaw'):
        self.jawGuideDict = {'moveall': [0, 0, 0], 'lcorner': [.31, -0.01, -.1], 'rcorner': [-.31, -0.01, -.1],
                             'jaw': [0, -.18, -.03], 'upperLip': [0, .15, -.01], 'pivot': [0, .15, -1.15],
                             'hold': [0, -.2, -1.5]}
        self.guideMoveall = None
        self.name = name

    def doGuide(self):
        if pm.objExists(self.name + 'Moveall_guide'):
            pm.delete(self.name + 'Moveall_guide')

        self.guideMoveall = pm.group(em=True, n=self.name + 'Moveall_guide')
        self.guideMoveall.translate.set(self.jawGuideDict['moveall'])

        self.lcornerGuide = pm.spaceLocator(n='lcorner')
        self.lcornerGuide.translate.set(self.jawGuideDict['lcorner'])
        self.lcornerGuide.localScale.set(0.1, 0.1, 0.1)

        self.rcornerGuide = pm.spaceLocator(n='rcorner')
        self.rcornerGuide.translate.set(self.jawGuideDict['rcorner'])
        self.rcornerGuide.localScale.set(0.1, 0.1, 0.1)

        self.jawGuide = pm.spaceLocator(n='jaw')
        self.jawGuide.translate.set(self.jawGuideDict['jaw'])
        self.jawGuide.localScale.set(0.1, 0.1, 0.1)

        self.upperLipGuide = pm.spaceLocator(n='upperLip')
        self.upperLipGuide.translate.set(self.jawGuideDict['upperLip'])
        self.upperLipGuide.localScale.set(0.1, 0.1, 0.1)

        self.pivotGuide = pm.spaceLocator(n='pivot')
        self.pivotGuide.translate.set(self.jawGuideDict['pivot'])
        self.pivotGuide.localScale.set(0.1, 0.1, 0.1)

        self.holdGuide = pm.spaceLocator(n='hold')
        self.holdGuide.translate.set(self.jawGuideDict['hold'])
        self.holdGuide.localScale.set(0.1, 0.1, 0.1)

        pm.parent(self.lcornerGuide, self.rcornerGuide, self.jawGuide, self.upperLipGuide, self.pivotGuide,
                  self.holdGuide, self.guideMoveall)

    def getGuideFromScene(self):

        self.guideMoveall = pm.PyNode(self.name + 'Moveall_guide')
        self.lcornerGuide = pm.PyNode('lcorner')
        self.rcornerGuide = pm.PyNode('rcorner')
        self.jawGuide = pm.PyNode('jaw')
        self.upperLipGuide = pm.PyNode('upperLip')
        self.pivotGuide = pm.PyNode('pivot')
        self.holdGuide = pm.PyNode('hold')

    def doRig(self):
        if not self.guideMoveall:
            self.doGuide()

        if pm.objExists(self.name + 'Moveall'):
            pm.delete(self.name + 'Moveall')

        self.moveall = pm.group(em=True, n=self.name + 'Moveall')

        pm.select(cl=True)
        pivot = pm.xform(self.pivotGuide, q=True, ws=True, t=True)
        self.jawJnt = pm.joint(p=pivot, n='jaw_jxt')
        jaw = pm.xform(self.jawGuide, q=True, ws=True, t=True)
        pm.joint(p=jaw, n='jaw_jnt')

        pm.select(cl=True)
        self.lcornerJnt = pm.joint(p=pivot, n='lcorner_jxt')
        lcorner = pm.xform(self.lcornerGuide, q=True, ws=True, t=True)
        pm.joint(p=lcorner, n='lcorner_jnt')

        pm.select(cl=True)
        self.rcornerJnt = pm.joint(p=pivot, n='rcorner_jxt')
        rcorner = pm.xform(self.rcornerGuide, q=True, ws=True, t=True)
        pm.joint(p=rcorner, n='rcorner_jnt')

        pm.select(cl=True)
        self.upperLipJnt = pm.joint(p=pivot, n='upperLip_jxt')
        upperLip = pm.xform(self.upperLipGuide, q=True, ws=True, t=True)
        pm.joint(p=upperLip, n='upperLip_jnt')

        pm.select(cl=True)
        hold = pm.xform(self.holdGuide, q=True, ws=True, t=True)
        self.holdJnt = pm.joint(p=hold, n='hold_jnt')
        pivot = pm.xform(self.pivotGuide, q=True, ws=True, t=True)
        pivotJnt = pm.joint(p=pivot, n='pivot_jxt')

        jawCntrlDrv = rigFunctions.cntrlCrv(name='jawCntrl_drv', obj=self.jawJnt, connType='parentConstraint', size=.5,
                                            icone='grp')
        self.jawCntrl = rigFunctions.cntrlCrv(name='jawCntrl', obj=jawCntrlDrv, connType='connection', size=.5,
                                              icone='circuloZ')
        self.jawCntrl.addAttr('L_cornerFollow', at='float', dv=0.5, k=1)
        self.jawCntrl.addAttr('R_cornerFollow', at='float', dv=0.5, k=1)

        b = jaw
        a = pivot
        shape = self.jawCntrl.getShape()
        pm.move(b[0] - a[0], (b[1] - a[1]) - .3, (b[2] - a[2]) + .4, shape.cv, r=True)

        pm.parent(jawCntrlDrv.getParent(), self.jawJnt, self.lcornerJnt, self.rcornerJnt, self.upperLipJnt,
                  self.holdJnt, self.jawCntrl.getParent(), self.moveall)

        multi1 = pm.createNode('multiplyDivide')
        multi2 = pm.createNode('multiplyDivide')
        multi3 = pm.createNode('multDoubleLinear')
        cond = pm.createNode('condition')

        self.jawCntrl.L_cornerFollow >> multi1.input2.input2X
        self.jawCntrl.L_cornerFollow >> multi1.input2.input2Y
        self.jawCntrl.L_cornerFollow >> multi1.input2.input2Z
        self.jawCntrl.R_cornerFollow >> multi2.input2.input2X
        self.jawCntrl.R_cornerFollow >> multi2.input2.input2Y
        self.jawCntrl.R_cornerFollow >> multi2.input2.input2Z

        self.jawJnt.rotate >> multi1.input1
        self.jawJnt.rotate >> multi2.input1
        multi1.output >> self.lcornerJnt.rotate
        multi2.output >> self.rcornerJnt.rotate

        self.jawJnt.rotateX >> cond.firstTerm
        cond.secondTerm.set(0)
        cond.operation.set(4)
        cond.colorIfFalseR.set(0)
        multi3.input2.set(.3)
        self.jawJnt.rotateX >> multi3.input1
        multi3.output >> cond.colorIfTrue.colorIfTrueR
        cond.outColor.outColorR >> self.upperLipJnt.rotateX