import pymel.core as pm
import autoRig3.tools.rigFunctions as rigFunctions

# implementar colocar os grupos dentro do FAcial, cntrls
# x= Tweaks(name='hairTweaks', num=3, type=None, cntrlSetup = {'nameTempl':'lipTweaks', 'icone':'circuloX','size':.5,'color':(1,1,0) })
# x.guideDict
# x.getGuideFromScene()
# x.doGuide()
# x.doRig()

class Tweaks:
    def __init__(self, name='tweak', num=1, type='static', **kwargs):
        self.name = name
        self.type = type
        self.num = num
        self.guideDict = {}
        self.jntPrefix = '_jnt'
        self.guideMoveall = None
        self.tweakDict = {'name': self.name, 'num': self.num, 'type': self.type, 'guideDict': {}}
        self.guideDict = {}
        for i in range(self.num):
            self.guideDict[self.name + str(i + 1)] = [i * .5, 0, 0]
        self.tweakDict['drvSetup'] = {'nameTempl': self.name + '_drv', 'icone': 'grp', 'size': 1, 'color': (1, 1, 0)}
        self.tweakDict['cntrlSetup'] = {'nameTempl': self.name, 'icone': 'circuloX', 'size': 1, 'color': (1, 1, 0)}

        self.tweakDict.update(kwargs)
        self.guideDict.update(self.tweakDict['guideDict'])
        self.tweakDict['guideDict'] = self.guideDict.copy()

    def doGuide(self):
        if pm.objExists(self.name + 'Moveall_guide'):
            pm.delete(self.name + 'Moveall_guide')
        self.guideMoveall = pm.group(em=True, n=self.name + 'Moveall_guide')

        self.guideList = []
        for i in range(self.num):
            guide = pm.spaceLocator(n=self.name + str(i + 1))
            guide.localScale.set(.2, .2, .2)
            guide.translate.set(self.guideDict[self.name + str(i + 1)])
            self.guideList.append(guide)
            guide.setParent(self.guideMoveall)

    def getGuideFromScene(self):
        self.guideMoveall = pm.PyNode(self.name + 'Moveall_guide')

        self.guideList = []
        for i in range(self.num):
            guide = pm.PyNode(self.name + str(i + 1))
            self.guideList.append(guide)

    def mirrorConnectGuide(self, tweak):
        if not self.guideMoveall:
            self.doGuide()
        if not tweak.guideMoveall:
            tweak.doGuide()

        if pm.objExists(self.name + 'MirrorGuide_grp'):
            pm.delete(self.name + 'MirrorGuide_grp')

        self.mirrorGuide = pm.group(em=True, n=self.name + 'MirrorGuide_grp')
        # if not pm.objExists('GUIDES'):
        #    pm.group ( self.name+'MirrorGuide_grp', n='GUIDES' )
        # else:
        #    pm.parent ( self.name+'MirrorGuide_grp', 'GUIDES')

        self.guideMoveall.setParent(self.mirrorGuide)
        self.mirrorGuide.scaleX.set(-1)
        self.mirrorGuide.template.set(1)

        tweak.guideMoveall.translate >> self.guideMoveall.translate
        tweak.guideMoveall.rotate >> self.guideMoveall.rotate
        tweak.guideMoveall.scale >> self.guideMoveall.scale

        for i in range(self.num):
            tweak.guideList[i].translate >> self.guideList[i].translate
            tweak.guideList[i].rotate >> self.guideList[i].rotate
            tweak.guideList[i].scale >> self.guideList[i].scale

    def doRig(self):
        if not self.guideMoveall:
            self.doGuide()

        if pm.objExists(self.name + 'Moveall'):
            pm.delete(self.name + 'Moveall')

        self.cntrlGrp = pm.group(em=True, n=self.name + 'Cntrls_grp')
        self.drvGrp = pm.group(em=True, n=self.name + 'Drivers_grp')
        self.moveall = pm.group(self.cntrlGrp, self.drvGrp, n=self.name + 'Moveall')

        self.cntrlList = []
        for i in range(self.num):
            pm.select(cl=True)
            jnt = pm.joint(n=self.name + str(i + 1) + self.jntPrefix)
            pos = pm.xform(self.guideList[i], q=True, ws=True, t=True)
            pm.xform(jnt, ws=True, t=pos)
            drvName = self.tweakDict['drvSetup']['nameTempl'] + str(i + 1) + '_drv'
            drv = rigFunctions.cntrlCrv(name=drvName, obj=jnt, connType='parent', **self.tweakDict['drvSetup'])
            cntrlName = self.tweakDict['cntrlSetup']['nameTempl'] + str(i + 1)
            cntrl = rigFunctions.cntrlCrv(name=cntrlName, obj=drv, connType='connection', offsets=1,
                                          **self.tweakDict['cntrlSetup'])

            if self.type == 'static':
                print 'static cntrl'
                mlt = pm.createNode('multiplyDivide')
                mlt.input2.set([-1, -1, -1])
                cntrl.translate >> mlt.input1
                mlt.output >> cntrl.getParent().translate

            self.cntrlList.append(cntrl)
            cntrl.getParent(2).setParent(self.cntrlGrp)
            drv.getParent().setParent(self.drvGrp)