import pymel.core as pm
import autoRig3.tools.rigFunctions as rigFunctions

class RibbonWire:
    """
        Cria um ribbon com uma curve nurbs como wire e uma superficie somente
        Parametros:
            name(string):nome
            width(int): tamanho do ribbon
            div(int): qnts joints vao ser colocados na superficie
        limitacao para criar twists
    """

    def __init__(self, name='ribbon', width=10, div=5.0):
        self.flexName = name
        self.width = width
        self.div = div

    def createFoll(self, name, nurbsSurf, uPos, vPos):
        nurbsSurfShape = nurbsSurf.getShape()
        follShape = pm.createNode('follicle', n=name + 'Shape')

        foll = follShape.getParent()
        foll = pm.rename(foll, name)
        follShape = foll.getShape()
        nurbsSurf.local >> foll.inputSurface
        nurbsSurf.worldMatrix[0] >> foll.inputWorldMatrix
        follShape.outRotate >> foll.rotate
        follShape.outTranslate >> foll.translate
        follShape.parameterU.set(uPos)
        follShape.parameterV.set(vPos)
        foll.translate.lock()
        foll.rotate.lock()
        follShape.visibility.set(False)
        return foll

    def doRig(self):
        nurbsSurf = pm.nurbsPlane(p=(0, 0, 0), ax=(0, 1, 0), w=self.width, lr=0.1, d=3, u=self.div, v=1, ch=0,
                                  n=self.flexName + 'FlexNurbsSrf')[0]
        nurbsSurf.visibility.set(False)
        nurbsSurf.translate.set(self.width / 2, 0, 0)
        spacing = 1.0 / float(self.div)
        start = spacing / 2.0
        grp1 = pm.group(n=self.flexName + 'Folicules_grp', empty=True)
        grp2 = pm.group(em=True, n=self.flexName + 'ribbonGlobalMove')
        grp3 = pm.group(em=True, n=self.flexName + 'FlexNoMove')

        for i in range(int(self.div)):
            foll = self.createFoll(self.flexName + 'Follicle' + str('%02d' % i), nurbsSurf, start + spacing * i, 0.5)
            jnt1 = pm.joint(p=(0, 0, 0), n=self.flexName + str('%02d' % i) + '_jnt')
            pm.move(0, 0, 0, jnt1, ls=True)
            pm.parent(foll, grp1)

        nurbsSurfBlend = pm.nurbsPlane(p=(0, 0, 0), ax=(0, 1, 0), w=self.width, lr=0.1, d=3, u=self.div, v=1, ch=0,
                                       n=self.flexName + 'FlexBlendNurbsSrf')[0]
        nurbsSurfBlend.translate.set(self.width / 2, 0, 0)
        pm.blendShape(nurbsSurfBlend, nurbsSurf, frontOfChain=True, tc=0, w=(0, 1))

        crv = pm.curve(d=2, p=[((self.width * -0.5), 0, 0), (0, 0, 0), ((self.width * 0.5), 0, 0)], k=[0, 0, 1, 1],
                       n=self.flexName + 'Crv')
        crv.translate.set(self.width / 2, 0, 0)

        cls1 = pm.cluster(crv + '.cv[0]', crv + '.cv[1]', rel=True, n=self.flexName + 'Cls1')
        pm.move((self.width * -0.5), 0, 0, cls1[1] + '.scalePivot', cls1[1] + '.rotatePivot')
        cls2 = pm.cluster(crv + '.cv[2]', crv + '.cv[1]', rel=True, n=self.flexName + 'Cls2')
        pm.move((self.width * 0.5), 0, 0, cls2[1] + '.scalePivot', cls2[1] + '.rotatePivot')
        cls3 = pm.cluster(crv + '.cv[1]', rel=True, n=self.flexName + 'Cls3')
        pm.percent(cls1[0], crv + '.cv[1]', v=0.5)
        pm.percent(cls2[0], crv + '.cv[1]', v=0.5)
        twist = pm.nonLinear(nurbsSurfBlend, type='twist', n=self.flexName + 'Twist')
        twist[1].rotate.set(0, 0, 90)

        wir = pm.wire(nurbsSurfBlend, gw=False, en=1.000000, ce=0.000000, li=0.000000, w=crv, dds=(0, 20))
        wireNode = pm.PyNode(wir[0])
        baseWire = [x for x in wireNode.connections() if 'BaseWire' in x.name()]
        cntrl1 = rigFunctions.cntrlCrv(name=self.flexName + 'aux1', icone='grp')
        cntrl2 = rigFunctions.cntrlCrv(name=self.flexName + 'aux2', icone='grp')
        cntrl3 = rigFunctions.cntrlCrv(name=self.flexName + 'aux3', icone='grp')

        pos = pm.pointOnSurface(nurbsSurfBlend, u=0.0, v=0.5)
        cntrl1.getParent().translate.set(pos)
        pos = pm.pointOnSurface(nurbsSurfBlend, u=1.0, v=0.5)
        cntrl2.getParent().translate.set(pos)
        pos = pm.pointOnSurface(nurbsSurfBlend, u=0.5, v=0.5)
        cntrl3.getParent().translate.set(pos)
        cntrl1.addAttr('twist', at='float', dv=0, k=1)
        cntrl2.addAttr('twist', at='float', dv=0, k=1)

        pm.pointConstraint(cntrl1, cntrl2, cntrl3.getParent())
        cntrl1.translate >> cls1[1].translate
        cntrl2.translate >> cls2[1].translate
        cntrl3.translate >> cls3[1].translate

        cntrl2.twist >> twist[0].startAngle
        cntrl1.twist >> twist[0].endAngle

        pm.parent(nurbsSurf, cntrl1.getParent(), cntrl2.getParent(), cntrl3.getParent(), grp2)
        pm.parent(grp1, nurbsSurfBlend, cls1[1], cls2[1], cls3[1], baseWire, crv, twist[1], grp3)
        pm.setAttr(grp3 + '.visibility', 0)
        # pm.group (grp1,grp2,grp3,n=self.flexName+'Flex_grp')
        # implementar squash/stretch
        # implementar o connect to limb