import pymel.core as pm
import autoRig3.tools.rigFunctions as rigFunctions
from autoRig3.modules import twistExtractor

class RibbonBezier:
    """
        Cria um ribbon bezier
        Parametros:
            name:
            size:
            numJoints:

    """

    ##IMPLEMENTAR:
    # controle de twist fique liberado pra q o usuario de offset, principalmente no inicio
    # stretch/squash com distancia ja no ribbon

    def __init__(self, **kwargs):

        self.ribbonDict = {}

        self.ribbonDict['size'] = kwargs.pop('size', 10)
        self.ribbonDict['name'] = kwargs.pop('name', 'ribbonBezier')
        self.ribbonDict['numJnts'] = kwargs.pop('numJnts', 10)
        self.ribbonDict['offsetStart'] = kwargs.pop('offsetStart', 0)
        self.ribbonDict['offsetEnd'] = kwargs.pop('offsetEnd', 0)
        self.skinJoints = []
        self.name = self.ribbonDict['name']
        self.size = self.ribbonDict['size']
        self.numJnts = self.ribbonDict['numJnts']
        self.offsetStart = self.ribbonDict['offsetStart']
        self.offsetEnd = self.ribbonDict['offsetEnd']

        self.jntSulfix = '_jnt'
        self.ribbonDict['moveallSetup'] = {'nameTempl': self.name + 'Moveall'}
        self.ribbonDict['noMoveSetup'] = {'nameTempl': self.name + 'NoMove'}

        self.ribbonDict['cntrlSetup'] = {'nameTempl': self.name + 'Pos', 'icone': 'grp', 'size': 0.6,
                                         'color': (0, 0, 1)}
        self.ribbonDict['midCntrlSetup'] = {'nameTempl': self.name + 'Pos', 'icone': 'circuloX', 'size': 1,
                                            'color': (0, .6, 1)}
        self.ribbonDict['cntrlTangSetup'] = {'nameTempl': self.name + 'Tang', 'icone': 'bola', 'size': 0.3,
                                             'color': (0, 1, 1)}
        self.ribbonDict['cntrlExtraSetup'] = {'nameTempl': self.name + 'Extra', 'icone': 'circuloX', 'size': 0.2}

        self.ribbonDict['jntSetup'] = {'nameTempl': self.name + 'Joint', 'icone': 'circuloX', 'size': 0.2}

    def doRig(self):
        anchorList = []
        cntrlList = []
        locList = []

        if pm.objExists(self.ribbonDict['moveallSetup']['nameTempl']):
            pm.delete(self.ribbonDict['moveallSetup']['nameTempl'])
        if pm.objExists(self.ribbonDict['noMoveSetup']['nameTempl']):
            pm.delete(self.ribbonDict['noMoveSetup']['nameTempl'])

        ###Estrutura que nao deve ter transformacao
        noMoveSpace = pm.group(empty=True, n=self.ribbonDict['noMoveSetup']['nameTempl'])
        if not pm.objExists('NOMOVE'):
            pm.group(self.ribbonDict['noMoveSetup']['nameTempl'], n='NOMOVE')
        else:
            pm.parent(self.ribbonDict['noMoveSetup']['nameTempl'], 'NOMOVE')

        noMoveSpace.visibility.set(0)
        noMoveSpace.translate.set(self.size * -0.5, 0, 0)
        noMoveBend1 = pm.nurbsPlane(p=(self.size * -0.25, 0, 0), ax=(0, 0, 1), w=self.size * 0.5, lr=.1, d=3, u=5, v=1)
        noMoveBend2 = pm.nurbsPlane(p=(self.size * 0.25, 0, 0), ax=(0, 0, 1), w=self.size * 0.5, lr=.1, d=3, u=5, v=1)
        # noMoveCrvJnt = pm.curve ( bezier=True, d=3, p=[(self.size*-0.5,0,0),(self.size*-0.4,0,0),(self.size*-0.1,0,0),(0,0,0),(self.size*0.1,0,0),(self.size*0.4,0,0),(self.size*0.5,0,0)], k=[0,0,0,1,1,1,2,2,2])
        noMoveCrvJnt = pm.curve(bezier=True, d=3,
                                p=[(self.size * -0.50, 0, 0), (self.size * -0.499, 0, 0), (self.size * -0.496, 0, 0),
                                   (self.size * -0.495, 0, 0), (self.size * -0.395, 0, 0), (self.size * -0.10, 0, 0),
                                   (0, 0, 0), (self.size * 0.10, 0, 0), (self.size * 0.395, 0, 0),
                                   (self.size * 0.495, 0, 0), (self.size * 0.496, 0, 0), (self.size * 0.499, 0, 0),
                                   (self.size * 0.50, 0, 0)], k=[0, 0, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 10, 10])

        # Deformers das superficies noMove
        twist1 = pm.nonLinear(noMoveBend1[0], type='twist')  # twist das superficies noMove
        twist2 = pm.nonLinear(noMoveBend2[0], type='twist')
        twist1[1].rotateZ.set(90)
        twist2[1].rotateZ.set(90)
        wireDef = pm.wire(noMoveBend1[0], noMoveBend2[0], w=noMoveCrvJnt, dds=[(0, 50)])  # Wire das superficies noMove
        wireDef[0].rotation.set(1)  # seta wire controlando rotacao
        baseWire = [x for x in wireDef[0].connections() if 'BaseWire' in x.name()]
        pm.group(baseWire, noMoveCrvJnt, noMoveBend1[0], noMoveBend2[0], p=noMoveSpace, n=self.name + 'Deforms')
        pm.parent(twist1[1], twist2[1], noMoveSpace)

        ###Estrutura que pode ser movida
        cntrlsSpace = pm.group(empty=True, n=self.ribbonDict['moveallSetup']['nameTempl'])
        cntrlsSpace.translate.set(self.size * -0.5, 0, 0)
        bendSurf1 = pm.nurbsPlane(p=(self.size * -0.25, 0, 0), ax=(0, 0, 1), w=self.size * 0.5, lr=.1, d=3, u=5, v=1)
        bendSurf2 = pm.nurbsPlane(p=(self.size * 0.25, 0, 0), ax=(0, 0, 1), w=self.size * 0.5, lr=.1, d=3, u=5, v=1)

        # blendShape transferindo as deformaacoes para a superficie move
        blend1 = pm.blendShape(noMoveBend1[0], bendSurf1[0])
        blend2 = pm.blendShape(noMoveBend2[0], bendSurf2[0])
        pm.blendShape(blend1, e=True, w=[(0, 1)])
        pm.blendShape(blend2, e=True, w=[(0, 1)])
        pm.parent(bendSurf1[0], bendSurf2[0], cntrlsSpace)

        ##Cntrls
        for i in range(0, 7):
            anchor = pm.cluster(noMoveCrvJnt.name() + '.cv[' + str(i + 3) + ']')
            clsHandle = anchor[1]
            anchorGrp = pm.group(em=True, n='clusterGrp' + str(i))
            anchorDrn = pm.group(em=True, n='clusterDrn' + str(i), p=anchorGrp)
            pos = pm.xform(anchor, q=True, ws=True, rp=True)
            pm.xform(anchorGrp, t=pos, ws=True)
            pm.parent(anchor[1], anchorDrn)
            anchorList.append(anchor[1])
            if i == 0 or i == 6:
                displaySetup = self.ribbonDict['cntrlSetup'].copy()
                cntrlName = displaySetup['nameTempl'] + str(i)
                cntrl = rigFunctions.cntrlCrv(name=cntrlName, obj=anchor[1], **displaySetup)
            elif i == 3:

                displaySetup = self.ribbonDict['midCntrlSetup'].copy()
                cntrlName = displaySetup['nameTempl'] + str(i)
                cntrl = rigFunctions.cntrlCrv(name=cntrlName, obj=anchor[1], **displaySetup)

            else:
                displaySetup = self.ribbonDict['cntrlTangSetup'].copy()
                cntrlName = displaySetup['nameTempl'] + str(i)
                cntrl = rigFunctions.cntrlCrv(name=cntrlName, obj=anchor[1], **displaySetup)

            # Nao pode fazer conexao na criacao do controle, pois tera conexao direta
            pm.xform(cntrl.getParent(), t=pos, ws=True)

            # estrutura de buffers para conexao direta
            auxLocGrp = pm.group(em=True, n=self.name + 'Aux_grp')
            auxLoc = pm.group(em=True, p=auxLocGrp, n=self.name + 'AuxLoc')
            pm.xform(auxLocGrp, t=pos, ws=True)
            loc = pm.PyNode(auxLoc)

            if i == 1 or i == 4:
                pm.xform(anchorGrp, s=(-1, 1, 1), r=True)
                pm.xform(cntrl.getParent(), s=(-1, 1, 1), r=True)
                pm.xform(loc.getParent(), s=(-1, 1, 1), r=True)

            # Conexoes dos buffers cm os clusters e com os controles
            pm.parentConstraint(cntrl, loc)
            loc.translate >> anchorDrn.translate
            loc.rotate >> anchorDrn.rotate
            cntrlList.append(cntrl)
            locList.append(loc)

            # workaround do flip do inicio do wire(adicao de mais pontos)
        startCls = pm.cluster(noMoveCrvJnt.name() + '.cv[0:2]')
        endCls = pm.cluster(noMoveCrvJnt.name() + '.cv[10:14]')

        pm.parent(startCls, anchorList[0])
        pm.parent(endCls, anchorList[6])

        cntrlsSpace.addAttr('cntrlsVis', at='double', dv=1, k=False, h=True)
        cntrlsSpace.addAttr('extraCntrlsVis', at='double', dv=0, k=False, h=True)
        cntrlList[0].addAttr('twist', at='double', dv=0, k=True)
        cntrlList[0].addAttr('stretchDist', at='double', dv=0, k=True)
        cntrlList[0].addAttr('autoVolumStregth', at='double', dv=0, k=True)
        cntrlList[3].addAttr('twist', at='double', dv=0, k=True)
        cntrlList[3].addAttr('autoVolume', at='double', dv=0, k=True)
        cntrlList[6].addAttr('twist', at='double', dv=0, k=True)
        cntrlList[6].addAttr('stretchDist', at='double', dv=0, k=True)
        cntrlList[6].addAttr('autoVolumStregth', at='double', dv=0, k=True)

        cntrlList[0].twist >> twist1[0].endAngle
        cntrlList[3].twist >> twist1[0].startAngle
        cntrlList[3].twist >> twist2[0].endAngle
        cntrlList[6].twist >> twist2[0].startAngle

        # hierarquia
        pm.parent(anchorList[1].getParent(2), anchorList[0])
        pm.parent(anchorList[5].getParent(2), anchorList[6])
        pm.parent(anchorList[2].getParent(2), anchorList[4].getParent(2), anchorList[3])
        pm.parent(cntrlList[1].getParent(), cntrlList[0])
        pm.parent(cntrlList[5].getParent(), cntrlList[6])
        pm.parent(cntrlList[2].getParent(), cntrlList[4].getParent(), cntrlList[3])
        pm.parent(cntrlList[3].getParent(), cntrlList[0].getParent(), cntrlList[6].getParent(), cntrlsSpace)
        pm.parent(locList[1].getParent(), locList[0])
        pm.parent(locList[5].getParent(), locList[6])
        pm.parent(locList[2].getParent(), locList[4].getParent(), locList[3])
        pm.parent(locList[3].getParent(), locList[0].getParent(), locList[6].getParent(), cntrlsSpace)
        pm.parent(anchorList[3].getParent(2), anchorList[0].getParent(2), anchorList[6].getParent(2), noMoveSpace)

        # Skin joints do ribbon
        skinJntsGrp = pm.group(em=True, n=self.name + 'SkinJnts')
        follGrp = pm.group(em=True, n=self.name + 'SkinJnts')

        # cria ramps para controlar o perfil de squash e stretch
        ramp1 = pm.createNode('ramp')
        ramp1.attr('type').set(1)

        ramp2 = pm.createNode('ramp')
        ramp2.attr('type').set(1)

        expre1 = "float $dummy = " + ramp1.name() + ".outAlpha;float $output[];float $color[];"
        expre2 = "float $dummy = " + ramp2.name() + ".outAlpha;float $output[];float $color[];"

        extraCntrlsGrp = pm.group(em=True, r=True, p=cntrlsSpace, n=self.name + 'ExtraCntrls')

        # loop pra fazer os colocar o numero escolhido de joints ao longo do ribbon.
        # cria tmb node tree pro squash/stretch
        # e controles extras
        vIncrement = float((1.0 - (self.offsetStart + self.offsetEnd)) / ((self.numJnts - 2) / 2.0))

        for i in range(1, (self.numJnts / 2) + 1):
            # cria estrutura pra superficie 1
            pm.select(cl=True)
            jntName = self.ribbonDict['jntSetup']['nameTempl'] + 'A' + str(i) + self.jntSulfix

            jnt1 = pm.joint(p=(0, 0, 0), n=jntName)
            self.skinJoints.append(jnt1)
            displaySetup = self.ribbonDict['cntrlExtraSetup'].copy()
            cntrlName = displaySetup['nameTempl'] + 'A' + str(i)
            cntrl1 = rigFunctions.cntrlCrv(name=cntrlName, obj=jnt1, connType='parentConstraint', **displaySetup)

            # node tree
            blend1A = pm.createNode('blendTwoAttr')
            blend1B = pm.createNode('blendTwoAttr')
            gammaCorr1 = pm.createNode('gammaCorrect')
            cntrlList[0].attr('autoVolumStregth') >> gammaCorr1.gammaX
            cntrlList[0].attr('stretchDist') >> gammaCorr1.value.valueX
            blend1A.input[0].set(1)
            gammaCorr1.outValueX >> blend1A.input[1]
            blend1B.input[0].set(1)
            blend1A.output >> blend1B.input[1]
            blend1B.output >> cntrl1.getParent().scaleY
            blend1B.output >> cntrl1.getParent().scaleZ
            # expressao que le a rampa para setar valores da escala de cada joint quando fizer squash/stretch
            expre1 = expre1 + "$color = `colorAtPoint -o RGB -u " + str(
                self.offsetStart + (i - 1) * vIncrement) + " -v 0.5 " + ramp1.name() + " `;$output[" + str(
                i) + "] = $color[0];" + blend1A.name() + ".attributesBlender=$output[" + str(i) + "];"

            # cria estrutura pra superficie 2
            pm.select(cl=True)

            jntName = self.ribbonDict['jntSetup']['nameTempl'] + 'B' + str(i) + self.jntSulfix
            jnt2 = pm.joint(p=(0, 0, 0), n=jntName)
            self.skinJoints.append(jnt2)
            displaySetup = self.ribbonDict['cntrlExtraSetup'].copy()
            cntrlName = displaySetup['nameTempl'] + 'B' + str(i)
            cntrl2 = rigFunctions.cntrlCrv(name=cntrlName, connType='parentConstraint', obj=jnt2, **displaySetup)

            # node tree
            blend2A = pm.createNode('blendTwoAttr')
            blend2B = pm.createNode('blendTwoAttr')
            gammaCorr2 = pm.createNode('gammaCorrect')
            cntrlList[6].attr('autoVolumStregth') >> gammaCorr2.gammaX
            cntrlList[6].attr('stretchDist') >> gammaCorr2.value.valueX
            blend2A.input[0].set(1)
            gammaCorr2.outValueX >> blend2A.input[1]
            blend2B.input[0].set(1)
            blend2A.output >> blend2B.input[1]
            cntrlList[3].attr('autoVolume') >> blend2B.attributesBlender
            blend2B.output >> cntrl2.getParent().scaleY
            blend2B.output >> cntrl2.getParent().scaleZ
            # expressao que le a rampa para setar valores da escala de cada joint quando fizer squash/stretch

            expre2 = expre2 + "$color = `colorAtPoint -o RGB -u " + str(
                self.offsetStart + (i - 1) * vIncrement) + " -v 0.5 " + ramp2.name() + " `;$output[" + str(
                i) + "] = $color[0];" + blend2A.name() + ".attributesBlender=$output[" + str(i) + "];"

            # prende joints nas supeficies com follicules
            foll1 = self.attachObj(cntrl1.getParent(), bendSurf1[0], self.offsetStart + (i - 1) * vIncrement, 0.5, 4)
            foll2 = self.attachObj(cntrl2.getParent(), bendSurf2[0], self.offsetStart + (i - 1) * vIncrement, 0.5, 4)

            pm.parent(cntrl1.getParent(), cntrl2.getParent(), extraCntrlsGrp)
            pm.parent(jnt1, jnt2, skinJntsGrp)
            pm.parent(foll1, foll2, follGrp)

            # seta expressoes para so serem avaliadas por demanda
        pm.expression(s=expre1, ae=False)
        pm.expression(s=expre2, ae=False)

        pm.parent(skinJntsGrp, cntrlsSpace)
        pm.parent(follGrp, noMoveSpace)

        # hideCntrls
        pm.toggle(bendSurf1[0], bendSurf2[0], g=True)
        # skinJntsGrp.visibility.set(0)
        cntrlsSpace.extraCntrlsVis >> extraCntrlsGrp.visibility
        cntrlsSpace.cntrlsVis >> cntrlList[0].getParent().visibility
        cntrlsSpace.cntrlsVis >> cntrlList[3].getParent().visibility
        cntrlsSpace.cntrlsVis >> cntrlList[6].getParent().visibility

        # povoa ribbon Dict
        self.ribbonDict['name'] = 'bezierRibbon'
        self.ribbonDict['ribbonMoveAll'] = cntrlsSpace
        for i in range(0, 7):
            self.ribbonDict['cntrl' + str(i)] = cntrlList[i]

    # Metodo para colar objetos por follicules
    def attachObj(self, obj, mesh, u, v, mode=1):
        foll = pm.createNode('follicle')
        follDag = foll.firstParent()
        mesh.worldMatrix[0] >> foll.inputWorldMatrix
        if pm.objectType(mesh) == 'mesh':
            mesh.outMesh >> foll.inputMesh
        else:
            mesh.local >> foll.inputSurface

        foll.outTranslate >> follDag.translate
        foll.outRotate >> follDag.rotate
        follDag.translate.lock()
        follDag.rotate.lock()
        follDag.parameterU.set(u)
        follDag.parameterV.set(v)
        if mode == 1:
            pm.parent(obj, follDag)
        elif mode == 2:
            pm.parentConstraint(follDag, obj, mo=True)
        elif mode == 3:
            pm.pointConstraint(follDag, obj, mo=True)
        elif mode == 4:
            pm.parentConstraint(follDag, obj, mo=False)
        return follDag

        # Metodo para descobrir ponto mais proximo da superficie onde devem objeto deve ser colado

    def hookJntsOnCurve(self, jntList, upList, jntCrv, upCrv):
        jntNPoC = pm.createNode('nearestPointOnCurve')
        jntGrpA = pm.group(empty=True, n=self.name + 'jntGrp')
        jntCrv.worldSpace[0] >> jntNPoC.inputCurve

        jntGrpA.translate >> jntNPoC.inPosition

        upNPoC = pm.createNode('nearestPointOnCurve')
        upGrpA = pm.group(empty=True, n=self.name + 'upGrpA')
        upCrv.worldSpace[0] >> upNPoC.inputCurve
        upGrpA.translate >> upNPoC.inPosition

        for jnt, up in zip(jntList, upList):
            wp = pm.xform(jnt, t=True, ws=True, q=True)
            pm.xform(jntGrpA, t=wp, ws=True)
            hookPoci = pm.createNode('pointOnCurveInfo')
            jntCrv.worldSpace[0] >> hookPoci.inputCurve
            hookPoci.position >> jnt.translate
            hookPar = jntNPoC.parameter.get()
            hookPoci.parameter.set(hookPar)
            pm.tangentConstraint(jntCrv, jnt, aimVector=(-1, 0, 0), upVector=(0, 1, 0), worldUpType="object",
                                 worldUpObject=up)

            wp = pm.xform(up, t=True, ws=True, q=True)
            pm.xform(upGrpA, t=wp, ws=True)
            hookPoci = pm.createNode('pointOnCurveInfo')
            upCrv.worldSpace[0] >> hookPoci.inputCurve
            hookPoci.position >> up.translate
            hookPar = upNPoC.parameter.get()
            hookPoci.parameter.set(hookPar)

        pm.delete(upNPoC, upGrpA, jntNPoC, jntGrpA)

    def connectToLimb(self, limbObject):
        # seta as variaveis locais com valores dos dicionarios dos objetos
        ribbonMoveAll = self.ribbonDict['ribbonMoveAll']
        limbMoveAll = limbObject.moveall
        limbJoint1 = limbObject.startJnt
        limbJoint2 = limbObject.midJnt
        limbJoint3 = limbObject.endJnt
        limbJoint4 = limbObject.lastJnt
        ribbonEndCntrl = self.ribbonDict['cntrl0']
        ribbonMidCntrl = self.ribbonDict['cntrl3']
        ribbonStartCntrl = self.ribbonDict['cntrl6']
        ribbonMid2TangCntrl = self.ribbonDict['cntrl4']
        ribbonMid1TangCntrl = self.ribbonDict['cntrl2']
        if limbObject.flipAxis:
            rotY = 180
        else:
            rotY = 0
        # grupos de conexao
        startGrp = pm.group(em=True, n=self.name + 'conStart_grp')
        midGrp = pm.group(em=True, n=self.name + 'conMid_grp')
        endGrp = pm.group(em=True, n=self.name + 'conEnd_grp')

        pm.parentConstraint(limbJoint1, endGrp, mo=False)
        pm.pointConstraint(limbJoint2, midGrp, mo=False)
        ori = pm.orientConstraint(limbJoint2, limbJoint1, midGrp, mo=False)
        ori.interpType.set(2)
        pm.parentConstraint(limbJoint3, startGrp, mo=False)

        # hierarquia
        pm.parent(ribbonMoveAll, limbJoint1)
        ribbonMoveAll.translate.set(0, 0, 0)
        ribbonMoveAll.rotate.set(0, rotY, 0)
        pm.parent(ribbonMoveAll, limbMoveAll)
        pm.parentConstraint(limbJoint1, ribbonMoveAll, mo=True)

        pm.parent(ribbonEndCntrl.getParent(), endGrp)
        pm.parent(ribbonMidCntrl.getParent(), midGrp)
        pm.parent(ribbonStartCntrl.getParent(), startGrp)
        pm.parent(startGrp, midGrp, endGrp, ribbonMoveAll)

        ##IMPLEMENTAR outras possibilidade de eixos. Hardcode de X
        ribbonEndCntrl.getParent().translate.set(0, 0, 0)
        ribbonEndCntrl.getParent().rotate.set(0, rotY, 0)
        ribbonMidCntrl.getParent().translate.set(0, 0, 0)
        ribbonMidCntrl.getParent().rotate.set(0, rotY, 0)
        ribbonStartCntrl.getParent().translate.set(0, 0, 0)
        ribbonStartCntrl.getParent().rotate.set(0, rotY, 0)

        # sistema de controle das tangentes suaves ou duras
        mid1AimGrp = pm.group(em=True, p=ribbonMidCntrl, n=self.name + 'mid1Aim_grp')
        mid2AimGrp = pm.group(em=True, p=ribbonMidCntrl, n=self.name + 'mid2Aim_grp')
        mid1SpcSwithGrp = pm.group(em=True, p=ribbonMidCntrl, n=self.name + 'mid1SpcSwith_grp')
        mid2SpcSwithGrp = pm.group(em=True, p=ribbonMidCntrl, n=self.name + 'mid2SpcSwith_grp')

        pm.aimConstraint(limbJoint1, mid1AimGrp, weight=1, aimVector=(-1, 0, 0), upVector=(0, 1, 0),
                         worldUpVector=(0, 1, 0), worldUpType='objectrotation', worldUpObject=limbJoint1)
        pm.aimConstraint(limbJoint3, mid2AimGrp, weight=1, aimVector=(1, 0, 0), upVector=(0, 1, 0),
                         worldUpVector=(0, 1, 0), worldUpType='objectrotation', worldUpObject=limbJoint1)
        pm.parent(ribbonMid1TangCntrl.getParent(), mid1SpcSwithGrp)
        pm.parent(ribbonMid2TangCntrl.getParent(), mid2SpcSwithGrp)
        # node tree
        aimBlend1 = pm.createNode('blendTwoAttr')
        aimBlend2 = pm.createNode('blendTwoAttr')
        ribbonMidCntrl.addAttr('softTang1', at='float', dv=1, max=1, min=0, k=1)
        ribbonMidCntrl.addAttr('softTang2', at='float', dv=1, max=1, min=0, k=1)
        aimBlend1.input[0].set(0)
        mid1AimGrp.rotateY >> aimBlend1.input[1]
        aimBlend2.input[0].set(0)
        mid2AimGrp.rotateY >> aimBlend2.input[1]
        ribbonMidCntrl.softTang1 >> aimBlend1.attributesBlender
        ribbonMidCntrl.softTang2 >> aimBlend2.attributesBlender
        aimBlend1.output >> mid1SpcSwithGrp.rotateY
        aimBlend2.output >> mid2SpcSwithGrp.rotateY

        # twist extractors
        extra1 = twistExtractor.twistExtractor(limbJoint4)
        extra2 = twistExtractor.twistExtractor(limbJoint1, None)
        pm.parent(extra1.extractorGrp, extra2.extractorGrp, limbMoveAll)
        pm.pointConstraint(limbJoint1, extra2.extractorGrp, mo=True)
        extra1.extractor.extractTwist >> ribbonStartCntrl.twist

        extractMulti1 = pm.createNode('multDoubleLinear')
        extra1.extractor.extractTwist >> extractMulti1.input1
        extractMulti2 = pm.createNode('multDoubleLinear')
        extra2.extractor.extractTwist >> extractMulti2.input1

        if limbObject.flipAxis:
            extractMulti1.input2.set(-1)
            extractMulti2.input2.set(1)
        else:
            extractMulti2.input2.set(-1)
            extractMulti1.input2.set(1)

        extractMulti1.output >> ribbonStartCntrl.twist
        extractMulti2.output >> ribbonEndCntrl.twist
        extra1.extractorGrp.visibility.set(0)
        extra2.extractorGrp.visibility.set(0)
