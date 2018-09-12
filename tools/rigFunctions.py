import pymel.core as pm
import maya.api.OpenMaya as om

def cntrlCrv(name='ctrl', obj=None, connType=None, offsets=0, hasZeroGrp=True, cntrlSulfix='_ctrl', hasHandle=False, posRot=None, **kwargs):
    #    Parametros:
    #        name (string): nome do novo controle
    #        obj(objeto) : objeto que sera controlado
    #        connType(string): tipo de conexao (parent,parentConstraint,orientConstraint)
    #        icone (string): tipo do icone (cubo,bola,circuloX,circuloY,circuloZ)
    #        size (float): escala do controle
    #        color (R,G,B): cor
    #        rotateOrder (int): ordem de rotacao default zxy

    # seta variaveis com os inputs
    # name=name

    cntrlledObj = obj
    connType = connType
    icone = kwargs.pop('icone', 'cubo')
    cntrlSize = kwargs.pop('size', 1)
    color = kwargs.pop('color', None)
    rotateOrder = kwargs.pop('rotateOrder', 0)  # default xyz
    nameConventions = kwargs.pop('nameConventions', None)  # default xyz
    cntrl = None
    cntrlGrp = None
    cnstr = None

    # constroi icone
    if icone == "cubo":
        crv = pm.curve(n=name + cntrlSulfix, d=1,
                       p=[(-0.5, 0.5, 0.5), (-0.5, 0.5, -0.5), (0.5, 0.5, -0.5), (0.5, 0.5, 0.5), (-0.5, 0.5, 0.5),
                          (0.5, 0.5, 0.5), (0.5, -0.5, 0.5), (-0.5, -0.5, 0.5), (-0.5, 0.5, 0.5), (-0.5, -0.5, 0.5),
                          (-0.5, -0.5, -0.5), (-0.5, 0.5, -0.5), (-0.5, -0.5, -0.5), (0.5, -0.5, -0.5),
                          (0.5, 0.5, -0.5), (0.5, -0.5, -0.5), (0.5, -0.5, 0.5)],
                       k=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16])
        crv.scale.set(cntrlSize, cntrlSize, cntrlSize)
        pm.makeIdentity(crv, a=True, t=True, r=True, s=True, n=False)
    elif icone == 'bola':
        crv = pm.circle(n=name + cntrlSulfix, c=(0, 0, 0), nr=(0, 1, 0), sw=360, r=0.5, d=3, ut=0, ch=0)[0]
        crv1 = pm.circle(n=name + "aux1", c=(0, 0, 0), nr=(1, 0, 0), sw=360, r=0.5, d=3, ut=0, ch=0)[0]
        crv2 = pm.circle(n=name + "aux2", c=(0, 0, 0), nr=(0, 0, 1), sw=360, r=0.5, d=3, ut=0, ch=0)[0]
        pm.parent([crv1.getShape(), crv2.getShape()], crv, shape=True, r=True)
        pm.delete(crv1, crv2)
        crv.scale.set(cntrlSize, cntrlSize, cntrlSize)
        pm.makeIdentity(crv, apply=True, t=1, r=1, s=1, n=0)
    elif icone == 'circuloY':
        crv = pm.circle(n=name + cntrlSulfix, c=(0, 0, 0), nr=(0, 1, 0), sw=360, r=0.5, d=3, ut=0, ch=0)[0]
        crv.scale.set(cntrlSize, cntrlSize, cntrlSize)
        pm.makeIdentity(crv, a=True, t=True, r=True, s=True, n=False)
    elif icone == 'circuloX':
        crv = pm.circle(n=name + cntrlSulfix, c=(0, 0, 0), nr=(1, 0, 0), sw=360, r=0.5, d=3, ut=0, ch=0)[0]
        crv.scale.set(cntrlSize, cntrlSize, cntrlSize)
        pm.makeIdentity(crv, a=True, t=True, r=True, s=True, n=False)
    elif icone == 'circuloZ':
        crv = pm.circle(n=name + cntrlSulfix, c=(0, 0, 0), nr=(0, 0, 1), sw=360, r=0.5, d=3, ut=0, ch=0)[0]
        crv.scale.set(cntrlSize, cntrlSize, cntrlSize)
        pm.makeIdentity(crv, a=True, t=True, r=True, s=True, n=False)
    elif icone == 'seta':
        crv = pm.curve(n=name + cntrlSulfix, d=1,
                       p=((-1, 0, 0), (-1, 0, -3), (-2, 0, -3), (0, 0, -5), (2, 0, -3), (1, 0, -3), (1, 0, 0)),
                       k=[0, 1, 2, 3, 4, 5, 6])
        crv.scale.set(cntrlSize, cntrlSize, cntrlSize)
        pm.makeIdentity(crv, a=True, t=True, r=True, s=True, n=False)
    elif icone == 'cog':
        crv = pm.curve(n=name + cntrlSulfix, d=1,
                       p=[(-4, 0, -4), (4, 0, -4), (4, 0, 3), (0, 0, 5), (-4, 0, 3), (-4, 0, -4)])
        crv.scale.set(cntrlSize * .1, cntrlSize * .1, cntrlSize * .1)
        pm.makeIdentity(crv, a=True, t=True, r=True, s=True, n=False)
    elif icone == "ponteiroX":
        crv = pm.curve(n=name + cntrlSulfix, d=1,
                       p=[(0, 0, 0), (1.691495, 1.691495, 0), (1.697056, 2.537859, 0), (2.545584, 2.545584, 0),
                          (2.545584, 1.707095, 0), (1.691504, 1.692763, 0)], k=[0, 1, 2, 3, 4, 5])
        crv.rotateZ.set(90)
        crv.scale.set(cntrlSize, cntrlSize, cntrlSize)
        pm.makeIdentity(crv, apply=True, t=1, r=1, s=1, n=0)
    elif icone == "ponteiroReto":
        crv = pm.curve(n=name + cntrlSulfix, d=1,
                       p=[(0, 0, 0), (0, 1.414597, 0), (0.569164, 2, 0), (0, 2.569164, 0), (-0.569164, 2, 0),
                          (0.00139909, 1.432235, 0)], k=[0, 1, 2, 3, 4, 5])
        pm.setAttr(name + "_ctrl.rotateY", 90)
        crv.scale.set(cntrlSize, cntrlSize, cntrlSize)
        pm.makeIdentity(crv, apply=True, t=1, r=1, s=1, n=0)
    elif icone == "ponteiroY":
        crv = pm.curve(n=name + cntrlSulfix, d=1,
                       p=[(0, 0, 0), (1.691495, 1.691495, 0), (1.697056, 2.537859, 0), (2.545584, 2.545584, 0),
                          (2.545584, 1.707095, 0), (1.691504, 1.692763, 0)], k=[0, 1, 2, 3, 4, 5])
        crv.rotateY.set(90)
        crv.rotateX.set(90)
        crv.scale.set(cntrlSize, cntrlSize, cntrlSize)
        pm.makeIdentity(crv, apply=True, t=1, r=1, s=1, n=0)
    elif icone == "ponteiroZ":
        crv = pm.curve(n=name + cntrlSulfix, d=1,
                       p=[(0, 0, 0), (1.691495, 1.691495, 0), (1.697056, 2.537859, 0), (2.545584, 2.545584, 0),
                          (2.545584, 1.707095, 0), (1.691504, 1.692763, 0)], k=[0, 1, 2, 3, 4, 5])
        crv.scale.set(cntrlSize, cntrlSize, cntrlSize)
        pm.makeIdentity(crv, apply=True, t=1, r=1, s=1, n=0)
    elif icone == "ponteiroMenosX":
        crv = pm.curve(n=name + cntrlSulfix, d=1,
                       p=[(0, 0, 0), (1.691495, 1.691495, 0), (1.697056, 2.537859, 0), (2.545584, 2.545584, 0),
                          (2.545584, 1.707095, 0), (1.691504, 1.692763, 0)], k=[0, 1, 2, 3, 4, 5])
        crv.rotateZ.set(-90)
        crv.scale.set(cntrlSize, cntrlSize, cntrlSize)
        pm.makeIdentity(crv, apply=True, t=1, r=1, s=1, n=0)
    elif icone == "ponteiroMenosY":
        crv = pm.curve(n=name + cntrlSulfix, d=1,
                       p=[(0, 0, 0), (1.691495, 1.691495, 0), (1.697056, 2.537859, 0), (2.545584, 2.545584, 0),
                          (2.545584, 1.707095, 0), (1.691504, 1.692763, 0)], k=[0, 1, 2, 3, 4, 5])
        crv.rotateY.set(-90)
        crv.rotateX.set(-90)
        crv.scale.set(cntrlSize, cntrlSize, cntrlSize)
        pm.makeIdentity(crv, apply=True, t=1, r=1, s=1, n=0)
    elif icone == "ponteiroMenosZ":
        crv = pm.curve(n=name + cntrlSulfix, d=1,
                       p=[(0, 0, 0), (1.691495, 1.691495, 0), (1.697056, 2.537859, 0), (2.545584, 2.545584, 0),
                          (2.545584, 1.707095, 0), (1.691504, 1.692763, 0)], k=[0, 1, 2, 3, 4, 5])
        crv.scale.set(cntrlSize, cntrlSize * -1, cntrlSize * -1)
        pm.makeIdentity(crv, apply=True, t=1, r=1, s=1, n=0)
    elif icone == 'quadradoX':
        crv = pm.curve(p=((.5, 0, -.5), (.5, 0, .5), (-.5, 0, .5), (-.5, 0, -.5), (.5, 0, -.5)), d=1,
                       n=name + cntrlSulfix)
        crv.rotateZ.set(90)
        crv.scale.set(cntrlSize, cntrlSize, cntrlSize)
        pm.makeIdentity(crv, a=True, t=True, r=True, s=True, n=False)
    elif icone == 'quadradoY':
        crv = pm.curve(p=((.5, 0, -.5), (.5, 0, .5), (-.5, 0, .5), (-.5, 0, -.5), (.5, 0, -.5)), d=1,
                       n=name + cntrlSulfix)
        crv.scale.set(cntrlSize, cntrlSize, cntrlSize)
        pm.makeIdentity(crv, a=True, t=True, r=True, s=True, n=False)
    elif icone == 'quadradoZ':
        crv = pm.curve(p=((.5, 0, -.5), (.5, 0, .5), (-.5, 0, .5), (-.5, 0, -.5), (.5, 0, -.5)), d=1,
                       n=name + cntrlSulfix)
        crv.rotateX.set(90)
        crv.scale.set(cntrlSize, cntrlSize, cntrlSize)
        pm.makeIdentity(crv, a=True, t=True, r=True, s=True, n=False)
    elif icone == 'dropY':
        crv = pm.circle(nr=[1, 0, 0], ch=0, n=name + cntrlSulfix)[0]
        pm.move(0, 3, 0, crv, r=1)
        pm.makeIdentity(crv, apply=1, t=1)
        pm.move(0, -3, 0, crv.scalePivot, crv.rotatePivot, r=1)
        pm.move(0, -1.8, crv.cv[5], r=1)
        pm.scale([crv.cv[4], crv.cv[6]], [1, 1, 0.01], r=1)
        pm.move(0, 0.5, 0, crv.cv[1], r=1)
        pm.move(0, 0.6, 0, crv.cv[0], crv.cv[2], r=1)
        crv.scale.set(cntrlSize, cntrlSize, cntrlSize)
        pm.makeIdentity(crv, a=True, t=True, r=True, s=True, n=False)
    elif icone == 'dropZ':
        crv = pm.circle(nr=[0, 1, 0], ch=0, n=name + cntrlSulfix)[0]
        pm.move(0, 0, -3, crv, r=1)
        pm.makeIdentity(crv, apply=1, t=1)
        pm.move(0, 0, 3, crv.scalePivot, crv.rotatePivot, r=1)
        pm.move(0, 0, 1.8, crv.cv[5], r=1)
        pm.scale([crv.cv[4], crv.cv[6]], [0.01, 1, 1], r=1)
        pm.move(0, 0, -0.5, crv.cv[1], r=1)
        pm.move(0, 0, -0.6, crv.cv[0], crv.cv[2], r=1)
        crv.scale.set(cntrlSize, cntrlSize, cntrlSize)
        pm.makeIdentity(crv, a=True, t=True, r=True, s=True, n=False)
    elif icone == 'dropMenosY':
        crv = pm.circle(nr=[1, 0, 0], ch=0, n=name + cntrlSulfix)[0]
        pm.move(0, 3, 0, crv, r=1)
        pm.makeIdentity(crv, apply=1, t=1)
        pm.move(0, -3, 0, crv.scalePivot, crv.rotatePivot, r=1)
        pm.move(0, -1.8, crv.cv[5], r=1)
        pm.scale([crv.cv[4], crv.cv[6]], [1, 1, 0.01], r=1)
        pm.move(0, 0.5, 0, crv.cv[1], r=1)
        pm.move(0, 0.6, 0, crv.cv[0], crv.cv[2], r=1)
        crv.scale.set(cntrlSize, cntrlSize * -1, cntrlSize)
        pm.makeIdentity(crv, a=True, t=True, r=True, s=True, n=False)
    elif icone == 'dropMenosZ':
        crv = pm.circle(nr=[0, 1, 0], ch=0, n=name + cntrlSulfix)[0]
        pm.move(0, 0, -3, crv, r=1)
        pm.makeIdentity(crv, apply=1, t=1)
        pm.move(0, 0, 3, crv.scalePivot, crv.rotatePivot, r=1)
        pm.move(0, 0, 1.8, crv.cv[5], r=1)
        pm.scale([crv.cv[4], crv.cv[6]], [0.01, 1, 1], r=1)
        pm.move(0, 0, -0.5, crv.cv[1], r=1)
        pm.move(0, 0, -0.6, crv.cv[0], crv.cv[2], r=1)
        crv.scale.set(cntrlSize, cntrlSize, cntrlSize * -1)
        pm.makeIdentity(crv, a=True, t=True, r=True, s=True, n=False)
    elif icone == 'circuloPontaY':
        tempCrv = pm.circle(n=name + "Aux", nr=[0, 1, 0], ch=0, s=6)[0]
        pm.scale([tempCrv.cv[3], tempCrv.cv[5]], [0.25, 1, 1])
        pm.move(0, 0, -0.5, tempCrv.cv[0], tempCrv.cv[2], r=1, ls=1)
        pm.move(0, 0, 1.25, tempCrv.cv[0:5], r=1, ls=1)
        pm.move(0, 0, 0.5, tempCrv.cv[1], r=1, ls=1)
        pm.scale(tempCrv.cv[0:5], [0.1, 0.1, 0.1], r=1, p=(0, 0, 1.25))
        crv = pm.circle(nr=[0, 1, 0], ch=0, n=name + cntrlSulfix)[0]
        pm.parent(tempCrv.getShape(), crv, r=1, s=1)
        pm.delete(tempCrv)
        crv.scale.set(cntrlSize * .5, cntrlSize * .5, cntrlSize * .5)
        pm.makeIdentity(crv, a=True, t=True, r=True, s=True, n=False)

    elif icone == 'hexagonoX':
        controlList = pm.circle(ch=1, n=name + cntrlSulfix, r=0.5)
        crv = controlList[0]
        history = controlList[1]
        history.degree.set(1)
        history.sections.set(6)
        history.normalZ.set(0)
        history.normalX.set(1)
        pm.delete(crv, ch=True)
        crv.scale.set(cntrlSize, cntrlSize, cntrlSize)
        pm.makeIdentity(crv, a=True, t=True, r=True, s=True, n=False)
    elif icone == 'hexagonoY':
        controlList = pm.circle(ch=1, n=name + cntrlSulfix, r=0.5)
        crv = controlList[0]
        history = controlList[1]
        history.degree.set(1)
        history.sections.set(6)
        history.normalZ.set(0)
        history.normalY.set(1)
        pm.delete(crv, ch=True)
        crv.scale.set(cntrlSize, cntrlSize, cntrlSize)
        pm.makeIdentity(crv, a=True, t=True, r=True, s=True, n=False)
    elif icone == 'hexagonoZ':
        controlList = pm.circle(ch=1, n=name + cntrlSulfix, r=0.5)
        crv = controlList[0]
        history = controlList[1]
        history.degree.set(1)
        history.sections.set(6)
        pm.delete(crv, ch=True)
        crv.scale.set(cntrlSize, cntrlSize, cntrlSize)
        pm.makeIdentity(crv, a=True, t=True, r=True, s=True, n=False)

    elif icone == 'pentagonoX':
        controlList = pm.circle(ch=1, n=name + cntrlSulfix, r=0.5)
        crv = controlList[0]
        history = controlList[1]
        history.degree.set(1)
        history.sections.set(5)
        history.normalZ.set(0)
        history.normalX.set(1)
        pm.delete(crv, ch=True)
        crv.scale.set(cntrlSize, cntrlSize, cntrlSize)
        pm.makeIdentity(crv, a=True, t=True, r=True, s=True, n=False)

    elif icone == 'pentagonoY':
        controlList = pm.circle(ch=1, n=name + cntrlSulfix, r=0.5)
        crv = controlList[0]
        history = controlList[1]
        history.degree.set(1)
        history.sections.set(5)
        history.normalZ.set(0)
        history.normalY.set(1)
        pm.delete(crv, ch=True)
        crv.scale.set(cntrlSize, cntrlSize, cntrlSize)
        pm.makeIdentity(crv, a=True, t=True, r=True, s=True, n=False)

    elif icone == 'pentagonoZ':
        controlList = pm.circle(ch=1, n=name + cntrlSulfix)
        crv = controlList[0]
        history = controlList[1]
        history.degree.set(1)
        history.sections.set(5)
        pm.delete(crv, ch=True)
        crv.scale.set(cntrlSize, cntrlSize, cntrlSize)
        pm.makeIdentity(crv, a=True, t=True, r=True, s=True, n=False)

    elif icone == 'crossX':
        crv = pm.curve(p=(
        (1, 0, -1), (1, 0, -2), (-1, 0, -2), (-1, 0, -1), (-2, 0, -1), (-2, 0, 1), (-1, 0, 1), (-1, 0, 2), (1, 0, 2),
        (1, 0, 1),
        (2, 0, 1), (2, 0, -1), (1, 0, -1)), d=1, n=name + cntrlSulfix)
        crv.rotateZ.set(90)
        crv.scale.set(cntrlSize, cntrlSize, cntrlSize)
        pm.makeIdentity(crv, a=True, t=True, r=True, s=True, n=False)

    elif icone == 'crossY':
        crv = pm.curve(p=(
        (1, 0, -1), (1, 0, -2), (-1, 0, -2), (-1, 0, -1), (-2, 0, -1), (-2, 0, 1), (-1, 0, 1), (-1, 0, 2), (1, 0, 2),
        (1, 0, 1),
        (2, 0, 1), (2, 0, -1), (1, 0, -1)), d=1, n=name + cntrlSulfix)
        crv.scale.set(cntrlSize, cntrlSize, cntrlSize)
        pm.makeIdentity(crv, a=True, t=True, r=True, s=True, n=False)

    elif icone == 'crossZ':
        crv = pm.curve(p=(
        (1, 0, -1), (1, 0, -2), (-1, 0, -2), (-1, 0, -1), (-2, 0, -1), (-2, 0, 1), (-1, 0, 1), (-1, 0, 2), (1, 0, 2),
        (1, 0, 1),
        (2, 0, 1), (2, 0, -1), (1, 0, -1)), d=1, n=name + cntrlSulfix)
        crv.rotateX.set(90)
        crv.scale.set(cntrlSize, cntrlSize, cntrlSize)
        pm.makeIdentity(crv, a=True, t=True, r=True, s=True, n=False)


    elif icone == 'fkShapeX':
        crv = pm.curve(p=(
        (0, 1, 1), (0, -1, 1), (2.903, -0.47, 0.522), (2.903, 0.573, 0.522), (0, 1, 1), (0, 1, -1), (0, -1, -1),
        (0, -1, 1), (0, 1, 1),
        (2.903, 0.573, 0.522), (2.903, 0.573, -0.522), (0, 1, -1), (0, -1, -1), (2.903, -0.47, -0.522),
        (2.903, -0.47, 0.522), (0, -1, 1), (0, -1, -1),
        (2.903, -0.47, -0.522), (2.903, 0.573, -0.522)), d=1, n=name + cntrlSulfix)
        crv.scale.set(cntrlSize, cntrlSize, cntrlSize)
        pm.makeIdentity(crv, a=True, t=True, r=True, s=True, n=False)

    elif icone == 'fkShapeY':
        crv = pm.curve(p=(
        (0, 1, 1), (0, -1, 1), (2.903, -0.47, 0.522), (2.903, 0.573, 0.522), (0, 1, 1), (0, 1, -1), (0, -1, -1),
        (0, -1, 1), (0, 1, 1),
        (2.903, 0.573, 0.522), (2.903, 0.573, -0.522), (0, 1, -1), (0, -1, -1), (2.903, -0.47, -0.522),
        (2.903, -0.47, 0.522), (0, -1, 1), (0, -1, -1),
        (2.903, -0.47, -0.522), (2.903, 0.573, -0.522)), d=1, n=name + cntrlSulfix)
        crv.rotateZ.set(90)
        crv.scale.set(cntrlSize, cntrlSize, cntrlSize)
        pm.makeIdentity(crv, a=True, t=True, r=True, s=True, n=False)

    elif icone == 'fkShapeZ':
        crv = pm.curve(p=(
        (0, 1, 1), (0, -1, 1), (2.903, -0.47, 0.522), (2.903, 0.573, 0.522), (0, 1, 1), (0, 1, -1), (0, -1, -1),
        (0, -1, 1), (0, 1, 1),
        (2.903, 0.573, 0.522), (2.903, 0.573, -0.522), (0, 1, -1), (0, -1, -1), (2.903, -0.47, -0.522),
        (2.903, -0.47, 0.522), (0, -1, 1), (0, -1, -1),
        (2.903, -0.47, -0.522), (2.903, 0.573, -0.522)), d=1, n=name + cntrlSulfix)
        crv.rotateY.set(-90)
        crv.scale.set(cntrlSize, cntrlSize, cntrlSize)
        pm.makeIdentity(crv, a=True, t=True, r=True, s=True, n=False)

    elif icone == 'fkShapeMinusX':
        crv = pm.curve(p=(
        (0, 1, 1), (0, -1, 1), (2.903, -0.47, 0.522), (2.903, 0.573, 0.522), (0, 1, 1), (0, 1, -1), (0, -1, -1),
        (0, -1, 1), (0, 1, 1),
        (2.903, 0.573, 0.522), (2.903, 0.573, -0.522), (0, 1, -1), (0, -1, -1), (2.903, -0.47, -0.522),
        (2.903, -0.47, 0.522), (0, -1, 1), (0, -1, -1),
        (2.903, -0.47, -0.522), (2.903, 0.573, -0.522)), d=1, n=name + cntrlSulfix)
        crv.scale.set(cntrlSize, cntrlSize, cntrlSize)
        crv.rotateZ.set(180)
        pm.makeIdentity(crv, a=True, t=True, r=True, s=True, n=False)
    elif icone == 'fkShapeMinusY':
        crv = pm.curve(p=(
        (0, 1, 1), (0, -1, 1), (2.903, -0.47, 0.522), (2.903, 0.573, 0.522), (0, 1, 1), (0, 1, -1), (0, -1, -1),
        (0, -1, 1), (0, 1, 1),
        (2.903, 0.573, 0.522), (2.903, 0.573, -0.522), (0, 1, -1), (0, -1, -1), (2.903, -0.47, -0.522),
        (2.903, -0.47, 0.522), (0, -1, 1), (0, -1, -1),
        (2.903, -0.47, -0.522), (2.903, 0.573, -0.522)), d=1, n=name + cntrlSulfix)
        crv.rotateZ.set(90)
        crv.scale.set(cntrlSize, cntrlSize, cntrlSize)
        crv.rotateX.set(180)
        pm.makeIdentity(crv, a=True, t=True, r=True, s=True, n=False)
    elif icone == 'fkShapeMinusZ':
        crv = pm.curve(p=(
        (0, 1, 1), (0, -1, 1), (2.903, -0.47, 0.522), (2.903, 0.573, 0.522), (0, 1, 1), (0, 1, -1), (0, -1, -1),
        (0, -1, 1), (0, 1, 1),
        (2.903, 0.573, 0.522), (2.903, 0.573, -0.522), (0, 1, -1), (0, -1, -1), (2.903, -0.47, -0.522),
        (2.903, -0.47, 0.522), (0, -1, 1), (0, -1, -1),
        (2.903, -0.47, -0.522), (2.903, 0.573, -0.522)), d=1, n=name + cntrlSulfix)
        crv.rotateY.set(-90)
        crv.scale.set(cntrlSize, cntrlSize, cntrlSize)
        crv.rotateX.set(180)
        pm.makeIdentity(crv, a=True, t=True, r=True, s=True, n=False)
    elif icone == 'guideDirectionShapeX':
        crv = pm.curve(p=(
        (-1, -1, 1), (1, -1, 1), (1, -1, -1), (-1, -1, -1), (-1, -1, 1), (-1, 1, 1), (-1, 1, -1), (-1, -1, -1),
        (-1, -1, 1),
        (-1, 1, 1), (1, 1, 1), (1, -1, 1), (1, -1, -1), (1, 1, -1), (1, 1, 1), (-1, 1, 1), (-1, 1, -1),
        (1, 1, -1), (0, 2.5, 0), (1, 1, 1), (-1, 1, 1), (0, 2.5, 0), (-1, 1, -1)), d=1, n=name + cntrlSulfix)
        crv.rotateZ.set(-90)
        crv.scale.set(cntrlSize, cntrlSize, cntrlSize)
        pm.makeIdentity(crv, a=True, t=True, r=True, s=True, n=False)
    elif icone == 'guideDirectionShapeY':
        crv = pm.curve(p=(
        (-1, -1, 1), (1, -1, 1), (1, -1, -1), (-1, -1, -1), (-1, -1, 1), (-1, 1, 1), (-1, 1, -1), (-1, -1, -1),
        (-1, -1, 1),
        (-1, 1, 1), (1, 1, 1), (1, -1, 1), (1, -1, -1), (1, 1, -1), (1, 1, 1), (-1, 1, 1), (-1, 1, -1),
        (1, 1, -1), (0, 2.5, 0), (1, 1, 1), (-1, 1, 1), (0, 2.5, 0), (-1, 1, -1)), d=1, n=name + cntrlSulfix)
        crv.scale.set(cntrlSize, cntrlSize, cntrlSize)
        pm.makeIdentity(crv, a=True, t=True, r=True, s=True, n=False)
    elif icone == 'guideDirectionShapeZ':
        crv = pm.curve(p=(
        (-1, -1, 1), (1, -1, 1), (1, -1, -1), (-1, -1, -1), (-1, -1, 1), (-1, 1, 1), (-1, 1, -1), (-1, -1, -1),
        (-1, -1, 1),
        (-1, 1, 1), (1, 1, 1), (1, -1, 1), (1, -1, -1), (1, 1, -1), (1, 1, 1), (-1, 1, 1), (-1, 1, -1),
        (1, 1, -1), (0, 2.5, 0), (1, 1, 1), (-1, 1, 1), (0, 2.5, 0), (-1, 1, -1)), d=1, n=name + cntrlSulfix)
        crv.rotateX.set(90)
        crv.scale.set(cntrlSize, cntrlSize, cntrlSize)
        pm.makeIdentity(crv, a=True, t=True, r=True, s=True, n=False)
    elif icone == 'arrowX':
        crv = pm.curve(p=((0, 4, 0), (-2, 2, 0), (-1, 2, 0), (-1, -2, 0), (1, -2, 0), (1, 2, 0), (2, 2, 0), (0, 4, 0)),
                       d=1, n=name + cntrlSulfix)
        crv.rotateZ.set(-90)
        crv.scale.set(cntrlSize, cntrlSize, cntrlSize)
        pm.makeIdentity(crv, a=True, t=True, r=True, s=True, n=False)
    elif icone == 'arrowY':
        crv = pm.curve(p=((0, 4, 0), (-2, 2, 0), (-1, 2, 0), (-1, -2, 0), (1, -2, 0), (1, 2, 0), (2, 2, 0), (0, 4, 0)),
                       d=1, n=name + cntrlSulfix)
        crv.scale.set(cntrlSize, cntrlSize, cntrlSize)
        pm.makeIdentity(crv, a=True, t=True, r=True, s=True, n=False)
    elif icone == 'arrowZ':
        crv = pm.curve(p=((0, 4, 0), (-2, 2, 0), (-1, 2, 0), (-1, -2, 0), (1, -2, 0), (1, 2, 0), (2, 2, 0), (0, 4, 0)),
                       d=1, n=name + cntrlSulfix)
        crv.rotateX.set(90)
        crv.scale.set(cntrlSize, cntrlSize, cntrlSize)
        pm.makeIdentity(crv, a=True, t=True, r=True, s=True, n=False)
    elif icone == "trianguloX":
        crv = pm.curve(n=name + cntrlSulfix, d=1,
                       p=[(0, 0, -0.471058), (-0.471058, 0, 0.471058), (0.471058, 0, 0.471058), (0, 0, -0.471058)],
                       k=[0, 1, 2, 3])
        crv.rotateX.set(90)
        crv.rotateY.set(90)
        crv.scale.set(cntrlSize, cntrlSize, cntrlSize)
        pm.makeIdentity(crv, apply=True, t=1, r=1, s=1, n=0)
    elif icone == "trianguloY":
        crv = pm.curve(n=name + cntrlSulfix, d=1,
                       p=[(0, 0, -0.471058), (-0.471058, 0, 0.471058), (0.471058, 0, 0.471058), (0, 0, -0.471058)],
                       k=[0, 1, 2, 3])
        crv.scale.set(cntrlSize, cntrlSize, cntrlSize)
        pm.makeIdentity(crv, apply=True, t=1, r=1, s=1, n=0)
    elif icone == "trianguloZ":
        crv = pm.curve(n=name + cntrlSulfix, d=1,
                       p=[(0, 0, -0.471058), (-0.471058, 0, 0.471058), (0.471058, 0, 0.471058), (0, 0, -0.471058)],
                       k=[0, 1, 2, 3])
        crv.rotateX.set(90)
        crv.scale.set(cntrlSize, cntrlSize, cntrlSize)
        pm.makeIdentity(crv, apply=True, t=1, r=1, s=1, n=0)
    elif icone == 'grp':
        crv = pm.group(n=name + cntrlSulfix, em=True)
    elif icone == 'null':
        crv = pm.spaceLocator(n=name + cntrlSulfix, p=(0, 0, 0))

        crv.localScale.set(cntrlSize, cntrlSize, cntrlSize)
    else:
        print 'shape nao reconhecido: %s' % icone

    if hasHandle:
        crv.displayHandle.set(1)

    # seta ordem de rotacao

    crv.rotateOrder.set(rotateOrder)
    if hasZeroGrp:
        grp = pm.group(n=name + "_grp", em=True)
        last = grp
        if offsets > 0:
            for i in range(1, offsets + 1):
                off = pm.group(n=name + "_off" + str(i), em=True)
                pm.parent(off, last)
                last = off
        pm.parent(crv, last)
        crv.rotateOrder.set(rotateOrder)
        pm.xform(grp, os=True, piv=[0, 0, 0])
    else:
        grp = crv
    # cor
    if color:
        shList = crv.getShapes()
        for sh in shList:
            sh.overrideEnabled.set(1)
            sh.overrideRGBColors.set(1)
            sh.overrideColorRGB.set(color)

        # faz a conexao
    if cntrlledObj:
        matrix = pm.xform(cntrlledObj, q=True, ws=True, m=True)

        pm.xform(grp, ws=True, m=matrix)
        pm.makeIdentity(grp, a=False, t=False, r=False, s=True, n=False)  ## garante q a escala nao fique negativa

        if connType == 'parent':
            cntrlledObj.setParent(crv)

        elif connType == 'parentConstraint':
            cnstr = pm.parentConstraint(crv, cntrlledObj, mo=True)

        elif connType == 'orientConstraint':
            cnstr = pm.orientConstraint(crv, cntrlledObj, mo=True)

        elif connType == 'constraint':
            cnstr = pm.parentConstraint(crv, cntrlledObj, mo=1)
            scaleConst = pm.scaleConstraint(crv, cntrlledObj, mo=1)

        elif connType == 'pointConstraint':
            cnstr = pm.pointConstraint(crv, cntrlledObj, mo=1)

        elif connType == 'scaleConstraint':
            cnstr = pm.scaleConstraint(crv, cntrlledObj, mo=1)

        elif connType == 'pointAndOrientConstraint':
            cnstr = pm.pointConstraint(crv, cntrlledObj, mo=1)
            cnstr = pm.orientConstraint(crv, cntrlledObj, mo=1)

        elif connType == 'pointAndScaleConstraint':
            cnstr = pm.pointConstraint(crv, cntrlledObj, mo=1)
            cnstr = pm.scaleConstraint(crv, cntrlledObj, mo=1)

        elif connType == 'orientAndScaleConstraint':
            cnstr = pm.orientConstraint(crv, cntrlledObj, mo=1)
            cnstr = pm.scaleConstraint(crv, cntrlledObj, mo=1)

        elif connType == 'connection':
            crv.tx >> cntrlledObj.tx
            crv.ty >> cntrlledObj.ty
            crv.tz >> cntrlledObj.tz
            crv.rx >> cntrlledObj.rx
            crv.ry >> cntrlledObj.ry
            crv.rz >> cntrlledObj.rz
            crv.sx >> cntrlledObj.sx
            crv.sy >> cntrlledObj.sy
            crv.sz >> cntrlledObj.sz

        elif connType == 'connectionT':
            crv.tx >> cntrlledObj.tx
            crv.ty >> cntrlledObj.ty
            crv.tz >> cntrlledObj.tz

        elif connType == 'connectionR':
            crv.rx >> cntrlledObj.rx
            crv.ry >> cntrlledObj.ry
            crv.rz >> cntrlledObj.rz

        elif connType == 'connectionS':
            crv.sx >> cntrlledObj.sx
            crv.sy >> cntrlledObj.sy
            crv.sz >> cntrlledObj.sz

        elif connType == 'connectionTR':
            crv.tx >> cntrlledObj.tx
            crv.ty >> cntrlledObj.ty
            crv.tz >> cntrlledObj.tz
            crv.rx >> cntrlledObj.rx
            crv.ry >> cntrlledObj.ry
            crv.rz >> cntrlledObj.rz

        elif connType == 'connectionTS':
            crv.tx >> cntrlledObj.tx
            crv.ty >> cntrlledObj.ty
            crv.tz >> cntrlledObj.tz
            crv.sx >> cntrlledObj.sx
            crv.sy >> cntrlledObj.sy
            crv.sz >> cntrlledObj.sz

        elif connType == 'connectionRS':
            crv.rx >> cntrlledObj.rx
            crv.ry >> cntrlledObj.ry
            crv.rz >> cntrlledObj.rz
            crv.sx >> cntrlledObj.sx
            crv.sy >> cntrlledObj.sy
            crv.sz >> cntrlledObj.sz
        elif connType == 'none':
            pass
    else:
        if posRot:
            grp.setTranslation(posRot[0], space='object')
            grp.setRotation(posRot[1], space='object')

    return (crv)


def createSpc(driver, name, type=None):
    drvGrp = pm.group(empty=True, n=name + '_drv')
    pos = pm.xform(driver, q=True, ws=True, t=True)
    pm.xform(drvGrp, t=pos, ws=True)

    if driver:
        pm.parentConstraint(driver, drvGrp, mo=True)
    spcGrp = pm.group(empty=True, n=name + '_spc')
    pm.parent(spcGrp, drvGrp)
    if not pm.objExists('spaces'):
        spcs = pm.group(name + '_drv', n='spaces')
        if not pm.objExists('MOVEALL'):
            pm.group(spcs, n='MOVEALL')
        else:
            pm.parent(spcs, 'MOVEALL')
    else:
        pm.parent(name + '_drv', 'spaces')


def addSpc(target, spaceList, switcher, type='parent', posSpc=None):
    for space in spaceList:
        if type == 'parent':
            cns = pm.parentConstraint(space + '_spc', switcher, mo=True)
        elif type == 'orient':
            cns = pm.orientConstraint(space + '_spc', switcher, mo=True)
            if posSpc:
                pm.pointConstraint(posSpc, switcher, mo=True)
            else:
                pm.pointConstraint(target.getParent(2), switcher, mo=True)

        if target.hasAttr('spcSwitch'):
            enumTxt = target.spcSwitch.getEnums()
            connects = target.spcSwitch.connections(d=True, s=False, p=True)
            index = len(enumTxt.keys())
            enumTxt[space] = index
            target.deleteAttr('spcSwitch')
            target.addAttr('spcSwitch', at='enum', en=enumTxt, k=True)
            if connects:
                for c in connects:
                    target.spcSwitch >> c
        else:
            target.addAttr('spcSwitch', at='enum', en=space, k=True)
            index = 0

        cond = pm.createNode('condition', n=switcher + space + 'Cond')
        target.spcSwitch >> cond.firstTerm
        cond.secondTerm.set(index)
        cond.operation.set(0)
        cond.colorIfTrueR.set(1)
        cond.colorIfFalseR.set(0)
        cond.outColor.outColorR >> cns.attr(space + '_spcW' + str(index))


def orientMatrix(mvector, normal, pos, axis):
    # criando a matriz do conforme a orientacao dada pela direcao AB, pela normal e na posicao pos
    AB = mvector
    nNormal = normal.normal()
    A = pos
    x = nNormal ^ AB.normal()
    t = x.normal() ^ nNormal

    if axis == 'Y':
        list = [nNormal.x, nNormal.y, nNormal.z, 0, t.x, t.y, t.z, 0, x.x, x.y, x.z, 0, A.x, A.y, A.z, 1]
    elif axis == 'Z':
        list = [x.x, x.y, x.z, 0, nNormal.x, nNormal.y, nNormal.z, 0, t.x, t.y, t.z, 0, A.x, A.y, A.z, 1]
    else:
        list = [t.x, t.y, t.z, 0, nNormal.x, nNormal.y, nNormal.z, 0, x.x * -1, x.y * -1, x.z * -1, 0, A.x, A.y, A.z, 1]
    m = om.MMatrix(list)
    return m


### Ainda nao usadas
def composeMMatrix(vecX, vecY, vecZ, vecP):
    list = [vecX.x, vecX.y, vecX.z, 0, vecY.x, vecY.y, vecY.z, 0, vecZ.x, vecZ.y, vecZ.z, 0, vecP.x, vecP.y, vecP.z, 1]
    m = om.MMatrix(list)
    return m


def makeJoint(name='joint', matrix=None, obj=None, connectToLast=False):
    if not connectToLast:
        pm.select(cl=True)
    jnt = pm.joint(n=name)
    if obj:
        pm.xform(obj, m=matrix, q=True, ws=True)
        pm.xform(jnt, m=matrix, ws=True)
    if matrix:
        pm.xform(jnt, m=matrix, ws=True)
    pm.makeIdentity(jnt, apply=True, r=1, t=0, s=0, n=0, pn=0)
    return jnt

def getObjTransforms(obj,space):

    if space == 'object':
        t = pm.xform(obj, q=True, t=True, wd=True)
        ro = pm.xform(obj, q=True, ro=True, wd=True)
    else:
        t = pm.xform (obj, q=True, t=True, ws=True)
        ro = pm.xform (obj, q=True, ro=True, ws=True)
    print obj.name()
    print [t,ro]
    return [t,ro]
