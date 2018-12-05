import pymel.core as pm
import os.path
import autoRig3.tools.interface as interface
from autoRig3.modules import limbModule
from autoRig3.modules import handModule
from autoRig3.modules import footModule
from autoRig3.modules import neckModule
from autoRig3.modules import spineModule
from autoRig3.modules import chainModule
from autoRig3.modules import moveAllModule
from autoRig3.modules import ribbonBezier

import autoRig3.tools.rigFunctions as rigFunctions
import json

class Biped:
    def __init__(self, rigName='character',footFingers=[],
                 handFingers=[(u'Thumb', 1), (u'Index', 1), (u'Middle', 1), (u'Ring', 1), (u'Pinky', 1)]):

        self.name = rigName
        self.handFingers = handFingers
        self.footFingers = footFingers
        self.skinJoints = []
        self.modelList = []
        print 'iniciando modulos...'
        self.larm = limbModule.Limb(name='L_arm')
        self.rarm = limbModule.Limb(name='R_arm')
        self.lhand = handModule.Hand(name='L_hand', fingers=self.handFingers)
        self.rhand = handModule.Hand(name='R_hand', fingers=self.handFingers)
        self.lfoot = footModule.Foot(name='L_foot', fingers=self.footFingers)
        self.rfoot = footModule.Foot(name='R_foot', fingers=footFingers)
        self.neck = neckModule.Neck(name='neck')
        self.spine = spineModule.Spine(name='spine')
        self.lclav = chainModule.Chain(name='L_clavicle', divNum=2)
        self.rclav = chainModule.Chain(name='R_clavicle', divNum=2)
        self.lleg = limbModule.Limb(name='L_leg')
        self.rleg = limbModule.Limb(name='R_leg')
        self.llegShoulder = chainModule.Chain(name='L_legShoulder')
        self.rlegShoulder = chainModule.Chain(name='R_legShoulder')
        self.master = moveAllModule.Moveall(name=rigName)
        self.setDefaultDicts()

        handFingerList = [x[0] for x in self.handFingers]
        self.lhand.handDict['fingers'] = {key: value for key, value in self.lhand.handDict['fingers'].iteritems() if key in handFingerList}
        self.rhand.handDict['fingers'] = {key: value for key, value in self.rhand.handDict['fingers'].iteritems() if key in handFingerList}

        footFingerList = [x[0] for x in self.footFingers]
        self.lfoot.footDict['fingers'] = {key: value for key, value in self.lfoot.footDict['fingers'].iteritems() if key in footFingerList}
        self.rfoot.footDict['fingers'] = {key: value for key, value in self.rfoot.footDict['fingers'].iteritems() if key in footFingerList}

    def setDefaultDicts(self):
        print 'gerando guides...'
        larmDict = {
                    'moveallGuideSetup': {'nameTempl': 'L_armMoveAll', 'icone': 'quadradoX', 'color': (1, 1, 0), 'size': 1},
                    'poleVecCntrlSetup': {'nameTempl': 'L_armPoleVec', 'icone': 'bola', 'color': (1, 0, 0),
                                          'size': 0.4},
                    'name': 'L_arm',
                    'axis': 'X',
                    'flipAxis': False,
                    'startJntSetup': {'nameTempl': 'L_armStart', 'size': 1},
                    'endJntSetup': {'nameTempl': 'L_armEnd', 'size': 1},
                    'midJntSetup': {'nameTempl': 'L_armMid', 'size': 1},
                    'lastJoint': True,
                    'lastJntSetup': {'nameTempl': 'L_armLast', 'size': 1},
                    'guideDict': {'start': [(0.0, 0.0, 0.0), (0.0, -0.0, 0.0)],
                                  'moveall': [(2.1300328024310566, 21.041404351843855, 0.0), (0.0, -0.0, 0.0)],
                                  'end': [(6.0, 0.0, 0.0), (0.0, -0.0, 0.0)],
                                  'mid': [(3.0, 0.0, -1.0), (0.0, -0.0, 0.0)],
                                  'last': [(2.0, 0.0, 0.0), (0.0, -0.0, 0.0)]},

                    'startGuideSetup': {'nameTempl': 'L_armStart', 'icone': 'circuloX', 'color': (1, 1, 0), 'size': 1},
                    'midGuideSetup': {'nameTempl': 'L_armMid', 'icone': 'circuloX', 'color': (1, 1, 0), 'size': 1},
                    'endGuideSetup': {'nameTempl': 'L_armEnd', 'icone': 'circuloX', 'color': (1, 1, 0), 'size': 1},
                    'lastGuideSetup': {'nameTempl': 'L_armLast', 'icone': 'circuloX', 'color': (1, 1, 0), 'size': 1},

                    'moveAll1CntrlSetup': {'nameTempl': 'L_armMoveAll', 'icone': 'grp', 'color': (1, 1, 0),
                                           'size': 1.8},
                    'startCntrlSetup': {'nameTempl': 'L_armFkStart', 'icone': 'cubo', 'color': (0, 1, 0), 'size': 1.5},
                    'midCntrlSetup': {'nameTempl': 'L_armFkMid', 'icone': 'cubo', 'color': (0, 1, 0), 'size': 1.5},
                    'endCntrlSetup': {'nameTempl': 'L_armFkEnd', 'icone': 'cubo', 'color': (0, 1, 0), 'size': 1.5},
                    'ikCntrlSetup': {'nameTempl': 'L_armIk', 'icone': 'circuloX', 'color': (1, 0, 0), 'size': 1}
                    }

        rarmDict = {'moveallGuideSetup': {'nameTempl': 'R_armMoveAll', 'icone': 'quadradoX', 'color': (1, 1, 0), 'size': 1},
                    'poleVecCntrlSetup': {'nameTempl': 'R_armPoleVec', 'icone': 'bola', 'color': (1, 0, 0),
                                          'size': 0.4},
                    'name': 'R_arm',
                    'axis': 'X',
                    'flipAxis': False,
                    'startJntSetup': {'nameTempl': 'R_armStart', 'size': 1},
                    'endJntSetup': {'nameTempl': 'R_armEnd', 'size': 1},
                    'midJntSetup': {'nameTempl': 'R_armMid', 'size': 1},
                    'lastJoint': True,
                    'lastJntSetup': {'nameTempl': 'R_armLast', 'size': 1},
                    'guideDict': {'start': [(0.0, 0.0, 0.0), (0.0, -0.0, 0.0)],
                                  'moveall': [(2.1300328024310566, 21.041404351843855, 0.0), (0.0, -0.0, 0.0)],
                                  'end': [(6.0, 0.0, 0.0), (0.0, -0.0, 0.0)],
                                  'mid': [(3.0, 0.0, -1.0), (0.0, -0.0, 0.0)],
                                  'last': [(2.0, 0.0, 0.0), (0.0, -0.0, 0.0)]},

                    'startGuideSetup': {'nameTempl': 'R_armStart', 'icone': 'circuloX', 'color': (1, 1, 0), 'size': 1},
                    'midGuideSetup': {'nameTempl': 'R_armMid', 'icone': 'circuloX', 'color': (1, 1, 0), 'size': 1},
                    'endGuideSetup': {'nameTempl': 'R_armEnd', 'icone': 'circuloX', 'color': (1, 1, 0), 'size': 1},
                    'lastGuideSetup': {'nameTempl': 'R_armLast', 'icone': 'circuloX', 'color': (1, 1, 0), 'size': 1},

                    'moveAll1CntrlSetup': {'nameTempl': 'R_armMoveAll', 'icone': 'grp', 'color': (1, 1, 0),
                                           'size': 1.8},
                    'startCntrlSetup': {'nameTempl': 'R_armFkStart', 'icone': 'cubo', 'color': (0, 1, 0), 'size': 1.5},
                    'midCntrlSetup': {'nameTempl': 'R_armFkMid', 'icone': 'cubo', 'color': (0, 1, 0), 'size': 1.5},
                    'endCntrlSetup': {'nameTempl': 'R_armFkEnd', 'icone': 'cubo', 'color': (0, 1, 0), 'size': 1.5},
                    'ikCntrlSetup': {'nameTempl': 'R_armIk', 'icone': 'circuloX', 'color': (1, 0, 0), 'size': 1}
                    }

        llegDict = {'name': 'L_leg',

                    'guideDict': {'start': [(0.0, 0.0, 0.0), (0.0, -0.0, 0.0)],
                                  'moveall': [(1.7596195990307493, 10.083546821207758, 0.0),
                                              (0.0, 0.0, -89.99999999999999)],
                                  'end': [(8.994202200049429, -2.2204460492503136e-16, 0.0), (0.0, -0.0, 0.0)],
                                  'mid': [(4.84264286826042, 0.0, 0.2978602780352708), (0.0, -0.0, 0.0)],
                                  'last': [(1.0, 0.0, 0.0), (0.0, -0.0, 0.0)]},

                    'moveallGuideSetup': {'nameTempl': 'L_legMoveAll','icone': 'circuloX', 'color': (1, 1, 0), 'size': 1},
                    'startGuideSetup': {'nameTempl': 'L_legStart','icone': 'circuloX', 'color': (1, 1, 0), 'size': 1},
                    'midGuideSetup': {'nameTempl': 'L_legMid','icone': 'circuloX', 'color': (1, 1, 0), 'size': 1},
                    'endGuideSetup': {'nameTempl': 'L_legEnd','icone': 'circuloX', 'color': (1, 1, 0), 'size': 1},
                    'lastGuideSetup': {'nameTempl': 'L_legLast','icone': 'circuloX', 'color': (1, 1, 0), 'size': 1},

                    'startJntSetup': {'nameTempl': 'L_legStart', 'size': 1},
                    'midJntSetup': {'nameTempl': 'L_legMid', 'size': 1},
                    'endJntSetup': {'nameTempl': 'L_legEnd', 'size': 1},
                    'lastJntSetup': {'nameTempl': 'L_legLast', 'size': 1},
                    'flipAxis': False,

                    'poleVecCntrlSetup': {'nameTempl': 'L_legPoleVec', 'icone': 'bola', 'color': (1, 0, 0),                                          'size': 0.4},
                    'moveAll1CntrlSetup': {'nameTempl': 'L_legMoveAll', 'icone': 'grp', 'color': (1, 1, 0),                                           'size': 1.8},
                    'ikCntrlSetup': {'nameTempl': 'L_footIk', 'icone': 'grp', 'color': (1, 1, 0), 'size': 0.8},
                    'startCntrlSetup': {'nameTempl': 'L_legFkStart', 'icone': 'cubo', 'color': (0, 1, 0),                                        'size': 1.5},
                    'midCntrlSetup': {'nameTempl': 'L_legFkMid', 'icone': 'cubo', 'color': (0, 1, 0), 'size': 1.5},
                    'endCntrlSetup': {'nameTempl': 'L_legFkEnd', 'icone': 'cubo', 'color': (0, 1, 0), 'size': 1.5},
                    'axis': 'X'}

        rlegDict = {'name': 'R_leg',

                    'guideDict': {'start': [(0.0, 0.0, 0.0), (0.0, -0.0, 0.0)],
                                  'moveall': [(1.7596195990307493, 10.083546821207758, 0.0),
                                              (0.0, 0.0, -89.99999999999999)],
                                  'end': [(8.994202200049429, -2.2204460492503136e-16, 0.0), (0.0, -0.0, 0.0)],
                                  'mid': [(4.84264286826042, 0.0, 0.2978602780352708), (0.0, -0.0, 0.0)],
                                  'last': [(1.0, 0.0, 0.0), (0.0, -0.0, 0.0)]},

                    'moveallGuideSetup': {'nameTempl': 'R_legMoveAll','icone': 'circuloX', 'color': (1, 1, 0), 'size': 1},
                    'startGuideSetup': {'nameTempl': 'R_legStart','icone': 'circuloX', 'color': (1, 1, 0), 'size': 1},
                    'midGuideSetup': {'nameTempl': 'R_legMid','icone': 'circuloX', 'color': (1, 1, 0), 'size': 1},
                    'endGuideSetup': {'nameTempl': 'R_legEnd','icone': 'circuloX', 'color': (1, 1, 0), 'size': 1},
                    'lastGuideSetup': {'nameTempl': 'R_legLast','icone': 'circuloX', 'color': (1, 1, 0), 'size': 1},

                    'startJntSetup': {'nameTempl': 'R_legStart', 'size': 1},
                    'midJntSetup': {'nameTempl': 'R_legMid', 'size': 1},
                    'endJntSetup': {'nameTempl': 'R_legEnd', 'size': 1},
                    'lastJntSetup': {'nameTempl': 'R_legLast', 'size': 1},
                    'flipAxis': False,
                    'poleVecCntrlSetup': {'nameTempl': 'R_legPoleVec', 'icone': 'bola', 'color': (1, 0, 0),
                                          'size': 0.4},
                    'moveAll1CntrlSetup': {'nameTempl': 'R_legMoveAll', 'icone': 'grp', 'color': (1, 1, 0),
                                           'size': 1.8},
                    'ikCntrlSetup': {'nameTempl': 'L_footIk', 'icone': 'grp', 'color': (1, 1, 0), 'size': 0.8},
                    'startCntrlSetup': {'nameTempl': 'R_legFkStart', 'icone': 'cubo', 'color': (0, 1, 0),
                                        'size': 1.5},
                    'midCntrlSetup': {'nameTempl': 'R_legFkMid', 'icone': 'cubo', 'color': (0, 1, 0), 'size': 1.5},
                    'endCntrlSetup': {'nameTempl': 'R_legFkEnd', 'icone': 'cubo', 'color': (0, 1, 0), 'size': 1.5},

                    'axis': 'X'}

        rhandDict = {
                        'Ring': {'finger4': {
                                    'fold2CntrlSetup': {'nameTempl': u'R_handRingfold2', 'icone': 'circuloX', 'color': (0, 1, 1),
                                                        'size': 0.3},
                                    'folds': 2,
                                    'moveallCntrlSetup': {'nameTempl': u'R_handRingMoveAll', 'icone': 'circuloX', 'color': (1, 1, 0),
                                                          'size': 0.1},
                                    'tipGuideSetup': {'nameTempl': u'R_handRingtip', 'color': (0, 1, 1), 'size': 0.3},
                                    'fold1GuideSetup': {'nameTempl': u'R_handRingfold1', 'color': (0, 1, 1), 'size': 0.3},
                                    'fold2JntSetup': {'nameTempl': u'R_handRingFold2', 'icone': 'Bone', 'size': 0.3},
                                    'fold2GuideSetup': {'nameTempl': u'R_handRingfold2', 'color': (0, 1, 1), 'size': 0.3},
                                    'axis': 'X',
                                    'fold1JntSetup': {'nameTempl': u'R_handRingFold1', 'icone': 'Bone', 'size': 0.3},
                                    'palmJntSetup': {'nameTempl': u'R_handRingPalm', 'icone': 'Bone', 'size': 0.2},
                                    'palmCntrlSetup': {'nameTempl': u'R_handRingpalm', 'icone': 'cubo', 'color': (1, 0, 0), 'size': 0.2},
                                    'tipJntSetup': {'nameTempl': u'R_handRing', 'icone': 'Bone', 'size': 0.3},
                                    'palmGuideSetup': {'nameTempl': u'R_handRingpalm', 'color': (1, 0, 0), 'size': 0.2},
                                    'guideDict': {
                                                    'moveall': [(0, 0, -0.25), (0.0, -0.0, 0.0)],
                                                    'palm': [(0.0, 0.0, 0.0), (0.0, -0.0, 0.0)],
                                                    'base': [(1.0, 0.0, 0.0), (0.0, -0.0, 7.1)],
                                                    'fold2': [(0.0, 0.0, 0.0), (0.0, -0.0, 0.0)],
                                                    'fold1': [(0.0, 0.05, 0.0), (0.0, 0.0, -4.7)],
                                                    'tip': [(2.0, 0.0, 0.0), (0.0, 0.0, -4.7)]},
                                    'baseJntSetup': {'nameTempl': u'R_handRingBase', 'icone': 'Bone', 'size': 0.3},
                                    'baseGuideSetup': {'nameTempl': u'R_handRingbase', 'color': (1, 1, 0), 'size': 0.3},
                                    'moveallGuideSetup': {'nameTempl': u'R_handRingMoveAll', 'color': (1, 1, 0), 'size': 0.1},
                                    'name': u'R_handRing',
                                    'baseCntrlSetup': {'nameTempl': u'R_handRingbase', 'icone': 'dropMenosZ', 'color': (1, 1, 0),
                                                       'size': 0.1},
                                    'fold1CntrlSetup': {'nameTempl': u'R_handRingfold1', 'icone': 'circuloX', 'color': (0, 1, 1),
                                                        'size': 0.3},
                                    'flipAxis': False},

                        'Pinky': {'fold2CntrlSetup': {'nameTempl': u'R_handPinkyfold2', 'icone': 'circuloX',
                                                        'color': (0, 1, 1), 'size': 0.3},
                                    'folds': 2,
                                    'moveallCntrlSetup': {'nameTempl': u'R_handPinkyMoveAll', 'icone': 'circuloX',
                                                          'color': (1, 1, 0), 'size': 0.1},
                                    'tipGuideSetup': {'nameTempl': u'R_handPinkytip', 'color': (0, 1, 1), 'size': 0.3},
                                    'fold1GuideSetup': {'nameTempl': u'R_handPinkyfold1', 'color': (0, 1, 1),
                                                        'size': 0.3},
                                    'fold2JntSetup': {'nameTempl': u'R_handPinkyFold2', 'icone': 'Bone', 'size': 0.3},
                                    'fold2GuideSetup': {'nameTempl': u'R_handPinkyfold2', 'color': (0, 1, 1),
                                                        'size': 0.3},
                                    'axis': 'X',
                                    'fold1JntSetup': {'nameTempl': u'R_handPinkyFold1', 'icone': 'Bone', 'size': 0.3},
                                    'palmJntSetup': {'nameTempl': u'R_handPinkyPalm', 'icone': 'Bone', 'size': 0.2},
                                    'palmCntrlSetup': {'nameTempl': u'R_handPinkypalm', 'icone': 'cubo',
                                                       'color': (1, 0, 0), 'size': 0.2},
                                    'tipJntSetup': {'nameTempl': u'R_handPinky', 'icone': 'Bone', 'size': 0.3},
                                    'palmGuideSetup': {'nameTempl': u'R_handPinkypalm', 'color': (1, 0, 0),
                                                       'size': 0.2},
                                    'guideDict': {
                                                    'moveall': [(0, 0, -0.75), (0.0, 0, 0.0)],
                                                    'palm': [(0.0, 0.0, 0.0), (0.0, -0.0, 0.0)],
                                                    'base': [(1.0, 0.0, 0.0), (0.0, -0.0, 7.12)],
                                                    'fold2': [(0.0, 0.0, 0.0), (0.0, -0.0, 0.0)],
                                                    'fold1': [(0.0, 0.05, 0.0), (0.0, 0.0, -4.76)],
                                                    'tip': [(2.0, 0.0, 0.0), (0.0, 0.0, -4.76)]},
                                    'baseJntSetup': {'nameTempl': u'R_handPinkyBase', 'icone': 'Bone', 'size': 0.3},
                                    'baseGuideSetup': {'nameTempl': u'R_handPinkybase', 'color': (1, 1, 0),
                                                       'size': 0.3},
                                    'moveallGuideSetup': {'nameTempl': u'R_handPinkyMoveAll', 'color': (1, 1, 0),
                                                          'size': 0.1},
                                    'name': u'R_handPinky',
                                    'baseCntrlSetup': {'nameTempl': u'R_handPinkybase', 'icone': 'dropMenosZ',
                                                       'color': (1, 1, 0), 'size': 0.1},
                                    'fold1CntrlSetup': {'nameTempl': u'R_handPinkyfold1', 'icone': 'circuloX',
                                                        'color': (0, 1, 1), 'size': 0.3},
                                    'flipAxis': False},

                        'Index': {'fold2CntrlSetup': {'nameTempl': u'R_handIndexfold2', 'icone': 'circuloX',
                                                        'color': (0, 1, 1), 'size': 0.3},
                                    'folds': 2,
                                    'moveallCntrlSetup': {'nameTempl': u'R_handIndexMoveAll', 'icone': 'circuloX',
                                                          'color': (1, 1, 0), 'size': 0.1},
                                    'tipGuideSetup': {'nameTempl': u'R_handIndextip', 'color': (0, 1, 1), 'size': 0.3},
                                    'fold1GuideSetup': {'nameTempl': u'R_handIndexfold1', 'color': (0, 1, 1),
                                                        'size': 0.3},
                                    'fold2JntSetup': {'nameTempl': u'R_handIndexFold2', 'icone': 'Bone', 'size': 0.3},
                                    'fold2GuideSetup': {'nameTempl': u'R_handIndexfold2', 'color': (0, 1, 1),
                                                        'size': 0.3},
                                    'axis': 'X',
                                    'fold1JntSetup': {'nameTempl': u'R_handIndexFold1', 'icone': 'Bone', 'size': 0.3},
                                    'palmJntSetup': {'nameTempl': u'R_handIndexPalm', 'icone': 'Bone', 'size': 0.2},
                                    'palmCntrlSetup': {'nameTempl': u'R_handIndexpalm', 'icone': 'cubo',
                                                       'color': (1, 0, 0), 'size': 0.2},
                                    'tipJntSetup': {'nameTempl': u'R_handIndex', 'icone': 'Bone', 'size': 0.3},
                                    'palmGuideSetup': {'nameTempl': u'R_handIndexpalm', 'color': (1, 0, 0),
                                                       'size': 0.2},
                                    'guideDict': {
                                                    'moveall': [(0.0, 0.0, 0.75), (0.0, 0.0, 0.0)],
                                                    'palm': [(0.0, 0.0, 0.0), (0.0, -0.0, 0.0)],
                                                    'base': [(1.0, 0.0, 0.0), (0.0, -0.0, 7.12)],
                                                    'fold2': [(0.0, 0.0, 0.0), (0.0, -0.0, 0.0)],
                                                    'fold1': [(0.0, 0.05, 0.0), (0.0, 0.0, -4.76)],
                                                    'tip': [(2.0, 0.0, 0.0), (0.0, 0.0, -4.76)]},
                                    'baseJntSetup': {'nameTempl': u'R_handIndexBase', 'icone': 'Bone', 'size': 0.3},
                                    'baseGuideSetup': {'nameTempl': u'R_handIndexbase', 'color': (1, 1, 0),
                                                       'size': 0.3},
                                    'moveallGuideSetup': {'nameTempl': u'R_handIndexMoveAll', 'color': (1, 1, 0),
                                                          'size': 0.1},
                                    'name': u'R_handIndex',
                                    'baseCntrlSetup': {'nameTempl': u'R_handIndexbase', 'icone': 'dropMenosZ',
                                                       'color': (1, 1, 0), 'size': 0.1},
                                    'fold1CntrlSetup': {'nameTempl': u'R_handIndexfold1', 'icone': 'circuloX',
                                                        'color': (0, 1, 1), 'size': 0.3},
                                    'flipAxis': False},

                        'Middle': {'fold2CntrlSetup': {'nameTempl': u'R_handMiddlefold2', 'icone': 'circuloX',
                                                        'color': (0, 1, 1), 'size': 0.3}, 'folds': 2,
                                    'moveallCntrlSetup': {'nameTempl': u'R_handMiddleMoveAll', 'icone': 'circuloX',
                                                          'color': (1, 1, 0), 'size': 0.1},
                                    'tipGuideSetup': {'nameTempl': u'R_handMiddletip', 'color': (0, 1, 1), 'size': 0.3},
                                    'fold1GuideSetup': {'nameTempl': u'R_handMiddlefold1', 'color': (0, 1, 1),
                                                        'size': 0.3},
                                    'fold2JntSetup': {'nameTempl': u'R_handMiddleFold2', 'icone': 'Bone', 'size': 0.3},
                                    'fold2GuideSetup': {'nameTempl': u'R_handMiddlefold2', 'color': (0, 1, 1),
                                                        'size': 0.3}, 'axis': 'X',
                                    'fold1JntSetup': {'nameTempl': u'R_handMiddleFold1', 'icone': 'Bone', 'size': 0.3},
                                    'palmJntSetup': {'nameTempl': u'R_handMiddlePalm', 'icone': 'Bone', 'size': 0.2},
                                    'palmCntrlSetup': {'nameTempl': u'R_handMiddlepalm', 'icone': 'cubo',
                                                       'color': (1, 0, 0), 'size': 0.2},
                                    'tipJntSetup': {'nameTempl': u'R_handMiddle', 'icone': 'Bone', 'size': 0.3},
                                    'palmGuideSetup': {'nameTempl': u'R_handMiddlepalm', 'color': (1, 0, 0),
                                                       'size': 0.2},
                                    'guideDict': {
                                                    'moveall': [(0.0, 0.0, 0.25), (0.0, 0.0, 0.0)],
                                                    'palm': [(0.0, 0.0, 0.0), (0.0, -0.0, 0.0)],
                                                    'base': [(1.0, 0.0, 0.0), (0.0, -0.0, 7.12)],
                                                    'fold2': [(0.0, 0.0, 0.0), (0.0, -0.0, 0.0)],
                                                    'fold1': [(0.0, 0.05, 0.0), (0.0, 0.0, -4.76)],
                                                    'tip': [(2.0, 0.0, 0.0), (0.0, 0.0, -4.76)]},
                                    'baseJntSetup': {'nameTempl': u'R_handMiddleBase', 'icone': 'Bone', 'size': 0.3},
                                    'baseGuideSetup': {'nameTempl': u'R_handMiddlebase', 'color': (1, 1, 0),
                                                       'size': 0.3},
                                    'moveallGuideSetup': {'nameTempl': u'R_handMiddleMoveAll', 'color': (1, 1, 0),
                                                          'size': 0.1}, 'name': u'R_handMiddle',
                                    'baseCntrlSetup': {'nameTempl': u'R_handMiddlebase', 'icone': 'dropMenosZ',
                                                       'color': (1, 1, 0), 'size': 0.1},
                                    'fold1CntrlSetup': {'nameTempl': u'R_handMiddlefold1', 'icone': 'circuloX',
                                                        'color': (0, 1, 1), 'size': 0.3}, 'flipAxis': False},
                        'Thumb': {'fold2CntrlSetup': {'nameTempl': u'R_handThumbfold2', 'icone': 'circuloX',
                                                        'color': (0, 1, 1), 'size': 0.3},
                                    'folds': 1,
                                    'moveallCntrlSetup': {'nameTempl': u'R_handThumbMoveAll', 'icone': 'circuloX',
                                                          'color': (1, 1, 0), 'size': 0.1},
                                    'tipGuideSetup': {'nameTempl': u'R_handThumbtip', 'color': (0, 1, 1), 'size': 0.3},
                                    'fold1GuideSetup': {'nameTempl': u'R_handThumbfold1', 'color': (0, 1, 1),
                                                        'size': 0.3},
                                    'fold2JntSetup': {'nameTempl': u'R_handThumbFold2', 'icone': 'Bone', 'size': 0.3},
                                    'fold2GuideSetup': {'nameTempl': u'R_handThumbfold2', 'color': (0, 1, 1),
                                                        'size': 0.3}, 'axis': 'X',
                                    'fold1JntSetup': {'nameTempl': u'R_handThumbFold1', 'icone': 'Bone', 'size': 0.3},
                                    'palmJntSetup': {'nameTempl': u'R_handThumbPalm', 'icone': 'Bone', 'size': 0.2},
                                    'palmCntrlSetup': {'nameTempl': u'R_handThumbpalm', 'icone': 'cubo',
                                                       'color': (1, 0, 0), 'size': 0.2},
                                    'tipJntSetup': {'nameTempl': u'R_handThumb', 'icone': 'Bone', 'size': 0.3},
                                    'palmGuideSetup': {'nameTempl': u'R_handThumbpalm', 'color': (1, 0, 0),
                                                       'size': 0.2},
                                    'guideDict': {
                                                    'moveall': [(0.0, -0.5, 1.0), (0.0, 0.0, 0.0)],
                                                    'palm': [(0.0, 0.0, 0.0), (0.0, 0.0, 0.0)],
                                                    'base': [(0.0, 0.0, -0),(0.0, 0.0, 7.12)],
                                                    'fold2': [(0, 0, 0), (0, 0, 0)],
                                                    'fold1': [(0.0, 0.05, 0.0), (0.0, 0.0, -4.76)],
                                                    'tip': [(2.0, 0.0, 0.0), (0.0,0.0, 0.0)]},
                                    'baseJntSetup': {'nameTempl': u'R_handThumbBase        self.setDefaultDicts()', 'icone': 'Bone', 'size': 0.3},
                                    'baseGuideSetup': {'nameTempl': u'R_handThumbbase', 'color': (1, 1, 0),
                                                       'size': 0.3},
                                    'moveallGuideSetup': {'nameTempl': u'R_handThumbMoveAll', 'color': (1, 1, 0),
                                                          'size': 0.1},
                                    'name': u'R_handThumb',
                                    'baseCntrlSetup': {'nameTempl': u'R_handThumbbase', 'icone': 'dropMenosZ',
                                                       'color': (1, 1, 0), 'size': 0.1},
                                    'fold1CntrlSetup': {'nameTempl': u'R_handThumbfold1', 'icone': 'circuloX',
                                                        'color': (0, 1, 1), 'size': 0.3}, 'flipAxis': False}},
            'flipAxis': False, 'name': 'R_hand',
            'guideDict': {'moveall': [(8.130032802431057, 21.041404351843855, 0.0), (0.0, 0.0, 0.0)]}, 'axis': 'X'}

        lhandDict = {
            'fingers': {'Ring': {
                                    'fold2CntrlSetup': {'nameTempl': u'L_handRingfold2', 'icone': 'circuloX', 'color': (0, 1, 1),
                                                        'size': 0.3},
                                    'folds': 2,
                                    'moveallCntrlSetup': {'nameTempl': u'L_handRingMoveAll', 'icone': 'circuloX', 'color': (1, 1, 0),
                                                          'size': 0.1},
                                    'tipGuideSetup': {'nameTempl': u'L_handRingtip', 'color': (0, 1, 1), 'size': 0.3},
                                    'fold1GuideSetup': {'nameTempl': u'L_handRingfold1', 'color': (0, 1, 1), 'size': 0.3},
                                    'fold2JntSetup': {'nameTempl': u'L_handRingFold2', 'icone': 'Bone', 'size': 0.3},
                                    'fold2GuideSetup': {'nameTempl': u'L_handRingfold2', 'color': (0, 1, 1), 'size': 0.3},
                                    'axis': 'X',
                                    'fold1JntSetup': {'nameTempl': u'L_handRingFold1', 'icone': 'Bone', 'size': 0.3},
                                    'palmJntSetup': {'nameTempl': u'L_handRingPalm', 'icone': 'Bone', 'size': 0.2},
                                    'palmCntrlSetup': {'nameTempl': u'L_handRingpalm', 'icone': 'cubo', 'color': (1, 0, 0), 'size': 0.2},
                                    'tipJntSetup': {'nameTempl': u'L_handRing', 'icone': 'Bone', 'size': 0.3},
                                    'palmGuideSetup': {'nameTempl': u'L_handRingpalm', 'color': (1, 0, 0), 'size': 0.2},
                                    'guideDict': {
                                                    'moveall': [(0, 0, -0.25), (0.0, -0.0, 0.0)],
                                                    'palm': [(0.0, 0.0, 0.0), (0.0, -0.0, 0.0)],
                                                    'base': [(1.0, 0.0, 0.0), (0.0, -0.0, 7.1)],
                                                    'fold2': [(0.0, 0.0, 0.0), (0.0, -0.0, 0.0)],
                                                    'fold1': [(0.0, 0.05, 0.0), (0.0, 0.0, -4.7)],
                                                    'tip': [(2.0, 0.0, 0.0), (0.0, 0.0, -4.7)]},
                                    'baseJntSetup': {'nameTempl': u'L_handRingBase', 'icone': 'Bone', 'size': 0.3},
                                    'baseGuideSetup': {'nameTempl': u'L_handRingbase', 'color': (1, 1, 0), 'size': 0.3},
                                    'moveallGuideSetup': {'nameTempl': u'L_handRingMoveAll', 'color': (1, 1, 0), 'size': 0.1},
                                    'name': u'L_handRing',
                                    'baseCntrlSetup': {'nameTempl': u'L_handRingbase', 'icone': 'dropMenosZ', 'color': (1, 1, 0),
                                                       'size': 0.1},
                                    'fold1CntrlSetup': {'nameTempl': u'L_handRingfold1', 'icone': 'circuloX', 'color': (0, 1, 1),
                                                        'size': 0.3},
                                    'flipAxis': False},

                        'Pinky': {'fold2CntrlSetup': {'nameTempl': u'L_handPinkyfold2', 'icone': 'circuloX',
                                                        'color': (0, 1, 1), 'size': 0.3},
                                    'folds': 2,
                                    'moveallCntrlSetup': {'nameTempl': u'L_handPinkyMoveAll', 'icone': 'circuloX',
                                                          'color': (1, 1, 0), 'size': 0.1},
                                    'tipGuideSetup': {'nameTempl': u'L_handPinkytip', 'color': (0, 1, 1), 'size': 0.3},
                                    'fold1GuideSetup': {'nameTempl': u'L_handPinkyfold1', 'color': (0, 1, 1),
                                                        'size': 0.3},
                                    'fold2JntSetup': {'nameTempl': u'L_handPinkyFold2', 'icone': 'Bone', 'size': 0.3},
                                    'fold2GuideSetup': {'nameTempl': u'L_handPinkyfold2', 'color': (0, 1, 1),
                                                        'size': 0.3},
                                    'axis': 'X',
                                    'fold1JntSetup': {'nameTempl': u'L_handPinkyFold1', 'icone': 'Bone', 'size': 0.3},
                                    'palmJntSetup': {'nameTempl': u'L_handPinkyPalm', 'icone': 'Bone', 'size': 0.2},
                                    'palmCntrlSetup': {'nameTempl': u'L_handPinkypalm', 'icone': 'cubo',
                                                       'color': (1, 0, 0), 'size': 0.2},
                                    'tipJntSetup': {'nameTempl': u'L_handPinky', 'icone': 'Bone', 'size': 0.3},
                                    'palmGuideSetup': {'nameTempl': u'L_handPinkypalm', 'color': (1, 0, 0),
                                                       'size': 0.2},
                                    'guideDict': {
                                                    'moveall': [(0, 0, -0.75), (0.0, 0, 0.0)],
                                                    'palm': [(0.0, 0.0, 0.0), (0.0, -0.0, 0.0)],
                                                    'base': [(1.0, 0.0, 0.0), (0.0, -0.0, 7.12)],
                                                    'fold2': [(0.0, 0.0, 0.0), (0.0, -0.0, 0.0)],
                                                    'fold1': [(0.0, 0.05, 0.0), (0.0, 0.0, -4.76)],
                                                    'tip': [(2.0, 0.0, 0.0), (0.0, 0.0, -4.76)]},
                                    'baseJntSetup': {'nameTempl': u'L_handPinkyBase', 'icone': 'Bone', 'size': 0.3},
                                    'baseGuideSetup': {'nameTempl': u'L_handPinkybase', 'color': (1, 1, 0),
                                                       'size': 0.3},
                                    'moveallGuideSetup': {'nameTempl': u'L_handPinkyMoveAll', 'color': (1, 1, 0),
                                                          'size': 0.1},
                                    'name': u'L_handPinky',
                                    'baseCntrlSetup': {'nameTempl': u'L_handPinkybase', 'icone': 'dropMenosZ',
                                                       'color': (1, 1, 0), 'size': 0.1},
                                    'fold1CntrlSetup': {'nameTempl': u'L_handPinkyfold1', 'icone': 'circuloX',
                                                        'color': (0, 1, 1), 'size': 0.3},
                                    'flipAxis': False},

                        'Index': {'fold2CntrlSetup': {'nameTempl': u'L_handIndexfold2', 'icone': 'circuloX',
                                                        'color': (0, 1, 1), 'size': 0.3},
                                    'folds': 2,
                                    'moveallCntrlSetup': {'nameTempl': u'L_handIndexMoveAll', 'icone': 'circuloX',
                                                          'color': (1, 1, 0), 'size': 0.1},
                                    'tipGuideSetup': {'nameTempl': u'L_handIndextip', 'color': (0, 1, 1), 'size': 0.3},
                                    'fold1GuideSetup': {'nameTempl': u'L_handIndexfold1', 'color': (0, 1, 1),
                                                        'size': 0.3},
                                    'fold2JntSetup': {'nameTempl': u'L_handIndexFold2', 'icone': 'Bone', 'size': 0.3},
                                    'fold2GuideSetup': {'nameTempl': u'L_handIndexfold2', 'color': (0, 1, 1),
                                                        'size': 0.3},
                                    'axis': 'X',
                                    'fold1JntSetup': {'nameTempl': u'L_handIndexFold1', 'icone': 'Bone', 'size': 0.3},
                                    'palmJntSetup': {'nameTempl': u'L_handIndexPalm', 'icone': 'Bone', 'size': 0.2},
                                    'palmCntrlSetup': {'nameTempl': u'L_handIndexpalm', 'icone': 'cubo',
                                                       'color': (1, 0, 0), 'size': 0.2},
                                    'tipJntSetup': {'nameTempl': u'L_handIndex', 'icone': 'Bone', 'size': 0.3},
                                    'palmGuideSetup': {'nameTempl': u'L_handIndexpalm', 'color': (1, 0, 0),
                                                       'size': 0.2},
                                    'guideDict': {
                                                    'moveall': [(0.0, 0.0, 0.75), (0.0, 0.0, 0.0)],
                                                    'palm': [(0.0, 0.0, 0.0), (0.0, -0.0, 0.0)],
                                                    'base': [(1.0, 0.0, 0.0), (0.0, -0.0, 7.12)],
                                                    'fold2': [(0.0, 0.0, 0.0), (0.0, -0.0, 0.0)],
                                                    'fold1': [(0.0, 0.05, 0.0), (0.0, 0.0, -4.76)],
                                                    'tip': [(2.0, 0.0, 0.0), (0.0, 0.0, -4.76)]},
                                    'baseJntSetup': {'nameTempl': u'L_handIndexBase', 'icone': 'Bone', 'size': 0.3},
                                    'baseGuideSetup': {'nameTempl': u'L_handIndexbase', 'color': (1, 1, 0),
                                                       'size': 0.3},
                                    'moveallGuideSetup': {'nameTempl': u'L_handIndexMoveAll', 'color': (1, 1, 0),
                                                          'size': 0.1},
                                    'name': u'L_handIndex',
                                    'baseCntrlSetup': {'nameTempl': u'L_handIndexbase', 'icone': 'dropMenosZ',
                                                       'color': (1, 1, 0), 'size': 0.1},
                                    'fold1CntrlSetup': {'nameTempl': u'L_handIndexfold1', 'icone': 'circuloX',
                                                        'color': (0, 1, 1), 'size': 0.3},
                                    'flipAxis': False},

                        'Middle': {'fold2CntrlSetup': {'nameTempl': u'L_handMiddlefold2', 'icone': 'circuloX',
                                                        'color': (0, 1, 1), 'size': 0.3}, 'folds': 2,
                                    'moveallCntrlSetup': {'nameTempl': u'L_handMiddleMoveAll', 'icone': 'circuloX',
                                                          'color': (1, 1, 0), 'size': 0.1},
                                    'tipGuideSetup': {'nameTempl': u'L_handMiddletip', 'color': (0, 1, 1), 'size': 0.3},
                                    'fold1GuideSetup': {'nameTempl': u'L_handMiddlefold1', 'color': (0, 1, 1),
                                                        'size': 0.3},
                                    'fold2JntSetup': {'nameTempl': u'L_handMiddleFold2', 'icone': 'Bone', 'size': 0.3},
                                    'fold2GuideSetup': {'nameTempl': u'L_handMiddlefold2', 'color': (0, 1, 1),
                                                        'size': 0.3}, 'axis': 'X',
                                    'fold1JntSetup': {'nameTempl': u'L_handMiddleFold1', 'icone': 'Bone', 'size': 0.3},
                                    'palmJntSetup': {'nameTempl': u'L_handMiddlePalm', 'icone': 'Bone', 'size': 0.2},
                                    'palmCntrlSetup': {'nameTempl': u'L_handMiddlepalm', 'icone': 'cubo',
                                                       'color': (1, 0, 0), 'size': 0.2},
                                    'tipJntSetup': {'nameTempl': u'L_handMiddle', 'icone': 'Bone', 'size': 0.3},
                                    'palmGuideSetup': {'nameTempl': u'L_handMiddlepalm', 'color': (1, 0, 0),
                                                       'size': 0.2},
                                    'guideDict': {
                                                    'moveall': [(0.0, 0.0, 0.25), (0.0, 0.0, 0.0)],
                                                    'palm': [(0.0, 0.0, 0.0), (0.0, -0.0, 0.0)],
                                                    'base': [(1.0, 0.0, 0.0), (0.0, -0.0, 7.12)],
                                                    'fold2': [(0.0, 0.0, 0.0), (0.0, -0.0, 0.0)],
                                                    'fold1': [(0.0, 0.05, 0.0), (0.0, 0.0, -4.76)],
                                                    'tip': [(2.0, 0.0, 0.0), (0.0, 0.0, -4.76)]},
                                    'baseJntSetup': {'nameTempl': u'L_handMiddleBase', 'icone': 'Bone', 'size': 0.3},
                                    'baseGuideSetup': {'nameTempl': u'L_handMiddlebase', 'color': (1, 1, 0),
                                                       'size': 0.3},
                                    'moveallGuideSetup': {'nameTempl': u'L_handMiddleMoveAll', 'color': (1, 1, 0),
                                                          'size': 0.1}, 'name': u'L_handMiddle',
                                    'baseCntrlSetup': {'nameTempl': u'L_handMiddlebase', 'icone': 'dropMenosZ',
                                                       'color': (1, 1, 0), 'size': 0.1},
                                    'fold1CntrlSetup': {'nameTempl': u'L_handMiddlefold1', 'icone': 'circuloX',
                                                        'color': (0, 1, 1), 'size': 0.3}, 'flipAxis': False},

                        'Thumb': {'fold2CntrlSetup': {'nameTempl': u'L_handThumbfold2', 'icone': 'circuloX',
                                                        'color': (0, 1, 1), 'size': 0.3}, 'folds': 1,
                                    'moveallCntrlSetup': {'nameTempl': u'L_handThumbMoveAll', 'icone': 'circuloX',
                                                          'color': (1, 1, 0), 'size': 0.1},
                                    'tipGuideSetup': {'nameTempl': u'L_handThumbtip', 'color': (0, 1, 1), 'size': 0.3},
                                    'fold1GuideSetup': {'nameTempl': u'L_handThumbfold1', 'color': (0, 1, 1),
                                                        'size': 0.3},
                                    'fold2JntSetup': {'nameTempl': u'L_handThumbFold2', 'icone': 'Bone', 'size': 0.3},
                                    'fold2GuideSetup': {'nameTempl': u'L_handThumbfold2', 'color': (0, 1, 1),
                                                        'size': 0.3}, 'axis': 'X',
                                    'fold1JntSetup': {'nameTempl': u'L_handThumbFold1', 'icone': 'Bone', 'size': 0.3},
                                    'palmJntSetup': {'nameTempl': u'L_handThumbPalm', 'icone': 'Bone', 'size': 0.2},
                                    'palmCntrlSetup': {'nameTempl': u'L_handThumbpalm', 'icone': 'cubo',
                                                       'color': (1, 0, 0), 'size': 0.2},
                                    'tipJntSetup': {'nameTempl': u'L_handThumb', 'icone': 'Bone', 'size': 0.3},
                                    'palmGuideSetup': {'nameTempl': u'L_handThumbpalm', 'color': (1, 0, 0),
                                                       'size': 0.2},
                                    'guideDict': {
                                                    'moveall': [(0.0, -0.5, 1.0), (0.0, 0.0, 0.0)],
                                                    'palm': [(0.0, 0.0, 0.0), (0.0, 0.0, 0.0)],
                                                    'base': [(0.0, 0.0, -0),(0.0, 0.0, 7.12)],
                                                    'fold2': [(0, 0, 0), (0, 0, 0)],
                                                    'fold1': [(0.0, 0.05, 0.0), (0.0, 0.0, -4.76)],
                                                    'tip': [(2.0, 0.0, 0.0), (0.0,0.0, 0.0)]},
                                    'baseJntSetup': {'nameTempl': u'L_handThumbBase', 'icone': 'Bone', 'size': 0.3},
                                    'baseGuideSetup': {'nameTempl': u'L_handThumbbase', 'color': (1, 1, 0),
                                                       'size': 0.3},
                                    'moveallGuideSetup': {'nameTempl': u'L_handThumbMoveAll', 'color': (1, 1, 0),
                                                          'size': 0.1}, 'name': u'L_handThumb',
                                    'baseCntrlSetup': {'nameTempl': u'L_handThumbbase', 'icone': 'dropMenosZ',
                                                       'color': (1, 1, 0), 'size': 0.1},
                                    'fold1CntrlSetup': {'nameTempl': u'L_handThumbfold1', 'icone': 'circuloX',
                                                        'color': (0, 1, 1), 'size': 0.3}, 'flipAxis': False}},
            'flipAxis': False, 'name': 'L_hand',
            'guideDict': {'moveall': [(8.130032802431057, 21.041404351843855, 0.0), (0.0, 0.0, 0.0)]}, 'axis': 'X'}

        lfootDict = {'slideCntrlSetup': {'nameTempl': 'L_footSlide', 'icone': 'bola', 'color': (1, 0, 0), 'size': 0.4},
                     'tipCntrlSetup': {'nameTempl': 'L_footTip', 'icone': 'bola', 'color': (0, 1, 1), 'size': 0.5},
                     'moveallCntrlSetup': {'nameTempl': 'L_footMoveAll', 'icone': 'circuloX', 'color': (1, 1, 0),
                                           'size': 1.8},
                     'toLimbCntrlSetup': {'nameTempl': 'L_footToLimb', 'icone': 'bola', 'color': (1, 1, 0),
                                          'size': 0.5},
                     'ankleFkCntrlSetup': {'nameTempl': 'L_footTnkleFk', 'icone': 'grp', 'color': (0, 1, 0),
                                           'size': 1.0},
                     'jointGuideSetup': {'nameTempl': 'L_footJoint', 'icone': 'null', 'color': (1, 0, 1), 'size': 0.5},
                     'axis': 'X',
                     'toeFkCntrlSetup': {'nameTempl': 'L_footToeFk', 'icone': 'cubo', 'color': (0, 1, 0),
                                         'size': 1.0},
                     'inGuideSetup': {'nameTempl': 'L_footIn', 'icone': 'bola', 'color': (0, 0, 1), 'size': 0.4},
                     'ankleJntSetup': {'nameTempl': 'L_footAnkle', 'icone': 'Bone', 'size': 1.0},
                     'ballGuideSetup': {'nameTempl': 'L_footBall', 'icone': 'bola', 'color': (0, 1, 1), 'size': 0.5},
                     'ankleGuideSetup': {'nameTempl': 'L_footAnkle', 'icone': 'bola', 'color': (0, 1, 1), 'size': 0.5},
                     'rollCntrlSetup': {'nameTempl': 'L_footRoll', 'icone': 'cubo', 'color': (0, 0.6, 1), 'size': 0.4},
                     'rollGuideSetup': {'nameTempl': 'L_footRoll', 'icone': 'bola', 'color': (1, 0, 1), 'size': 0.4},
                     'outGuideSetup': {'nameTempl': 'L_footOut', 'icone': 'bola', 'color': (0, 0, 1), 'size': 0.4},
                     'toeGuideSetup': {'nameTempl': 'L_footToe', 'icone': 'null', 'color': (1, 1, 0), 'size': 1.0},
                     'fingerNames': ['Thumb', 'Index', 'Middle', 'Ring', 'Pink', 'Other', 'Other1'],
                     'outCntrlSetup': {'nameTempl': 'L_footOut', 'icone': 'bola', 'color': (0, 1, 1), 'size': 0.4},
                     'heelGuideSetup': {'nameTempl': 'L_footHeel', 'icone': 'bola', 'color': (0, 1, 1), 'size': 0.5},

                     'fingers': {
                         'Ring': {
                                     'fold2CntrlSetup': {'nameTempl': u'L_footRingfold2', 'icone': 'circuloX',
                                                         'color': (0, 1, 1),'size': 0.3},
                                     'folds': 1,
                                     'moveallCntrlSetup': {'nameTempl': u'L_footRingMoveAll', 'icone': 'circuloX',
                                                           'color': (1, 1, 0), 'size': 0.1},
                                     'guideDict':   {
                                                     'moveall': [(-0.85, 0, -0.5), (0.0, 0, 0.0)],
                                                     'palm': [(0.0, 0.0, 0.0), (0.0, 0.0, 0.0)],
                                                     'base': [(0.3, 0.0, 0.0), (0.0, 0.0, 0)],
                                                     'fold2': [(0, 0, 0), (0, 0, 0)],
                                                     'fold1': [(0.0, 0.05, 0.0), (0.0, 0.0, 0.0)],
                                                     'tip': [(0.8, 0.0, 0.0), (0.0, 0.0, 0)]
                                                    },
                                     'fold1GuideSetup': {'nameTempl': u'L_footRingfold1', 'icone': 'circuloX', 'color': (0, 0, 1),
                                                         'size': 0.4},
                                     'baseJntSetup': {'nameTempl': u'L_footRingBase', 'icone': 'Bone', 'size': 0.3},
                                     'fold2JntSetup': {'nameTempl': u'L_footRingFold2', 'icone': 'Bone', 'size': 0.3},
                                     'isHeelFinger': False,
                                     'baseGuideSetup': {'nameTempl': u'L_footRingbase', 'icone': 'circuloX', 'color': (0, 0, 1),
                                                        'size': 0.4},
                                     'fold1CntrlSetup': {'nameTempl': u'L_footRingfold1', 'icone': 'circuloX', 'color': (0, 1, 1),
                                                         'size': 0.3},
                                     'fold2GuideSetup': {'nameTempl': u'L_footRingfold2', 'icone': 'circuloX', 'color': (0, 0, 1),
                                                         'size': 0.4}, 'axis': 'X',
                                     'fold1JntSetup': {'nameTempl': u'L_footRingFold1', 'icone': 'Bone', 'size': 0.3},
                                     'moveallGuideSetup': {'nameTempl': u'L_footRingMoveAll', 'icone': 'quadradoX',
                                                           'color': (0.6, 0, 0), 'size': 0.5}, 'name': u'L_footRing',
                                     'tipGuideSetup': {'nameTempl': u'L_footRingtip', 'icone': 'circuloX', 'color': (0, 0, 1),
                                                       'size': 0.4},
                                     'baseCntrlSetup': {'nameTempl': u'L_footRingbase', 'icone': 'dropMenosZ', 'color': (1, 1, 0),
                                                        'size': 0.1},
                                     'palmJntSetup': {'nameTempl': u'L_footRingPalm', 'icone': 'Bone', 'size': 0.2},
                                     'palmCntrlSetup': {'nameTempl': u'L_footRingpalm', 'icone': 'cubo', 'color': (1, 0, 0),
                                                        'size': 0.2},
                                     'palmGuideSetup': {'nameTempl': u'L_footRingpalm', 'icone': 'circuloX', 'color': (0, 0, 1),
                                                        'size': 0.4}, 'flipAxis': False,
                                     'tipJntSetup': {'nameTempl': u'L_footRing', 'icone': 'Bone', 'size': 0.3}},

                         'Pinky': {
                                     'fold2CntrlSetup': {'nameTempl': u'L_footPinkyfold2', 'icone': 'circuloX', 'color': (0, 1, 1),
                                                         'size': 0.3}, 'folds': 1,
                                     'moveallCntrlSetup': {'nameTempl': u'L_footPinkyMoveAll', 'icone': 'circuloX',
                                                           'color': (1, 1, 0), 'size': 0.1},
                                     'guideDict':   {
                                                     'moveall': [(-0.85, 0, -1.0),(0.0, 0, 0.0)],
                                                     'palm': [(0.0, 0.0, 0.0), (0.0, 0.0, 0.0)],
                                                     'base': [(0.3, 0.0, 0.0), (0.0, 0.0, 0)],
                                                     'fold2': [(0, 0, 0), (0, 0, 0)],
                                                     'fold1': [(0.0, 0.05, 0.0), (0.0, 0.0, 0.0)],
                                                     'tip': [(0.8, 0.0, 0.0), (0.0, 0.0, 0)]
                                                    },

                                     'fold1GuideSetup': {'nameTempl': u'L_footPinkyfold1', 'icone': 'circuloX', 'color': (0, 0, 1),
                                                         'size': 0.4},
                                     'baseJntSetup': {'nameTempl': u'L_footPinkyBase', 'icone': 'Bone', 'size': 0.3},
                                     'fold2JntSetup': {'nameTempl': u'L_footPinkyFold2', 'icone': 'Bone', 'size': 0.3},
                                     'isHeelFinger': False,
                                     'baseGuideSetup': {'nameTempl': u'L_footPinkybase', 'icone': 'circuloX', 'color': (0, 0, 1),
                                                        'size': 0.4},
                                     'fold1CntrlSetup': {'nameTempl': u'L_footPinkyfold1', 'icone': 'circuloX', 'color': (0, 1, 1),
                                                         'size': 0.3},
                                     'fold2GuideSetup': {'nameTempl': u'L_footPinkyfold2', 'icone': 'circuloX', 'color': (0, 0, 1),
                                                         'size': 0.4}, 'axis': 'X',
                                     'fold1JntSetup': {'nameTempl': u'L_footPinkyFold1', 'icone': 'Bone', 'size': 0.3},
                                     'moveallGuideSetup': {'nameTempl': u'L_footPinkyMoveAll', 'icone': 'quadradoX',
                                                           'color': (0.6, 0, 0), 'size': 0.5}, 'name': u'L_footPinky',
                                     'tipGuideSetup': {'nameTempl': u'L_footPinkytip', 'icone': 'circuloX', 'color': (0, 0, 1),
                                                       'size': 0.4},
                                     'baseCntrlSetup': {'nameTempl': u'L_footPinkybase', 'icone': 'dropMenosZ', 'color': (1, 1, 0),
                                                        'size': 0.1},
                                     'palmJntSetup': {'nameTempl': u'L_footPinkyPalm', 'icone': 'Bone', 'size': 0.2},
                                     'palmCntrlSetup': {'nameTempl': u'L_footPinkypalm', 'icone': 'cubo', 'color': (1, 0, 0),
                                                        'size': 0.2},
                                     'palmGuideSetup': {'nameTempl': u'L_footPinkypalm', 'icone': 'circuloX', 'color': (0, 0, 1),
                                                        'size': 0.4}, 'flipAxis': False,
                                     'tipJntSetup': {'nameTempl': u'L_footPinky', 'icone': 'Bone', 'size': 0.3}},

                         'Index': {
                                     'fold2CntrlSetup': {'nameTempl': u'L_footIndexfold2', 'icone': 'circuloX', 'color': (0, 1, 1),
                                                         'size': 0.3}, 'folds': 1,
                                     'moveallCntrlSetup': {'nameTempl': u'L_footIndexMoveAll', 'icone': 'circuloX',
                                                           'color': (1, 1, 0), 'size': 0.1},
                                     'guideDict':   {
                                                     'moveall': [(-0.85, 0, 0.5), (0.0, 0, 0.0)],
                                                     'palm': [(0.0, 0.0, 0.0), (0.0, 0.0, 0.0)],
                                                     'base': [(0.3, 0.0, 0.0), (0.0, 0.0, 0)],
                                                     'fold2': [(0, 0, 0), (0, 0, 0)],
                                                     'fold1': [(0.0, 0.05, 0.0), (0.0, 0.0, 0.0)],
                                                     'tip': [(0.8, 0.0, 0.0), (0.0, 0.0, 0)]
                                                    },
                                     'fold1GuideSetup': {'nameTempl': u'L_footIndexfold1', 'icone': 'circuloX', 'color': (0, 0, 1),
                                                         'size': 0.4},
                                     'baseJntSetup': {'nameTempl': u'L_footIndexBase', 'icone': 'Bone', 'size': 0.3},
                                     'fold2JntSetup': {'nameTempl': u'L_footIndexFold2', 'icone': 'Bone', 'size': 0.3},
                                     'isHeelFinger': False,
                                     'baseGuideSetup': {'nameTempl': u'L_footIndexbase', 'icone': 'circuloX', 'color': (0, 0, 1),
                                                        'size': 0.4},
                                     'fold1CntrlSetup': {'nameTempl': u'L_footIndexfold1', 'icone': 'circuloX', 'color': (0, 1, 1),
                                                         'size': 0.3},
                                     'fold2GuideSetup': {'nameTempl': u'L_footIndexfold2', 'icone': 'circuloX', 'color': (0, 0, 1),
                                                         'size': 0.4}, 'axis': 'X',
                                     'fold1JntSetup': {'nameTempl': u'L_footIndexFold1', 'icone': 'Bone', 'size': 0.3},
                                     'moveallGuideSetup': {'nameTempl': u'L_footIndexMoveAll', 'icone': 'quadradoX',
                                                           'color': (0.6, 0, 0), 'size': 0.5}, 'name': u'L_footIndex',
                                     'tipGuideSetup': {'nameTempl': u'L_footIndextip', 'icone': 'circuloX', 'color': (0, 0, 1),
                                                       'size': 0.4},
                                     'baseCntrlSetup': {'nameTempl': u'L_footIndexbase', 'icone': 'dropMenosZ', 'color': (1, 1, 0),
                                                        'size': 0.1},
                                     'palmJntSetup': {'nameTempl': u'L_footIndexPalm', 'icone': 'Bone', 'size': 0.2},
                                     'palmCntrlSetup': {'nameTempl': u'L_footIndexpalm', 'icone': 'cubo', 'color': (1, 0, 0),
                                                        'size': 0.2},
                                     'palmGuideSetup': {'nameTempl': u'L_footIndexpalm', 'icone': 'circuloX', 'color': (0, 0, 1),
                                                        'size': 0.4}, 'flipAxis': False,
                                     'tipJntSetup': {'nameTempl': u'L_footIndex', 'icone': 'Bone', 'size': 0.3}},


                         'Middle': {
                                     'fold2CntrlSetup': {'nameTempl': u'L_footMiddlefold2', 'icone': 'circuloX', 'color': (0, 1, 1),
                                                         'size': 0.3}, 'folds': 1,
                                     'moveallCntrlSetup': {'nameTempl': u'L_footMiddleMoveAll', 'icone': 'circuloX',
                                                           'color': (1, 1, 0), 'size': 0.1},
                                     'guideDict':   {
                                                     'moveall': [(-0.85, 0.0, 0.0), (0.0, 0.0, 0.0)],
                                                     'palm': [(0.0, 0.0, 0.0), (0.0, 0.0, 0.0)],
                                                     'base': [(0.3, 0.0, 0.0), (0.0, -0.0, 0.0)],
                                                     'fold2': [(0, 0, 0), (0, 0, 0)],
                                                     'fold1': [(0.0, 0.05, 0.0), (0.0, 0.0, 0.0)],
                                                     'tip': [(0.8, 0.0, 0.0), (0.0, 0.0, 0.0)]
                                                    },
                                     'fold1GuideSetup': {'nameTempl': u'L_footMiddlefold1', 'icone': 'circuloX', 'color': (0, 0, 1),
                                                         'size': 0.4},
                                     'baseJntSetup': {'nameTempl': u'L_footMiddleBase', 'icone': 'Bone', 'size': 0.3},
                                     'fold2JntSetup': {'nameTempl': u'L_footMiddleFold2', 'icone': 'Bone', 'size': 0.3},
                                     'isHeelFinger': False,
                                     'baseGuideSetup': {'nameTempl': u'L_footMiddlebase', 'icone': 'circuloX', 'color': (0, 0, 1),
                                                        'size': 0.4},
                                     'fold1CntrlSetup': {'nameTempl': u'L_footMiddlefold1', 'icone': 'circuloX', 'color': (0, 1, 1),
                                                         'size': 0.3},
                                     'fold2GuideSetup': {'nameTempl': u'L_footMiddlefold2', 'icone': 'circuloX', 'color': (0, 0, 1),
                                                         'size': 0.4}, 'axis': 'X',
                                     'fold1JntSetup': {'nameTempl': u'L_footMiddleFold1', 'icone': 'Bone', 'size': 0.3},
                                     'moveallGuideSetup': {'nameTempl': u'L_footMiddleMoveAll', 'icone': 'quadradoX',
                                                           'color': (0.6, 0, 0), 'size': 0.5}, 'name': u'L_footMiddle',
                                     'tipGuideSetup': {'nameTempl': u'L_footMiddletip', 'icone': 'circuloX', 'color': (0, 0, 1),
                                                       'size': 0.4},
                                     'baseCntrlSetup': {'nameTempl': u'L_footMiddlebase', 'icone': 'dropMenosZ', 'color': (1, 1, 0),
                                                        'size': 0.1},
                                     'palmJntSetup': {'nameTempl': u'L_footMiddlePalm', 'icone': 'Bone', 'size': 0.2},
                                     'palmCntrlSetup': {'nameTempl': u'L_footMiddlepalm', 'icone': 'cubo', 'color': (1, 0, 0),
                                                        'size': 0.2},
                                     'palmGuideSetup': {'nameTempl': u'L_footMiddlepalm', 'icone': 'circuloX', 'color': (0, 0, 1),
                                                        'size': 0.4}, 'flipAxis': False,
                                     'tipJntSetup': {'nameTempl': u'L_footMiddle', 'icone': 'Bone', 'size': 0.3}},


                         'Thumb': {
                                     'fold2CntrlSetup': {'nameTempl': u'L_footThumbfold2', 'icone': 'circuloX', 'color': (0, 1, 1),
                                                     'size': 0.3}, 'folds': 1,
                                     'moveallCntrlSetup': {'nameTempl': u'L_footThumbMoveAll', 'icone': 'circuloX',
                                                           'color': (1, 1, 0), 'size': 0.1},
                                     'guideDict':   {
                                                     'moveall': [(-0.85, 0, 1), (0.0, 0.0, 0.0)],
                                                     'palm': [(0.0, 0.0, 0.0), (0.0, -0.0, 0.0)],
                                                     'base': [(0.3, 0.0, 0.0),(0.0, 0.0, 0.0)],
                                                     'fold2': [(0, 0, 0), (0, 0, 0)],
                                                     'fold1': [(0.0, 0.05, 0.0), (0.0, -0.0, 0.0)],
                                                     'tip': [(0.8, 0.0, 0.0),(0.0, 0.0, 0.0)]
                                                    },
                                     'fold1GuideSetup': {'nameTempl': u'L_footThumbfold1', 'icone': 'circuloX', 'color': (0, 0, 1),
                                                         'size': 0.4},
                                     'baseJntSetup': {'nameTempl': u'L_footThumbBase', 'icone': 'Bone', 'size': 0.3},
                                     'fold2JntSetup': {'nameTempl': u'L_footThumbFold2', 'icone': 'Bone', 'size': 0.3},
                                     'isHeelFinger': False,
                                     'baseGuideSetup': {'nameTempl': u'L_footThumbbase', 'icone': 'circuloX', 'color': (0, 0, 1),
                                                        'size': 0.4},
                                     'fold1CntrlSetup': {'nameTempl': u'L_footThumbfold1', 'icone': 'circuloX', 'color': (0, 1, 1),
                                                         'size': 0.3},
                                     'fold2GuideSetup': {'nameTempl': u'L_footThumbfold2', 'icone': 'circuloX', 'color': (0, 0, 1),
                                                         'size': 0.4}, 'axis': 'X',
                                     'fold1JntSetup': {'nameTempl': u'L_footThumbFold1', 'icone': 'Bone', 'size': 0.3},
                                     'moveallGuideSetup': {'nameTempl': u'L_footThumbMoveAll', 'icone': 'quadradoX',
                                                           'color': (0.6, 0, 0), 'size': 0.5}, 'name': u'L_footThumb',
                                     'tipGuideSetup': {'nameTempl': u'L_footThumbtip', 'icone': 'circuloX', 'color': (0, 0, 1),
                                                       'size': 0.4},
                                     'baseCntrlSetup': {'nameTempl': u'L_footThumbbase', 'icone': 'dropMenosZ', 'color': (1, 1, 0),
                                                        'size': 0.1},
                                     'palmJntSetup': {'nameTempl': u'L_footThumbPalm', 'icone': 'Bone', 'size': 0.2},
                                     'palmCntrlSetup': {'nameTempl': u'L_footThumbpalm', 'icone': 'cubo', 'color': (1, 0, 0),
                                                        'size': 0.2},
                                     'palmGuideSetup': {'nameTempl': u'L_footThumbpalm', 'icone': 'circuloX', 'color': (0, 0, 1),
                                                        'size': 0.4}, 'flipAxis': False,
                                     'tipJntSetup': {'nameTempl': u'L_footThumb', 'icone': 'Bone', 'size': 0.3}}
                     },

                     'heelCntrlSetup': {'nameTempl': 'L_footHeel', 'icone': 'bola', 'color': (0, 1, 1), 'size': 0.5},
                     'ballCntrlSetup': {'nameTempl': 'L_footBall', 'icone': 'circuloX', 'color': (1, 1, 0),
                                        'size': 1.5},
                     'baseGuideSetup': {'nameTempl': 'L_footBase', 'icone': 'quadradoY', 'color': (1, 0, 1), 'size': 3},
                     'name': 'L_foot',
                     'moveallGuideSetup': {'nameTempl': 'L_footMoveAll', 'icone': 'quadradoY', 'color': (1, 0, 0),
                                           'size': 1.8},
                     'slideGuideSetup': {'nameTempl': 'L_footSlide', 'icone': 'null', 'color': (1, 0, 1), 'size': 0.4},
                     'centerCntrlSetup': {'nameTempl': 'L_footCenter', 'icone': 'circuloX', 'color': (0, 0, 1),
                                          'size': 2},
                     'baseCntrlSetup': {'nameTempl': 'L_footBase', 'icone': 'quadradoY', 'color': (0, 0, 1), 'size': 3},
                     'toeCntrlSetup': {'nameTempl': 'L_footToe', 'icone': 'circuloX', 'color': (1, 1, 0), 'size': 1.0},
                     'toeJntSetup': {'nameTempl': 'L_footToe', 'icone': 'Bone', 'size': 1.0},
                     'ankleCntrlSetup': {'nameTempl': 'L_footAnkle', 'icone': 'cubo', 'color': (0, 1, 1), 'size': 1},
                     'centerGuideSetup': {'nameTempl': 'L_footCenter', 'icone': 'grp', 'color': (1, 1, 0), 'size': 0.5},
                     'flipAxis': False,
                     'inCntrlSetup': {'nameTempl': 'L_footIn', 'icone': 'bola', 'color': (0, 1, 1), 'size': 0.4},
                     'tipGuideSetup': {'nameTempl': 'L_footTip', 'icone': 'bola', 'color': (0, 1, 1), 'size': 0.5},

                     'guideDict': {'ball': [(-1.0, 0.5, 0.0), (0.0, -0.0, 0.0)],
                                   'center': [(0.0, 0.0, 0.0), (0.0, 0.0, 0.0)],
                                   'tip': [(3.0, 0.0, 0.0), (0.0, -0.0, 0.0)],
                                   'moveall': [(1.76, 0.089, 0.0), (0.0, -90.0, 0.0)],
                                   'in': [(-1.0, 0.0, -1.0), (0.0, -0.0, 0.0)],
                                   'ankle': [(0.0, 1.0, 0.0), (0.0, -0.0, 0.0)],
                                   'heel': [(-1.0, 0.0, 0.0), (0.0, -0.0, 0.0)],
                                   'out': [(-1.0, 0.0, 1.0), (0.0, -0.0, 0.0)]}}

        rfootDict = {'slideCntrlSetup': {'nameTempl': 'R_footSlide', 'icone': 'bola', 'color': (1, 0, 0), 'size': 0.4},
                     'tipCntrlSetup': {'nameTempl': 'R_footTip', 'icone': 'bola', 'color': (0, 1, 1), 'size': 0.5},
                     'moveallCntrlSetup': {'nameTempl': 'R_footMoveAll', 'icone': 'circuloX', 'color': (1, 1, 0),
                                           'size': 1.8},
                     'toLimbCntrlSetup': {'nameTempl': 'R_footToLimb', 'icone': 'bola', 'color': (1, 1, 0),
                                          'size': 0.5},
                     'ankleFkCntrlSetup': {'nameTempl': 'R_footTnkleFk', 'icone': 'grp', 'color': (0, 1, 0),
                                           'size': 1.0},
                     'jointGuideSetup': {'nameTempl': 'R_footJoint', 'icone': 'null', 'color': (1, 0, 1), 'size': 0.5},
                     'axis': 'X',
                     'toeFkCntrlSetup': {'nameTempl': 'R_footToeFk', 'icone': 'cubo', 'color': (0, 1, 0),
                                         'size': 1.0},
                     'inGuideSetup': {'nameTempl': 'R_footIn', 'icone': 'bola', 'color': (0, 0, 1), 'size': 0.4},
                     'ankleJntSetup': {'nameTempl': 'R_footAnkle', 'icone': 'Bone', 'size': 1.0},
                     'ballGuideSetup': {'nameTempl': 'R_footBall', 'icone': 'bola', 'color': (0, 1, 1), 'size': 0.5},
                     'ankleGuideSetup': {'nameTempl': 'R_footAnkle', 'icone': 'bola', 'color': (0, 1, 1), 'size': 0.5},
                     'rollCntrlSetup': {'nameTempl': 'R_footRoll', 'icone': 'cubo', 'color': (0, 0.6, 1), 'size': 0.4},
                     'rollGuideSetup': {'nameTempl': 'R_footRoll', 'icone': 'bola', 'color': (1, 0, 1), 'size': 0.4},
                     'outGuideSetup': {'nameTempl': 'R_footOut', 'icone': 'bola', 'color': (0, 0, 1), 'size': 0.4},
                     'toeGuideSetup': {'nameTempl': 'R_footToe', 'icone': 'null', 'color': (1, 1, 0), 'size': 1.0},
                     'fingerNames': ['Thumb', 'Index', 'Middle', 'Ring', 'Pink', 'Other', 'Other1'],
                     'outCntrlSetup': {'nameTempl': 'R_footOut', 'icone': 'bola', 'color': (0, 1, 1), 'size': 0.4},
                     'heelGuideSetup': {'nameTempl': 'R_footHeel', 'icone': 'bola', 'color': (0, 1, 1), 'size': 0.5},
                     'fingers': {
                         'Ring': {
                                     'fold2CntrlSetup': {'nameTempl': u'R_footRingfold2', 'icone': 'circuloX',
                                                         'color': (0, 1, 1),'size': 0.3},
                                     'folds': 1,
                                     'moveallCntrlSetup': {'nameTempl': u'R_footRingMoveAll', 'icone': 'circuloX',
                                                           'color': (1, 1, 0), 'size': 0.1},
                                     'guideDict':   {
                                                     'moveall': [(-0.85, 0, -0.5), (0.0, 0, 0.0)],
                                                     'palm': [(0.0, 0.0, 0.0), (0.0, 0.0, 0.0)],
                                                     'base': [(0.3, 0.0, 0.0), (0.0, 0.0, 0)],
                                                     'fold2': [(0, 0, 0), (0, 0, 0)],
                                                     'fold1': [(0.0, -0.05, 0.0), (0.0, 0.0, 0.0)],
                                                     'tip': [(0.8, 0.0, 0.0), (0.0, 0.0, 0)]
                                                    },
                                     'fold1GuideSetup': {'nameTempl': u'R_footRingfold1', 'icone': 'circuloX', 'color': (0, 0, 1),
                                                         'size': 0.4},
                                     'baseJntSetup': {'nameTempl': u'R_footRingBase', 'icone': 'Bone', 'size': 0.3},
                                     'fold2JntSetup': {'nameTempl': u'R_footRingFold2', 'icone': 'Bone', 'size': 0.3},
                                     'isHeelFinger': False,
                                     'baseGuideSetup': {'nameTempl': u'R_footRingbase', 'icone': 'circuloX', 'color': (0, 0, 1),
                                                        'size': 0.4},
                                     'fold1CntrlSetup': {'nameTempl': u'R_footRingfold1', 'icone': 'circuloX', 'color': (0, 1, 1),
                                                         'size': 0.3},
                                     'fold2GuideSetup': {'nameTempl': u'R_footRingfold2', 'icone': 'circuloX', 'color': (0, 0, 1),
                                                         'size': 0.4}, 'axis': 'X',
                                     'fold1JntSetup': {'nameTempl': u'R_footRingFold1', 'icone': 'Bone', 'size': 0.3},
                                     'moveallGuideSetup': {'nameTempl': u'R_footRingMoveAll', 'icone': 'quadradoX',
                                                           'color': (0.6, 0, 0), 'size': 0.5}, 'name': u'R_footRing',
                                     'tipGuideSetup': {'nameTempl': u'R_footRingtip', 'icone': 'circuloX', 'color': (0, 0, 1),
                                                       'size': 0.4},
                                     'baseCntrlSetup': {'nameTempl': u'R_footRingbase', 'icone': 'dropMenosZ', 'color': (1, 1, 0),
                                                        'size': 0.1},
                                     'palmJntSetup': {'nameTempl': u'R_footRingPalm', 'icone': 'Bone', 'size': 0.2},
                                     'palmCntrlSetup': {'nameTempl': u'R_footRingpalm', 'icone': 'cubo', 'color': (1, 0, 0),
                                                        'size': 0.2},
                                     'palmGuideSetup': {'nameTempl': u'R_footRingpalm', 'icone': 'circuloX', 'color': (0, 0, 1),
                                                        'size': 0.4}, 'flipAxis': False,
                                     'tipJntSetup': {'nameTempl': u'R_footRing', 'icone': 'Bone', 'size': 0.3}},

                         'Pinky': {
                                     'fold2CntrlSetup': {'nameTempl': u'R_footPinkyfold2', 'icone': 'circuloX', 'color': (0, 1, 1),
                                                         'size': 0.3}, 'folds': 1,
                                     'moveallCntrlSetup': {'nameTempl': u'R_footPinkyMoveAll', 'icone': 'circuloX',
                                                           'color': (1, 1, 0), 'size': 0.1},
                                     'guideDict':   {
                                                     'moveall': [(-0.85, 0, -1),(0.0, 0, 0.0)],
                                                     'palm': [(0.0, 0.0, 0.0), (0.0, 0.0, 0.0)],
                                                     'base': [(0.3, 0.0, 0.0), (0.0, 0.0, 0)],
                                                     'fold2': [(0, 0, 0), (0, 0, 0)],
                                                     'fold1': [(0.0, -0.05, 0.0), (0.0, 0.0, 0.0)],
                                                     'tip': [(0.8, 0.0, 0.0), (0.0, 0.0, 0)]
                                                    },

                                     'fold1GuideSetup': {'nameTempl': u'R_footPinkyfold1', 'icone': 'circuloX', 'color': (0, 0, 1),
                                                         'size': 0.4},
                                     'baseJntSetup': {'nameTempl': u'R_footPinkyBase', 'icone': 'Bone', 'size': 0.3},
                                     'fold2JntSetup': {'nameTempl': u'R_footPinkyFold2', 'icone': 'Bone', 'size': 0.3},
                                     'isHeelFinger': False,
                                     'baseGuideSetup': {'nameTempl': u'R_footPinkybase', 'icone': 'circuloX', 'color': (0, 0, 1),
                                                        'size': 0.4},
                                     'fold1CntrlSetup': {'nameTempl': u'R_footPinkyfold1', 'icone': 'circuloX', 'color': (0, 1, 1),
                                                         'size': 0.3},
                                     'fold2GuideSetup': {'nameTempl': u'R_footPinkyfold2', 'icone': 'circuloX', 'color': (0, 0, 1),
                                                         'size': 0.4}, 'axis': 'X',
                                     'fold1JntSetup': {'nameTempl': u'R_footPinkyFold1', 'icone': 'Bone', 'size': 0.3},
                                     'moveallGuideSetup': {'nameTempl': u'R_footPinkyMoveAll', 'icone': 'quadradoX',
                                                           'color': (0.6, 0, 0), 'size': 0.5}, 'name': u'R_footPinky',
                                     'tipGuideSetup': {'nameTempl': u'R_footPinkytip', 'icone': 'circuloX', 'color': (0, 0, 1),
                                                       'size': 0.4},
                                     'baseCntrlSetup': {'nameTempl': u'R_footPinkybase', 'icone': 'dropMenosZ', 'color': (1, 1, 0),
                                                        'size': 0.1},
                                     'palmJntSetup': {'nameTempl': u'R_footPinkyPalm', 'icone': 'Bone', 'size': 0.2},
                                     'palmCntrlSetup': {'nameTempl': u'R_footPinkypalm', 'icone': 'cubo', 'color': (1, 0, 0),
                                                        'size': 0.2},
                                     'palmGuideSetup': {'nameTempl': u'R_footPinkypalm', 'icone': 'circuloX', 'color': (0, 0, 1),
                                                        'size': 0.4}, 'flipAxis': False,
                                     'tipJntSetup': {'nameTempl': u'R_footPinky', 'icone': 'Bone', 'size': 0.3}},

                         'Index': {
                                     'fold2CntrlSetup': {'nameTempl': u'R_footIndexfold2', 'icone': 'circuloX', 'color': (0, 1, 1),
                                                         'size': 0.3}, 'folds': 1,
                                     'moveallCntrlSetup': {'nameTempl': u'R_footIndexMoveAll', 'icone': 'circuloX',
                                                           'color': (1, 1, 0), 'size': 0.1},
                                     'guideDict':   {
                                                     'moveall': [(-0.85, 0, 0.5), (0.0, 0, 0.0)],
                                                     'palm': [(0.0, 0.0, 0.0), (0.0, 0.0, 0.0)],
                                                     'base': [(0.3, 0.0, 0.0), (0.0, 0.0, 0)],
                                                     'fold2': [(0, 0, 0), (0, 0, 0)],
                                                     'fold1': [(0.0, -0.05, 0.0), (0.0, 0.0, 0.0)],
                                                     'tip': [(0.8, 0.0, 0.0), (0.0, 0.0, 0)]
                                                    },
                                     'fold1GuideSetup': {'nameTempl': u'R_footIndexfold1', 'icone': 'circuloX', 'color': (0, 0, 1),
                                                         'size': 0.4},
                                     'baseJntSetup': {'nameTempl': u'R_footIndexBase', 'icone': 'Bone', 'size': 0.3},
                                     'fold2JntSetup': {'nameTempl': u'R_footIndexFold2', 'icone': 'Bone', 'size': 0.3},
                                     'isHeelFinger': False,
                                     'baseGuideSetup': {'nameTempl': u'R_footIndexbase', 'icone': 'circuloX', 'color': (0, 0, 1),
                                                        'size': 0.4},
                                     'fold1CntrlSetup': {'nameTempl': u'R_footIndexfold1', 'icone': 'circuloX', 'color': (0, 1, 1),
                                                         'size': 0.3},
                                     'fold2GuideSetup': {'nameTempl': u'R_footIndexfold2', 'icone': 'circuloX', 'color': (0, 0, 1),
                                                         'size': 0.4}, 'axis': 'X',
                                     'fold1JntSetup': {'nameTempl': u'R_footIndexFold1', 'icone': 'Bone', 'size': 0.3},
                                     'moveallGuideSetup': {'nameTempl': u'R_footIndexMoveAll', 'icone': 'quadradoX',
                                                           'color': (0.6, 0, 0), 'size': 0.5}, 'name': u'R_footIndex',
                                     'tipGuideSetup': {'nameTempl': u'R_footIndextip', 'icone': 'circuloX', 'color': (0, 0, 1),
                                                       'size': 0.4},
                                     'baseCntrlSetup': {'nameTempl': u'R_footIndexbase', 'icone': 'dropMenosZ', 'color': (1, 1, 0),
                                                        'size': 0.1},
                                     'palmJntSetup': {'nameTempl': u'R_footIndexPalm', 'icone': 'Bone', 'size': 0.2},
                                     'palmCntrlSetup': {'nameTempl': u'R_footIndexpalm', 'icone': 'cubo', 'color': (1, 0, 0),
                                                        'size': 0.2},
                                     'palmGuideSetup': {'nameTempl': u'R_footIndexpalm', 'icone': 'circuloX', 'color': (0, 0, 1),
                                                        'size': 0.4}, 'flipAxis': False,
                                     'tipJntSetup': {'nameTempl': u'R_footIndex', 'icone': 'Bone', 'size': 0.3}},


                         'Middle': {
                                     'fold2CntrlSetup': {'nameTempl': u'R_footMiddlefold2', 'icone': 'circuloX', 'color': (0, 1, 1),
                                                         'size': 0.3}, 'folds': 1,
                                     'moveallCntrlSetup': {'nameTempl': u'R_footMiddleMoveAll', 'icone': 'circuloX',
                                                           'color': (1, 1, 0), 'size': 0.1},
                                     'guideDict':   {
                                                     'moveall': [(-0.85, 0.0, 0), (0.0, 0.0, 0.0)],
                                                     'palm': [(0.0, 0.0, 0.0), (0.0, 0.0, 0.0)],
                                                     'base': [(0.3, 0.0, 0.0), (0.0, -0.0, 0.0)],
                                                     'fold2': [(0, 0, 0), (0, 0, 0)],
                                                     'fold1': [(0.0, -0.05, 0.0), (0.0, 0.0, 0.0)],
                                                     'tip': [(0.8, 0.0, 0.0), (0.0, 0.0, 0.0)]
                                                    },
                                     'fold1GuideSetup': {'nameTempl': u'R_footMiddlefold1', 'icone': 'circuloX', 'color': (0, 0, 1),
                                                         'size': 0.4},
                                     'baseJntSetup': {'nameTempl': u'R_footMiddleBase', 'icone': 'Bone', 'size': 0.3},
                                     'fold2JntSetup': {'nameTempl': u'R_footMiddleFold2', 'icone': 'Bone', 'size': 0.3},
                                     'isHeelFinger': False,
                                     'baseGuideSetup': {'nameTempl': u'R_footMiddlebase', 'icone': 'circuloX', 'color': (0, 0, 1),
                                                        'size': 0.4},
                                     'fold1CntrlSetup': {'nameTempl': u'R_footMiddlefold1', 'icone': 'circuloX', 'color': (0, 1, 1),
                                                         'size': 0.3},
                                     'fold2GuideSetup': {'nameTempl': u'R_footMiddlefold2', 'icone': 'circuloX', 'color': (0, 0, 1),
                                                         'size': 0.4}, 'axis': 'X',
                                     'fold1JntSetup': {'nameTempl': u'R_footMiddleFold1', 'icone': 'Bone', 'size': 0.3},
                                     'moveallGuideSetup': {'nameTempl': u'R_footMiddleMoveAll', 'icone': 'quadradoX',
                                                           'color': (0.6, 0, 0), 'size': 0.5}, 'name': u'R_footMiddle',
                                     'tipGuideSetup': {'nameTempl': u'R_footMiddletip', 'icone': 'circuloX', 'color': (0, 0, 1),
                                                       'size': 0.4},
                                     'baseCntrlSetup': {'nameTempl': u'R_footMiddlebase', 'icone': 'dropMenosZ', 'color': (1, 1, 0),
                                                        'size': 0.1},
                                     'palmJntSetup': {'nameTempl': u'R_footMiddlePalm', 'icone': 'Bone', 'size': 0.2},
                                     'palmCntrlSetup': {'nameTempl': u'R_footMiddlepalm', 'icone': 'cubo', 'color': (1, 0, 0),
                                                        'size': 0.2},
                                     'palmGuideSetup': {'nameTempl': u'R_footMiddlepalm', 'icone': 'circuloX', 'color': (0, 0, 1),
                                                        'size': 0.4}, 'flipAxis': False,
                                     'tipJntSetup': {'nameTempl': u'R_footMiddle', 'icone': 'Bone', 'size': 0.3}},


                         'Thumb': {
                                     'fold2CntrlSetup': {'nameTempl': u'R_footThumbfold2', 'icone': 'circuloX', 'color': (0, 1, 1),
                                                     'size': 0.3}, 'folds': 1,
                                     'moveallCntrlSetup': {'nameTempl': u'R_footThumbMoveAll', 'icone': 'circuloX',
                                                           'color': (1, 1, 0), 'size': 0.1},
                                     'guideDict':   {
                                                     'moveall': [(-0.85, 0.0, 1), (0.0, 0.0, 0.0)],
                                                     'palm': [(0.0, 0.0, 0.0), (0.0, -0.0, 0.0)],
                                                     'base': [(0.3, 0.0, 0.0),(0.0, 0.0, 0.0)],
                                                     'fold2': [(0, 0, 0), (0, 0, 0)],
                                                     'fold1': [(0.0, -0.05, 0.0), (0.0, -0.0, 0.0)],
                                                     'tip': [(0.8, 0.0, 0.0),(0.0, 0.0, 0.0)]
                                                    },
                                     'fold1GuideSetup': {'nameTempl': u'R_footThumbfold1', 'icone': 'circuloX', 'color': (0, 0, 1),
                                                         'size': 0.4},
                                     'baseJntSetup': {'nameTempl': u'R_footThumbBase', 'icone': 'Bone', 'size': 0.3},
                                     'fold2JntSetup': {'nameTempl': u'R_footThumbFold2', 'icone': 'Bone', 'size': 0.3},
                                     'isHeelFinger': False,
                                     'baseGuideSetup': {'nameTempl': u'R_footThumbbase', 'icone': 'circuloX', 'color': (0, 0, 1),
                                                        'size': 0.4},
                                     'fold1CntrlSetup': {'nameTempl': u'R_footThumbfold1', 'icone': 'circuloX', 'color': (0, 1, 1),
                                                         'size': 0.3},
                                     'fold2GuideSetup': {'nameTempl': u'R_footThumbfold2', 'icone': 'circuloX', 'color': (0, 0, 1),
                                                         'size': 0.4}, 'axis': 'X',
                                     'fold1JntSetup': {'nameTempl': u'R_footThumbFold1', 'icone': 'Bone', 'size': 0.3},
                                     'moveallGuideSetup': {'nameTempl': u'R_footThumbMoveAll', 'icone': 'quadradoX',
                                                           'color': (0.6, 0, 0), 'size': 0.5}, 'name': u'R_footThumb',
                                     'tipGuideSetup': {'nameTempl': u'R_footThumbtip', 'icone': 'circuloX', 'color': (0, 0, 1),
                                                       'size': 0.4},
                                     'baseCntrlSetup': {'nameTempl': u'R_footThumbbase', 'icone': 'dropMenosZ', 'color': (1, 1, 0),
                                                        'size': 0.1},
                                     'palmJntSetup': {'nameTempl': u'R_footThumbPalm', 'icone': 'Bone', 'size': 0.2},
                                     'palmCntrlSetup': {'nameTempl': u'R_footThumbpalm', 'icone': 'cubo', 'color': (1, 0, 0),
                                                        'size': 0.2},
                                     'palmGuideSetup': {'nameTempl': u'R_footThumbpalm', 'icone': 'circuloX', 'color': (0, 0, 1),
                                                        'size': 0.4}, 'flipAxis': False,
                                     'tipJntSetup': {'nameTempl': u'R_footThumb', 'icone': 'Bone', 'size': 0.3}}
                     },

                     'heelCntrlSetup': {'nameTempl': 'R_footHeel', 'icone': 'bola', 'color': (0, 1, 1), 'size': 0.5},
                     'ballCntrlSetup': {'nameTempl': 'R_footBall', 'icone': 'circuloX', 'color': (1, 1, 0),
                                        'size': 1.5},
                     'baseGuideSetup': {'nameTempl': 'R_footBase', 'icone': 'quadradoY', 'color': (1, 0, 1), 'size': 3},
                     'name': 'R_foot',
                     'moveallGuideSetup': {'nameTempl': 'R_footMoveAll', 'icone': 'quadradoY', 'color': (1, 0, 0),
                                           'size': 1.8},
                     'slideGuideSetup': {'nameTempl': 'R_footSlide', 'icone': 'null', 'color': (1, 0, 1), 'size': 0.4},
                     'centerCntrlSetup': {'nameTempl': 'R_footCenter', 'icone': 'circuloX', 'color': (0, 0, 1),
                                          'size': 2},
                     'baseCntrlSetup': {'nameTempl': 'R_footBase', 'icone': 'quadradoY', 'color': (0, 0, 1), 'size': 3},
                     'toeCntrlSetup': {'nameTempl': 'R_footToe', 'icone': 'circuloX', 'color': (1, 1, 0), 'size': 1.0},
                     'toeJntSetup': {'nameTempl': 'R_footToe', 'icone': 'Bone', 'size': 1.0},
                     'ankleCntrlSetup': {'nameTempl': 'R_footAnkle', 'icone': 'cubo', 'color': (0, 1, 1), 'size': 1},
                     'centerGuideSetup': {'nameTempl': 'R_footCenter', 'icone': 'grp', 'color': (1, 1, 0), 'size': 0.5},
                     'flipAxis': False,
                     'inCntrlSetup': {'nameTempl': 'R_footIn', 'icone': 'bola', 'color': (0, 1, 1), 'size': 0.4},
                     'tipGuideSetup': {'nameTempl': 'R_footTip', 'icone': 'bola', 'color': (0, 1, 1), 'size': 0.5},
                     'guideDict': {'ball': [(-1.0, 0.5, 0.0), (0.0, -0.0, 0.0)],
                                   'center': [(0.0, 0.0, 0.0), (0.0, 0.0, 0.0)],
                                   'tip': [(3.0, 0.0, 0.0), (0.0, -0.0, 0.0)],
                                   'moveall': [(1.76, 0.089, 0.0), (0.0, -90.0, 0.0)],
                                   'in': [(-1.0, 0.0, -1.0), (0.0, -0.0, 0.0)],
                                   'ankle': [(0.0, 1.0, 0.0), (0.0, -0.0, 0.0)],
                                   'heel': [(-1.0, 0.0, 0.0), (0.0, -0.0, 0.0)],
                                   'out': [(-1.0, 0.0, 1.0), (0.0, -0.0, 0.0)]}}

        neckDict = {
                    'moveAllGuideSetup': {'nameTempl': 'neckMoveall','icone': 'circuloX',},

                    'name': 'neck',

                    'guideDict': {'start': [(0.0, 0.0, 0.0), (0.0, -0.0, 0.0)],
                                  'moveall': [(0.0, 21.09, 0.0), (0.0, -0.0, 0.0)],
                                  'end': [(0.0, 2.0, 0.0), (0.0, -0.0, 0.0)]
                                  },
                    'endGuideSetup': {'nameTempl': 'head','icone': 'circuloZ', 'color': (0, 1, 0), 'size': 3},
                    'moveAllCntrlSetup': {'nameTempl': 'neckMoveall', 'icone': 'circuloX', 'color': (0, 1, 0),
                                          'size': 1},
                    'midGuideSetup': {'nameTempl': 'midNeck','icone': 'circuloX', 'color': (0, 1, 0), 'size': 1},
                    'startCntrlSetup': {'nameTempl': 'Neck', 'icone': 'circuloY', 'color': (0, 1, 0), 'size': 3},
                    'endCntrlSetup': {'nameTempl': 'Head', 'icone': 'circuloZ', 'color': (0, 1, 0), 'size': 2},
                    'flipAxis': False,
                    'startGuideSetup': {'nameTempl': 'neck','icone': 'circuloY', 'color': (0, 1, 0), 'size': 1},
                    'axis': 'X'}

        spineDict = {
                     'spineFkCntrlSetup': {'nameTempl': 'spineWaistFk', 'icone': 'cubo', 'color': (0, 1, 0),
                                           'size': 4}, 'name': 'spine',
                     'startFkCntrlSetup': {'nameTempl': 'spineHipFk', 'icone': 'cubo',
                                           'color': (1, 1, 0), 'size': 3.0},
                     'endFkCntrlSetup': {'nameTempl': 'spineChestFk', 'icone': 'cubo',
                                         'color': (0, 1, 0), 'size': 4},
                     'midFkCntrlSetup': {'nameTempl': 'spineAbdomenFk', 'icone': 'cubo',
                                         'color': (0, 1, 0),'size': 4},
                     'midFkOffsetCntrlSetup': {'nameTempl': 'spineAbdomenFkOff', 'icone': 'circuloY',
                                               'color': (1, 1, 0), 'size': 2.5},

                     'moveallGuideSetup': {'nameTempl': 'spineMoveall', 'icone': 'quadradoY', 'color': (1, 0, 0), 'size': 6},
                     'startGuideSetup': {'nameTempl': 'spineHip', 'icone': 'circuloY', 'color': (0, 1, 0), 'size': 5},
                     'midGuideSetup': {'nameTempl': 'spineAbdomen','icone': 'circuloY', 'color': (0, 1, 0), 'size': 5},
                     'endGuideSetup': {'nameTempl': 'spineChest', 'icone': 'circuloY', 'color': (0, 1, 0), 'size': 5},
                     'endTipGuideSetup': {'nameTempl': 'spineChestTip','icone': 'null', 'color': (0, 1, 0), 'size': 1},
                     'startTipGuideSetup': {'nameTempl': 'spineHipTip','icone': 'null', 'color': (0, 1, 0), 'size': 1},
                     'startJntSetup': {'nameTempl': 'spineHip', 'icone': 'Bone', 'size': 2}, 'axis': 'X',
                     'endJntSetup': {'nameTempl': 'spineChest', 'icone': 'Bone', 'size': 2},

                     'guideDict': {'start': [(0.0, 0.0, 0.0), (0.0, -0.0, 0.0)],
                                   'moveall': [(0.0, 11.071150831072309, 0.0), (0.0, -0.0, 0.0)],
                                   'end': [(0.0, 8.0, 0.0), (0.0, -0.0, 0.0)],
                                   'endTip': [(0.0, 2.0, 0.0), (0.0, -0.0, 0.0)],
                                   'startTip': [(0.0, -1.0, 0.0), (0.0, -0.0, 0.0)],
                                   'mid': [(0.0, 0.0, 0.0), (0.0, -0.0, 0.0)]
                                  } ,

                     'flipAxis': False,
                     'hipCntrlSetup': {'nameTempl': 'spineCOG', 'icone': 'cog', 'color': (0, 0, 1), 'size': 5.5},
                     'moveallSetup': {'nameTempl': 'spineMoveAll', 'icone': 'grp', 'color': (1, 1, 0), 'size': 1.8},

                     'startIkCntrlSetup': {'nameTempl': 'spineHipIk', 'icone': 'circuloPontaY',
                                          'color': (1, 0, 0), 'size': 4},
                     'midIkCntrlSetup': {'nameTempl': 'spineAbdomenIk', 'icone': 'circuloY', 'color': (1, 1, 0),
                                        'size': 4},
                     'endIkCntrlSetup': {'nameTempl': 'spineChestIk', 'icone': 'circuloPontaY', 'color': (1, 0, 0),
                                         'size': 4}}
        lclavDict = {
                     'name': 'L_clavicle',
                     'moveAllCntrlSetup': {'nameTempl': 'L_clavicleMoveall', 'icone': 'circuloX',
                                           'color': (1, 1, 0), 'size': 2.5},
                     'guideDict': {
                                    'moveall': [(0.344, 21.07, 0.27), (0.0, -0.0, 0.0)],
                                    'guide2': [(1.78, -0.03, -0.27), (0.0, -0.0, 0.0)],
                                    'guide1': [(0.0, 0.0, 0.0), (0.0, -0.0, 0.0)]
                                },
                     'fkCntrlSetup': {'nameTempl': 'L_clavicleChainFk', 'icone': 'circuloX', 'color': (0, 1, 0),
                                      'size': 0.8}, 'flipAxis': False,
                     'jntSetup': {'nameTempl': 'L_clavicleChain', 'icone': 'Bone', 'size': 0.8},
                     'guideSetup': {'nameTempl': 'L_clavicleChain','icone': 'circuloX',
                                    'color': (0, 1, 0), 'size': 0.8}, 'axis': 'X'}

        rclavDict = {
                     'name': 'R_clavicle',
                     'moveAllCntrlSetup': {'nameTempl': 'R_clavicleMoveall', 'icone': 'circuloX',
                                           'color': (1, 1, 0),'size': 2.5},
                     'guideDict': {
                                    'moveall': [(0.344, 21.07, 0.27), (0.0, -0.0, 0.0)],
                                    'guide2': [(1.78, -0.03, -0.27), (0.0, -0.0, 0.0)],
                                    'guide1': [(0.0, 0.0, 0.0), (0.0, -0.0, 0.0)]
                                    },

                     'fkCntrlSetup': {'nameTempl': 'R_clavicleChainFk', 'icone': 'circuloX', 'color': (0, 1, 0),
                                      'size': 0.8}, 'flipAxis': False,
                     'jntSetup': {'nameTempl': 'R_clavicleChain', 'icone': 'Bone', 'size': 0.8},
                     'guideSetup': {'nameTempl': 'R_clavicleChain','icone': 'circuloX', 'color': (0, 1, 0), 'size': 0.8},
                     'axis': 'X'
                    }

        llegShoulderDict = {'name': 'L_legShoulder',
                            'moveAllCntrlSetup': {'nameTempl': 'L_legShoulderMoveAll', 'icone': 'circuloX',
                                                  'color': (1, 1, 0), 'size': 1.8},
                            'guideDict': {
                                            'moveall': [(1.82, 11.045, 0.0), (0.0, 0.0, -89.99)],
                                            'guide2': [(1.0, 0.0, 0.0), (0.0, -0.0, 0.0)],
                                            'guide1': [(0.0, 0.0, 0.0), (0.0, -0.0, 0.0)]
                                        },

                            'fkCntrlSetup': {'nameTempl': 'L_legShoulderChainFk', 'icone': 'circuloX',
                                             'color': (0, 1, 0), 'size': 2.5}, 'flipAxis': False,
                            'jntSetup': {'nameTempl': 'L_legShoulderChain', 'icone': 'Bone', 'size': 0.8},
                            'guideSetup': {'nameTempl': 'L_legShoulderChain', 'icone': 'circuloX', 'color': (0, 1, 0), 'size': 0.8},
                            'axis': 'X'}
        rlegShoulderDict = {'name': 'R_legShoulder',
                            'moveAllCntrlSetup': {'nameTempl': 'R_legShoulderMoveAll', 'icone': 'circuloX',
                                                  'color': (1, 1, 0), 'size': 1.8},
                            'guideDict': {
                                            'moveall': [(1.82, 11.045, 0.0), (0.0, 0.0, -89.99)],
                                            'guide2': [(1.0, 0.0, 0.0), (0.0, -0.0, 0.0)],
                                            'guide1': [(0.0, 0.0, 0.0), (0.0, -0.0, 0.0)]},

                            'fkCntrlSetup': {'nameTempl': 'R_legShoulderChainFk', 'icone': 'circuloX',
                                             'color': (0, 1, 0), 'size': 2.5}, 'flipAxis': False,
                            'jntSetup': {'nameTempl': 'R_legShoulderChain', 'icone': 'Bone', 'size': 0.8},
                            'guideSetup': {'nameTempl': 'R_legShoulderChain','icone': 'circuloX', 'color': (0, 1, 0), 'size': 0.8},
                            'axis': 'X'}

        self.larm.limbDict.update(**larmDict)
        self.rarm.limbDict.update(**rarmDict)

        self.lhand.handDict.update(**lhandDict)
        self.rhand.handDict.update(**rhandDict)

        self.lfoot.footDict.update(**lfootDict)
        self.rfoot.footDict.update(**rfootDict)

        self.lclav.chainDict.update(**lclavDict)
        self.rclav.chainDict.update(**rclavDict)

        self.lleg.limbDict.update(**llegDict)
        self.rleg.limbDict.update(**rlegDict)

        self.llegShoulder.chainDict.update(**llegShoulderDict)
        self.rlegShoulder.chainDict.update(**rlegShoulderDict)

        self.spine.spineDict.update(**spineDict)
        self.neck.neckDict.update(**neckDict)


    def generateGuides(self):

        self.larm.doGuide()
        self.rarm.doGuide()
        self.rarm.mirrorConnectGuide(self.larm)

        self.lhand.doGuide()
        self.rhand.doGuide()
        self.rhand.mirrorConnectGuide(self.lhand)

        self.lfoot.doGuide()
        self.rfoot.doGuide()
        self.rfoot.mirrorConnectGuide(self.lfoot)

        self.lclav.doGuide()
        self.rclav.doGuide()
        self.rclav.mirrorConnectGuide(self.lclav)

        self.lleg.doGuide()
        self.rleg.doGuide()
        self.rleg.mirrorConnectGuide(self.lleg)

        self.llegShoulder.doGuide()
        self.rlegShoulder.doGuide()
        self.rlegShoulder.mirrorConnectGuide(self.llegShoulder)

        self.spine.doGuide()
        self.neck.doGuide()
        self.master.doGuide()

        pm.parent(self.larm.guideMoveall, self.rarm.mirrorGuide, self.lhand.guideMoveall,
                  self.rhand.mirrorGuide, self.lfoot.guideMoveall, self.rfoot.mirrorGuide,
                  self.lclav.guideMoveall, self.rclav.mirrorGuide, self.lleg.guideMoveall, self.rleg.mirrorGuide,
                  self.llegShoulder.guideMoveall, self.rlegShoulder.mirrorGuide, self.spine.guideMoveall,
                  self.neck.guideMoveall, self.master.guideMoveall)

        pm.parentConstraint(self.larm.lastGuide, self.lhand.guideMoveall, mo=True)
        pm.parentConstraint(self.rarm.lastGuide, self.rhand.guideMoveall, mo=True)
        pm.parentConstraint(self.lleg.lastGuide, self.lfoot.guideMoveall, mo=True)
        pm.parentConstraint(self.rleg.lastGuide, self.rfoot.guideMoveall, mo=True)

    def getDictsFromScene(self):
        print 'pegando guides da cena'
        self.larm.getDict()
        self.rarm.getDict()
        self.lhand.getDict()
        self.rhand.getDict()
        self.lfoot.getDict()
        self.rfoot.getDict()
        self.lleg.getDict()
        self.rleg.getDict()
        self.llegShoulder.getDict()
        self.rlegShoulder.getDict()
        self.neck.getDict()
        self.spine.getDict()
        self.lclav.getDict()
        self.rclav.getDict()
        self.master.getDict()

    def saveSkin(self):
        dirName = os.path.expanduser('~/maya/autoRig3')
        if not os.path.exists(dirName):
            os.mkdir(dirName)
        path = os.path.join(dirName, self.name + '.skin')

        if not self.skinJoints:
            self.skinJoints = pm.ls ('*_jnt', type='joint')

        modelList = []
        for jnt in self.skinJoints:
            skinCls = list(set(jnt.listConnections(type='skinCluster')))
            if skinCls:
                msh = list(set(skinCls[0].listConnections(d=True, s=False, sh=True, type='surfaceShape')))
                modelList.append(msh[0])

        self.modelList = list(set(modelList))
        interface.saveSkinning(path, meshes= self.modelList)

    def loadSkin(self):
        dirName = os.path.expanduser('~/maya/autoRig3')
        path = os.path.join(dirName, self.name + '.skin')

        if not os.path.exists(path):
            print 'file not found!!'
            return

        all = self.modelList+self.skinJoints
        print 'all', all
        for obj in self.modelList:
            pm.skinCluster(obj, self.skinJoints, tsb=True, omi=False)

        print 'load'
        interface.loadSkinning(path)

    def generateRig(self, armRibbons=True, legRibbons=True, parentModules=True):
        self.rhand.doRig()
        self.lhand.doRig()
        self.larm.doRig()
        self.rarm.doRig()
        self.rfoot.doRig()
        self.lfoot.doRig()
        self.lleg.doRig()
        self.rleg.doRig()
        self.llegShoulder.doRig()
        self.rlegShoulder.doRig()
        self.master.doRig()
        self.neck.doRig()
        self.spine.doRig()
        self.lclav.doRig()
        self.rclav.doRig()

        self.skinJoints = self.rhand.skinJoints + self.lhand.skinJoints +\
                          self.rfoot.skinJoints + self.lfoot.skinJoints + self.llegShoulder.skinJoints +\
                          self.rlegShoulder.skinJoints + self.neck.skinJoints + self.spine.skinJoints +\
                          self.lclav.skinJoints + self.rclav.skinJoints

        if armRibbons:
            ribbonSkinJnts = self.generateArmRibbons()
            self.skinJoints += ribbonSkinJnts
        else:
            self.skinJoints += self.larm.skinJoints + self.rarm.skinJoints

        if legRibbons:
            ribbonSkinJnts = self.generateLegRibbons()
            self.skinJoints += ribbonSkinJnts
        else:
            self.skinJoints += self.lleg.skinJoints + self.rleg.skinJoints

        if parentModules:
            self.parentModules()
        else:
            self.constraintModules()

        self.hipAttrs()
        self.footAttrs()
        self.generateSpaceSwitches()

        pm.addAttr(self.master.moveall, ln='armDict', dt='string')
        pm.addAttr(self.master.moveall, ln='legDict', dt='string')
        pm.addAttr(self.master.moveall, ln='handDict', dt='string')
        pm.addAttr(self.master.moveall, ln='footDict', dt='string')
        pm.addAttr(self.master.moveall, ln='neckDict', dt='string')
        pm.addAttr(self.master.moveall, ln='spineDict', dt='string')
        pm.addAttr(self.master.moveall, ln='clavDict', dt='string')
        pm.addAttr(self.master.moveall, ln='legShoulderDict', dt='string')

        self.larm.getGuideFromScene()
        self.master.moveall.armDict.set(json.dumps(self.larm.limbDict))
        self.lleg.getGuideFromScene()
        self.master.moveall.legDict.set(json.dumps(self.lleg.limbDict))
        self.lhand.getGuideFromScene()
        self.master.moveall.handDict.set(json.dumps(self.lhand.handDict))
        self.lfoot.getGuideFromScene()
        self.master.moveall.footDict.set(json.dumps(self.lfoot.footDict))
        self.neck.getGuideFromScene()
        self.master.moveall.neckDict.set(json.dumps(self.neck.neckDict))
        self.spine.getGuideFromScene()
        self.master.moveall.spineDict.set(json.dumps(self.spine.spineDict))
        self.lclav.getGuideFromScene()
        self.master.moveall.clavDict.set(json.dumps(self.lclav.chainDict))
        self.llegShoulder.getGuideFromScene()
        self.master.moveall.legShoulderDict.set(json.dumps(self.llegShoulder.chainDict))

    def generateArmRibbons(self, numJnts=10, offsetStart=0.08, offsetEnd=0.1):
        self.larb = ribbonBezier.RibbonBezier(name='L_armBezier', size=self.larm.jointLength, numJnts=10,
                                              offsetStart=0.08, offsetEnd=0.1)
        self.larb.doRig()
        self.larb.connectToLimb(self.larm)
        self.rarb = ribbonBezier.RibbonBezier(name='R_armBezier', size=self.rarm.jointLength, numJnts=10,
                                              offsetStart=0.1, offsetEnd=0.08)
        self.rarb.doRig()
        self.rarb.connectToLimb(self.rarm)

        startJntName = self.larm.startJnt.replace('_jnt', '_jxt')
        self.larm.startJnt.rename(startJntName)
        midJntName = self.larm.midJnt.replace('_jnt', '_jxt')
        self.larm.midJnt.rename(midJntName)
        endJntName = self.larm.endJnt.replace('_jnt', '_jxt')
        self.larm.endJnt.rename(endJntName)

        startJntName = self.rarm.startJnt.replace('_jnt', '_jxt')
        self.rarm.startJnt.rename(startJntName)
        midJntName = self.rarm.midJnt.replace('_jnt', '_jxt')
        self.rarm.midJnt.rename(midJntName)
        endJntName = self.rarm.endJnt.replace('_jnt', '_jxt')
        self.rarm.endJnt.rename(endJntName)

        return self.larb.skinJoints + self.rarb.skinJoints

    def generateLegRibbons(self, numJnts=10, offsetStart=0.08, offsetEnd=0.1):
        self.llrb = ribbonBezier.RibbonBezier(name='L_legBezier', size=self.lleg.jointLength, offsetStart=0.1,
                                              offsetEnd=0.1)
        self.llrb.doRig()
        self.llrb.connectToLimb(self.lleg)
        self.rlrb = ribbonBezier.RibbonBezier(name='R_legBezier', size=self.lleg.jointLength, offsetStart=0.1,
                                              offsetEnd=0.1)
        self.rlrb.doRig()
        self.rlrb.connectToLimb(self.rleg)

        startJntName = self.lleg.startJnt.replace('_jnt', '_jxt')
        self.lleg.startJnt.rename(startJntName)
        midJntName = self.lleg.midJnt.replace('_jnt', '_jxt')
        self.lleg.midJnt.rename(midJntName)
        endJntName = self.lleg.endJnt.replace('_jnt', '_jxt')
        self.lleg.endJnt.rename(endJntName)

        startJntName = self.rleg.startJnt.replace('_jnt', '_jxt')
        self.rleg.startJnt.rename(startJntName)
        midJntName = self.rleg.midJnt.replace('_jnt', '_jxt')
        self.rleg.midJnt.rename(midJntName)
        endJntName = self.rleg.endJnt.replace('_jnt', '_jxt')
        self.rleg.endJnt.rename(endJntName)

        return self.rlrb.skinJoints + self.llrb.skinJoints

    def constraintModules(self):
        pm.parentConstraint(self.spine.endTipJnt, self.lclav.moveall, mo=True)
        pm.parentConstraint(self.spine.endTipJnt, self.rclav.moveall, mo=True)
        pm.parentConstraint(self.spine.endTipJnt, self.neck.moveall, mo=True)
        pm.parentConstraint(self.rclav.jntList[-1], self.rarm.moveall, mo=True)
        pm.parentConstraint(self.lclav.jntList[-1], self.larm.moveall, mo=True)
        pm.parentConstraint(self.larm.lastTipJnt, self.lhand.moveall, mo=True)
        pm.parentConstraint(self.rarm.lastTipJnt, self.rhand.moveall, mo=True)
        pm.parentConstraint(self.spine.startTipJnt, self.llegShoulder.moveall, mo=True)
        pm.parentConstraint(self.spine.startTipJnt, self.rlegShoulder.moveall, mo=True)
        pm.parentConstraint(self.rlegShoulder.jntList[-1], self.rleg.moveall, mo=True)
        pm.parentConstraint(self.llegShoulder.jntList[-1], self.lleg.moveall, mo=True)
        pm.parentConstraint(self.lfoot.ballCntrl, self.lleg.ikCntrl, mo=True)  # checar...
        pm.parentConstraint(self.rfoot.ballCntrl, self.rleg.ikCntrl, mo=True)
        pm.parentConstraint(self.lleg.lastJnt, self.lfoot.limbConnectionCntrl.getParent())
        pm.parentConstraint(self.rleg.lastJnt, self.rfoot.limbConnectionCntrl.getParent())

    def parentModules(self):
        pm.parent(self.lhand.moveall, self.larm.lastTipJnt)
        pm.parent(self.rhand.moveall, self.rarm.lastTipJnt)
        pm.parent(self.lleg.ikCntrl.getParent(), self.lfoot.ballCntrl)
        pm.parent(self.rleg.ikCntrl.getParent(), self.rfoot.ballCntrl)

        pm.parentConstraint(self.lleg.startCntrl, self.lfoot.ankleFkCntrl, mo=True)
        pm.parentConstraint(self.rleg.startCntrl, self.rfoot.ankleFkCntrl, mo=True)
        pm.parent(self.lclav.moveall, self.spine.endTipJnt)
        pm.parent(self.rclav.moveall, self.spine.endTipJnt)
        pm.parent(self.neck.moveall, self.spine.endTipJnt)
        pm.parent(self.rarm.moveall, self.rclav.jntList[-1])
        pm.parent(self.larm.moveall, self.lclav.jntList[-1])
        pm.parent(self.llegShoulder.moveall, self.spine.startTipJnt)
        pm.parent(self.rlegShoulder.moveall, self.spine.startTipJnt)
        pm.parent(self.rleg.moveall, self.rlegShoulder.jntList[-1])
        pm.parent(self.lleg.moveall, self.llegShoulder.jntList[-1])
        pm.parent(self.lfoot.limbConnectionCntrl.getParent(), self.lleg.lastJnt)
        pm.parent(self.rfoot.limbConnectionCntrl.getParent(), self.rleg.lastJnt)

    def hipAttrs(self):
        self.spine.cogCntrl.addAttr('L_Arm_IkFk', at='float', dv=1, max=1, min=0, k=1)
        self.spine.cogCntrl.addAttr('R_Arm_IkFk', at='float', dv=1, max=1, min=0, k=1)
        self.spine.cogCntrl.addAttr('L_Leg_IkFk', at='float', dv=1, max=1, min=0, k=1)
        self.spine.cogCntrl.addAttr('R_Leg_IkFk', at='float', dv=1, max=1, min=0, k=1)
        self.spine.cogCntrl.addAttr('Spine_IkFk', at='float', dv=1, max=1, min=0, k=1)

        self.spine.cogCntrl.addAttr('L_Arm_poleVec', at='float', dv=0, max=1, min=0, k=1)
        self.spine.cogCntrl.addAttr('R_Arm_poleVec', at='float', dv=0, max=1, min=0, k=1)
        self.spine.cogCntrl.addAttr('L_Leg_poleVec', at='float', dv=0, max=1, min=0, k=1)
        self.spine.cogCntrl.addAttr('R_Leg_poleVec', at='float', dv=0, max=1, min=0, k=1)

        self.spine.cogCntrl.Spine_IkFk >> self.spine.moveall.ikfk
        self.spine.cogCntrl.R_Leg_IkFk >> self.rleg.moveall.ikfk
        self.spine.cogCntrl.L_Leg_IkFk >> self.lleg.moveall.ikfk
        self.spine.cogCntrl.R_Leg_IkFk >> self.rfoot.moveall.ikfk
        self.spine.cogCntrl.L_Leg_IkFk >> self.lfoot.moveall.ikfk
        self.spine.cogCntrl.R_Arm_IkFk >> self.rarm.moveall.ikfk
        self.spine.cogCntrl.L_Arm_IkFk >> self.larm.moveall.ikfk

        self.spine.cogCntrl.R_Arm_poleVec >> self.rarm.moveall.poleVec
        self.spine.cogCntrl.L_Arm_poleVec >> self.larm.moveall.poleVec
        self.spine.cogCntrl.R_Leg_poleVec >> self.rleg.moveall.poleVec
        self.spine.cogCntrl.L_Leg_poleVec >> self.lleg.moveall.poleVec

    def footAttrs(self):
        self.lfoot.baseCntrl.addAttr('pin', at='float', min=0, max=1, dv=0, k=1)
        self.lfoot.baseCntrl.addAttr('bias', at='float', min=-0.9, max=0.9, k=1)
        self.lfoot.baseCntrl.addAttr('autoStretch', at='float', min=0, max=1, dv=1, k=1)
        self.lfoot.baseCntrl.addAttr('manualStretch', at='float', dv=1, k=1)
        self.lfoot.baseCntrl.addAttr('twist', at='float', dv=0, k=1)
        self.lfoot.baseCntrl.pin >> self.lleg.ikCntrl.pin
        self.lfoot.baseCntrl.bias >> self.lleg.ikCntrl.bias
        self.lfoot.baseCntrl.autoStretch >> self.lleg.ikCntrl.autoStretch
        self.lfoot.baseCntrl.manualStretch >> self.lleg.ikCntrl.manualStretch
        self.lfoot.baseCntrl.twist >> self.lleg.ikCntrl.twist

        self.rfoot.baseCntrl.addAttr('pin', at='float', min=0, max=1, dv=0, k=1)
        self.rfoot.baseCntrl.addAttr('bias', at='float', min=-0.9, max=0.9, k=1)
        self.rfoot.baseCntrl.addAttr('autoStretch', at='float', min=0, max=1, dv=1, k=1)
        self.rfoot.baseCntrl.addAttr('manualStretch', at='float', dv=1, k=1)
        self.rfoot.baseCntrl.addAttr('twist', at='float', dv=0, k=1)
        self.rfoot.baseCntrl.pin >> self.rleg.ikCntrl.pin
        self.rfoot.baseCntrl.bias >> self.rleg.ikCntrl.bias
        self.rfoot.baseCntrl.autoStretch >> self.rleg.ikCntrl.autoStretch
        self.rfoot.baseCntrl.manualStretch >> self.rleg.ikCntrl.manualStretch
        self.rfoot.baseCntrl.twist >> self.rleg.ikCntrl.twist

    def generateSpaceSwitches(self):
        if pm.objExists('spaces'):
            pm.delete('spaces')

        rigFunctions.createSpc(None, 'global')
        rigFunctions.createSpc(self.larm.lastJnt, 'lhand')
        rigFunctions.createSpc(self.rarm.lastJnt, 'rhand')
        rigFunctions.createSpc(self.spine.cogCntrl, 'hip')
        rigFunctions.createSpc(self.spine.endJnt, 'chest')
        rigFunctions.createSpc(self.spine.startJnt, 'cog')
        rigFunctions.createSpc(self.lleg.lastJnt, 'lfoot')
        rigFunctions.createSpc(self.rleg.lastJnt, 'rfoot')
        rigFunctions.createSpc(self.lclav.jntList[-1], 'lclav')
        rigFunctions.createSpc(self.rclav.jntList[-1], 'rclav')
        rigFunctions.createSpc(self.neck.startJnt, 'neck')
        rigFunctions.createSpc(self.neck.endJnt, 'head')

        rigFunctions.addSpc(target=self.larm.ikCntrl, spaceList=['global', 'chest', 'cog', 'lclav'],
                            switcher=self.larm.ikCntrl.getParent(), type='parent')
        rigFunctions.addSpc(target=self.rarm.ikCntrl, spaceList=['global', 'chest', 'cog', 'rclav'],
                            switcher=self.rarm.ikCntrl.getParent(), type='parent')
        rigFunctions.addSpc(target=self.larm.poleVec, spaceList=['hip', 'global', 'chest', 'cog', 'lclav'],
                            switcher=self.larm.poleVec.getParent(), type='parent')
        rigFunctions.addSpc(target=self.rarm.poleVec, spaceList=['hip', 'global', 'chest', 'cog', 'rclav'],
                            switcher=self.rarm.poleVec.getParent(), type='parent')
        rigFunctions.addSpc(target=self.lleg.poleVec, spaceList=['hip', 'global', 'chest', 'cog'],
                            switcher=self.lleg.poleVec.getParent(), type='parent')
        rigFunctions.addSpc(target=self.rleg.poleVec, spaceList=['hip', 'global', 'chest', 'cog'],
                            switcher=self.rleg.poleVec.getParent(), type='parent')
        rigFunctions.addSpc(target=self.spine.endIkCntrl, spaceList=['hip', 'global', 'cog'],
                            switcher=self.spine.endIkCntrl.getParent(), type='parent')
        rigFunctions.addSpc(target=self.neck.endCntrl, spaceList=['global', 'hip', 'chest', 'cog', 'neck'],
                            switcher=self.neck.endCntrl.getParent(), type='orient', posSpc=self.neck.startJnt)
        rigFunctions.addSpc(target=self.larm.endCntrl, spaceList=['global', 'hip', 'chest', 'cog', 'lclav'],
                            switcher=self.larm.endCntrl.getParent(), type='orient', posSpc=self.lclav.jntList[-1])
        rigFunctions.addSpc(target=self.rarm.endCntrl, spaceList=['global', 'hip', 'chest', 'cog', 'rclav'],
                            switcher=self.rarm.endCntrl.getParent(), type='orient', posSpc=self.rclav.jntList[-1])