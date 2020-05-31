import pymel.core as pm
import cPickle as pickle
import logging

logger = logging.getLogger('autoRig')

def cntrlCrv(name='ctrl', cntrlSulfix='_ctrl', obj=None, connType=None, icone='cubo', color=None, cntrlSize=1,
             align='parent', hasZeroGrp=True, offsets=0, hasHandle=False,  rotateOrder=0, localAxis=False, template=False,
             hideShape=False, lockChannels=[], returnParent=False, coords=None, posRot=None, parent=None, **kwargs):
    '''
    create a control with a curve shape

    :param name:
    :param cntrlSulfix:
    :param obj:
    :param connType:
    :param icone:
    :param color:
    :param cntrlSize:
    :param align:
    :param hasZeroGrp:
    :param offsets:
    :param hasHandle:
    :param rotateOrder:
    :param localAxis:
    :param template:
    :param hideShape:
    :param lockChannels:
    :param returnParent:
    :param coords:
    :param posRot:
    :param parent:
    :param kwargs:
    :return:
    '''

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
        
    elif icone == 'circuloY' or icone == 'circulo_Y':
        crv = pm.circle(n=name + cntrlSulfix, c=(0, 0, 0), nr=(0, 1, 0), sw=360, r=0.5, d=3, ut=0, ch=0)[0]
        crv.scale.set(cntrlSize, cntrlSize, cntrlSize)
        pm.makeIdentity(crv, a=True, t=True, r=True, s=True, n=False)
        
    elif icone == 'circuloX' or icone == 'circulo_X':
        crv = pm.circle(n=name + cntrlSulfix, c=(0, 0, 0), nr=(1, 0, 0), sw=360, r=0.5, d=3, ut=0, ch=0)[0]
        crv.scale.set(cntrlSize, cntrlSize, cntrlSize)
        pm.makeIdentity(crv, a=True, t=True, r=True, s=True, n=False)
        
    elif icone == 'circuloZ' or icone == 'circulo_Z':
        crv = pm.circle(n=name + cntrlSulfix, c=(0, 0, 0), nr=(0, 0, 1), sw=360, r=0.5, d=3, ut=0, ch=0)[0]
        crv.scale.set(cntrlSize, cntrlSize, cntrlSize)
        pm.makeIdentity(crv, a=True, t=True, r=True, s=True, n=False)
        
    elif icone == 'seta':
        crv = pm.curve(n=name + cntrlSulfix, d=1,
                       p=((-1, 0, 0), (-1, 0, -3), (-2, 0, -3), (0, 0, -5), (2, 0, -3), (1, 0, -3), (1, 0, 0)),
                       k=[0, 1, 2, 3, 4, 5, 6])
        crv.scale.set(cntrlSize*0.096, cntrlSize*0.096, cntrlSize*0.096)
        pm.makeIdentity(crv, a=True, t=True, r=True, s=True, n=False)
        
    elif icone == 'cog' or icone =='cog_Y':
        crv = pm.curve(n=name + cntrlSulfix, d=1,
                       p=[(-4, 0, -4), (4, 0, -4), (4, 0, 3), (0, 0, 5), (-4, 0, 3), (-4, 0, -4)])
        crv.scale.set(cntrlSize * 0.1253, cntrlSize * 0.1253, cntrlSize * 0.1253)
        pm.makeIdentity(crv, a=True, t=True, r=True, s=True, n=False)

    elif icone == 'cogX' or icone == 'cog_X':
        crv = pm.curve(n=name + cntrlSulfix, d=1,
                       p=[(-4, 0, -4), (4, 0, -4), (4, 0, 3), (0, 0, 5), (-4, 0, 3), (-4, 0, -4)])
        crv.rotateZ.set(90)
        crv.scale.set(cntrlSize *0.1253, cntrlSize *0.1253, cntrlSize * 0.1253)
        pm.makeIdentity(crv, a=True, t=True, r=True, s=True, n=False)

    elif icone == 'cogZ' or icone == 'cog_Z':
        crv = pm.curve(n=name + cntrlSulfix, d=1,
                       p=[(-4, 0, -4), (4, 0, -4), (4, 0, 3), (0, 0, 5), (-4, 0, 3), (-4, 0, -4)])
        crv.rotateX.set(90)
        crv.scale.set(cntrlSize *0.1253, cntrlSize *0.1253, cntrlSize * 0.1253)
        pm.makeIdentity(crv, a=True, t=True, r=True, s=True, n=False)
        
    elif icone == "ponteiroX" or icone == "ponteiro_X":
        crv = pm.curve(n=name + cntrlSulfix, d=1,
                       p=[(0, 0, 0), (1.691495, 1.691495, 0), (1.697056, 2.537859, 0), (2.545584, 2.545584, 0),
                          (2.545584, 1.707095, 0), (1.691504, 1.692763, 0)], k=[0, 1, 2, 3, 4, 5])
        crv.rotateZ.set(90)
        crv.scale.set(cntrlSize*.196, cntrlSize*.196, cntrlSize*.196)
        pm.makeIdentity(crv, apply=True, t=1, r=1, s=1, n=0)
        
    elif icone == "ponteiroY" or icone == "ponteiro_Y":
        crv = pm.curve(n=name + cntrlSulfix, d=1,
                       p=[(0, 0, 0), (1.691495, 1.691495, 0), (1.697056, 2.537859, 0), (2.545584, 2.545584, 0),
                          (2.545584, 1.707095, 0), (1.691504, 1.692763, 0)], k=[0, 1, 2, 3, 4, 5])
        crv.rotateY.set(90)
        crv.rotateX.set(90)
        crv.scale.set(cntrlSize*.196, cntrlSize*.196, cntrlSize*.196)
        pm.makeIdentity(crv, apply=True, t=1, r=1, s=1, n=0)
        
    elif icone == "ponteiroZ" or  icone == "ponteiro_Z":
        crv = pm.curve(n=name + cntrlSulfix, d=1,
                       p=[(0, 0, 0), (1.691495, 1.691495, 0), (1.697056, 2.537859, 0), (2.545584, 2.545584, 0),
                          (2.545584, 1.707095, 0), (1.691504, 1.692763, 0)], k=[0, 1, 2, 3, 4, 5])
        crv.rotateY.set(-90)
        crv.scale.set(cntrlSize * .196, cntrlSize * .196, cntrlSize * .196)
        pm.makeIdentity(crv, apply=True, t=1, r=1, s=1, n=0)
        
    elif icone == "ponteiroMenosX":
        crv = pm.curve(n=name + cntrlSulfix, d=1,
                       p=[(0, 0, 0), (1.691495, 1.691495, 0), (1.697056, 2.537859, 0), (2.545584, 2.545584, 0),
                          (2.545584, 1.707095, 0), (1.691504, 1.692763, 0)], k=[0, 1, 2, 3, 4, 5])
        crv.rotateZ.set(-90)
        crv.scale.set(cntrlSize * .196, cntrlSize * .196, cntrlSize * .196)
        pm.makeIdentity(crv, apply=True, t=1, r=1, s=1, n=0)
        
    elif icone == "ponteiroMenosY":
        crv = pm.curve(n=name + cntrlSulfix, d=1,
                       p=[(0, 0, 0), (1.691495, 1.691495, 0), (1.697056, 2.537859, 0), (2.545584, 2.545584, 0),
                          (2.545584, 1.707095, 0), (1.691504, 1.692763, 0)], k=[0, 1, 2, 3, 4, 5])
        crv.rotateY.set(-90)
        crv.rotateX.set(-90)
        crv.scale.set(cntrlSize * .196, cntrlSize * .196, cntrlSize * .196)
        pm.makeIdentity(crv, apply=True, t=1, r=1, s=1, n=0)
        
    elif icone == "ponteiroMenosZ":
        crv = pm.curve(n=name + cntrlSulfix, d=1,
                       p=[(0, 0, 0), (1.691495, 1.691495, 0), (1.697056, 2.537859, 0), (2.545584, 2.545584, 0),
                          (2.545584, 1.707095, 0), (1.691504, 1.692763, 0)], k=[0, 1, 2, 3, 4, 5])
        crv.scale.set(cntrlSize*.196, cntrlSize * -.196, cntrlSize * -.196)
        pm.makeIdentity(crv, apply=True, t=1, r=1, s=1, n=0)

    elif icone == "ponteiroReto" or icone == "ponteiroReto_X":
        crv = pm.curve(n=name + cntrlSulfix, d=1,
                       p=[(0, 0, 0), (0, 6.414597, 0), (0.569164, 7, 0), (0, 7.569164, 0), (-0.569164, 7, 0),
                          (0.00139909, 6.432235, 0)], k=[0, 1, 2, 3, 4, 5])
        crv.rotateZ.set(-90)
        crv.scale.set(cntrlSize * .196, cntrlSize * .196, cntrlSize * .196)
        pm.makeIdentity(crv, apply=True, t=1, r=1, s=1, n=0)

    elif icone == "ponteiroReto_Y":
        crv = pm.curve(n=name + cntrlSulfix, d=1,
                       p=[(0, 0, 0), (0, 6.414597, 0), (0.569164, 7, 0), (0, 7.569164, 0), (-0.569164, 7, 0),
                          (0.00139909, 6.432235, 0)], k=[0, 1, 2, 3, 4, 5])

        crv.scale.set(cntrlSize * .196, cntrlSize * .196, cntrlSize * .196)
        pm.makeIdentity(crv, apply=True, t=1, r=1, s=1, n=0)

    elif icone == "ponteiroReto_Z":
        crv = pm.curve(n=name + cntrlSulfix, d=1,
                       p=[(0, 0, 0), (0, 6.414597, 0), (0.569164, 7, 0), (0, 7.569164, 0), (-0.569164, 7, 0),
                          (0.00139909, 6.432235, 0)], k=[0, 1, 2, 3, 4, 5])
        crv.rotateX.set(90)
        crv.scale.set(cntrlSize * .196, cntrlSize * .196, cntrlSize * .196)
        pm.makeIdentity(crv, apply=True, t=1, r=1, s=1, n=0)

    elif icone == 'quadradoX' or icone == 'quadrado_X':
        crv = pm.curve(p=((.5, 0, -.5), (.5, 0, .5), (-.5, 0, .5), (-.5, 0, -.5), (.5, 0, -.5)), d=1,
                       n=name + cntrlSulfix)
        crv.rotateZ.set(90)
        crv.scale.set(cntrlSize, cntrlSize, cntrlSize)
        pm.makeIdentity(crv, a=True, t=True, r=True, s=True, n=False)
        
    elif icone == 'quadradoY' or icone == 'quadrado_Y':
        crv = pm.curve(p=((.5, 0, -.5), (.5, 0, .5), (-.5, 0, .5), (-.5, 0, -.5), (.5, 0, -.5)), d=1,
                       n=name + cntrlSulfix)
        crv.scale.set(cntrlSize, cntrlSize, cntrlSize)
        pm.makeIdentity(crv, a=True, t=True, r=True, s=True, n=False)
        
    elif icone == 'quadradoZ' or icone == 'quadrado_Z':
        crv = pm.curve(p=((.5, 0, -.5), (.5, 0, .5), (-.5, 0, .5), (-.5, 0, -.5), (.5, 0, -.5)), d=1,
                       n=name + cntrlSulfix)
        crv.rotateX.set(90)
        crv.scale.set(cntrlSize, cntrlSize, cntrlSize)
        pm.makeIdentity(crv, a=True, t=True, r=True, s=True, n=False)
        
    elif icone == 'retanguloZ' or icone == 'retangulo_Z':
        crv = pm.curve(p=((5, 0, -.2), (5, 0, .2), (-5, 0, .2), (-5, 0, -.2), (5, 0, -.2)), d=1,
                       n=name + cntrlSulfix)
        crv.rotateX.set(90)
        crv.scale.set(cntrlSize*0.101, cntrlSize*0.227, cntrlSize*0.101)
        pm.makeIdentity(crv, a=True, t=True, r=True, s=True, n=False)

    elif icone == 'retanguloX' or icone == 'retangulo_X':
        crv = pm.curve(p=((5, 0, -.2), (5, 0, .2), (-5, 0, .2), (-5, 0, -.2), (5, 0, -.2)), d=1,
                       n=name + cntrlSulfix)
        crv.rotateX.set(90)
        crv.rotateY.set(90)
        crv.scale.set(cntrlSize*0.101, cntrlSize*0.227, cntrlSize*0.101)
        pm.makeIdentity(crv, a=True, t=True, r=True, s=True, n=False)

    elif icone == 'retanguloY' or icone == 'retangulo_Y':
        crv = pm.curve(p=((5, 0, -.2), (5, 0, .2), (-5, 0, .2), (-5, 0, -.2), (5, 0, -.2)), d=1,
                       n=name + cntrlSulfix)
        crv.scale.set(cntrlSize*0.101, cntrlSize*0.227, cntrlSize*0.101)
        pm.makeIdentity(crv, a=True, t=True, r=True, s=True, n=False)

    elif icone == 'dropY' or icone == 'drop_Y':
        crv = pm.circle(nr=[1, 0, 0], ch=0, n=name + cntrlSulfix)[0]
        pm.move(0, 3, 0, crv, r=1)
        pm.makeIdentity(crv, apply=1, t=1)
        pm.move(0, -3, 0, crv.scalePivot, crv.rotatePivot, r=1)
        pm.move(0, -1.8, crv.cv[5], r=1)
        pm.scale([crv.cv[4], crv.cv[6]], [1, 1, 0.01], r=1)
        pm.move(0, 0.5, 0, crv.cv[1], r=1)
        pm.move(0, 0.6, 0, crv.cv[0], crv.cv[2], r=1)
        crv.scale.set(cntrlSize*0.22, cntrlSize*0.22, cntrlSize*0.22)
        pm.makeIdentity(crv, a=True, t=True, r=True, s=True, n=False)
        
    elif icone == 'dropZ' or icone == 'drop_Z':
        crv = pm.circle(nr=[0, 1, 0], ch=0, n=name + cntrlSulfix)[0]
        pm.move(0, 0, -3, crv, r=1)
        pm.makeIdentity(crv, apply=1, t=1)
        pm.move(0, 0, 3, crv.scalePivot, crv.rotatePivot, r=1)
        pm.move(0, 0, 1.8, crv.cv[5], r=1)
        pm.scale([crv.cv[4], crv.cv[6]], [0.01, 1, 1], r=1)
        pm.move(0, 0, -0.5, crv.cv[1], r=1)
        pm.move(0, 0, -0.6, crv.cv[0], crv.cv[2], r=1)
        crv.scale.set(cntrlSize * 0.22, cntrlSize * 0.22, cntrlSize * 0.22)
        pm.makeIdentity(crv, a=True, t=True, r=True, s=True, n=False)

    elif icone == 'dropX' or icone == 'drop_X':
        crv = pm.circle(nr=[0, 0, 1], ch=0, n=name + cntrlSulfix)[0]
        pm.move(0, 0, -3, crv, r=1)
        pm.makeIdentity(crv, apply=1, t=1)
        pm.move(0, 0, 3, crv.scalePivot, crv.rotatePivot, r=1)
        pm.move(0, 0, 1.8, crv.cv[5], r=1)
        pm.scale([crv.cv[4], crv.cv[6]], [0.01, 1, 1], r=1)
        pm.move(0, 0, -0.5, crv.cv[1], r=1)
        pm.move(0, 0, -0.6, crv.cv[0], crv.cv[2], r=1)
        crv.scale.set(cntrlSize * 0.22, cntrlSize * 0.22, cntrlSize * 0.22)
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
        crv.scale.set(cntrlSize * 0.22, cntrlSize * -0.22, cntrlSize * 0.22)
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
        crv.scale.set(cntrlSize * 0.22, cntrlSize * 0.22, cntrlSize * -0.22)
        pm.makeIdentity(crv, a=True, t=True, r=True, s=True, n=False)

    elif icone == 'circuloPontaX' or icone == 'circuloPonta_X':
        tempCrv = pm.circle(n=name + "Aux", nr=[0, 1, 0], ch=0, s=6)[0]
        pm.scale([tempCrv.cv[3], tempCrv.cv[5]], [0.25, 1, 1])
        pm.move(0, 0, -0.5, tempCrv.cv[0], tempCrv.cv[2], r=1, ls=1)
        pm.move(0, 0, 1.25, tempCrv.cv[0:5], r=1, ls=1)
        pm.move(0, 0, 0.5, tempCrv.cv[1], r=1, ls=1)
        pm.scale(tempCrv.cv[0:5], [0.1, 0.1, 0.1], r=1, p=(0, 0, 1.25))
        crv = pm.circle(nr=[0, 1, 0], ch=0, n=name + cntrlSulfix)[0]
        pm.parent(tempCrv.getShape(), crv, r=1, s=1)
        pm.delete(tempCrv)
        crv.scale.set(cntrlSize *0.4815, cntrlSize*0.4815,cntrlSize*0.4815)
        crv.rotateZ.set(90)
        crv.rotateY.set (180)
        pm.makeIdentity(crv, a=True, t=True, r=True, s=True, n=False)

    elif icone == 'circuloPontaY' or icone == 'circuloPonta_Y':
        tempCrv = pm.circle(n=name + "Aux", nr=[0, 1, 0], ch=0, s=6)[0]
        pm.scale([tempCrv.cv[3], tempCrv.cv[5]], [0.25, 1, 1])
        pm.move(0, 0, -0.5, tempCrv.cv[0], tempCrv.cv[2], r=1, ls=1)
        pm.move(0, 0, 1.25, tempCrv.cv[0:5], r=1, ls=1)
        pm.move(0, 0, 0.5, tempCrv.cv[1], r=1, ls=1)
        pm.scale(tempCrv.cv[0:5], [0.1, 0.1, 0.1], r=1, p=(0, 0, 1.25))
        crv = pm.circle(nr=[0, 1, 0], ch=0, n=name + cntrlSulfix)[0]
        pm.parent(tempCrv.getShape(), crv, r=1, s=1)
        pm.delete(tempCrv)
        crv.scale.set(cntrlSize * 0.4815, cntrlSize * 0.4815, cntrlSize * 0.4815)
        pm.makeIdentity(crv, a=True, t=True, r=True, s=True, n=False)

    elif icone == 'circuloPontaZ' or icone == 'circuloPonta_Z':
        tempCrv = pm.circle(n=name + "Aux", nr=[0, 1, 0], ch=0, s=6)[0]
        pm.scale([tempCrv.cv[3], tempCrv.cv[5]], [0.25, 1, 1])
        pm.move(0, 0, -0.5, tempCrv.cv[0], tempCrv.cv[2], r=1, ls=1)
        pm.move(0, 0, 1.25, tempCrv.cv[0:5], r=1, ls=1)
        pm.move(0, 0, 0.5, tempCrv.cv[1], r=1, ls=1)
        pm.scale(tempCrv.cv[0:5], [0.1, 0.1, 0.1], r=1, p=(0, 0, 1.25))
        crv = pm.circle(nr=[0, 1, 0], ch=0, n=name + cntrlSulfix)[0]
        pm.parent(tempCrv.getShape(), crv, r=1, s=1)
        pm.delete(tempCrv)
        crv.scale.set(cntrlSize * 0.4815, cntrlSize * 0.4815, cntrlSize * 0.4815)
        crv.rotateX.set(90)
        pm.makeIdentity(crv, a=True, t=True, r=True, s=True, n=False)

    elif icone == 'hexagonoX' or icone == 'hexagono_X':
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

    elif icone == 'hexagonoY' or icone == 'hexagono_Y':
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
        
    elif icone == 'hexagonoZ' or icone == 'hexagono_Z':
        controlList = pm.circle(ch=1, n=name + cntrlSulfix, r=0.5)
        crv = controlList[0]
        history = controlList[1]
        history.degree.set(1)
        history.sections.set(6)
        pm.delete(crv, ch=True)
        crv.scale.set(cntrlSize, cntrlSize, cntrlSize)
        pm.makeIdentity(crv, a=True, t=True, r=True, s=True, n=False)
        
    elif icone == 'pentagonoX' or icone == 'pentagono_X':
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
        
    elif icone == 'pentagonoY' or icone == 'pentagono_Y':
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

    elif icone == 'pentagonoZ' or icone == 'pentagono_Z':
        controlList = pm.circle(ch=1, n=name + cntrlSulfix, r=0.5)
        crv = controlList[0]
        history = controlList[1]
        history.degree.set(1)
        history.sections.set(5)
        pm.delete(crv, ch=True)
        crv.scale.set(cntrlSize, cntrlSize, cntrlSize)
        pm.makeIdentity(crv, a=True, t=True, r=True, s=True, n=False)

    elif icone == 'crossX' or icone == 'cross_X':
        crv = pm.curve(p=(
        (1, 0, -1), (1, 0, -2), (-1, 0, -2), (-1, 0, -1), (-2, 0, -1), (-2, 0, 1), (-1, 0, 1), (-1, 0, 2), (1, 0, 2),
        (1, 0, 1),
        (2, 0, 1), (2, 0, -1), (1, 0, -1)), d=1, n=name + cntrlSulfix)
        crv.rotateZ.set(90)
        crv.scale.set(cntrlSize*0.245, cntrlSize*0.245, cntrlSize*0.245)
        pm.makeIdentity(crv, a=True, t=True, r=True, s=True, n=False)

    elif icone == 'crossY' or icone == 'cross_Y':
        crv = pm.curve(p=(
        (1, 0, -1), (1, 0, -2), (-1, 0, -2), (-1, 0, -1), (-2, 0, -1), (-2, 0, 1), (-1, 0, 1), (-1, 0, 2), (1, 0, 2),
        (1, 0, 1),
        (2, 0, 1), (2, 0, -1), (1, 0, -1)), d=1, n=name + cntrlSulfix)
        crv.scale.set(cntrlSize * 0.245, cntrlSize * 0.245, cntrlSize * 0.245)
        pm.makeIdentity(crv, a=True, t=True, r=True, s=True, n=False)

    elif icone == 'crossZ' or icone == 'cross_Z':
        crv = pm.curve(p=(
        (1, 0, -1), (1, 0, -2), (-1, 0, -2), (-1, 0, -1), (-2, 0, -1), (-2, 0, 1), (-1, 0, 1), (-1, 0, 2), (1, 0, 2),
        (1, 0, 1),
        (2, 0, 1), (2, 0, -1), (1, 0, -1)), d=1, n=name + cntrlSulfix)
        crv.rotateX.set(90)
        crv.scale.set(cntrlSize * 0.245, cntrlSize * 0.245, cntrlSize * 0.245)
        pm.makeIdentity(crv, a=True, t=True, r=True, s=True, n=False)

    elif icone == 'fkShapeX' or icone == 'fkShape_X':
        crv = pm.curve(p=(
        (0, 1, 1), (0, -1, 1), (2.903, -0.47, 0.522), (2.903, 0.573, 0.522), (0, 1, 1), (0, 1, -1), (0, -1, -1),
        (0, -1, 1), (0, 1, 1),
        (2.903, 0.573, 0.522), (2.903, 0.573, -0.522), (0, 1, -1), (0, -1, -1), (2.903, -0.47, -0.522),
        (2.903, -0.47, 0.522), (0, -1, 1), (0, -1, -1),
        (2.903, -0.47, -0.522), (2.903, 0.573, -0.522)), d=1, n=name + cntrlSulfix)
        crv.scale.set(cntrlSize*0.327, cntrlSize*0.327, cntrlSize*0.327)
        pm.makeIdentity(crv, a=True, t=True, r=True, s=True, n=False)

    elif icone == 'fkShapeY' or icone == 'fkShape_Y':
        crv = pm.curve(p=(
        (0, 1, 1), (0, -1, 1), (2.903, -0.47, 0.522), (2.903, 0.573, 0.522), (0, 1, 1), (0, 1, -1), (0, -1, -1),
        (0, -1, 1), (0, 1, 1),
        (2.903, 0.573, 0.522), (2.903, 0.573, -0.522), (0, 1, -1), (0, -1, -1), (2.903, -0.47, -0.522),
        (2.903, -0.47, 0.522), (0, -1, 1), (0, -1, -1),
        (2.903, -0.47, -0.522), (2.903, 0.573, -0.522)), d=1, n=name + cntrlSulfix)
        crv.rotateZ.set(90)
        crv.scale.set(cntrlSize * 0.327, cntrlSize * 0.327, cntrlSize * 0.327)
        pm.makeIdentity(crv, a=True, t=True, r=True, s=True, n=False)

    elif icone == 'fkShapeZ' or icone == 'fkShape_Z':
        crv = pm.curve(p=(
        (0, 1, 1), (0, -1, 1), (2.903, -0.47, 0.522), (2.903, 0.573, 0.522), (0, 1, 1), (0, 1, -1), (0, -1, -1),
        (0, -1, 1), (0, 1, 1),
        (2.903, 0.573, 0.522), (2.903, 0.573, -0.522), (0, 1, -1), (0, -1, -1), (2.903, -0.47, -0.522),
        (2.903, -0.47, 0.522), (0, -1, 1), (0, -1, -1),
        (2.903, -0.47, -0.522), (2.903, 0.573, -0.522)), d=1, n=name + cntrlSulfix)
        crv.rotateY.set(-90)
        crv.scale.set(cntrlSize * 0.327, cntrlSize * 0.327, cntrlSize * 0.327)
        pm.makeIdentity(crv, a=True, t=True, r=True, s=True, n=False)

    elif icone == 'fkShapeMinusX':
        crv = pm.curve(p=(
        (0, 1, 1), (0, -1, 1), (2.903, -0.47, 0.522), (2.903, 0.573, 0.522), (0, 1, 1), (0, 1, -1), (0, -1, -1),
        (0, -1, 1), (0, 1, 1),
        (2.903, 0.573, 0.522), (2.903, 0.573, -0.522), (0, 1, -1), (0, -1, -1), (2.903, -0.47, -0.522),
        (2.903, -0.47, 0.522), (0, -1, 1), (0, -1, -1),
        (2.903, -0.47, -0.522), (2.903, 0.573, -0.522)), d=1, n=name + cntrlSulfix)
        crv.scale.set(cntrlSize * 0.327, cntrlSize * 0.327, cntrlSize * 0.327)
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
        crv.scale.set(cntrlSize * 0.327, cntrlSize * 0.327, cntrlSize * 0.327)
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
        crv.scale.set(cntrlSize * 0.327, cntrlSize * 0.327, cntrlSize * 0.327)
        crv.rotateX.set(180)
        pm.makeIdentity(crv, a=True, t=True, r=True, s=True, n=False)
        
    elif icone == 'guideDirectionShapeX' or icone == 'guideDirectionShape_X':
        crv = pm.curve(p=(
        (-1, -1, 1), (1, -1, 1), (1, -1, -1), (-1, -1, -1), (-1, -1, 1), (-1, 1, 1), (-1, 1, -1), (-1, -1, -1),
        (-1, -1, 1),
        (-1, 1, 1), (1, 1, 1), (1, -1, 1), (1, -1, -1), (1, 1, -1), (1, 1, 1), (-1, 1, 1), (-1, 1, -1),
        (1, 1, -1), (0, 2.5, 0), (1, 1, 1), (-1, 1, 1), (0, 2.5, 0), (-1, 1, -1)), d=1, n=name + cntrlSulfix)
        crv.rotateZ.set(-90)
        crv.scale.set(cntrlSize*0.487, cntrlSize*0.487, cntrlSize*0.487)
        pm.makeIdentity(crv, a=True, t=True, r=True, s=True, n=False)
        
    elif icone == 'guideDirectionShapeY' or icone == 'guideDirectionShape_Y':
        crv = pm.curve(p=(
        (-1, -1, 1), (1, -1, 1), (1, -1, -1), (-1, -1, -1), (-1, -1, 1), (-1, 1, 1), (-1, 1, -1), (-1, -1, -1),
        (-1, -1, 1),
        (-1, 1, 1), (1, 1, 1), (1, -1, 1), (1, -1, -1), (1, 1, -1), (1, 1, 1), (-1, 1, 1), (-1, 1, -1),
        (1, 1, -1), (0, 2.5, 0), (1, 1, 1), (-1, 1, 1), (0, 2.5, 0), (-1, 1, -1)), d=1, n=name + cntrlSulfix)
        crv.scale.set(cntrlSize * 0.487, cntrlSize * 0.487, cntrlSize * 0.487)
        pm.makeIdentity(crv, a=True, t=True, r=True, s=True, n=False)
        
    elif icone == 'guideDirectionShapeZ' or icone == 'guideDirectionShape_Z':
        crv = pm.curve(p=(
        (-1, -1, 1), (1, -1, 1), (1, -1, -1), (-1, -1, -1), (-1, -1, 1), (-1, 1, 1), (-1, 1, -1), (-1, -1, -1),
        (-1, -1, 1),
        (-1, 1, 1), (1, 1, 1), (1, -1, 1), (1, -1, -1), (1, 1, -1), (1, 1, 1), (-1, 1, 1), (-1, 1, -1),
        (1, 1, -1), (0, 2.5, 0), (1, 1, 1), (-1, 1, 1), (0, 2.5, 0), (-1, 1, -1)), d=1, n=name + cntrlSulfix)
        crv.rotateX.set(90)
        crv.scale.set(cntrlSize * 0.487, cntrlSize * 0.487, cntrlSize * 0.487)
        pm.makeIdentity(crv, a=True, t=True, r=True, s=True, n=False)
        
    elif icone == 'arrowX' or icone == 'arrow_X':
        crv = pm.curve(p=((0, 4, 0), (-2, 2, 0), (-1, 2, 0), (-1, -2, 0), (1, -2, 0), (1, 2, 0), (2, 2, 0), (0, 4, 0)),
                       d=1, n=name + cntrlSulfix)
        crv.rotateZ.set(-90)
        crv.scale.set(cntrlSize*0.123, cntrlSize*0.123, cntrlSize*0.123)
        pm.makeIdentity(crv, a=True, t=True, r=True, s=True, n=False)
        
    elif icone == 'arrowY' or icone == 'arrow_Y':
        crv = pm.curve(p=((0, 4, 0), (-2, 2, 0), (-1, 2, 0), (-1, -2, 0), (1, -2, 0), (1, 2, 0), (2, 2, 0), (0, 4, 0)),
                       d=1, n=name + cntrlSulfix)
        crv.scale.set(cntrlSize * 0.123, cntrlSize * 0.123, cntrlSize * 0.123)
        pm.makeIdentity(crv, a=True, t=True, r=True, s=True, n=False)
        
    elif icone == 'arrowZ' or icone == 'arrow_Z':
        crv = pm.curve(p=((0, 4, 0), (-2, 2, 0), (-1, 2, 0), (-1, -2, 0), (1, -2, 0), (1, 2, 0), (2, 2, 0), (0, 4, 0)),
                       d=1, n=name + cntrlSulfix)
        crv.rotateX.set(90)
        crv.scale.set(cntrlSize * 0.123, cntrlSize * 0.123, cntrlSize * 0.123)
        pm.makeIdentity(crv, a=True, t=True, r=True, s=True, n=False)
        
    elif icone == "trianguloX" or icone == "triangulo_X":
        crv = pm.curve(n=name + cntrlSulfix, d=1,
                       p=[(0, 0, -0.471058), (-0.471058, 0, 0.471058), (0.471058, 0, 0.471058), (0, 0, -0.471058)],
                       k=[0, 1, 2, 3])
        crv.rotateX.set(90)
        crv.rotateY.set(90)
        crv.scale.set(cntrlSize, cntrlSize, cntrlSize)
        pm.makeIdentity(crv, apply=True, t=1, r=1, s=1, n=0)
        
    elif icone == "trianguloY" or icone == "triangulo_Y":
        crv = pm.curve(n=name + cntrlSulfix, d=1,
                       p=[(0, 0, -0.471058), (-0.471058, 0, 0.471058), (0.471058, 0, 0.471058), (0, 0, -0.471058)],
                       k=[0, 1, 2, 3])
        crv.scale.set(cntrlSize, cntrlSize, cntrlSize)
        pm.makeIdentity(crv, apply=True, t=1, r=1, s=1, n=0)
        
    elif icone == "trianguloZ" or  icone == "triangulo_Z":
        crv = pm.curve(n=name + cntrlSulfix, d=1,
                       p=[(0, 0, -0.471058), (-0.471058, 0, 0.471058), (0.471058, 0, 0.471058), (0, 0, -0.471058)],
                       k=[0, 1, 2, 3])
        crv.rotateZ.set(90)
        crv.scale.set(cntrlSize, cntrlSize, cntrlSize)
        pm.makeIdentity(crv, apply=True, t=1, r=1, s=1, n=0)
        
    elif icone == "trianguloMinusZ":
        crv = pm.curve(n=name + cntrlSulfix, d=1,
                       p=[(0, 0, -0.471058), (-0.471058, 0, 0.471058), (0.471058, 0, 0.471058), (0, 0, -0.471058)],
                       k=[0, 1, 2, 3])
        crv.rotateX.set(-90)
        crv.rotateZ.set(90)
        crv.scale.set(cntrlSize, -1*cntrlSize, cntrlSize)
        pm.makeIdentity(crv, apply=True, t=1, r=1, s=1, n=0)

    elif icone == "jaw":
        crv = pm.circle(nr=[0,0,1], ch=0, name=name)[0]
        pm.move( 0.78,-0.01,-0.3, crv+'.cv[0]')
        pm.move( 0,-0.09,0, crv+'.cv[1]')
        pm.move( -0.78,-0.01,-0.3, crv+'.cv[2]')
        pm.move( -1.108,-0,-0.55, crv+'.cv[3]')
        pm.move( -0.78,-0.78,-0.3, crv+'.cv[4]')
        pm.move( 0,-1.108,0, crv+'.cv[5]')
        pm.move( 0.78,-0.78,-0.3, crv+'.cv[6]')
        pm.move( 1.109,0,-0.55, crv+'.cv[7]' )
        crv.scale.set(cntrlSize*0.501, 0.501*cntrlSize, cntrlSize*0.501)
        pm.makeIdentity(crv, apply=True, t=1, r=1, s=1, n=0)

    elif icone == "upTeeth":
        crv = pm.curve(name=name, d=3, p=[(-0.80380731394020355, -0.22720474003408064, 0), (-0.78833906954303412, -0.32153249588067823, 0),
                                                     (-0.76088405517014568, -0.41013482375058707, 0), (-0.62735291342491006, -0.43040000647965293, 0),
                                                     (-0.41534271707226456, -0.43191082347433429, 0), (-0.42495970029949337, -0.040047557704252057, 0),
                                                     (-0.40579495988262604, -0.024586361881729246, 0), (-0.38693255181790942, -0.039628633322768891, 0),
                                                     (-0.3964314271448357, -0.43358651947575311, 0), (-0.18695799902989041, -0.42411614361856564, 0),
                                                     (0.028288611981836631, -0.43359457401211543, 0), (0.02464596629930238, -0.03959641334886399, 0),
                                                     (0.031931321369774501, -0.024707184158323514, 0), (0.039216483222223708, -0.039596484482549599, 0),
                                                     (0.035573866478620708, -0.43359428947729661, 0), (0.25081890272400198, -0.42411721050207163, 0),
                                                     (0.46621969146686748, -0.43358253565918936, 0), (0.46280056649138057, -0.039643499755065648, 0),
                                                     (0.46963982619053457, -0.02453087688648381, 0), (0.47646879021640753, -0.040254627919388497, 0),
                                                     (0.47308055216016864, -0.43113802756945674, 0), (0.68669251473786996, -0.43328412048568588, 0),
                                                     (0.84162660358193353, -0.39937116285575591, 0), (0.90911721139256318, -0.16732208539539606, 0),
                                                     (0.92458015941006, 0.34843743085733081, 0), (0.027431509404153509, 0.43359457401211188, 0),
                                                     (-0.92458015941005645, 0.31110756712332055, 0), (-0.82201559109450617, -0.086251710757503375, 0),
                                                     (-0.80380731394038829, -0.22720474003434887, 0)])
        crv.scale.set(cntrlSize*0.519, 0.519*cntrlSize, cntrlSize*0.519)
        pm.makeIdentity(crv, apply=True, t=1, r=1, s=1, n=0)

    elif icone == "dwTeeth":
        crv = pm.curve(name=name, d=3, p=[(-0.80380731394020355, 0.22720474003407709, 0), (-0.78833906954303412, 0.32153249588067467, 0),
                                                     (-0.76088405517014568, 0.41013482375058352, 0), (-0.62735291342491006, 0.43040000647964938, 0),
                                                     (-0.41534271707226456, 0.43191082347433074, 0), (-0.42495970029949337, 0.040047557704248504, 0),
                                                     (-0.40579495988262604, 0.024586361881725693, 0), (-0.38693255181790942, 0.039628633322765339, 0),
                                                     (-0.3964314271448357, 0.43358651947574955, 0), (-0.18695799902989041, 0.42411614361856209, 0),
                                                     (0.028288611981836631, 0.43359457401211188, 0), (0.02464596629930238, 0.039596413348860438, 0),
                                                     (0.031931321369774501, 0.024707184158319961, 0), (0.039216483222223708, 0.039596484482546046, 0),
                                                     (0.035573866478620708, 0.43359428947729306, 0), (0.25081890272400198, 0.42411721050206808, 0),
                                                     (0.46621969146686748, 0.43358253565918581, 0), (0.46280056649138057, 0.039643499755062095, 0),
                                                     (0.46963982619053457, 0.024530876886480257, 0), (0.47646879021640753, 0.040254627919384944, 0),
                                                     (0.47308055216016864, 0.43113802756945319, 0), (0.68669251473786996, 0.43328412048568232, 0),
                                                     (0.84162660358193353, 0.39937116285575236, 0), (0.90911721139256318, 0.16732208539539251, 0),
                                                     (0.92458015941006, -0.34843743085733436, 0), (0.027431509404153509, -0.43359457401211543, 0),
                                                     (-0.92458015941005645, -0.3111075671233241, 0), (-0.82201559109450617, 0.086251710757499822, 0),
                                                     (-0.80380731394038829, 0.22720474003434532, 0)])
        crv.scale.set(cntrlSize * 0.519, 0.519 * cntrlSize, cntrlSize * 0.519)
        pm.makeIdentity(crv, apply=True, t=1, r=1, s=1, n=0)

    elif icone =='semiCirculoY' or icone =='semiCirculo_Y':
        crv = pm.curve(name=name, per=True, p=[(0.784, 0.784, 0), (0, 1.108, 0), (-0.784, 0.784, 0),
                       (-1.108, 0, 0), (-0.784, 0, 0), (0, 0, 0),(0.784, 0, 0),(1.108, 0, 0),
                       (0.784, 0.784, 0), (0, 1.108, 0), (-0.784, 0.784, 0)],
                        k=[-2, -1, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
        crv.scale.set(cntrlSize*0.491, cntrlSize*0.491, cntrlSize*0.491)
        pm.makeIdentity(crv, apply=True, t=1, r=1, s=1, n=0)

    elif icone =='semiCirculoMenosY':
        crv = pm.curve(name=name, per=True, p=[(0.784, 0.784, 0), (0, 1.108, 0), (-0.784, 0.784, 0),
                       (-1.108, 0, 0), (-0.784, 0, 0), (0, 0, 0),(0.784, 0, 0),(1.108, 0, 0),
                       (0.784, 0.784, 0), (0, 1.108, 0), (-0.784, 0.784, 0)],
                        k=[-2, -1, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
        crv.rotateZ.set(180)
        crv.scale.set(cntrlSize*0.491, cntrlSize*0.491, cntrlSize*0.491)
        pm.makeIdentity(crv, apply=True, t=1, r=1, s=1, n=0)

    elif icone =='semiCirculoX' or icone =='semiCirculo_X':
        crv = pm.curve(name=name, per=True, p=[(0.784, 0.784, 0), (0, 1.108, 0), (-0.784, 0.784, 0),
                       (-1.108, 0, 0), (-0.784, 0, 0), (0, 0, 0),(0.784, 0, 0),(1.108, 0, 0),
                       (0.784, 0.784, 0), (0, 1.108, 0), (-0.784, 0.784, 0)],
                        k=[-2, -1, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
        crv.scale.set(cntrlSize*0.491, cntrlSize*0.491, cntrlSize*0.491)
        crv.rotateZ.set(-90)
        pm.makeIdentity(crv, apply=True, t=1, r=1, s=1, n=0)

    elif icone =='semiCirculoZ' or icone =='semiCirculo_Z':
        crv = pm.curve(name=name, per=True, p=[(0.784, 0.784, 0), (0, 1.108, 0), (-0.784, 0.784, 0),
                       (-1.108, 0, 0), (-0.784, 0, 0), (0, 0, 0),(0.784, 0, 0),(1.108, 0, 0),
                       (0.784, 0.784, 0), (0, 1.108, 0), (-0.784, 0.784, 0)],
                        k=[-2, -1, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
        crv.scale.set(cntrlSize*0.491, cntrlSize*0.491, cntrlSize*0.491)
        crv.rotateX.set(90)
        pm.makeIdentity(crv, apply=True, t=1, r=1, s=1, n=0)

    elif icone =='semiCirculoMenosX':
        crv = pm.curve(name=name, per=True, p=[(0.784, 0.784, 0), (0, 1.108, 0), (-0.784, 0.784, 0),
                       (-1.108, 0, 0), (-0.784, 0, 0), (0, 0, 0),(0.784, 0, 0),(1.108, 0, 0),
                       (0.784, 0.784, 0), (0, 1.108, 0), (-0.784, 0.784, 0)],
                        k=[-2, -1, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
        crv.scale.set(cntrlSize*0.491, cntrlSize*0.491, cntrlSize*0.491)
        crv.rotateZ.set(90)
        pm.makeIdentity(crv, apply=True, t=1, r=1, s=1, n=0)

    elif icone == 'gota':
        crv = pm.circle(nr=[0, 0, 1], r=0.1, n=name, ch=0)[0]
        pm.move(0,.05, 0, crv + ".cv[5]", r=1, ls=1, wd=1)
        pm.move(-.05, 0, 0, crv + ".cv[0]", r=1, ls=1, wd=1)
        pm.move(.05, 0, 0, crv + ".cv[2]", r=1, ls=1, wd=1)
        crv.scale.set(cntrlSize*4.849, cntrlSize*4.849, cntrlSize*4.849)
        pm.makeIdentity(crv, apply=True, t=1, r=1, s=1, n=0)

    elif icone == 'grp':
        crv = pm.group(n=name + cntrlSulfix, em=True)

    elif icone == 'null':
        crv = pm.spaceLocator(n=name + cntrlSulfix, p=(0, 0, 0))
        crv.localScale.set(cntrlSize, cntrlSize, cntrlSize)
        
    else:
        logger.debug('shape nao reconhecido: %s' % icone)
        return

    #display settings
    if hasHandle:
        crv.displayHandle.set(1)

    if localAxis:
        pm.toggle(crv, localAxis=1)

    if template:
        pm.toggle(crv, template=1)

    if hideShape:
        shape = crv.getShape()
        shape.hide()

    if color:
        shList = crv.getShapes()
        if isinstance(color, int):
            for sh in shList:
                sh.overrideRGBColors.set(0)
                sh.overrideEnabled.set(1)
                sh.overrideColor.set(color)

        else:
            for sh in shList:
                sh.overrideEnabled.set(1)
                sh.overrideRGBColors.set(1)
                sh.overrideColorRGB.set(color)

    if lockChannels != []:
        for channel in lockChannels:
            pm.setAttr(crv + '.' + channel, l=1, k=0)
            
    #transform settings
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

    if coords:
        pm.xform(grp, t=coords[0], ro=coords[1], s=coords[2], ws=1)

    if parent:
        grp.setParent(parent)

    #connections settings
    if obj:
        if align == 'point':
            matrix = pm.xform(obj, q=True, ws=True, t=True)
            pm.xform(grp, ws=True, t=matrix)
            pm.makeIdentity(grp, a=False, t=False, r=False, s=True, n=False)  ## garante q a escala nao fique negativa
        elif align == 'pivot':
            pos = pm.xform(obj, q=True, ws=True, rp=True)
            rot = pm.xform(obj, q=True, ws=True, ro=True)
            pm.xform(grp, ws=True, t=pos)
            pm.xform(grp, ws=True, ro=rot)
            pm.makeIdentity(grp, a=False, t=False, r=False, s=True, n=False)  ## garante q a escala nao fique negativa
        else:
            matrix = pm.xform(obj, q=True, ws=True, m=True)
            pm.xform(grp, ws=True, m=matrix)
            pm.makeIdentity(grp, a=False, t=False, r=False, s=True, n=False)  ## garante q a escala nao fique negativa

        if connType == 'parent':
            obj.setParent(crv)
        elif connType == 'parentConstraint':
            cnstr = pm.parentConstraint(crv, obj, mo=True)
        elif connType == 'orientConstraint':
            cnstr = pm.orientConstraint(crv, obj, mo=True)
        elif connType == 'constraint' or connType == 'parentScaleConstraint':
            cnstr = pm.parentConstraint(crv, obj, mo=1)
            scaleConst = pm.scaleConstraint(crv, obj, mo=1)
        elif connType == 'pointConstraint':
            cnstr = pm.pointConstraint(crv, obj, mo=1)
        elif connType == 'scaleConstraint':
            cnstr = pm.scaleConstraint(crv, obj, mo=1)
        elif connType == 'pointOrientConstraint':
            cnstr = pm.pointConstraint(crv, obj, mo=1)
            cnstr = pm.orientConstraint(crv, obj, mo=1)
        elif connType == 'pointScaleConstraint':
            cnstr = pm.pointConstraint(crv, obj, mo=1)
            cnstr = pm.scaleConstraint(crv, obj, mo=1)
        elif connType == 'orientScaleConstraint':
            cnstr = pm.orientConstraint(crv, obj, mo=1)
            cnstr = pm.scaleConstraint(crv, obj, mo=1)
        elif connType == 'connection' or connType == 'connectionTRS':
            crv.tx >> obj.tx
            crv.ty >> obj.ty
            crv.tz >> obj.tz
            crv.rx >> obj.rx
            crv.ry >> obj.ry
            crv.rz >> obj.rz
            crv.sx >> obj.sx
            crv.sy >> obj.sy
            crv.sz >> obj.sz
        elif connType == 'connectionT':
            crv.tx >> obj.tx
            crv.ty >> obj.ty
            crv.tz >> obj.tz
        elif connType == 'connectionR':
            crv.rx >> obj.rx
            crv.ry >> obj.ry
            crv.rz >> obj.rz
        elif connType == 'connectionS':
            crv.sx >> obj.sx
            crv.sy >> obj.sy
            crv.sz >> obj.sz
        elif connType == 'connectionTR':
            crv.tx >> obj.tx
            crv.ty >> obj.ty
            crv.tz >> obj.tz
            crv.rx >> obj.rx
            crv.ry >> obj.ry
            crv.rz >> obj.rz
        elif connType == 'connectionTS':
            crv.tx >> obj.tx
            crv.ty >> obj.ty
            crv.tz >> obj.tz
            crv.sx >> obj.sx
            crv.sy >> obj.sy
            crv.sz >> obj.sz
        elif connType == 'connectionRS':
            crv.rx >> obj.rx
            crv.ry >> obj.ry
            crv.rz >> obj.rz
            crv.sx >> obj.sx
            crv.sy >> obj.sy
            crv.sz >> obj.sz
        elif connType == 'none':
            pass      
    else:
        if posRot:
            grp.setTranslation(posRot[0], space='object')
            grp.setRotation(posRot[1], space='object')

    if returnParent == True:
        returnObj = grp
    else:
        returnObj = crv

    return (returnObj)

def addMultiply(sel=None):
    if not sel:
        sel = pm.ls (sl=True)

    for obj in sel:
        grp = obj.listRelatives(p=True)[0]
        obj = grp.listRelatives(c=True)[0]
        nm=obj.name()
        off=obj.duplicate (n=nm+'Offset')[0]
        shp=off.getShape()
        pm.delete (shp)
        child=off.listRelatives (c=True)
        pm.delete (child)
        pm.parent (obj, off)
        mlt = pm.createNode ('multiplyDivide')
        mlt.input2.set([-1,-1,-1])
        obj.translate >> mlt.input1
        mlt.output >> off.translate

def saveCntrlsShape(objs, path):
    sel = [x for x in objs if '_ctrl' in x.name() and x.nodeType() == 'transform']
    filename = path
    cntrlShapeDict = {}
    for obj in sel:
        tempDict = {}
        for shp in obj.getShapes():
            if pm.nodeType(shp) == 'nurbsCurve':
                pointList = []
                for i in range(len(shp.cv)):
                    pointList.append(pm.pointPosition(shp.cv[i], l=True))
                tempDict[shp.name()] = pointList
        cntrlShapeDict[obj.name()] = tempDict
    with open(filename, 'wb') as f:
        pickle.dump(cntrlShapeDict, f)
    logger.debug('cntrl save ok')

def loadCntrlShape(path):
    cntrlShapeDict = {}
    filename = path
    with open(filename, 'rb') as f:
        cntrlShapeDict = pickle.load(f)
    for obj in cntrlShapeDict:
        for s in cntrlShapeDict[obj]:
            if pm.objExists(s):
                shp = pm.PyNode(s)
                if len(shp.cv) == len(cntrlShapeDict[obj][s]):
                    for i in range(len(shp.cv)):
                        pm.xform(shp.cv[i], t=cntrlShapeDict[obj][s][i])
    logger.debug('cntl load ok')
