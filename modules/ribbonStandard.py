import pymel.core as pm
import maya.api.OpenMaya as om
import logging

logger = logging.getLogger('autoRig')

class RibbonStandard:
    """
        Cria um ribbon com uma superficie levada por joints e um sistema de aims
        Parametros:
            name(string):
            guide1, guide2, guide3 (locators)
            sections:

    """

    ##IMPLEMENTAR:
    # controle de twist fique liberado pra q o usuario de offset, principalmente no inicio
    # stretch/squash com distancia ja no ribbon

    def __init__(self, **kwargs):

        self.guide1 = kwargs.pop('guide1', 'locator1')
        self.guide2 = kwargs.pop('guide2', 'locator2')
        self.guide3 = kwargs.pop('guide3', 'locator3')
        self.name = kwargs.pop('name', 'ribbon')
        self.sections = kwargs.pop('sections', 5)
        self.upVector = kwargs.pop('upVector', (0, 1, 0))
        self.direction = kwargs.pop('direction', (1, 0, 0))
        self.createCtrls = kwargs.pop('createCtrls', 0)
        self.ctrlNormal = kwargs.pop('ctrlNormal', (1, 0, 0))
        self.topCtrl = kwargs.pop('topCtrl', 'top')
        self.midCtrl = kwargs.pop('midCtrl', 'mid')
        self.lwrCtrl = kwargs.pop('lwrCtrl', 'lwr')
        self.visibility = kwargs.pop('visibility', 0)

    def doRig(self):
        p1 = pm.xform(self.guide1, q=1, t=1)
        p2 = pm.xform(self.guide2, q=1, t=1)
        p3 = pm.xform(self.guide3, q=1, t=1)

        A = om.MVector(p1)
        B = om.MVector(p2)
        C = om.MVector(p3)

        AC = A - C
        nurbsLength = AC.length()

        # setup do nurbs plane e follicles
        nurbs = pm.nurbsPlane(w=nurbsLength / self.sections, lr=self.sections, v=self.sections)[0]
        nurbsShp = nurbs.getShape()
        pm.rebuildSurface(nurbs, ch=1, rpo=1, rt=0, end=1, kr=0, kcp=0, kc=0, su=1, du=1, dv=3, tol=0.01, fr=0, dir=0)

        pm.xform(nurbs, t=p1, ws=True)

        guide2Up = pm.duplicate(self.guide2, n=self.guide2 + '_up')[0]
        pm.delete(pm.pointConstraint(self.guide1, self.guide3, guide2Up))
        pm.xform(guide2Up, r=True, t=(self.direction[0], self.direction[1], self.direction[2]))
        pm.delete(pm.aimConstraint(self.guide3, nurbs, w=1, o=(0, 0, 0), aim=(0, 1, 0), u=(-1, 0, 0), wut='object',
                                   wuo=guide2Up))
        pm.delete(guide2Up)
        pm.delete(pm.pointConstraint(self.guide1, self.guide3, nurbs))

        grpFol = pm.group(em=1, n=self.name + 'Foll_grp')
        grpScale = pm.group(em=1, n=self.name + 'Scale_grp')
        vValue = 0
        vSections = 1.0 / self.sections
        vOffset = vSections / 2
        id = 0

        # medindo o comprimento do nurbs para o squash stretch
        arcLengthShp = pm.createNode('arcLengthDimension')
        arcLength = arcLengthShp.getParent()
        nurbsShp.worldSpace[0] >> arcLengthShp.nurbsGeometry
        arcLengthShp.vParamValue.set(1)
        arcLengthShp.uParamValue.set(0)
        arcLenValue = arcLengthShp.arcLengthInV.get()
        autoManualList = []
        factorList = []
        on_offList = []
        skinJntsList = []

        for follicle in range(self.sections):
            id += 1
            # criando nodes para o stretch squash
            normalizeTo0 = pm.createNode('plusMinusAverage', n=self.name + 'RbbnNormalize0' + `id` + '_pma')
            scaleAux = pm.createNode('multiplyDivide', n=self.name + 'RbbnScaleAux0' + `id` + '_md')
            factor = pm.createNode('multiplyDivide', n=self.name + 'RbbnFactor0' + `id` + '_md')
            on_off = pm.createNode('multiplyDivide', n=self.name + 'RbbnOnOff0' + `id` + '_md')
            autoManual = pm.createNode('plusMinusAverage', n=self.name + 'RbbnAutoManual0' + `id` + '_pma')
            autoReverse = pm.createNode('reverse', n=self.name + 'RbbnReverse0' + `id` + '_rev')

            # ajustando valores dos nodes de stretch squash
            normalizeTo0.operation.set(2)
            scaleAux.input2.set((arcLenValue, arcLenValue, arcLenValue))

            # conectando os nodes de stretch squash
            arcLength.arcLengthInV >> normalizeTo0.input3D[0].input3Dx
            arcLength.arcLengthInV >> normalizeTo0.input3D[0].input3Dy
            arcLength.arcLengthInV >> normalizeTo0.input3D[0].input3Dz

            scaleAux.output >> normalizeTo0.input3D[1]
            grpScale.scale >> scaleAux.input1
            normalizeTo0.output3D >> factor.input2
            factor.output >> on_off.input1
            on_off.output >> autoReverse.input
            autoReverse.output >> autoManual.input3D[0]

            # criando nodes do rbbn
            folShp = pm.createNode('follicle')
            fol = folShp.getParent()

            # escondendo os follicles
            if self.visibility == 0:
                folShp.visibility.set(0)

            jnt = pm.joint(radius=nurbsLength * 0.2)
            skinJntsList.append(jnt)

            # conectando e ajustando nodes do rbbn
            autoManual.output3Dx >> jnt.scaleX
            autoManual.output3Dz >> jnt.scaleZ
            nurbsShp.local >> folShp.inputSurface
            nurbsShp.worldMatrix[0] >> folShp.inputWorldMatrix
            folShp.outRotate >> fol.rotate
            folShp.outTranslate >> fol.translate
            folShp.parameterU.set(0.5)
            vValue += vSections
            folShp.parameterV.set(vValue - vOffset)
            pm.parent(fol, grpFol)

            pm.scaleConstraint(grpScale, fol, mo=1)

            # listas para loops posteriores
            on_offList.append(on_off)
            factorList.append(factor)
            autoManualList.append(autoManual)

        # fk setup
        FKSIZE = (nurbsLength / 2) / self.sections

        topPosLoc = pm.spaceLocator()
        topAimLoc = pm.spaceLocator()
        topAimLoc.setParent(topPosLoc)

        topToSkin = pm.joint(radius=nurbsLength * 0.2, p=(0, 0, 0), )
        pm.joint(radius=nurbsLength * 0.15, p=(0, -FKSIZE, 0), )
        topUpLoc = pm.spaceLocator()
        topUpLoc.setParent(topPosLoc)

        pm.move(FKSIZE * 3 * self.upVector[0], FKSIZE * 3 * self.upVector[1], FKSIZE * 3 * self.upVector[2], topUpLoc)
        pm.delete(pm.pointConstraint(self.guide3, topPosLoc))
        # pm.delete(pm.parentConstraint(guide3,topPosLoc))

        midPosLoc = pm.spaceLocator()
        midAimLoc = pm.spaceLocator()
        midAimLoc.setParent(midPosLoc)

        midOffLoc = pm.spaceLocator()
        midOffLoc.setParent(midAimLoc)

        midToSkin = pm.joint(radius=nurbsLength * 0.2, p=(0, 0, 0))
        midUpLoc = pm.spaceLocator()
        midUpLoc.setParent(midPosLoc)

        pm.move(FKSIZE * 3 * self.upVector[0], FKSIZE * 3 * self.upVector[1], FKSIZE * 3 * self.upVector[2], midUpLoc)

        lwrPosLoc = pm.spaceLocator()
        lwrAimLoc = pm.spaceLocator()
        lwrAimLoc.setParent(lwrPosLoc)

        lwrToSkin = pm.joint(radius=nurbsLength * 0.2, p=(0, 0, 0))
        pm.joint(radius=nurbsLength * 0.15, p=(0, FKSIZE, 0))

        lwrUpLoc = pm.spaceLocator()
        lwrUpLoc.setParent(lwrPosLoc)

        pm.move(FKSIZE * 3 * self.upVector[0], FKSIZE * 3 * self.upVector[1], FKSIZE * 3 * self.upVector[2], lwrUpLoc)
        pm.delete(pm.pointConstraint(self.guide1, lwrPosLoc))

        topPosLocShp = topPosLoc.getShape()
        midPosLocShp = midPosLoc.getShape()
        lwrPosLocShp = lwrPosLoc.getShape()
        topAimLocShp = topAimLoc.getShape()
        midAimLocShp = midAimLoc.getShape()
        lwrAimLocShp = lwrAimLoc.getShape()
        topUpLocShp = topUpLoc.getShape()
        midUpLocShp = midUpLoc.getShape()
        lwrUpLocShp = lwrUpLoc.getShape()
        midOffLocShp = midOffLoc.getShape()

        topPosLocShp.localScale.set((nurbsLength * 0.2, nurbsLength * 0.2, nurbsLength * 0.2))
        topAimLocShp.localScale.set((nurbsLength * 0.2, nurbsLength * 0.2, nurbsLength * 0.2))
        topUpLocShp.localScale.set((nurbsLength * 0.05, nurbsLength * 0.05, nurbsLength * 0.05))
        midPosLocShp.localScale.set((nurbsLength * 0.2, nurbsLength * 0.2, nurbsLength * 0.2))
        midAimLocShp.localScale.set((nurbsLength * 0.2, nurbsLength * 0.2, nurbsLength * 0.2))
        midUpLocShp.localScale.set((nurbsLength * 0.05, nurbsLength * 0.05, nurbsLength * 0.05))
        midOffLocShp.localScale.set((nurbsLength * 0.2, nurbsLength * 0.2, nurbsLength * 0.2))
        lwrPosLocShp.localScale.set((nurbsLength * 0.2, nurbsLength * 0.2, nurbsLength * 0.2))
        lwrAimLocShp.localScale.set((nurbsLength * 0.2, nurbsLength * 0.2, nurbsLength * 0.2))
        lwrUpLocShp.localScale.set((nurbsLength * 0.05, nurbsLength * 0.05, nurbsLength * 0.05))

        pm.parent(topPosLoc, midPosLoc, lwrPosLoc, grpScale)

        # criando constraints para os locators do rbbn
        pm.aimConstraint(midToSkin, topAimLoc, aim=(0, -1, 0), u=(1, 0, 0), wut='object', wuo=topUpLoc)
        pm.aimConstraint(midToSkin, lwrAimLoc, aim=(0, 1, 0), u=(1, 0, 0), wut='object', wuo=lwrUpLoc)
        pm.aimConstraint(topPosLoc, midAimLoc, aim=(0, 1, 0), u=(1, 0, 0), wut='object', wuo=midUpLoc)

        pm.pointConstraint(topPosLoc, lwrPosLoc, midPosLoc)
        pm.pointConstraint(topUpLoc, lwrUpLoc, midUpLoc)

        # skin setup

        skin = pm.skinCluster(topToSkin, midToSkin, lwrToSkin, nurbs, tsb=1)
        if self.sections == 3:
            pm.skinPercent(skin, nurbs + '.cv[0:1][5]', tv=(topToSkin, 1))
            pm.skinPercent(skin, nurbs + '.cv[0:1][4]', tv=[(topToSkin, 0.6), (midToSkin, 0.4)])
            pm.skinPercent(skin, nurbs + '.cv[0:1][3]', tv=[(topToSkin, 0.2), (midToSkin, 0.8)])
            pm.skinPercent(skin, nurbs + '.cv[0:1][2]', tv=[(topToSkin, 0.2), (midToSkin, 0.8)])
            pm.skinPercent(skin, nurbs + '.cv[0:1][1]', tv=[(topToSkin, 0.6), (midToSkin, 0.4)])
            pm.skinPercent(skin, nurbs + '.cv[0:1][0]', tv=(topToSkin, 1))

        elif self.sections == 5:
            pm.skinPercent(skin, nurbs + '.cv[0:1][7]', tv=(topToSkin, 1))
            pm.skinPercent(skin, nurbs + '.cv[0:1][6]', tv=[(topToSkin, 0.80), (midToSkin, 0.2)])
            pm.skinPercent(skin, nurbs + '.cv[0:1][5]', tv=[(topToSkin, 0.5), (midToSkin, 0.5)])
            pm.skinPercent(skin, nurbs + '.cv[0:1][4]', tv=[(topToSkin, 0.25), (midToSkin, 0.75)])
            pm.skinPercent(skin, nurbs + '.cv[0:1][3]', tv=[(lwrToSkin, 0.25), (midToSkin, 0.75)])
            pm.skinPercent(skin, nurbs + '.cv[0:1][2]', tv=[(lwrToSkin, 0.5), (midToSkin, 0.5)])
            pm.skinPercent(skin, nurbs + '.cv[0:1][1]', tv=[(lwrToSkin, 0.8), (midToSkin, 0.2)])
            pm.skinPercent(skin, nurbs + '.cv[0:1][0]', tv=(lwrToSkin, 1))

        elif self.sections == 7:
            pm.skinPercent(skin, nurbs + '.cv[0:1][9]', tv=(topToSkin, 1))
            pm.skinPercent(skin, nurbs + '.cv[0:1][8]', tv=[(topToSkin, 0.85), (midToSkin, 0.15)])
            pm.skinPercent(skin, nurbs + '.cv[0:1][7]', tv=[(topToSkin, 0.6), (midToSkin, 0.4)])
            pm.skinPercent(skin, nurbs + '.cv[0:1][6]', tv=[(topToSkin, 0.35), (midToSkin, 0.65)])
            pm.skinPercent(skin, nurbs + '.cv[0:1][5]', tv=[(topToSkin, 0.25), (midToSkin, 0.75)])
            pm.skinPercent(skin, nurbs + '.cv[0:1][4]', tv=[(lwrToSkin, 0.25), (midToSkin, 0.75)])
            pm.skinPercent(skin, nurbs + '.cv[0:1][3]', tv=[(lwrToSkin, 0.35), (midToSkin, 0.65)])
            pm.skinPercent(skin, nurbs + '.cv[0:1][2]', tv=[(lwrToSkin, 0.6), (midToSkin, 0.4)])
            pm.skinPercent(skin, nurbs + '.cv[0:1][1]', tv=[(lwrToSkin, 0.85), (midToSkin, 0.15)])
            pm.skinPercent(skin, nurbs + '.cv[0:1][0]', tv=(lwrToSkin, 1))
        else:
            print "!!!There's skinning support for 3,5 and 7 sections only!!!"

        # posicionando o controle do meio
        pm.delete(pm.pointConstraint(self.guide2, midOffLoc))

        # criando controles
        if self.createCtrls == 0:
            topCircle = pm.circle(r=nurbsLength * .2, nr=(self.ctrlNormal[0], self.ctrlNormal[1], self.ctrlNormal[2]))
            topCtrlGrp = pm.group()
            topCtrlGrp.setParent(grpScale)
            pm.delete(pm.parentConstraint(self.guide3, topCtrlGrp, mo=0))
            pm.parentConstraint(topCircle[0], topPosLoc)

            midCircle = pm.circle(r=nurbsLength * .2, nr=(self.ctrlNormal[0], self.ctrlNormal[1], self.ctrlNormal[2]))
            midCtrlGrp = pm.group()
            midCtrlGrp.setParent(midOffLoc)
            pm.delete(pm.parentConstraint(midToSkin, midCtrlGrp))
            midJointZerado = self.zeroOut(midToSkin, returnGrpName=1)[0]
            pm.parent(midJointZerado, grpScale)
            pm.parentConstraint(midCircle[0], midJointZerado, mo=1)

            lwrCircle = pm.circle(r=nurbsLength * .2, nr=(self.ctrlNormal[0], self.ctrlNormal[1], self.ctrlNormal[2]))
            lwrCtrlGrp = pm.parent(pm.group(), grpScale)
            pm.delete(pm.parentConstraint(self.guide1, lwrCtrlGrp, mo=0))
            pm.parentConstraint(lwrCircle[0], lwrPosLoc)
        else:
            midCircle = pm.circle(r=nurbsLength * .2, nr=(self.ctrlNormal[0], self.ctrlNormal[1], self.ctrlNormal[2]))
            midCtrlGrp = pm.parent(pm.group(), midOffLoc)
            pm.delete(pm.parentConstraint(midToSkin, midCtrlGrp))
            midJointZerado = self.zeroOut(midToSkin, returnGrpName=1)[0]
            pm.parent(midJointZerado, grpScale)
            pm.parentConstraint(midCircle[0], midJointZerado, mo=1)

        id = 0

        midCircle[0].addAttr('autoSS', k=1, dv=0.0, at='double', min=0, max=1)
        midCircleShp = midCircle[0].getShape()

        if self.createCtrls:
            midCircleShp.v.set(0)

        for autoManualAuxNodes in autoManualList:
            id += 1
            # criando e ajustando nodes para stretch squash
            manualNormalize = pm.createNode('plusMinusAverage', n=self.name + 'RbbnManualNormalize0' + str(id) + '_pma')
            manualFactor = pm.createNode('multiplyDivide', n=self.name + 'RbbnManualFactor0' + str(id) + '_md')
            ratioScale = pm.createNode('multiplyDivide', n=self.name + 'RbbnRatioScale0' + str(id) + 'md')
            zRatio = pm.createNode('multiplyDivide', n=self.name + 'RbbnSsManualZratio' + str(id) + '_md')

            manualFactor.output >> autoManualAuxNodes.input3D[1]
            midCircle[0].scale >> manualNormalize.input3D[0]
            manualNormalize.output3D >> manualFactor.input2

            manualNormalize.operation.set(2)
            manualNormalize.input3D[1].input3D.set((1, 1, 1))
            ratioScale.operation.set(2)

            # adicionando atributos de squash
            midCircleShp.addAttr('manualFactorX0' + str(id), k=1, at='float', dv=1)
            midCircleShp.addAttr('manualRatioZ0' + str(id), k=1, at='float')
            midCircleShp.addAttr('autoFactorX0' + str(id), k=1, at='float')
            midCircleShp.addAttr('autoRatioZ0' + str(id), k=1, at='float')

            # conectando os atributos acima
            midCircleShp.attr('manualRatioZ0' + str(id)) >> zRatio.input1Z
            midCircleShp.attr('autoRatioZ0' + str(id)) >> zRatio.input1X

            midCircle[0].autoSS >> on_offList[id - 1].input2X  # on_off
            midCircle[0].autoSS >> on_offList[id - 1].input2Z  # on_off
            midCircleShp.attr('manualFactorX0' + str(id)) >> manualFactor.input1X
            midCircleShp.attr('manualFactorX0' + str(id)) >> zRatio.input2Z
            ratioScale.outputX >> zRatio.input2X
            zRatio.outputZ >> manualFactor.input1Z
            ratioScale.outputX >> factorList[id - 1].input1X  # factor
            zRatio.outputX >> factorList[id - 1].input1Z  # factor
            grpScale.scale >> ratioScale.input2
            midCircleShp.attr('autoFactorX0' + str(id)) >> ratioScale.input1X

            # ajustando os atributos
            midCircleShp.attr('manualRatioZ0' + str(id)).set(1)
            midCircleShp.attr('autoRatioZ0' + str(id)).set(1)

        # ajustando valores iniciais para os factores de squash

        if self.sections == 3:
            midCircleShp.autoFactorX02.set(0.08)
        elif self.sections == 5:
            midCircleShp.autoFactorX01.set(0.02)
            midCircleShp.autoFactorX02.set(0.25)
            midCircleShp.autoFactorX03.set(0.22)
            midCircleShp.autoFactorX04.set(0.25)
            midCircleShp.autoFactorX05.set(0.02)
        elif self.sections == 7:
            midCircleShp.autoFactorX01.set(0)
            midCircleShp.autoFactorX02.set(0.11)
            midCircleShp.autoFactorX03.set(0.1)
            midCircleShp.autoFactorX04.set(0.16)
            midCircleShp.autoFactorX05.set(0.1)
            midCircleShp.autoFactorX06.set(0.11)
            midCircleShp.autoFactorX07.set(0)

        # toggles displays
        if self.visibility == 0:
            pm.toggle(nurbs, g=1, te=1)
            pm.toggle(arcLength, te=1)
            arcLength.visibility.set(0)
            topPosLoc.visibility.set(0)
            midPosLocShp = midPosLoc.getShape()
            midPosLocShp.visibility.set(0)
            midAimLocShp = midAimLoc.getShape()
            midAimLocShp.visibility.set(0)
            midOffLocShp = midOffLoc.getShape()
            midOffLocShp.visibility.set(0)
            lwrPosLoc.visibility.set(0)
            midUpLoc.visibility.set(0)
            grpScale.visibility.set(0)
            grpFol.visibility.set(0)

        # agrupando tudo
        finalRbbnGrp = pm.group(em=1, n=self.name + 'finalRbbn_grp')
        pm.parent(nurbs, grpFol, grpScale, arcLength, finalRbbnGrp)

    def zeroOut(self, objeto=None, supressScale=0, returnGrpName=0):
        """ZeroOut Static Function
        -agrupa o objeto em questao e passa seus valores para o grupo
        -Inputs: (string) nome do node a levar zeroOut
             (boolean=0) nao mexer na escala durante o processo
             (boolean=0) retorna o nome do grupo criado?
        """
        # se nao for passado um nome, usar selecao atual
        if objeto == None:
            objetos = pm.ls(sl=1)
        else:
            objetos = [objeto]

        returnList = []
        # loop para multiplas selecoes
        for objeto in objetos:
            grp = pm.group(n=objeto + "_grp", em=1)
            pm.delete(pm.parentConstraint(objeto, grp))
            # vai que da algum problema...
            if not supressScale:
                pm.delete(pm.scaleConstraint(objeto, grp))

            pm.parent(objeto, grp)
            if returnGrpName:
                returnList.append(grp)

        if returnGrpName:
            return returnList