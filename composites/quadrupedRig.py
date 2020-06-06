import pymel.core as pm
import os.path
from autoRig3.modules import limbModule, footModule, spineModule, moveAllModule, chainModule, neckModule
from autoRig3.modules import ribbonBezier

import autoRig3.tools.spaceSwitchTools as spaceSwitchTools
import autoRig3.tools.skinTools as skinTools
import json
import logging

logger = logging.getLogger('autoRig')

class Quadruped:
    def __init__(self, rigName='character',
                 tailJnts=10,
                 footFingers=[(u'Thumb', 1),
                              (u'Index', 1),
                              (u'Middle', 1),
                              (u'Ring', 1),
                              (u'Pinky', 1)],
                 handFingers=[(u'Thumb', 1),
                              (u'Index', 1),
                              (u'Middle', 1),
                              (u'Ring', 1),
                              (u'Pinky', 1)],
                 moduleConnection=1,
                 armRibbonJnts=5,
                 armRibbonFirstOffset=1,
                 armRibbonLastOffset=1,
                 legRibbonJnts=5,
                 legRibbonFirstOffset=1,
                 legRibbonLastOffset=1,
                 spineRibbonJnts=5,
                 progressBar=None):

        self.name = rigName
        self.handFingers = handFingers
        self.footFingers = footFingers
        self.armRibbonJnts = armRibbonJnts
        self.armRibbonFirstOffset = armRibbonFirstOffset
        self.armRibbonLastOffset = armRibbonLastOffset
        self.legRibbonJnts = legRibbonJnts
        self.legRibbonFirstOffset = legRibbonFirstOffset
        self.legRibbonLastOffset = legRibbonLastOffset
        self.spineRibbonJnts = spineRibbonJnts
        self.moduleConnection = moduleConnection
        self.progressBar = progressBar
        self.tailJnts = tailJnts
        self.skinJoints = []
        self.modelList = []

        self.toExport = {'name',
                         'handFingers',
                         'footFingers',
                         'armRibbonJnts',
                         'armRibbonFirstOffset',
                         'armRibbonLastOffset',
                         'legRibbonJnts',
                         'legRibbonFirstOffset',
                         'legRibbonLastOffset',
                         'spineRibbonJnts',
                         'moduleConnection',
                         'tailJnts'
                         }

        self.lfrFoot = footModule.Foot(name='L_fr_foot', fingers=self.handFingers)
        self.rfrFoot = footModule.Foot(name='R_fr_foot', fingers=self.handFingers)
        self.lbkFoot = footModule.Foot(name='L_bk_foot', fingers=self.footFingers)
        self.rbkFoot = footModule.Foot(name='R_bk_foot', fingers=self.footFingers)
        self.neck = neckModule.Neck(name='neck')
        self.spine = spineModule.Spine(name='spine', ribbonJntNum=self.skinJoints)

        self.lbkLeg = limbModule.Limb(name='L_bk_leg')
        self.rbkLeg = limbModule.Limb(name='R_bk_leg')
        self.lfrLeg = limbModule.Limb(name='L_fr_leg')
        self.rfrLeg = limbModule.Limb(name='R_fr_leg')

        self.llegShoulder = chainModule.Chain(name='L_legShoulder')
        self.rlegShoulder = chainModule.Chain(name='R_legShoulder')
        self.lclav = chainModule.Chain(name='L_clavicle')
        self.rclav = chainModule.Chain(name='R_clavicle')

        if self.tailJnts > 0:
            self.tail = chainModule.Chain(name='tail', divNum=self.tailJnts)
        else:
            self.tail = None

        self.master = moveAllModule.Moveall(name=rigName)
        self.setDefaultDicts()

        handFingerList = [x[0] for x in self.handFingers]
        self.lfrFoot.fingers = {key: value for key, value in self.lfrFoot.fingers.iteritems() if key in handFingerList}
        self.rfrFoot.fingers = {key: value for key, value in self.rfrFoot.fingers.iteritems() if key in handFingerList}

        footFingerList = [x[0] for x in self.footFingers]
        self.lbkFoot.fingers = {key: value for key, value in self.lbkFoot.fingers.iteritems() if key in footFingerList}
        self.rbkFoot.fingers = {key: value for key, value in self.rbkFoot.fingers.iteritems() if key in footFingerList}


        handFingerList = [x[0] for x in self.handFingers]
        for i, finger in enumerate(handFingerList):
            try:
                self.lfrFoot.fingers[finger]['fingerId'] = i
                self.rfrFoot.fingers[finger]['fingerId'] = i
            except:
                pass

        footFingerList = [x[0] for x in self.footFingers]
        for i, finger in enumerate(footFingerList):
            try:
                self.lbkFoot.fingers[finger]['fingerId'] = i
                self.rbkFoot.fingers[finger]['fingerId'] = i
            except:
                pass


    def setDefaultDicts(self):
        tailDict = { 'name': 'tail',
                     'moveAllCntrlSetup': {'nameTempl': 'tailMoveall', 'icone': 'circuloX',
                                           'color': (1, 1, 0), 'size': 2.5},
                     'fkCntrlSetup': {'nameTempl': 'tailChainFk', 'icone': 'circuloX', 'color': (0.01, 0.05, 0.2),
                                      'size': 0.8},
                     'flipAxis': False,
                     'jntSetup': {'nameTempl': 'tailChain', 'icone': 'Bone', 'size': 0.8},
                     'guideSetup': {'nameTempl': 'tailChain','icone': 'circuloX',
                                    'color': (0.010, 0.050, 0.2), 'size': 0.8}, 'axis': 'X'
                     }

        larmDict = {
                    'moveallGuideSetup': {'nameTempl': 'L_armMoveAll', 'icone': 'quadradoX', 'color': (1, 1, 0), 'size': 1},
                    'poleVecCntrlSetup': {'nameTempl': 'L_armPoleVec', 'icone': 'bola', 'color': (0.010, 0.050, 0.2),
                                          'size': 0.4},
                    'name': 'L_arm',
                    'axis': 'X',
                    'flipAxis': False,
                    'startJntSetup': {'nameTempl': 'L_armStart', 'size': 1},
                    'endJntSetup': {'nameTempl': 'L_armEnd', 'size': 1},
                    'midJntSetup': {'nameTempl': 'L_armMid', 'size': 1},
                    'lastJoint': True,
                    'lastJntSetup': {'nameTempl': 'L_armLast', 'size': 1},
                    'guideDict': {'start': [(0.0, 0.0, 0.0), (0.0, -0.0, 0.0), (1.0, 1.0, 1.0)],
                                  'moveall': [(1.82, 10.0, 9.73), (0.0, -0.0, -90), (1.0, 1.0, 1.0)],
                                  'end': [(9, 0.0, 0.0), (0.0, -0.0, 0.0), (1.0, 1.0, 1.0)],
                                  'mid': [(4.5, 0, -0.5), (0.0, -0.0, 0.0), (1.0, 1.0, 1.0)],
                                  'last': [(1.0, 0.0, 0.0), (0.0, -0.0, 0.0), (1.0, 1.0, 1.0)]},

                    'startGuideSetup': {'nameTempl': 'L_armStart', 'icone': 'circuloX', 'color': (1, 1, 0), 'size': 1},
                    'midGuideSetup': {'nameTempl': 'L_armMid', 'icone': 'circuloX', 'color': (1, 1, 0), 'size': 1},
                    'endGuideSetup': {'nameTempl': 'L_armEnd', 'icone': 'circuloX', 'color': (1, 1, 0), 'size': 1},
                    'lastGuideSetup': {'nameTempl': 'L_armLast', 'icone': 'circuloX', 'color': (1, 1, 0), 'size': 1},

                    'moveAll1CntrlSetup': {'nameTempl': 'L_armMoveAll', 'icone': 'grp', 'color': (1, 1, 0),
                                           'size': 1.8},
                    'startCntrlSetup': {'nameTempl': 'L_armFkStart', 'icone': 'cubo', 'color': (0.010, 0.050, 0.2), 'size': 1.5},
                    'midCntrlSetup': {'nameTempl': 'L_armFkMid', 'icone': 'cubo', 'color': (0.010, 0.050, 0.2), 'size': 1.5},
                    'endCntrlSetup': {'nameTempl': 'L_armFkEnd', 'icone': 'cubo', 'color': (0.010, 0.050, 0.2), 'size': 1.5},
                    'ikCntrlSetup': {'nameTempl': 'L_armIk', 'icone': 'circuloX', 'color': (0.010, 0.050, 0.2), 'size': 1}
                    }

        rarmDict = {'moveallGuideSetup': {'nameTempl': 'R_armMoveAll', 'icone': 'quadradoX', 'color': (1, 1, 0), 'size': 1},
                    'poleVecCntrlSetup': {'nameTempl': 'R_armPoleVec', 'icone': 'bola', 'color': (0.4, 0, 0),
                                          'size': 0.4},
                    'name': 'R_arm',
                    'axis': 'X',
                    'flipAxis': False,
                    'startJntSetup': {'nameTempl': 'R_armStart', 'size': 1},
                    'endJntSetup': {'nameTempl': 'R_armEnd', 'size': 1},
                    'midJntSetup': {'nameTempl': 'R_armMid', 'size': 1},
                    'lastJoint': True,
                    'lastJntSetup': {'nameTempl': 'R_armLast', 'size': 1},
                    'guideDict': {'start': [(0.0, 0.0, 0.0), (0.0, -0.0, 0.0), (1.0, 1.0, 1.0)],
                                  'moveall': [(1.82, 10, 0), (0.0, -0.0, -90), (1.0, 1.0, 1.0)],
                                  'end': [(9, 0.0, 0.0), (0.0, -0.0, 0.0), (1.0, 1.0, 1.0)],
                                  'mid': [(4.5, 0, -0.5), (0.0, -0.0, 0.0), (1.0, 1.0, 1.0)],
                                  'last': [(1.0, 0.0, 0.0), (0.0, -0.0, 0.0), (1.0, 1.0, 1.0)]},

                    'startGuideSetup': {'nameTempl': 'R_armStart', 'icone': 'circuloX', 'color': (1, 1, 0), 'size': 1},
                    'midGuideSetup': {'nameTempl': 'R_armMid', 'icone': 'circuloX', 'color': (1, 1, 0), 'size': 1},
                    'endGuideSetup': {'nameTempl': 'R_armEnd', 'icone': 'circuloX', 'color': (1, 1, 0), 'size': 1},
                    'lastGuideSetup': {'nameTempl': 'R_armLast', 'icone': 'circuloX', 'color': (1, 1, 0), 'size': 1},

                    'moveAll1CntrlSetup': {'nameTempl': 'R_armMoveAll', 'icone': 'grp', 'color': (1, 1, 0),
                                           'size': 1.8},
                    'startCntrlSetup': {'nameTempl': 'R_armFkStart', 'icone': 'cubo', 'color': (0.4, 0, 0), 'size': 1.5},
                    'midCntrlSetup': {'nameTempl': 'R_armFkMid', 'icone': 'cubo', 'color': (0.4, 0, 0), 'size': 1.5},
                    'endCntrlSetup': {'nameTempl': 'R_armFkEnd', 'icone': 'cubo', 'color': (0.4, 0, 0), 'size': 1.5},
                    'ikCntrlSetup': {'nameTempl': 'R_armIk', 'icone': 'circuloX', 'color': (0.4, 0, 0), 'size': 1}
                    }

        llegDict = {'name': 'L_leg',

                    'guideDict': {'start': [(0.0, 0.0, 0.0), (0.0, -0.0, 0.0), (1.0, 1.0, 1.0)],
                                  'moveall': [(1.82, 10, 0.0), (0.0, 0.0, -90), (1.0, 1.0, 1.0)],
                                  'end': [(9, 0, 0.0), (0.0, -0.0, 0.0), (1.0, 1.0, 1.0)],
                                  'mid': [(4.5, 0.0, 0.5), (0.0, -0.0, 0.0), (1.0, 1.0, 1.0)],
                                  'last': [(1.0, 0.0, 0.0), (0.0, -0.0, 0.0), (1.0, 1.0, 1.0)]},

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

                    'poleVecCntrlSetup': {'nameTempl': 'L_legPoleVec', 'icone': 'bola', 'color': (0.010, 0.050, 0.2), 'size': 0.4},
                    'moveAll1CntrlSetup': {'nameTempl': 'L_legMoveAll', 'icone': 'grp', 'color': (1, 1, 0), 'size': 1.8},
                    'ikCntrlSetup': {'nameTempl': 'L_footIk', 'icone': 'grp', 'color': (1, 1, 0), 'size': 0.8},
                    'startCntrlSetup': {'nameTempl': 'L_legFkStart', 'icone': 'cubo', 'color': (0.01, 0.05, 0.2), 'size': 1.5},
                    'midCntrlSetup': {'nameTempl': 'L_legFkMid', 'icone': 'cubo', 'color': (0.01, 0.05, 0.2), 'size': 1.5},
                    'endCntrlSetup': {'nameTempl': 'L_legFkEnd', 'icone': 'cubo', 'color': (0.01, 0.05, 0.2), 'size': 1.5},
                    'axis': 'X'}

        rlegDict = {'name': 'R_leg',

                    'guideDict': {'start': [(0.0, 0.0, 0.0), (0.0, -0.0, 0.0), (1.0, 1.0, 1.0)],
                                  'moveall': [(1.82, 10, 0.0), (0.0, 0.0, -90), (1.0, 1.0, 1.0)],
                                  'end': [(9, 0, 0.0), (0.0, -0.0, 0.0), (1.0, 1.0, 1.0)],
                                  'mid': [(4.5, 0.0, 0.5), (0.0, -0.0, 0.0), (1.0, 1.0, 1.0)],
                                  'last': [(1.0, 0.0, 0.0), (0.0, -0.0, 0.0), (1.0, 1.0, 1.0)]},

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
                    'poleVecCntrlSetup': {'nameTempl': 'R_legPoleVec', 'icone': 'bola', 'color': (.4, 0, 0),
                                          'size': 0.4},
                    'moveAll1CntrlSetup': {'nameTempl': 'R_legMoveAll', 'icone': 'grp', 'color': (1, 1, 0),
                                           'size': 1.8},
                    'ikCntrlSetup': {'nameTempl': 'R_footIk', 'icone': 'grp', 'color': (1, 1, 0), 'size': 0.8},
                    'startCntrlSetup': {'nameTempl': 'R_legFkStart', 'icone': 'cubo', 'color': (.4, 0, 0),
                                        'size': 1.5},
                    'midCntrlSetup': {'nameTempl': 'R_legFkMid', 'icone': 'cubo', 'color': (.4, 0, 0), 'size': 1.5},
                    'endCntrlSetup': {'nameTempl': 'R_legFkEnd', 'icone': 'cubo', 'color': (.4, 0, 0), 'size': 1.5},

                    'axis': 'X'}

        lhandDict = {'slideCntrlSetup': {'nameTempl': 'L_fr_footSlide', 'icone': 'bola', 'color': (0.01, 0.05, 0.2), 'size': 0.4},
                     'tipCntrlSetup': {'nameTempl': 'L_fr_footTip', 'icone': 'bola', 'color': (0.01, 0.05, 0.2), 'size': 0.5},
                     'moveallCntrlSetup': {'nameTempl': 'L_fr_footMoveAll', 'icone': 'circuloX', 'color': (1, 1, 0),
                                           'size': 1.8},
                     'toLimbCntrlSetup': {'nameTempl': 'L_fr_footToLimb', 'icone': 'grp', 'color': (0.01, 0.05, 0.2),
                                          'size': 0.5},
                     'ankleFkCntrlSetup': {'nameTempl': 'L_fr_footTnkleFk', 'icone': 'grp', 'color': (0, 1, 0),
                                           'size': 1.0},
                     'jointGuideSetup': {'nameTempl': 'L_fr_footJoint', 'icone': 'null', 'color': (1, 0, 1), 'size': 0.5},
                     'axis': 'X',
                     'toeFkCntrlSetup': {'nameTempl': 'L_fr_footToeFk', 'icone': 'cubo', 'color': (0.01, 0.05, 0.2),
                                         'size': 1.0},
                     'inGuideSetup': {'nameTempl': 'L_fr_footIn', 'icone': 'bola', 'color': (0, 0, 1), 'size': 0.4},
                     'ankleJntSetup': {'nameTempl': 'L_fr_footAnkle', 'icone': 'Bone', 'size': 1.0},
                     'ballGuideSetup': {'nameTempl': 'L_fr_footBall', 'icone': 'bola', 'color': (0, 1, 1), 'size': 0.5},
                     'ankleGuideSetup': {'nameTempl': 'L_fr_footAnkle', 'icone': 'bola', 'color': (0, 1, 1), 'size': 0.5},
                     'rollCntrlSetup': {'nameTempl': 'L_fr_footRoll', 'icone': 'cubo', 'color': (0.01, 0.05, 0.2), 'size': 0.4},
                     'rollGuideSetup': {'nameTempl': 'L_fr_footRoll', 'icone': 'bola', 'color': (1, 0, 1), 'size': 0.4},
                     'outGuideSetup': {'nameTempl': 'L_fr_footOut', 'icone': 'bola', 'color': (0, 0, 1), 'size': 0.4},
                     'toeGuideSetup': {'nameTempl': 'L_fr_footToe', 'icone': 'null', 'color': (1, 1, 0), 'size': 1.0},
                     'fingerNames': ['Thumb', 'Index', 'Middle', 'Ring', 'Pinky', 'Other', 'Other1'],
                     'outCntrlSetup': {'nameTempl': 'L_fr_footOut', 'icone': 'bola', 'color': (0.01, 0.05, 0.2), 'size': 0.4},
                     'heelGuideSetup': {'nameTempl': 'L_fr_footHeel', 'icone': 'bola', 'color': (0, 1, 1), 'size': 0.5},

                     'fingers': {
                         'Ring': {
                                     'fold2CntrlSetup': {'nameTempl': u'L_fr_footRingfold2', 'icone': 'circuloX',
                                                         'color': (0.4, 0, 0),'size': 0.3},
                                     'folds': 1,
                                     'moveallCntrlSetup': {'nameTempl': u'L_fr_footRingMoveAll', 'icone': 'circuloX',
                                                           'color': (.4, 0, 0), 'size': 0.1},
                                     'guideDict':   {
                                                     'moveall': [(-0.85, 0, -0.5), (0.0, 0, 0.0), (1.0, 1.0, 1.0)],
                                                     'palm': [(0.0, 0.0, 0.0), (0.0, 0.0, 0.0)],
                                                     'base': [(0.3, 0.0, 0.0), (0.0, 0.0, 0)],
                                                     'fold2': [(0, 0, 0), (0, 0, 0)],
                                                     'fold1': [(0.0, -0.05, 0.0), (0.0, 0.0, 0.0)],
                                                     'tip': [(0.8, 0.0, 0.0), (0.0, 0.0, 0)]
                                                    },
                                     'fold1GuideSetup': {'nameTempl': u'L_fr_footRingfold1', 'icone': 'circuloX', 'color': (0, 0, 1),
                                                         'size': 0.4},
                                     'baseJntSetup': {'nameTempl': u'L_fr_footRingBase', 'icone': 'Bone', 'size': 0.3},
                                     'fold2JntSetup': {'nameTempl': u'L_fr_footRingFold2', 'icone': 'Bone', 'size': 0.3},
                                     'isHeelFinger': False,
                                     'baseGuideSetup': {'nameTempl': u'L_fr_footRingbase', 'icone': 'circuloX', 'color': (0, 0, 1),
                                                        'size': 0.4},
                                     'fold1CntrlSetup': {'nameTempl': u'L_fr_footRingfold1', 'icone': 'circuloX', 'color': (.4, 0, 0),
                                                         'size': 0.3},
                                     'fold2GuideSetup': {'nameTempl': u'L_fr_footRingfold2', 'icone': 'circuloX', 'color': (0, 0, 1),
                                                         'size': 0.4}, 'axis': 'X',
                                     'fold1JntSetup': {'nameTempl': u'L_fr_footRingFold1', 'icone': 'Bone', 'size': 0.3},
                                     'moveallGuideSetup': {'nameTempl': u'L_fr_footRingMoveAll', 'icone': 'quadradoX',
                                                           'color': (0.6, 0, 0), 'size': 0.5}, 'name': u'L_fr_footRing',
                                     'tipGuideSetup': {'nameTempl': u'L_fr_footRingtip', 'icone': 'circuloX', 'color': (0, 0, 1),
                                                       'size': 0.4},
                                     'baseCntrlSetup': {'nameTempl': u'L_fr_footRingbase', 'icone': 'dropMenosZ', 'color': (.4, 0, 0),
                                                        'size': 0.1},
                                     'palmJntSetup': {'nameTempl': u'L_fr_footRingPalm', 'icone': 'Bone', 'size': 0.2},
                                     'palmCntrlSetup': {'nameTempl': u'L_fr_footRingpalm', 'icone': 'cubo', 'color': (.4, 0, 0),
                                                        'size': 0.2},
                                     'palmGuideSetup': {'nameTempl': u'L_fr_footRingpalm', 'icone': 'circuloX', 'color': (0, 0, 1),
                                                        'size': 0.4}, 'flipAxis': False,
                                     'tipJntSetup': {'nameTempl': u'L_fr_footRing', 'icone': 'Bone', 'size': 0.3}},

                         'Pinky': {
                                     'fold2CntrlSetup': {'nameTempl': u'L_fr_footPinkyfold2', 'icone': 'circuloX', 'color': (.4, 0, 0),
                                                         'size': 0.3}, 'folds': 1,
                                     'moveallCntrlSetup': {'nameTempl': u'L_fr_footPinkyMoveAll', 'icone': 'circuloX',
                                                           'color': (.4, 0, 0), 'size': 0.1},
                                     'guideDict':   {
                                                     'moveall': [(-0.85, 0, -1),(0.0, 0, 0.0), (1.0, 1.0, 1.0)],
                                                     'palm': [(0.0, 0.0, 0.0), (0.0, 0.0, 0.0)],
                                                     'base': [(0.3, 0.0, 0.0), (0.0, 0.0, 0)],
                                                     'fold2': [(0, 0, 0), (0, 0, 0)],
                                                     'fold1': [(0.0, -0.05, 0.0), (0.0, 0.0, 0.0)],
                                                     'tip': [(0.8, 0.0, 0.0), (0.0, 0.0, 0)]
                                                    },

                                     'fold1GuideSetup': {'nameTempl': u'L_fr_footPinkyfold1', 'icone': 'circuloX', 'color': (0, 0, 1),
                                                         'size': 0.4},
                                     'baseJntSetup': {'nameTempl': u'L_fr_footPinkyBase', 'icone': 'Bone', 'size': 0.3},
                                     'fold2JntSetup': {'nameTempl': u'L_fr_footPinkyFold2', 'icone': 'Bone', 'size': 0.3},
                                     'isHeelFinger': False,
                                     'baseGuideSetup': {'nameTempl': u'L_fr_footPinkybase', 'icone': 'circuloX', 'color': (0, 0, 1),
                                                        'size': 0.4},
                                     'fold1CntrlSetup': {'nameTempl': u'L_fr_footPinkyfold1', 'icone': 'circuloX', 'color': (.4, 0, 0),
                                                         'size': 0.3},
                                     'fold2GuideSetup': {'nameTempl': u'L_fr_footPinkyfold2', 'icone': 'circuloX', 'color': (0, 0, 1),
                                                         'size': 0.4}, 'axis': 'X',
                                     'fold1JntSetup': {'nameTempl': u'L_fr_footPinkyFold1', 'icone': 'Bone', 'size': 0.3},
                                     'moveallGuideSetup': {'nameTempl': u'L_fr_footPinkyMoveAll', 'icone': 'quadradoX',
                                                           'color': (0.6, 0, 0), 'size': 0.5}, 'name': u'L_fr_footPinky',
                                     'tipGuideSetup': {'nameTempl': u'L_fr_footPinkytip', 'icone': 'circuloX', 'color': (0, 0, 1),
                                                       'size': 0.4},
                                     'baseCntrlSetup': {'nameTempl': u'L_fr_footPinkybase', 'icone': 'dropMenosZ', 'color': (.4, 0, 0),
                                                        'size': 0.1},
                                     'palmJntSetup': {'nameTempl': u'L_fr_footPinkyPalm', 'icone': 'Bone', 'size': 0.2},
                                     'palmCntrlSetup': {'nameTempl': u'L_fr_footPinkypalm', 'icone': 'cubo', 'color': (.4, 0, 0),
                                                        'size': 0.2},
                                     'palmGuideSetup': {'nameTempl': u'L_fr_footPinkypalm', 'icone': 'circuloX', 'color': (0, 0, 1),
                                                        'size': 0.4}, 'flipAxis': False,
                                     'tipJntSetup': {'nameTempl': u'L_fr_footPinky', 'icone': 'Bone', 'size': 0.3}},

                         'Index': {
                                     'fold2CntrlSetup': {'nameTempl': u'L_fr_footIndexfold2', 'icone': 'circuloX', 'color': (.4, 0, 0),
                                                         'size': 0.3}, 'folds': 1,
                                     'moveallCntrlSetup': {'nameTempl': u'L_fr_footIndexMoveAll', 'icone': 'circuloX',
                                                           'color': (.4, 0, 0), 'size': 0.1},
                                     'guideDict':   {
                                                     'moveall': [(-0.85, 0, 0.5), (0.0, 0, 0.0), (1.0, 1.0, 1.0)],
                                                     'palm': [(0.0, 0.0, 0.0), (0.0, 0.0, 0.0)],
                                                     'base': [(0.3, 0.0, 0.0), (0.0, 0.0, 0)],
                                                     'fold2': [(0, 0, 0), (0, 0, 0)],
                                                     'fold1': [(0.0, -0.05, 0.0), (0.0, 0.0, 0.0)],
                                                     'tip': [(0.8, 0.0, 0.0), (0.0, 0.0, 0)]
                                                    },
                                     'fold1GuideSetup': {'nameTempl': u'L_fr_footIndexfold1', 'icone': 'circuloX', 'color': (0, 0, 1),
                                                         'size': 0.4},
                                     'baseJntSetup': {'nameTempl': u'L_fr_footIndexBase', 'icone': 'Bone', 'size': 0.3},
                                     'fold2JntSetup': {'nameTempl': u'L_fr_footIndexFold2', 'icone': 'Bone', 'size': 0.3},
                                     'isHeelFinger': False,
                                     'baseGuideSetup': {'nameTempl': u'L_fr_footIndexbase', 'icone': 'circuloX', 'color': (0, 0, 1),
                                                        'size': 0.4},
                                     'fold1CntrlSetup': {'nameTempl': u'L_fr_footIndexfold1', 'icone': 'circuloX', 'color': (.4, 0, 0),
                                                         'size': 0.3},
                                     'fold2GuideSetup': {'nameTempl': u'L_fr_footIndexfold2', 'icone': 'circuloX', 'color': (0, 0, 1),
                                                         'size': 0.4}, 'axis': 'X',
                                     'fold1JntSetup': {'nameTempl': u'L_fr_footIndexFold1', 'icone': 'Bone', 'size': 0.3},
                                     'moveallGuideSetup': {'nameTempl': u'L_fr_footIndexMoveAll', 'icone': 'quadradoX',
                                                           'color': (0.6, 0, 0), 'size': 0.5}, 'name': u'L_fr_footIndex',
                                     'tipGuideSetup': {'nameTempl': u'L_fr_footIndextip', 'icone': 'circuloX', 'color': (0, 0, 1),
                                                       'size': 0.4},
                                     'baseCntrlSetup': {'nameTempl': u'L_fr_footIndexbase', 'icone': 'dropMenosZ', 'color': (.4, 0, 0),
                                                        'size': 0.1},
                                     'palmJntSetup': {'nameTempl': u'L_fr_footIndexPalm', 'icone': 'Bone', 'size': 0.2},
                                     'palmCntrlSetup': {'nameTempl': u'L_fr_footIndexpalm', 'icone': 'cubo', 'color': (.4, 0, 0),
                                                        'size': 0.2},
                                     'palmGuideSetup': {'nameTempl': u'L_fr_footIndexpalm', 'icone': 'circuloX', 'color': (0, 0, 1),
                                                        'size': 0.4}, 'flipAxis': False,
                                     'tipJntSetup': {'nameTempl': u'L_fr_footIndex', 'icone': 'Bone', 'size': 0.3}},

                         'Middle': {
                                     'fold2CntrlSetup': {'nameTempl': u'L_fr_footMiddlefold2', 'icone': 'circuloX', 'color': (.4, 0, 0),
                                                         'size': 0.3}, 'folds': 1,
                                     'moveallCntrlSetup': {'nameTempl': u'L_fr_footMiddleMoveAll', 'icone': 'circuloX',
                                                           'color': (.4, 0, 0), 'size': 0.1},
                                     'guideDict':   {
                                                     'moveall': [(-0.85, 0.0, 0), (0.0, 0.0, 0.0), (1.0, 1.0, 1.0)],
                                                     'palm': [(0.0, 0.0, 0.0), (0.0, 0.0, 0.0)],
                                                     'base': [(0.3, 0.0, 0.0), (0.0, -0.0, 0.0)],
                                                     'fold2': [(0, 0, 0), (0, 0, 0)],
                                                     'fold1': [(0.0, -0.05, 0.0), (0.0, 0.0, 0.0)],
                                                     'tip': [(0.8, 0.0, 0.0), (0.0, 0.0, 0.0)]
                                                    },
                                     'fold1GuideSetup': {'nameTempl': u'L_fr_footMiddlefold1', 'icone': 'circuloX', 'color': (0, 0, 1),
                                                         'size': 0.4},
                                     'baseJntSetup': {'nameTempl': u'L_fr_footMiddleBase', 'icone': 'Bone', 'size': 0.3},
                                     'fold2JntSetup': {'nameTempl': u'L_fr_footMiddleFold2', 'icone': 'Bone', 'size': 0.3},
                                     'isHeelFinger': False,
                                     'baseGuideSetup': {'nameTempl': u'L_fr_footMiddlebase', 'icone': 'circuloX', 'color': (0, 0, 1),
                                                        'size': 0.4},
                                     'fold1CntrlSetup': {'nameTempl': u'L_fr_footMiddlefold1', 'icone': 'circuloX', 'color': (.4, 0, 0),
                                                         'size': 0.3},
                                     'fold2GuideSetup': {'nameTempl': u'L_fr_footMiddlefold2', 'icone': 'circuloX', 'color': (0, 0, 1),
                                                         'size': 0.4}, 'axis': 'X',
                                     'fold1JntSetup': {'nameTempl': u'L_fr_footMiddleFold1', 'icone': 'Bone', 'size': 0.3},
                                     'moveallGuideSetup': {'nameTempl': u'L_fr_footMiddleMoveAll', 'icone': 'quadradoX',
                                                           'color': (0.6, 0, 0), 'size': 0.5}, 'name': u'L_fr_footMiddle',
                                     'tipGuideSetup': {'nameTempl': u'L_fr_footMiddletip', 'icone': 'circuloX', 'color': (0, 0, 1),
                                                       'size': 0.4},
                                     'baseCntrlSetup': {'nameTempl': u'L_fr_footMiddlebase', 'icone': 'dropMenosZ', 'color': (.4, 0, 0),
                                                        'size': 0.1},
                                     'palmJntSetup': {'nameTempl': u'L_fr_footMiddlePalm', 'icone': 'Bone', 'size': 0.2},
                                     'palmCntrlSetup': {'nameTempl': u'L_fr_footMiddlepalm', 'icone': 'cubo', 'color': (.4, 0, 0),
                                                        'size': 0.2},
                                     'palmGuideSetup': {'nameTempl': u'L_fr_footMiddlepalm', 'icone': 'circuloX', 'color': (0, 0, 1),
                                                        'size': 0.4}, 'flipAxis': False,
                                     'tipJntSetup': {'nameTempl': u'L_fr_footMiddle', 'icone': 'Bone', 'size': 0.3}},

                         'Thumb': {
                                     'fold2CntrlSetup': {'nameTempl': u'L_fr_footThumbfold2', 'icone': 'circuloX', 'color': (.4, 0, 0),
                                                     'size': 0.3}, 'folds': 1,
                                     'moveallCntrlSetup': {'nameTempl': u'L_fr_footThumbMoveAll', 'icone': 'circuloX',
                                                           'color': (.4, 0, 0), 'size': 0.1},
                                     'guideDict':   {
                                                     'moveall': [(-0.85, 0.0, 1), (0.0, 0.0, 0.0), (1.0, 1.0, 1.0)],
                                                     'palm': [(0.0, 0.0, 0.0), (0.0, -0.0, 0.0)],
                                                     'base': [(0.3, 0.0, 0.0),(0.0, 0.0, 0.0)],
                                                     'fold2': [(0, 0, 0), (0, 0, 0)],
                                                     'fold1': [(0.0, -0.05, 0.0), (0.0, -0.0, 0.0)],
                                                     'tip': [(0.8, 0.0, 0.0),(0.0, 0.0, 0.0)]
                                                    },
                                     'fold1GuideSetup': {'nameTempl': u'L_fr_footThumbfold1', 'icone': 'circuloX', 'color': (0, 0, 1),
                                                         'size': 0.4},
                                     'baseJntSetup': {'nameTempl': u'L_fr_footThumbBase', 'icone': 'Bone', 'size': 0.3},
                                     'fold2JntSetup': {'nameTempl': u'L_fr_footThumbFold2', 'icone': 'Bone', 'size': 0.3},
                                     'isHeelFinger': False,
                                     'baseGuideSetup': {'nameTempl': u'L_fr_footThumbbase', 'icone': 'circuloX', 'color': (0, 0, 1),
                                                        'size': 0.4},
                                     'fold1CntrlSetup': {'nameTempl': u'L_fr_footThumbfold1', 'icone': 'circuloX', 'color': (.4, 0, 0),
                                                         'size': 0.3},
                                     'fold2GuideSetup': {'nameTempl': u'L_fr_footThumbfold2', 'icone': 'circuloX', 'color': (0, 0, 1),
                                                         'size': 0.4}, 'axis': 'X',
                                     'fold1JntSetup': {'nameTempl': u'L_fr_footThumbFold1', 'icone': 'Bone', 'size': 0.3},
                                     'moveallGuideSetup': {'nameTempl': u'L_fr_footThumbMoveAll', 'icone': 'quadradoX',
                                                           'color': (0.6, 0, 0), 'size': 0.5}, 'name': u'L_fr_footThumb',
                                     'tipGuideSetup': {'nameTempl': u'L_fr_footThumbtip', 'icone': 'circuloX', 'color': (0, 0, 1),
                                                       'size': 0.4},
                                     'baseCntrlSetup': {'nameTempl': u'L_fr_footThumbbase', 'icone': 'dropMenosZ', 'color': (.4, 0, 0),
                                                        'size': 0.1},
                                     'palmJntSetup': {'nameTempl': u'L_fr_footThumbPalm', 'icone': 'Bone', 'size': 0.2},
                                     'palmCntrlSetup': {'nameTempl': u'L_fr_footThumbpalm', 'icone': 'cubo', 'color': (.4, 0, 0),
                                                        'size': 0.2},
                                     'palmGuideSetup': {'nameTempl': u'L_fr_footThumbpalm', 'icone': 'circuloX', 'color': (0, 0, 1),
                                                        'size': 0.4}, 'flipAxis': False,
                                     'tipJntSetup': {'nameTempl': u'L_fr_footThumb', 'icone': 'Bone', 'size': 0.3}}
                     },

                     'heelCntrlSetup': {'nameTempl': 'L_fr_footHeel', 'icone': 'bola', 'color': (0.01, 0.05, 0.2), 'size': 0.5},
                     'ballCntrlSetup': {'nameTempl': 'L_fr_footBall', 'icone': 'circuloX', 'color': (0.01, 0.05, 0.2),
                                        'size': 1.5},
                     'baseGuideSetup': {'nameTempl': 'L_fr_footBase', 'icone': 'quadradoY', 'color': (1, 0, 1), 'size': 3},
                     'name': 'L_fr_foot',
                     'moveallGuideSetup': {'nameTempl': 'L_fr_footMoveAll', 'icone': 'quadradoY', 'color': (1, 0, 0),
                                           'size': 1.8},
                     'slideGuideSetup': {'nameTempl': 'L_fr_footSlide', 'icone': 'null', 'color': (1, 0, 1), 'size': 0.4},
                     'centerCntrlSetup': {'nameTempl': 'L_fr_footCenter', 'icone': 'circuloX', 'color': (0.01, 0.05, 0.2),
                                          'size': 2},
                     'baseCntrlSetup': {'nameTempl': 'L_fr_footBase', 'icone': 'quadradoY', 'color': (0.01, 0.05, 0.2), 'size': 3},
                     'toeCntrlSetup': {'nameTempl': 'L_fr_footToe', 'icone': 'circuloX', 'color': (0.01, 0.05, 0.2), 'size': 1.0},
                     'toeJntSetup': {'nameTempl': 'L_fr_footToe', 'icone': 'Bone', 'size': 1.0},
                     'ankleCntrlSetup': {'nameTempl': 'L_fr_footAnkle', 'icone': 'cubo', 'color': (0.01, 0.05, 0.2), 'size': 1},
                     'centerGuideSetup': {'nameTempl': 'L_fr_footCenter', 'icone': 'grp', 'color': (1, 1, 0), 'size': 0.5},
                     'flipAxis': False,
                     'inCntrlSetup': {'nameTempl': 'L_fr_footIn', 'icone': 'bola', 'color': (0.01, 0.05, 0.2), 'size': 0.4},
                     'tipGuideSetup': {'nameTempl': 'L_fr_footTip', 'icone': 'bola', 'color': (0, 1, 1), 'size': 0.5},

                     'guideDict': {'ball': [(-1.0, 0.5, 0.0), (0.0, -0.0, 0.0), (1.0, 1.0, 1.0)],
                                   'center': [(0.0, 0.0, 0.0), (0.0, 0.0, 0.0), (1.0, 1.0, 1.0)],
                                   'tip': [(3.0, 0.0, 0.0), (0.0, -0.0, 0.0), (1.0, 1.0, 1.0)],
                                   'moveall': [(1.82, 0, 9.73), (0.0, -90.0, 0.0), (1.0, 1.0, 1.0)],
                                   'in': [(-1.0, 0.0, -1.0), (0.0, -0.0, 0.0), (1.0, 1.0, 1.0)],
                                   'ankle': [(0.0, 1.0, 0.0), (0.0, -0.0, 0.0), (1.0, 1.0, 1.0)],
                                   'heel': [(-1.0, 0.0, 0.0), (0.0, -0.0, 0.0), (1.0, 1.0, 1.0)],
                                   'out': [(-1.0, 0.0, 1.0), (0.0, -0.0, 0.0), (1.0, 1.0, 1.0)]}}

        rhandDict = {'slideCntrlSetup': {'nameTempl': 'R_fr_footSlide', 'icone': 'bola', 'color': (.4, 0, 0), 'size': 0.4},
                     'tipCntrlSetup': {'nameTempl': 'R_fr_footTip', 'icone': 'bola', 'color': (0.01, 0.05, 0.2), 'size': 0.5},
                     'moveallCntrlSetup': {'nameTempl': 'R_fr_footMoveAll', 'icone': 'circuloX', 'color': (1, 1, 0),
                                           'size': 1.8},
                     'toLimbCntrlSetup': {'nameTempl': 'R_fr_footToLimb', 'icone': 'grp', 'color': (0.01, 0.05, 0.2),
                                          'size': 0.5},
                     'ankleFkCntrlSetup': {'nameTempl': 'R_fr_footTnkleFk', 'icone': 'grp', 'color': (0, 1, 0),
                                           'size': 1.0},
                     'jointGuideSetup': {'nameTempl': 'R_fr_footJoint', 'icone': 'null', 'color': (1, 0, 1), 'size': 0.5},
                     'axis': 'X',
                     'toeFkCntrlSetup': {'nameTempl': 'R_fr_footToeFk', 'icone': 'cubo', 'color': (0.01, 0.05, 0.2),
                                         'size': 1.0},
                     'inGuideSetup': {'nameTempl': 'R_fr_footIn', 'icone': 'bola', 'color': (0, 0, 1), 'size': 0.4},
                     'ankleJntSetup': {'nameTempl': 'R_fr_footAnkle', 'icone': 'Bone', 'size': 1.0},
                     'ballGuideSetup': {'nameTempl': 'R_fr_footBall', 'icone': 'bola', 'color': (0, 1, 1), 'size': 0.5},
                     'ankleGuideSetup': {'nameTempl': 'R_fr_footAnkle', 'icone': 'bola', 'color': (0, 1, 1), 'size': 0.5},
                     'rollCntrlSetup': {'nameTempl': 'R_fr_footRoll', 'icone': 'cubo', 'color': (.4, 0, 0), 'size': 0.4},
                     'rollGuideSetup': {'nameTempl': 'R_fr_footRoll', 'icone': 'bola', 'color': (1, 0, 1), 'size': 0.4},
                     'outGuideSetup': {'nameTempl': 'R_fr_footOut', 'icone': 'bola', 'color': (0, 0, 1), 'size': 0.4},
                     'toeGuideSetup': {'nameTempl': 'R_fr_footToe', 'icone': 'null', 'color': (1, 1, 0), 'size': 1.0},
                     'fingerNames': ['Thumb', 'Index', 'Middle', 'Ring', 'Pinky', 'Other', 'Other1'],
                     'outCntrlSetup': {'nameTempl': 'R_fr_footOut', 'icone': 'bola', 'color': (0.01, 0.05, 0.2), 'size': 0.4},
                     'heelGuideSetup': {'nameTempl': 'R_fr_footHeel', 'icone': 'bola', 'color': (0, 1, 1), 'size': 0.5},

                     'fingers': {
                         'Ring': {
                                     'fold2CntrlSetup': {'nameTempl': u'R_fr_footRingfold2', 'icone': 'circuloX',
                                                         'color': (0.4, 0, 0),'size': 0.3},
                                     'folds': 1,
                                     'moveallCntrlSetup': {'nameTempl': u'R_fr_footRingMoveAll', 'icone': 'circuloX',
                                                           'color': (.4, 0, 0), 'size': 0.1},
                                     'guideDict':   {
                                                     'moveall': [(-0.85, 0, -0.5), (0.0, 0, 0.0), (1.0, 1.0, 1.0)],
                                                     'palm': [(0.0, 0.0, 0.0), (0.0, 0.0, 0.0)],
                                                     'base': [(0.3, 0.0, 0.0), (0.0, 0.0, 0)],
                                                     'fold2': [(0, 0, 0), (0, 0, 0)],
                                                     'fold1': [(0.0, -0.05, 0.0), (0.0, 0.0, 0.0)],
                                                     'tip': [(0.8, 0.0, 0.0), (0.0, 0.0, 0)]
                                                    },
                                     'fold1GuideSetup': {'nameTempl': u'R_fr_footRingfold1', 'icone': 'circuloX', 'color': (0, 0, 1),
                                                         'size': 0.4},
                                     'baseJntSetup': {'nameTempl': u'R_fr_footRingBase', 'icone': 'Bone', 'size': 0.3},
                                     'fold2JntSetup': {'nameTempl': u'R_fr_footRingFold2', 'icone': 'Bone', 'size': 0.3},
                                     'isHeelFinger': False,
                                     'baseGuideSetup': {'nameTempl': u'R_fr_footRingbase', 'icone': 'circuloX', 'color': (0, 0, 1),
                                                        'size': 0.4},
                                     'fold1CntrlSetup': {'nameTempl': u'R_fr_footRingfold1', 'icone': 'circuloX', 'color': (.4, 0, 0),
                                                         'size': 0.3},
                                     'fold2GuideSetup': {'nameTempl': u'R_fr_footRingfold2', 'icone': 'circuloX', 'color': (0, 0, 1),
                                                         'size': 0.4}, 'axis': 'X',
                                     'fold1JntSetup': {'nameTempl': u'R_fr_footRingFold1', 'icone': 'Bone', 'size': 0.3},
                                     'moveallGuideSetup': {'nameTempl': u'R_fr_footRingMoveAll', 'icone': 'quadradoX',
                                                           'color': (0.6, 0, 0), 'size': 0.5}, 'name': u'R_fr_footRing',
                                     'tipGuideSetup': {'nameTempl': u'R_fr_footRingtip', 'icone': 'circuloX', 'color': (0, 0, 1),
                                                       'size': 0.4},
                                     'baseCntrlSetup': {'nameTempl': u'R_fr_footRingbase', 'icone': 'dropMenosZ', 'color': (.4, 0, 0),
                                                        'size': 0.1},
                                     'palmJntSetup': {'nameTempl': u'R_fr_footRingPalm', 'icone': 'Bone', 'size': 0.2},
                                     'palmCntrlSetup': {'nameTempl': u'R_fr_footRingpalm', 'icone': 'cubo', 'color': (.4, 0, 0),
                                                        'size': 0.2},
                                     'palmGuideSetup': {'nameTempl': u'R_fr_footRingpalm', 'icone': 'circuloX', 'color': (0, 0, 1),
                                                        'size': 0.4}, 'flipAxis': False,
                                     'tipJntSetup': {'nameTempl': u'R_fr_footRing', 'icone': 'Bone', 'size': 0.3}},

                         'Pinky': {
                                     'fold2CntrlSetup': {'nameTempl': u'R_fr_footPinkyfold2', 'icone': 'circuloX', 'color': (.4, 0, 0),
                                                         'size': 0.3}, 'folds': 1,
                                     'moveallCntrlSetup': {'nameTempl': u'R_fr_footPinkyMoveAll', 'icone': 'circuloX',
                                                           'color': (.4, 0, 0), 'size': 0.1},
                                     'guideDict':   {
                                                     'moveall': [(-0.85, 0, -1),(0.0, 0, 0.0), (1.0, 1.0, 1.0)],
                                                     'palm': [(0.0, 0.0, 0.0), (0.0, 0.0, 0.0)],
                                                     'base': [(0.3, 0.0, 0.0), (0.0, 0.0, 0)],
                                                     'fold2': [(0, 0, 0), (0, 0, 0)],
                                                     'fold1': [(0.0, -0.05, 0.0), (0.0, 0.0, 0.0)],
                                                     'tip': [(0.8, 0.0, 0.0), (0.0, 0.0, 0)]
                                                    },

                                     'fold1GuideSetup': {'nameTempl': u'R_fr_footPinkyfold1', 'icone': 'circuloX', 'color': (0, 0, 1),
                                                         'size': 0.4},
                                     'baseJntSetup': {'nameTempl': u'R_fr_footPinkyBase', 'icone': 'Bone', 'size': 0.3},
                                     'fold2JntSetup': {'nameTempl': u'R_fr_footPinkyFold2', 'icone': 'Bone', 'size': 0.3},
                                     'isHeelFinger': False,
                                     'baseGuideSetup': {'nameTempl': u'R_fr_footPinkybase', 'icone': 'circuloX', 'color': (0, 0, 1),
                                                        'size': 0.4},
                                     'fold1CntrlSetup': {'nameTempl': u'R_fr_footPinkyfold1', 'icone': 'circuloX', 'color': (.4, 0, 0),
                                                         'size': 0.3},
                                     'fold2GuideSetup': {'nameTempl': u'R_fr_footPinkyfold2', 'icone': 'circuloX', 'color': (0, 0, 1),
                                                         'size': 0.4}, 'axis': 'X',
                                     'fold1JntSetup': {'nameTempl': u'R_fr_footPinkyFold1', 'icone': 'Bone', 'size': 0.3},
                                     'moveallGuideSetup': {'nameTempl': u'R_fr_footPinkyMoveAll', 'icone': 'quadradoX',
                                                           'color': (0.6, 0, 0), 'size': 0.5}, 'name': u'R_fr_footPinky',
                                     'tipGuideSetup': {'nameTempl': u'R_fr_footPinkytip', 'icone': 'circuloX', 'color': (0, 0, 1),
                                                       'size': 0.4},
                                     'baseCntrlSetup': {'nameTempl': u'R_fr_footPinkybase', 'icone': 'dropMenosZ', 'color': (.4, 0, 0),
                                                        'size': 0.1},
                                     'palmJntSetup': {'nameTempl': u'R_fr_footPinkyPalm', 'icone': 'Bone', 'size': 0.2},
                                     'palmCntrlSetup': {'nameTempl': u'R_fr_footPinkypalm', 'icone': 'cubo', 'color': (.4, 0, 0),
                                                        'size': 0.2},
                                     'palmGuideSetup': {'nameTempl': u'R_fr_footPinkypalm', 'icone': 'circuloX', 'color': (0, 0, 1),
                                                        'size': 0.4}, 'flipAxis': False,
                                     'tipJntSetup': {'nameTempl': u'R_fr_footPinky', 'icone': 'Bone', 'size': 0.3}},

                         'Index': {
                                     'fold2CntrlSetup': {'nameTempl': u'R_fr_footIndexfold2', 'icone': 'circuloX', 'color': (.4, 0, 0),
                                                         'size': 0.3}, 'folds': 1,
                                     'moveallCntrlSetup': {'nameTempl': u'R_fr_footIndexMoveAll', 'icone': 'circuloX',
                                                           'color': (.4, 0, 0), 'size': 0.1},
                                     'guideDict':   {
                                                     'moveall': [(-0.85, 0, 0.5), (0.0, 0, 0.0), (1.0, 1.0, 1.0)],
                                                     'palm': [(0.0, 0.0, 0.0), (0.0, 0.0, 0.0)],
                                                     'base': [(0.3, 0.0, 0.0), (0.0, 0.0, 0)],
                                                     'fold2': [(0, 0, 0), (0, 0, 0)],
                                                     'fold1': [(0.0, -0.05, 0.0), (0.0, 0.0, 0.0)],
                                                     'tip': [(0.8, 0.0, 0.0), (0.0, 0.0, 0)]
                                                    },
                                     'fold1GuideSetup': {'nameTempl': u'R_fr_footIndexfold1', 'icone': 'circuloX', 'color': (0, 0, 1),
                                                         'size': 0.4},
                                     'baseJntSetup': {'nameTempl': u'R_fr_footIndexBase', 'icone': 'Bone', 'size': 0.3},
                                     'fold2JntSetup': {'nameTempl': u'R_fr_footIndexFold2', 'icone': 'Bone', 'size': 0.3},
                                     'isHeelFinger': False,
                                     'baseGuideSetup': {'nameTempl': u'R_fr_footIndexbase', 'icone': 'circuloX', 'color': (0, 0, 1),
                                                        'size': 0.4},
                                     'fold1CntrlSetup': {'nameTempl': u'R_fr_footIndexfold1', 'icone': 'circuloX', 'color': (.4, 0, 0),
                                                         'size': 0.3},
                                     'fold2GuideSetup': {'nameTempl': u'R_fr_footIndexfold2', 'icone': 'circuloX', 'color': (0, 0, 1),
                                                         'size': 0.4}, 'axis': 'X',
                                     'fold1JntSetup': {'nameTempl': u'R_fr_footIndexFold1', 'icone': 'Bone', 'size': 0.3},
                                     'moveallGuideSetup': {'nameTempl': u'R_fr_footIndexMoveAll', 'icone': 'quadradoX',
                                                           'color': (0.6, 0, 0), 'size': 0.5}, 'name': u'R_fr_footIndex',
                                     'tipGuideSetup': {'nameTempl': u'R_fr_footIndextip', 'icone': 'circuloX', 'color': (0, 0, 1),
                                                       'size': 0.4},
                                     'baseCntrlSetup': {'nameTempl': u'R_fr_footIndexbase', 'icone': 'dropMenosZ', 'color': (.4, 0, 0),
                                                        'size': 0.1},
                                     'palmJntSetup': {'nameTempl': u'R_fr_footIndexPalm', 'icone': 'Bone', 'size': 0.2},
                                     'palmCntrlSetup': {'nameTempl': u'R_fr_footIndexpalm', 'icone': 'cubo', 'color': (.4, 0, 0),
                                                        'size': 0.2},
                                     'palmGuideSetup': {'nameTempl': u'R_fr_footIndexpalm', 'icone': 'circuloX', 'color': (0, 0, 1),
                                                        'size': 0.4}, 'flipAxis': False,
                                     'tipJntSetup': {'nameTempl': u'R_fr_footIndex', 'icone': 'Bone', 'size': 0.3}},


                         'Middle': {
                                     'fold2CntrlSetup': {'nameTempl': u'R_fr_footMiddlefold2', 'icone': 'circuloX', 'color': (.4, 0, 0),
                                                         'size': 0.3}, 'folds': 1,
                                     'moveallCntrlSetup': {'nameTempl': u'R_fr_footMiddleMoveAll', 'icone': 'circuloX',
                                                           'color': (.4, 0, 0), 'size': 0.1},
                                     'guideDict':   {
                                                     'moveall': [(-0.85, 0.0, 0), (0.0, 0.0, 0.0), (1.0, 1.0, 1.0)],
                                                     'palm': [(0.0, 0.0, 0.0), (0.0, 0.0, 0.0)],
                                                     'base': [(0.3, 0.0, 0.0), (0.0, -0.0, 0.0)],
                                                     'fold2': [(0, 0, 0), (0, 0, 0)],
                                                     'fold1': [(0.0, -0.05, 0.0), (0.0, 0.0, 0.0)],
                                                     'tip': [(0.8, 0.0, 0.0), (0.0, 0.0, 0.0)]
                                                    },
                                     'fold1GuideSetup': {'nameTempl': u'R_fr_footMiddlefold1', 'icone': 'circuloX', 'color': (0, 0, 1),
                                                         'size': 0.4},
                                     'baseJntSetup': {'nameTempl': u'R_fr_footMiddleBase', 'icone': 'Bone', 'size': 0.3},
                                     'fold2JntSetup': {'nameTempl': u'R_fr_footMiddleFold2', 'icone': 'Bone', 'size': 0.3},
                                     'isHeelFinger': False,
                                     'baseGuideSetup': {'nameTempl': u'R_fr_footMiddlebase', 'icone': 'circuloX', 'color': (0, 0, 1),
                                                        'size': 0.4},
                                     'fold1CntrlSetup': {'nameTempl': u'R_fr_footMiddlefold1', 'icone': 'circuloX', 'color': (.4, 0, 0),
                                                         'size': 0.3},
                                     'fold2GuideSetup': {'nameTempl': u'R_fr_footMiddlefold2', 'icone': 'circuloX', 'color': (0, 0, 1),
                                                         'size': 0.4}, 'axis': 'X',
                                     'fold1JntSetup': {'nameTempl': u'R_fr_footMiddleFold1', 'icone': 'Bone', 'size': 0.3},
                                     'moveallGuideSetup': {'nameTempl': u'R_fr_footMiddleMoveAll', 'icone': 'quadradoX',
                                                           'color': (0.6, 0, 0), 'size': 0.5}, 'name': u'R_fr_footMiddle',
                                     'tipGuideSetup': {'nameTempl': u'R_fr_footMiddletip', 'icone': 'circuloX', 'color': (0, 0, 1),
                                                       'size': 0.4},
                                     'baseCntrlSetup': {'nameTempl': u'R_fr_footMiddlebase', 'icone': 'dropMenosZ', 'color': (.4, 0, 0),
                                                        'size': 0.1},
                                     'palmJntSetup': {'nameTempl': u'R_fr_footMiddlePalm', 'icone': 'Bone', 'size': 0.2},
                                     'palmCntrlSetup': {'nameTempl': u'R_fr_footMiddlepalm', 'icone': 'cubo', 'color': (.4, 0, 0),
                                                        'size': 0.2},
                                     'palmGuideSetup': {'nameTempl': u'R_fr_footMiddlepalm', 'icone': 'circuloX', 'color': (0, 0, 1),
                                                        'size': 0.4}, 'flipAxis': False,
                                     'tipJntSetup': {'nameTempl': u'R_fr_footMiddle', 'icone': 'Bone', 'size': 0.3}},


                         'Thumb': {
                                     'fold2CntrlSetup': {'nameTempl': u'R_fr_footThumbfold2', 'icone': 'circuloX', 'color': (.4, 0, 0),
                                                     'size': 0.3}, 'folds': 1,
                                     'moveallCntrlSetup': {'nameTempl': u'R_fr_footThumbMoveAll', 'icone': 'circuloX',
                                                           'color': (.4, 0, 0), 'size': 0.1},
                                     'guideDict':   {
                                                     'moveall': [(-0.85, 0.0, 1), (0.0, 0.0, 0.0), (1.0, 1.0, 1.0)],
                                                     'palm': [(0.0, 0.0, 0.0), (0.0, -0.0, 0.0)],
                                                     'base': [(0.3, 0.0, 0.0),(0.0, 0.0, 0.0)],
                                                     'fold2': [(0, 0, 0), (0, 0, 0)],
                                                     'fold1': [(0.0, -0.05, 0.0), (0.0, -0.0, 0.0)],
                                                     'tip': [(0.8, 0.0, 0.0),(0.0, 0.0, 0.0)]
                                                    },
                                     'fold1GuideSetup': {'nameTempl': u'R_fr_footThumbfold1', 'icone': 'circuloX', 'color': (0, 0, 1),
                                                         'size': 0.4},
                                     'baseJntSetup': {'nameTempl': u'R_fr_footThumbBase', 'icone': 'Bone', 'size': 0.3},
                                     'fold2JntSetup': {'nameTempl': u'R_fr_footThumbFold2', 'icone': 'Bone', 'size': 0.3},
                                     'isHeelFinger': False,
                                     'baseGuideSetup': {'nameTempl': u'R_fr_footThumbbase', 'icone': 'circuloX', 'color': (0, 0, 1),
                                                        'size': 0.4},
                                     'fold1CntrlSetup': {'nameTempl': u'R_fr_footThumbfold1', 'icone': 'circuloX', 'color': (.4, 0, 0),
                                                         'size': 0.3},
                                     'fold2GuideSetup': {'nameTempl': u'R_fr_footThumbfold2', 'icone': 'circuloX', 'color': (0, 0, 1),
                                                         'size': 0.4}, 'axis': 'X',
                                     'fold1JntSetup': {'nameTempl': u'R_fr_footThumbFold1', 'icone': 'Bone', 'size': 0.3},
                                     'moveallGuideSetup': {'nameTempl': u'R_fr_footThumbMoveAll', 'icone': 'quadradoX',
                                                           'color': (0.6, 0, 0), 'size': 0.5}, 'name': u'R_fr_footThumb',
                                     'tipGuideSetup': {'nameTempl': u'R_fr_footThumbtip', 'icone': 'circuloX', 'color': (0, 0, 1),
                                                       'size': 0.4},
                                     'baseCntrlSetup': {'nameTempl': u'R_fr_footThumbbase', 'icone': 'dropMenosZ', 'color': (.4, 0, 0),
                                                        'size': 0.1},
                                     'palmJntSetup': {'nameTempl': u'R_fr_footThumbPalm', 'icone': 'Bone', 'size': 0.2},
                                     'palmCntrlSetup': {'nameTempl': u'R_fr_footThumbpalm', 'icone': 'cubo', 'color': (.4, 0, 0),
                                                        'size': 0.2},
                                     'palmGuideSetup': {'nameTempl': u'R_fr_footThumbpalm', 'icone': 'circuloX', 'color': (0, 0, 1),
                                                        'size': 0.4}, 'flipAxis': False,
                                     'tipJntSetup': {'nameTempl': u'R_fr_footThumb', 'icone': 'Bone', 'size': 0.3}}
                     },

                     'heelCntrlSetup': {'nameTempl': 'R_fr_footHeel', 'icone': 'bola', 'color': (0.01, 0.05, 0.2), 'size': 0.5},
                     'ballCntrlSetup': {'nameTempl': 'R_fr_footBall', 'icone': 'circuloX', 'color': (0.01, 0.05, 0.2),
                                        'size': 1.5},
                     'baseGuideSetup': {'nameTempl': 'R_fr_footBase', 'icone': 'quadradoY', 'color': (1, 0, 1), 'size': 3},
                     'name': 'R_fr_foot',
                     'moveallGuideSetup': {'nameTempl': 'R_fr_footMoveAll', 'icone': 'quadradoY', 'color': (1, 0, 0),
                                           'size': 1.8},
                     'slideGuideSetup': {'nameTempl': 'R_fr_footSlide', 'icone': 'null', 'color': (1, 0, 1), 'size': 0.4},
                     'centerCntrlSetup': {'nameTempl': 'R_fr_footCenter', 'icone': 'circuloX', 'color': (0.01, 0.05, 0.2),
                                          'size': 2},
                     'baseCntrlSetup': {'nameTempl': 'R_fr_footBase', 'icone': 'quadradoY', 'color': (0.01, 0.05, 0.2), 'size': 3},
                     'toeCntrlSetup': {'nameTempl': 'R_fr_footToe', 'icone': 'circuloX', 'color': (0.01, 0.05, 0.2), 'size': 1.0},
                     'toeJntSetup': {'nameTempl': 'R_fr_footToe', 'icone': 'Bone', 'size': 1.0},
                     'ankleCntrlSetup': {'nameTempl': 'R_fr_footAnkle', 'icone': 'cubo', 'color': (0.01, 0.05, 0.2), 'size': 1},
                     'centerGuideSetup': {'nameTempl': 'R_fr_footCenter', 'icone': 'grp', 'color': (1, 1, 0), 'size': 0.5},
                     'flipAxis': False,
                     'inCntrlSetup': {'nameTempl': 'R_fr_footIn', 'icone': 'bola', 'color': (0.01, 0.05, 0.2), 'size': 0.4},
                     'tipGuideSetup': {'nameTempl': 'R_fr_footTip', 'icone': 'bola', 'color': (0, 1, 1), 'size': 0.5},

                     'guideDict': {'ball': [(-1.0, 0.5, 0.0), (0.0, -0.0, 0.0), (1.0, 1.0, 1.0)],
                                   'center': [(0.0, 0.0, 0.0), (0.0, 0.0, 0.0), (1.0, 1.0, 1.0)],
                                   'tip': [(3.0, 0.0, 0.0), (0.0, -0.0, 0.0), (1.0, 1.0, 1.0)],
                                   'moveall': [(1.82, 0, 9.73), (0.0, -90.0, 0.0), (1.0, 1.0, 1.0)],
                                   'in': [(-1.0, 0.0, -1.0), (0.0, -0.0, 0.0), (1.0, 1.0, 1.0)],
                                   'ankle': [(0.0, 1.0, 0.0), (0.0, -0.0, 0.0), (1.0, 1.0, 1.0)],
                                   'heel': [(-1.0, 0.0, 0.0), (0.0, -0.0, 0.0), (1.0, 1.0, 1.0)],
                                   'out': [(-1.0, 0.0, 1.0), (0.0, -0.0, 0.0), (1.0, 1.0, 1.0)]}}

        lfootDict = {'slideCntrlSetup': {'nameTempl': 'L_bk_footSlide', 'icone': 'bola', 'color': (0.01, 0.05, 0.2), 'size': 0.4},
                     'tipCntrlSetup': {'nameTempl': 'L_bk_footTip', 'icone': 'bola', 'color': (0.01, 0.05, 0.2), 'size': 0.5},
                     'moveallCntrlSetup': {'nameTempl': 'L_bk_footMoveAll', 'icone': 'circuloX', 'color': (1, 1, 0),
                                           'size': 1.8},
                     'toLimbCntrlSetup': {'nameTempl': 'L_bk_footToLimb', 'icone': 'grp', 'color': (0.01, 0.05, 0.2),
                                          'size': 0.5},
                     'ankleFkCntrlSetup': {'nameTempl': 'L_bk_footTnkleFk', 'icone': 'grp', 'color': (0, 1, 0),
                                           'size': 1.0},
                     'jointGuideSetup': {'nameTempl': 'L_bk_footJoint', 'icone': 'null', 'color': (1, 0, 1), 'size': 0.5},
                     'axis': 'X',
                     'toeFkCntrlSetup': {'nameTempl': 'L_bk_footToeFk', 'icone': 'cubo', 'color': (0.01, 0.05, 0.2),
                                         'size': 1.0},
                     'inGuideSetup': {'nameTempl': 'L_bk_footIn', 'icone': 'bola', 'color': (0, 0, 1), 'size': 0.4},
                     'ankleJntSetup': {'nameTempl': 'L_bk_footAnkle', 'icone': 'Bone', 'size': 1.0},
                     'ballGuideSetup': {'nameTempl': 'L_bk_footBall', 'icone': 'bola', 'color': (0, 1, 1), 'size': 0.5},
                     'ankleGuideSetup': {'nameTempl': 'L_bk_footAnkle', 'icone': 'bola', 'color': (0, 1, 1), 'size': 0.5},
                     'rollCntrlSetup': {'nameTempl': 'L_bk_footRoll', 'icone': 'cubo', 'color': (0.01, 0.05, 0.2), 'size': 0.4},
                     'rollGuideSetup': {'nameTempl': 'L_bk_footRoll', 'icone': 'bola', 'color': (1, 0, 1), 'size': 0.4},
                     'outGuideSetup': {'nameTempl': 'L_bk_footOut', 'icone': 'bola', 'color': (0, 0, 1), 'size': 0.4},
                     'toeGuideSetup': {'nameTempl': 'L_bk_footToe', 'icone': 'null', 'color': (1, 1, 0), 'size': 1.0},
                     'fingerNames': ['Thumb', 'Index', 'Middle', 'Ring', 'Pinky', 'Other', 'Other1'],
                     'outCntrlSetup': {'nameTempl': 'L_bk_footOut', 'icone': 'bola', 'color': (0.01, 0.05, 0.2), 'size': 0.4},
                     'heelGuideSetup': {'nameTempl': 'L_bk_footHeel', 'icone': 'bola', 'color': (0, 1, 1), 'size': 0.5},

                     'fingers': {
                         'Ring': {
                                     'fold2CntrlSetup': {'nameTempl': u'L_bk_footRingfold2', 'icone': 'circuloX',
                                                         'color': (0.4, 0, 0),'size': 0.3},
                                     'folds': 1,
                                     'moveallCntrlSetup': {'nameTempl': u'L_bk_footRingMoveAll', 'icone': 'circuloX',
                                                           'color': (.4, 0, 0), 'size': 0.1},
                                     'guideDict':   {
                                                     'moveall': [(-0.85, 0, -0.5), (0.0, 0, 0.0), (1.0, 1.0, 1.0)],
                                                     'palm': [(0.0, 0.0, 0.0), (0.0, 0.0, 0.0)],
                                                     'base': [(0.3, 0.0, 0.0), (0.0, 0.0, 0)],
                                                     'fold2': [(0, 0, 0), (0, 0, 0)],
                                                     'fold1': [(0.0, -0.05, 0.0), (0.0, 0.0, 0.0)],
                                                     'tip': [(0.8, 0.0, 0.0), (0.0, 0.0, 0)]
                                                    },
                                     'fold1GuideSetup': {'nameTempl': u'L_bk_footRingfold1', 'icone': 'circuloX', 'color': (0, 0, 1),
                                                         'size': 0.4},
                                     'baseJntSetup': {'nameTempl': u'L_bk_footRingBase', 'icone': 'Bone', 'size': 0.3},
                                     'fold2JntSetup': {'nameTempl': u'L_bk_footRingFold2', 'icone': 'Bone', 'size': 0.3},
                                     'isHeelFinger': False,
                                     'baseGuideSetup': {'nameTempl': u'L_bk_footRingbase', 'icone': 'circuloX', 'color': (0, 0, 1),
                                                        'size': 0.4},
                                     'fold1CntrlSetup': {'nameTempl': u'L_bk_footRingfold1', 'icone': 'circuloX', 'color': (.4, 0, 0),
                                                         'size': 0.3},
                                     'fold2GuideSetup': {'nameTempl': u'L_bk_footRingfold2', 'icone': 'circuloX', 'color': (0, 0, 1),
                                                         'size': 0.4}, 'axis': 'X',
                                     'fold1JntSetup': {'nameTempl': u'L_bk_footRingFold1', 'icone': 'Bone', 'size': 0.3},
                                     'moveallGuideSetup': {'nameTempl': u'L_bk_footRingMoveAll', 'icone': 'quadradoX',
                                                           'color': (0.6, 0, 0), 'size': 0.5}, 'name': u'L_bk_footRing',
                                     'tipGuideSetup': {'nameTempl': u'L_bk_footRingtip', 'icone': 'circuloX', 'color': (0, 0, 1),
                                                       'size': 0.4},
                                     'baseCntrlSetup': {'nameTempl': u'L_bk_footRingbase', 'icone': 'dropMenosZ', 'color': (.4, 0, 0),
                                                        'size': 0.1},
                                     'palmJntSetup': {'nameTempl': u'L_bk_footRingPalm', 'icone': 'Bone', 'size': 0.2},
                                     'palmCntrlSetup': {'nameTempl': u'L_bk_footRingpalm', 'icone': 'cubo', 'color': (.4, 0, 0),
                                                        'size': 0.2},
                                     'palmGuideSetup': {'nameTempl': u'L_bk_footRingpalm', 'icone': 'circuloX', 'color': (0, 0, 1),
                                                        'size': 0.4}, 'flipAxis': False,
                                     'tipJntSetup': {'nameTempl': u'L_bk_footRing', 'icone': 'Bone', 'size': 0.3}},

                         'Pinky': {
                                     'fold2CntrlSetup': {'nameTempl': u'L_bk_footPinkyfold2', 'icone': 'circuloX', 'color': (.4, 0, 0),
                                                         'size': 0.3}, 'folds': 1,
                                     'moveallCntrlSetup': {'nameTempl': u'L_bk_footPinkyMoveAll', 'icone': 'circuloX',
                                                           'color': (.4, 0, 0), 'size': 0.1},
                                     'guideDict':   {
                                                     'moveall': [(-0.85, 0, -1),(0.0, 0, 0.0), (1.0, 1.0, 1.0)],
                                                     'palm': [(0.0, 0.0, 0.0), (0.0, 0.0, 0.0)],
                                                     'base': [(0.3, 0.0, 0.0), (0.0, 0.0, 0)],
                                                     'fold2': [(0, 0, 0), (0, 0, 0)],
                                                     'fold1': [(0.0, -0.05, 0.0), (0.0, 0.0, 0.0)],
                                                     'tip': [(0.8, 0.0, 0.0), (0.0, 0.0, 0)]
                                                    },

                                     'fold1GuideSetup': {'nameTempl': u'L_bk_footPinkyfold1', 'icone': 'circuloX', 'color': (0, 0, 1),
                                                         'size': 0.4},
                                     'baseJntSetup': {'nameTempl': u'L_bk_footPinkyBase', 'icone': 'Bone', 'size': 0.3},
                                     'fold2JntSetup': {'nameTempl': u'L_bk_footPinkyFold2', 'icone': 'Bone', 'size': 0.3},
                                     'isHeelFinger': False,
                                     'baseGuideSetup': {'nameTempl': u'L_bk_footPinkybase', 'icone': 'circuloX', 'color': (0, 0, 1),
                                                        'size': 0.4},
                                     'fold1CntrlSetup': {'nameTempl': u'L_bk_footPinkyfold1', 'icone': 'circuloX', 'color': (.4, 0, 0),
                                                         'size': 0.3},
                                     'fold2GuideSetup': {'nameTempl': u'L_bk_footPinkyfold2', 'icone': 'circuloX', 'color': (0, 0, 1),
                                                         'size': 0.4}, 'axis': 'X',
                                     'fold1JntSetup': {'nameTempl': u'L_bk_footPinkyFold1', 'icone': 'Bone', 'size': 0.3},
                                     'moveallGuideSetup': {'nameTempl': u'L_bk_footPinkyMoveAll', 'icone': 'quadradoX',
                                                           'color': (0.6, 0, 0), 'size': 0.5}, 'name': u'L_bk_footPinky',
                                     'tipGuideSetup': {'nameTempl': u'L_bk_footPinkytip', 'icone': 'circuloX', 'color': (0, 0, 1),
                                                       'size': 0.4},
                                     'baseCntrlSetup': {'nameTempl': u'L_bk_footPinkybase', 'icone': 'dropMenosZ', 'color': (.4, 0, 0),
                                                        'size': 0.1},
                                     'palmJntSetup': {'nameTempl': u'L_bk_footPinkyPalm', 'icone': 'Bone', 'size': 0.2},
                                     'palmCntrlSetup': {'nameTempl': u'L_bk_footPinkypalm', 'icone': 'cubo', 'color': (.4, 0, 0),
                                                        'size': 0.2},
                                     'palmGuideSetup': {'nameTempl': u'L_bk_footPinkypalm', 'icone': 'circuloX', 'color': (0, 0, 1),
                                                        'size': 0.4}, 'flipAxis': False,
                                     'tipJntSetup': {'nameTempl': u'L_bk_footPinky', 'icone': 'Bone', 'size': 0.3}},

                         'Index': {
                                     'fold2CntrlSetup': {'nameTempl': u'L_bk_footIndexfold2', 'icone': 'circuloX', 'color': (.4, 0, 0),
                                                         'size': 0.3}, 'folds': 1,
                                     'moveallCntrlSetup': {'nameTempl': u'L_bk_footIndexMoveAll', 'icone': 'circuloX',
                                                           'color': (.4, 0, 0), 'size': 0.1},
                                     'guideDict':   {
                                                     'moveall': [(-0.85, 0, 0.5), (0.0, 0, 0.0), (1.0, 1.0, 1.0)],
                                                     'palm': [(0.0, 0.0, 0.0), (0.0, 0.0, 0.0)],
                                                     'base': [(0.3, 0.0, 0.0), (0.0, 0.0, 0)],
                                                     'fold2': [(0, 0, 0), (0, 0, 0)],
                                                     'fold1': [(0.0, -0.05, 0.0), (0.0, 0.0, 0.0)],
                                                     'tip': [(0.8, 0.0, 0.0), (0.0, 0.0, 0)]
                                                    },
                                     'fold1GuideSetup': {'nameTempl': u'L_bk_footIndexfold1', 'icone': 'circuloX', 'color': (0, 0, 1),
                                                         'size': 0.4},
                                     'baseJntSetup': {'nameTempl': u'L_bk_footIndexBase', 'icone': 'Bone', 'size': 0.3},
                                     'fold2JntSetup': {'nameTempl': u'L_bk_footIndexFold2', 'icone': 'Bone', 'size': 0.3},
                                     'isHeelFinger': False,
                                     'baseGuideSetup': {'nameTempl': u'L_bk_footIndexbase', 'icone': 'circuloX', 'color': (0, 0, 1),
                                                        'size': 0.4},
                                     'fold1CntrlSetup': {'nameTempl': u'L_bk_footIndexfold1', 'icone': 'circuloX', 'color': (.4, 0, 0),
                                                         'size': 0.3},
                                     'fold2GuideSetup': {'nameTempl': u'L_bk_footIndexfold2', 'icone': 'circuloX', 'color': (0, 0, 1),
                                                         'size': 0.4}, 'axis': 'X',
                                     'fold1JntSetup': {'nameTempl': u'L_bk_footIndexFold1', 'icone': 'Bone', 'size': 0.3},
                                     'moveallGuideSetup': {'nameTempl': u'L_bk_footIndexMoveAll', 'icone': 'quadradoX',
                                                           'color': (0.6, 0, 0), 'size': 0.5}, 'name': u'L_bk_footIndex',
                                     'tipGuideSetup': {'nameTempl': u'L_bk_footIndextip', 'icone': 'circuloX', 'color': (0, 0, 1),
                                                       'size': 0.4},
                                     'baseCntrlSetup': {'nameTempl': u'L_bk_footIndexbase', 'icone': 'dropMenosZ', 'color': (.4, 0, 0),
                                                        'size': 0.1},
                                     'palmJntSetup': {'nameTempl': u'L_bk_footIndexPalm', 'icone': 'Bone', 'size': 0.2},
                                     'palmCntrlSetup': {'nameTempl': u'L_bk_footIndexpalm', 'icone': 'cubo', 'color': (.4, 0, 0),
                                                        'size': 0.2},
                                     'palmGuideSetup': {'nameTempl': u'L_bk_footIndexpalm', 'icone': 'circuloX', 'color': (0, 0, 1),
                                                        'size': 0.4}, 'flipAxis': False,
                                     'tipJntSetup': {'nameTempl': u'L_bk_footIndex', 'icone': 'Bone', 'size': 0.3}},


                         'Middle': {
                                     'fold2CntrlSetup': {'nameTempl': u'L_bk_footMiddlefold2', 'icone': 'circuloX', 'color': (.4, 0, 0),
                                                         'size': 0.3}, 'folds': 1,
                                     'moveallCntrlSetup': {'nameTempl': u'L_bk_footMiddleMoveAll', 'icone': 'circuloX',
                                                           'color': (.4, 0, 0), 'size': 0.1},
                                     'guideDict':   {
                                                     'moveall': [(-0.85, 0.0, 0), (0.0, 0.0, 0.0), (1.0, 1.0, 1.0)],
                                                     'palm': [(0.0, 0.0, 0.0), (0.0, 0.0, 0.0)],
                                                     'base': [(0.3, 0.0, 0.0), (0.0, -0.0, 0.0)],
                                                     'fold2': [(0, 0, 0), (0, 0, 0)],
                                                     'fold1': [(0.0, -0.05, 0.0), (0.0, 0.0, 0.0)],
                                                     'tip': [(0.8, 0.0, 0.0), (0.0, 0.0, 0.0)]
                                                    },
                                     'fold1GuideSetup': {'nameTempl': u'L_bk_footMiddlefold1', 'icone': 'circuloX', 'color': (0, 0, 1),
                                                         'size': 0.4},
                                     'baseJntSetup': {'nameTempl': u'L_bk_footMiddleBase', 'icone': 'Bone', 'size': 0.3},
                                     'fold2JntSetup': {'nameTempl': u'L_bk_footMiddleFold2', 'icone': 'Bone', 'size': 0.3},
                                     'isHeelFinger': False,
                                     'baseGuideSetup': {'nameTempl': u'L_bk_footMiddlebase', 'icone': 'circuloX', 'color': (0, 0, 1),
                                                        'size': 0.4},
                                     'fold1CntrlSetup': {'nameTempl': u'L_bk_footMiddlefold1', 'icone': 'circuloX', 'color': (.4, 0, 0),
                                                         'size': 0.3},
                                     'fold2GuideSetup': {'nameTempl': u'L_bk_footMiddlefold2', 'icone': 'circuloX', 'color': (0, 0, 1),
                                                         'size': 0.4}, 'axis': 'X',
                                     'fold1JntSetup': {'nameTempl': u'L_bk_footMiddleFold1', 'icone': 'Bone', 'size': 0.3},
                                     'moveallGuideSetup': {'nameTempl': u'L_bk_footMiddleMoveAll', 'icone': 'quadradoX',
                                                           'color': (0.6, 0, 0), 'size': 0.5}, 'name': u'L_bk_footMiddle',
                                     'tipGuideSetup': {'nameTempl': u'L_bk_footMiddletip', 'icone': 'circuloX', 'color': (0, 0, 1),
                                                       'size': 0.4},
                                     'baseCntrlSetup': {'nameTempl': u'L_bk_footMiddlebase', 'icone': 'dropMenosZ', 'color': (.4, 0, 0),
                                                        'size': 0.1},
                                     'palmJntSetup': {'nameTempl': u'L_bk_footMiddlePalm', 'icone': 'Bone', 'size': 0.2},
                                     'palmCntrlSetup': {'nameTempl': u'L_bk_footMiddlepalm', 'icone': 'cubo', 'color': (.4, 0, 0),
                                                        'size': 0.2},
                                     'palmGuideSetup': {'nameTempl': u'L_bk_footMiddlepalm', 'icone': 'circuloX', 'color': (0, 0, 1),
                                                        'size': 0.4}, 'flipAxis': False,
                                     'tipJntSetup': {'nameTempl': u'L_bk_footMiddle', 'icone': 'Bone', 'size': 0.3}},


                         'Thumb': {
                                     'fold2CntrlSetup': {'nameTempl': u'L_bk_footThumbfold2', 'icone': 'circuloX', 'color': (.4, 0, 0),
                                                     'size': 0.3}, 'folds': 1,
                                     'moveallCntrlSetup': {'nameTempl': u'L_bk_footThumbMoveAll', 'icone': 'circuloX',
                                                           'color': (.4, 0, 0), 'size': 0.1},
                                     'guideDict':   {
                                                     'moveall': [(-0.85, 0.0, 1), (0.0, 0.0, 0.0), (1.0, 1.0, 1.0)],
                                                     'palm': [(0.0, 0.0, 0.0), (0.0, -0.0, 0.0)],
                                                     'base': [(0.3, 0.0, 0.0),(0.0, 0.0, 0.0)],
                                                     'fold2': [(0, 0, 0), (0, 0, 0)],
                                                     'fold1': [(0.0, -0.05, 0.0), (0.0, -0.0, 0.0)],
                                                     'tip': [(0.8, 0.0, 0.0),(0.0, 0.0, 0.0)]
                                                    },
                                     'fold1GuideSetup': {'nameTempl': u'L_bk_footThumbfold1', 'icone': 'circuloX', 'color': (0, 0, 1),
                                                         'size': 0.4},
                                     'baseJntSetup': {'nameTempl': u'L_bk_footThumbBase', 'icone': 'Bone', 'size': 0.3},
                                     'fold2JntSetup': {'nameTempl': u'L_bk_footThumbFold2', 'icone': 'Bone', 'size': 0.3},
                                     'isHeelFinger': False,
                                     'baseGuideSetup': {'nameTempl': u'L_bk_footThumbbase', 'icone': 'circuloX', 'color': (0, 0, 1),
                                                        'size': 0.4},
                                     'fold1CntrlSetup': {'nameTempl': u'L_bk_footThumbfold1', 'icone': 'circuloX', 'color': (.4, 0, 0),
                                                         'size': 0.3},
                                     'fold2GuideSetup': {'nameTempl': u'L_bk_footThumbfold2', 'icone': 'circuloX', 'color': (0, 0, 1),
                                                         'size': 0.4}, 'axis': 'X',
                                     'fold1JntSetup': {'nameTempl': u'L_bk_footThumbFold1', 'icone': 'Bone', 'size': 0.3},
                                     'moveallGuideSetup': {'nameTempl': u'L_bk_footThumbMoveAll', 'icone': 'quadradoX',
                                                           'color': (0.6, 0, 0), 'size': 0.5}, 'name': u'L_bk_footThumb',
                                     'tipGuideSetup': {'nameTempl': u'L_bk_footThumbtip', 'icone': 'circuloX', 'color': (0, 0, 1),
                                                       'size': 0.4},
                                     'baseCntrlSetup': {'nameTempl': u'L_bk_footThumbbase', 'icone': 'dropMenosZ', 'color': (.4, 0, 0),
                                                        'size': 0.1},
                                     'palmJntSetup': {'nameTempl': u'L_bk_footThumbPalm', 'icone': 'Bone', 'size': 0.2},
                                     'palmCntrlSetup': {'nameTempl': u'L_bk_footThumbpalm', 'icone': 'cubo', 'color': (.4, 0, 0),
                                                        'size': 0.2},
                                     'palmGuideSetup': {'nameTempl': u'L_bk_footThumbpalm', 'icone': 'circuloX', 'color': (0, 0, 1),
                                                        'size': 0.4}, 'flipAxis': False,
                                     'tipJntSetup': {'nameTempl': u'L_bk_footThumb', 'icone': 'Bone', 'size': 0.3}}
                     },

                     'heelCntrlSetup': {'nameTempl': 'L_bk_footHeel', 'icone': 'bola', 'color': (0.01, 0.05, 0.2), 'size': 0.5},
                     'ballCntrlSetup': {'nameTempl': 'L_bk_footBall', 'icone': 'circuloX', 'color': (0.01, 0.05, 0.2),
                                        'size': 1.5},
                     'baseGuideSetup': {'nameTempl': 'L_bk_footBase', 'icone': 'quadradoY', 'color': (1, 0, 1), 'size': 3},
                     'name': 'L_bk_foot',
                     'moveallGuideSetup': {'nameTempl': 'L_bk_footMoveAll', 'icone': 'quadradoY', 'color': (1, 0, 0),
                                           'size': 1.8},
                     'slideGuideSetup': {'nameTempl': 'L_bk_footSlide', 'icone': 'null', 'color': (1, 0, 1), 'size': 0.4},
                     'centerCntrlSetup': {'nameTempl': 'L_bk_footCenter', 'icone': 'circuloX', 'color': (0.01, 0.05, 0.2),
                                          'size': 2},
                     'baseCntrlSetup': {'nameTempl': 'L_bk_footBase', 'icone': 'quadradoY', 'color': (0.01, 0.05, 0.2), 'size': 3},
                     'toeCntrlSetup': {'nameTempl': 'L_bk_footToe', 'icone': 'circuloX', 'color': (0.01, 0.05, 0.2), 'size': 1.0},
                     'toeJntSetup': {'nameTempl': 'L_bk_footToe', 'icone': 'Bone', 'size': 1.0},
                     'ankleCntrlSetup': {'nameTempl': 'L_bk_footAnkle', 'icone': 'cubo', 'color': (0.01, 0.05, 0.2), 'size': 1},
                     'centerGuideSetup': {'nameTempl': 'L_bk_footCenter', 'icone': 'grp', 'color': (1, 1, 0), 'size': 0.5},
                     'flipAxis': False,
                     'inCntrlSetup': {'nameTempl': 'L_bk_footIn', 'icone': 'bola', 'color': (0.01, 0.05, 0.2), 'size': 0.4},
                     'tipGuideSetup': {'nameTempl': 'L_bk_footTip', 'icone': 'bola', 'color': (0, 1, 1), 'size': 0.5},

                     'guideDict': {'ball': [(-1.0, 0.5, 0.0), (0.0, -0.0, 0.0), (1.0, 1.0, 1.0)],
                                   'center': [(0.0, 0.0, 0.0), (0.0, 0.0, 0.0), (1.0, 1.0, 1.0)],
                                   'tip': [(3.0, 0.0, 0.0), (0.0, -0.0, 0.0), (1.0, 1.0, 1.0)],
                                   'moveall': [(1.82, 0.0, 0.0), (0.0, -90.0, 0.0), (1.0, 1.0, 1.0)],
                                   'in': [(-1.0, 0.0, -1.0), (0.0, -0.0, 0.0), (1.0, 1.0, 1.0)],
                                   'ankle': [(0.0, 1.0, 0.0), (0.0, -0.0, 0.0), (1.0, 1.0, 1.0)],
                                   'heel': [(-1.0, 0.0, 0.0), (0.0, -0.0, 0.0), (1.0, 1.0, 1.0)],
                                   'out': [(-1.0, 0.0, 1.0), (0.0, -0.0, 0.0), (1.0, 1.0, 1.0)]}}

        rfootDict = {'slideCntrlSetup': {'nameTempl': 'R_bk_footSlide', 'icone': 'bola', 'color': (.4, 0, 0), 'size': 0.4},
                     'tipCntrlSetup': {'nameTempl': 'R_bk_footTip', 'icone': 'bola', 'color': (.4, 0, 0), 'size': 0.5},
                     'moveallCntrlSetup': {'nameTempl': 'R_bk_footMoveAll', 'icone': 'circuloX', 'color': (1, 1, 0),
                                           'size': 1.8},
                     'toLimbCntrlSetup': {'nameTempl': 'R_bk_footToLimb', 'icone': 'grp', 'color': (.4, 0, 0),
                                          'size': 0.5},
                     'ankleFkCntrlSetup': {'nameTempl': 'R_bk_footTnkleFk', 'icone': 'grp', 'color': (0, 1, 0),
                                           'size': 1.0},
                     'jointGuideSetup': {'nameTempl': 'R_bk_footJoint', 'icone': 'null', 'color': (1, 0, 1), 'size': 0.5},
                     'axis': 'X',
                     'toeFkCntrlSetup': {'nameTempl': 'R_bk_footToeFk', 'icone': 'cubo', 'color': (.4, 0, 0),
                                         'size': 1.0},
                     'inGuideSetup': {'nameTempl': 'R_bk_footIn', 'icone': 'bola', 'color': (0, 0, 1), 'size': 0.4},
                     'ankleJntSetup': {'nameTempl': 'R_bk_footAnkle', 'icone': 'Bone', 'size': 1.0},
                     'ballGuideSetup': {'nameTempl': 'R_bk_footBall', 'icone': 'bola', 'color': (0, 1, 1), 'size': 0.5},
                     'ankleGuideSetup': {'nameTempl': 'R_bk_footAnkle', 'icone': 'bola', 'color': (0, 1, 1), 'size': 0.5},
                     'rollCntrlSetup': {'nameTempl': 'R_bk_footRoll', 'icone': 'cubo', 'color': (.4, 0, 0), 'size': 0.4},
                     'rollGuideSetup': {'nameTempl': 'R_bk_footRoll', 'icone': 'bola', 'color': (1, 0, 1), 'size': 0.4},
                     'outGuideSetup': {'nameTempl': 'R_bk_footOut', 'icone': 'bola', 'color': (0, 0, 1), 'size': 0.4},
                     'toeGuideSetup': {'nameTempl': 'R_bk_footToe', 'icone': 'null', 'color': (1, 1, 0), 'size': 1.0},
                     'fingerNames': ['Thumb', 'Index', 'Middle', 'Ring', 'Pinky', 'Other', 'Other1'],
                     'outCntrlSetup': {'nameTempl': 'R_bk_footOut', 'icone': 'bola', 'color': (.4, 0, 0), 'size': 0.4},
                     'heelGuideSetup': {'nameTempl': 'R_bk_footHeel', 'icone': 'bola', 'color': (0, 1, 1), 'size': 0.5},
                     'fingers': {
                         'Ring': {
                                     'fold2CntrlSetup': {'nameTempl': u'R_bk_footRingfold2', 'icone': 'circuloX',
                                                         'color': (0.4, 0, 0),'size': 0.3},
                                     'folds': 1,
                                     'moveallCntrlSetup': {'nameTempl': u'R_bk_footRingMoveAll', 'icone': 'circuloX',
                                                           'color': (.4, 0, 0), 'size': 0.1},
                                     'guideDict':   {
                                                     'moveall': [(-0.85, 0, -0.5), (0.0, 0, 0.0), (1.0, 1.0, 1.0)],
                                                     'palm': [(0.0, 0.0, 0.0), (0.0, 0.0, 0.0)],
                                                     'base': [(0.3, 0.0, 0.0), (0.0, 0.0, 0)],
                                                     'fold2': [(0, 0, 0), (0, 0, 0)],
                                                     'fold1': [(0.0, -0.05, 0.0), (0.0, 0.0, 0.0)],
                                                     'tip': [(0.8, 0.0, 0.0), (0.0, 0.0, 0)]
                                                    },
                                     'fold1GuideSetup': {'nameTempl': u'R_bk_footRingfold1', 'icone': 'circuloX', 'color': (0, 0, 1),
                                                         'size': 0.4},
                                     'baseJntSetup': {'nameTempl': u'R_bk_footRingBase', 'icone': 'Bone', 'size': 0.3},
                                     'fold2JntSetup': {'nameTempl': u'R_bk_footRingFold2', 'icone': 'Bone', 'size': 0.3},
                                     'isHeelFinger': False,
                                     'baseGuideSetup': {'nameTempl': u'R_bk_footRingbase', 'icone': 'circuloX', 'color': (0, 0, 1),
                                                        'size': 0.4},
                                     'fold1CntrlSetup': {'nameTempl': u'R_bk_footRingfold1', 'icone': 'circuloX', 'color': (.4, 0, 0),
                                                         'size': 0.3},
                                     'fold2GuideSetup': {'nameTempl': u'R_bk_footRingfold2', 'icone': 'circuloX', 'color': (0, 0, 1),
                                                         'size': 0.4}, 'axis': 'X',
                                     'fold1JntSetup': {'nameTempl': u'R_bk_footRingFold1', 'icone': 'Bone', 'size': 0.3},
                                     'moveallGuideSetup': {'nameTempl': u'R_bk_footRingMoveAll', 'icone': 'quadradoX',
                                                           'color': (0.6, 0, 0), 'size': 0.5}, 'name': u'R_bk_footRing',
                                     'tipGuideSetup': {'nameTempl': u'R_bk_footRingtip', 'icone': 'circuloX', 'color': (0, 0, 1),
                                                       'size': 0.4},
                                     'baseCntrlSetup': {'nameTempl': u'R_bk_footRingbase', 'icone': 'dropMenosZ', 'color': (.4, 0, 0),
                                                        'size': 0.1},
                                     'palmJntSetup': {'nameTempl': u'R_bk_footRingPalm', 'icone': 'Bone', 'size': 0.2},
                                     'palmCntrlSetup': {'nameTempl': u'R_bk_footRingpalm', 'icone': 'cubo', 'color': (.4, 0, 0),
                                                        'size': 0.2},
                                     'palmGuideSetup': {'nameTempl': u'R_bk_footRingpalm', 'icone': 'circuloX', 'color': (0, 0, 1),
                                                        'size': 0.4}, 'flipAxis': False,
                                     'tipJntSetup': {'nameTempl': u'R_bk_footRing', 'icone': 'Bone', 'size': 0.3}},

                         'Pinky': {
                                     'fold2CntrlSetup': {'nameTempl': u'R_bk_footPinkyfold2', 'icone': 'circuloX', 'color': (.4, 0, 0),
                                                         'size': 0.3}, 'folds': 1,
                                     'moveallCntrlSetup': {'nameTempl': u'R_bk_footPinkyMoveAll', 'icone': 'circuloX',
                                                           'color': (.4, 0, 0), 'size': 0.1},
                                     'guideDict':   {
                                                     'moveall': [(-0.85, 0, -1),(0.0, 0, 0.0), (1.0, 1.0, 1.0)],
                                                     'palm': [(0.0, 0.0, 0.0), (0.0, 0.0, 0.0)],
                                                     'base': [(0.3, 0.0, 0.0), (0.0, 0.0, 0)],
                                                     'fold2': [(0, 0, 0), (0, 0, 0)],
                                                     'fold1': [(0.0, -0.05, 0.0), (0.0, 0.0, 0.0)],
                                                     'tip': [(0.8, 0.0, 0.0), (0.0, 0.0, 0)]
                                                    },

                                     'fold1GuideSetup': {'nameTempl': u'R_bk_footPinkyfold1', 'icone': 'circuloX', 'color': (0, 0, 1),
                                                         'size': 0.4},
                                     'baseJntSetup': {'nameTempl': u'R_bk_footPinkyBase', 'icone': 'Bone', 'size': 0.3},
                                     'fold2JntSetup': {'nameTempl': u'R_bk_footPinkyFold2', 'icone': 'Bone', 'size': 0.3},
                                     'isHeelFinger': False,
                                     'baseGuideSetup': {'nameTempl': u'R_bk_footPinkybase', 'icone': 'circuloX', 'color': (0, 0, 1),
                                                        'size': 0.4},
                                     'fold1CntrlSetup': {'nameTempl': u'R_bk_footPinkyfold1', 'icone': 'circuloX', 'color': (.4, 0, 0),
                                                         'size': 0.3},
                                     'fold2GuideSetup': {'nameTempl': u'R_bk_footPinkyfold2', 'icone': 'circuloX', 'color': (0, 0, 1),
                                                         'size': 0.4}, 'axis': 'X',
                                     'fold1JntSetup': {'nameTempl': u'R_bk_footPinkyFold1', 'icone': 'Bone', 'size': 0.3},
                                     'moveallGuideSetup': {'nameTempl': u'R_bk_footPinkyMoveAll', 'icone': 'quadradoX',
                                                           'color': (0.6, 0, 0), 'size': 0.5}, 'name': u'R_bk_footPinky',
                                     'tipGuideSetup': {'nameTempl': u'R_bk_footPinkytip', 'icone': 'circuloX', 'color': (0, 0, 1),
                                                       'size': 0.4},
                                     'baseCntrlSetup': {'nameTempl': u'R_bk_footPinkybase', 'icone': 'dropMenosZ', 'color': (.4, 0, 0),
                                                        'size': 0.1},
                                     'palmJntSetup': {'nameTempl': u'R_bk_footPinkyPalm', 'icone': 'Bone', 'size': 0.2},
                                     'palmCntrlSetup': {'nameTempl': u'R_bk_footPinkypalm', 'icone': 'cubo', 'color': (.4, 0, 0),
                                                        'size': 0.2},
                                     'palmGuideSetup': {'nameTempl': u'R_bk_footPinkypalm', 'icone': 'circuloX', 'color': (0, 0, 1),
                                                        'size': 0.4}, 'flipAxis': False,
                                     'tipJntSetup': {'nameTempl': u'R_bk_footPinky', 'icone': 'Bone', 'size': 0.3}},

                         'Index': {
                                     'fold2CntrlSetup': {'nameTempl': u'R_bk_footIndexfold2', 'icone': 'circuloX', 'color': (.4, 0, 0),
                                                         'size': 0.3}, 'folds': 1,
                                     'moveallCntrlSetup': {'nameTempl': u'R_bk_footIndexMoveAll', 'icone': 'circuloX',
                                                           'color': (.4, 0, 0), 'size': 0.1},
                                     'guideDict':   {
                                                     'moveall': [(-0.85, 0, 0.5), (0.0, 0, 0.0), (1.0, 1.0, 1.0)],
                                                     'palm': [(0.0, 0.0, 0.0), (0.0, 0.0, 0.0)],
                                                     'base': [(0.3, 0.0, 0.0), (0.0, 0.0, 0)],
                                                     'fold2': [(0, 0, 0), (0, 0, 0)],
                                                     'fold1': [(0.0, -0.05, 0.0), (0.0, 0.0, 0.0)],
                                                     'tip': [(0.8, 0.0, 0.0), (0.0, 0.0, 0)]
                                                    },
                                     'fold1GuideSetup': {'nameTempl': u'R_bk_footIndexfold1', 'icone': 'circuloX', 'color': (0, 0, 1),
                                                         'size': 0.4},
                                     'baseJntSetup': {'nameTempl': u'R_bk_footIndexBase', 'icone': 'Bone', 'size': 0.3},
                                     'fold2JntSetup': {'nameTempl': u'R_bk_footIndexFold2', 'icone': 'Bone', 'size': 0.3},
                                     'isHeelFinger': False,
                                     'baseGuideSetup': {'nameTempl': u'R_bk_footIndexbase', 'icone': 'circuloX', 'color': (0, 0, 1),
                                                        'size': 0.4},
                                     'fold1CntrlSetup': {'nameTempl': u'R_bk_footIndexfold1', 'icone': 'circuloX', 'color': (.4, 0, 0),
                                                         'size': 0.3},
                                     'fold2GuideSetup': {'nameTempl': u'R_bk_footIndexfold2', 'icone': 'circuloX', 'color': (0, 0, 1),
                                                         'size': 0.4}, 'axis': 'X',
                                     'fold1JntSetup': {'nameTempl': u'R_bk_footIndexFold1', 'icone': 'Bone', 'size': 0.3},
                                     'moveallGuideSetup': {'nameTempl': u'R_bk_footIndexMoveAll', 'icone': 'quadradoX',
                                                           'color': (0.6, 0, 0), 'size': 0.5}, 'name': u'R_bk_footIndex',
                                     'tipGuideSetup': {'nameTempl': u'R_bk_footIndextip', 'icone': 'circuloX', 'color': (0, 0, 1),
                                                       'size': 0.4},
                                     'baseCntrlSetup': {'nameTempl': u'R_bk_footIndexbase', 'icone': 'dropMenosZ', 'color': (.4, 0, 0),
                                                        'size': 0.1},
                                     'palmJntSetup': {'nameTempl': u'R_bk_footIndexPalm', 'icone': 'Bone', 'size': 0.2},
                                     'palmCntrlSetup': {'nameTempl': u'R_bk_footIndexpalm', 'icone': 'cubo', 'color': (.4, 0, 0),
                                                        'size': 0.2},
                                     'palmGuideSetup': {'nameTempl': u'R_bk_footIndexpalm', 'icone': 'circuloX', 'color': (0, 0, 1),
                                                        'size': 0.4}, 'flipAxis': False,
                                     'tipJntSetup': {'nameTempl': u'R_bk_footIndex', 'icone': 'Bone', 'size': 0.3}},


                         'Middle': {
                                     'fold2CntrlSetup': {'nameTempl': u'R_bk_footMiddlefold2', 'icone': 'circuloX', 'color': (.4, 0, 0),
                                                         'size': 0.3}, 'folds': 1,
                                     'moveallCntrlSetup': {'nameTempl': u'R_bk_footMiddleMoveAll', 'icone': 'circuloX',
                                                           'color': (.4, 0, 0), 'size': 0.1},
                                     'guideDict':   {
                                                     'moveall': [(-0.85, 0.0, 0), (0.0, 0.0, 0.0), (1.0, 1.0, 1.0)],
                                                     'palm': [(0.0, 0.0, 0.0), (0.0, 0.0, 0.0)],
                                                     'base': [(0.3, 0.0, 0.0), (0.0, -0.0, 0.0)],
                                                     'fold2': [(0, 0, 0), (0, 0, 0)],
                                                     'fold1': [(0.0, -0.05, 0.0), (0.0, 0.0, 0.0)],
                                                     'tip': [(0.8, 0.0, 0.0), (0.0, 0.0, 0.0)]
                                                    },
                                     'fold1GuideSetup': {'nameTempl': u'R_bk_footMiddlefold1', 'icone': 'circuloX', 'color': (0, 0, 1),
                                                         'size': 0.4},
                                     'baseJntSetup': {'nameTempl': u'R_bk_footMiddleBase', 'icone': 'Bone', 'size': 0.3},
                                     'fold2JntSetup': {'nameTempl': u'R_bk_footMiddleFold2', 'icone': 'Bone', 'size': 0.3},
                                     'isHeelFinger': False,
                                     'baseGuideSetup': {'nameTempl': u'R_bk_footMiddlebase', 'icone': 'circuloX', 'color': (0, 0, 1),
                                                        'size': 0.4},
                                     'fold1CntrlSetup': {'nameTempl': u'R_bk_footMiddlefold1', 'icone': 'circuloX', 'color': (.4, 0, 0),
                                                         'size': 0.3},
                                     'fold2GuideSetup': {'nameTempl': u'R_bk_footMiddlefold2', 'icone': 'circuloX', 'color': (0, 0, 1),
                                                         'size': 0.4}, 'axis': 'X',
                                     'fold1JntSetup': {'nameTempl': u'R_bk_footMiddleFold1', 'icone': 'Bone', 'size': 0.3},
                                     'moveallGuideSetup': {'nameTempl': u'R_bk_footMiddleMoveAll', 'icone': 'quadradoX',
                                                           'color': (0.6, 0, 0), 'size': 0.5}, 'name': u'R_bk_footMiddle',
                                     'tipGuideSetup': {'nameTempl': u'R_bk_footMiddletip', 'icone': 'circuloX', 'color': (0, 0, 1),
                                                       'size': 0.4},
                                     'baseCntrlSetup': {'nameTempl': u'R_bk_footMiddlebase', 'icone': 'dropMenosZ', 'color': (.4, 0, 0),
                                                        'size': 0.1},
                                     'palmJntSetup': {'nameTempl': u'R_bk_footMiddlePalm', 'icone': 'Bone', 'size': 0.2},
                                     'palmCntrlSetup': {'nameTempl': u'R_bk_footMiddlepalm', 'icone': 'cubo', 'color': (.4, 0, 0),
                                                        'size': 0.2},
                                     'palmGuideSetup': {'nameTempl': u'R_bk_footMiddlepalm', 'icone': 'circuloX', 'color': (0, 0, 1),
                                                        'size': 0.4}, 'flipAxis': False,
                                     'tipJntSetup': {'nameTempl': u'R_bk_footMiddle', 'icone': 'Bone', 'size': 0.3}},


                         'Thumb': {
                                     'fold2CntrlSetup': {'nameTempl': u'R_bk_footThumbfold2', 'icone': 'circuloX', 'color': (.4, 0, 0),
                                                     'size': 0.3}, 'folds': 1,
                                     'moveallCntrlSetup': {'nameTempl': u'R_bk_footThumbMoveAll', 'icone': 'circuloX',
                                                           'color': (.4, 0, 0), 'size': 0.1},
                                     'guideDict':   {
                                                     'moveall': [(-0.85, 0.0, 1), (0.0, 0.0, 0.0), (1.0, 1.0, 1.0)],
                                                     'palm': [(0.0, 0.0, 0.0), (0.0, -0.0, 0.0)],
                                                     'base': [(0.3, 0.0, 0.0),(0.0, 0.0, 0.0)],
                                                     'fold2': [(0, 0, 0), (0, 0, 0)],
                                                     'fold1': [(0.0, -0.05, 0.0), (0.0, -0.0, 0.0)],
                                                     'tip': [(0.8, 0.0, 0.0),(0.0, 0.0, 0.0)]
                                                    },
                                     'fold1GuideSetup': {'nameTempl': u'R_bk_footThumbfold1', 'icone': 'circuloX', 'color': (0, 0, 1),
                                                         'size': 0.4},
                                     'baseJntSetup': {'nameTempl': u'R_bk_footThumbBase', 'icone': 'Bone', 'size': 0.3},
                                     'fold2JntSetup': {'nameTempl': u'R_bk_footThumbFold2', 'icone': 'Bone', 'size': 0.3},
                                     'isHeelFinger': False,
                                     'baseGuideSetup': {'nameTempl': u'R_bk_footThumbbase', 'icone': 'circuloX', 'color': (0, 0, 1),
                                                        'size': 0.4},
                                     'fold1CntrlSetup': {'nameTempl': u'R_bk_footThumbfold1', 'icone': 'circuloX', 'color': (.4, 0, 0),
                                                         'size': 0.3},
                                     'fold2GuideSetup': {'nameTempl': u'R_bk_footThumbfold2', 'icone': 'circuloX', 'color': (0, 0, 1),
                                                         'size': 0.4}, 'axis': 'X',
                                     'fold1JntSetup': {'nameTempl': u'R_bk_footThumbFold1', 'icone': 'Bone', 'size': 0.3},
                                     'moveallGuideSetup': {'nameTempl': u'R_bk_footThumbMoveAll', 'icone': 'quadradoX',
                                                           'color': (0.6, 0, 0), 'size': 0.5}, 'name': u'R_bk_footThumb',
                                     'tipGuideSetup': {'nameTempl': u'R_bk_footThumbtip', 'icone': 'circuloX', 'color': (0, 0, 1),
                                                       'size': 0.4},
                                     'baseCntrlSetup': {'nameTempl': u'R_bk_footThumbbase', 'icone': 'dropMenosZ', 'color': (.4, 0, 0),
                                                        'size': 0.1},
                                     'palmJntSetup': {'nameTempl': u'R_bk_footThumbPalm', 'icone': 'Bone', 'size': 0.2},
                                     'palmCntrlSetup': {'nameTempl': u'R_bk_footThumbpalm', 'icone': 'cubo', 'color': (.4, 0, 0),
                                                        'size': 0.2},
                                     'palmGuideSetup': {'nameTempl': u'R_bk_footThumbpalm', 'icone': 'circuloX', 'color': (0, 0, 1),
                                                        'size': 0.4}, 'flipAxis': False,
                                     'tipJntSetup': {'nameTempl': u'R_bk_footThumb', 'icone': 'Bone', 'size': 0.3}}
                     },

                     'heelCntrlSetup': {'nameTempl': 'R_bk_footHeel', 'icone': 'bola', 'color': (.4, 0, 0), 'size': 0.5},
                     'ballCntrlSetup': {'nameTempl': 'R_bk_footBall', 'icone': 'circuloX', 'color': (.4, 0, 0),
                                        'size': 1.5},
                     'baseGuideSetup': {'nameTempl': 'R_bk_footBase', 'icone': 'quadradoY', 'color': (1, 0, 1), 'size': 3},
                     'name': 'R_bk_foot',
                     'moveallGuideSetup': {'nameTempl': 'R_bk_footMoveAll', 'icone': 'quadradoY', 'color': (1, 0, 0),
                                           'size': 1.8},
                     'slideGuideSetup': {'nameTempl': 'R_bk_footSlide', 'icone': 'null', 'color': (1, 0, 1), 'size': 0.4},
                     'centerCntrlSetup': {'nameTempl': 'R_bk_footCenter', 'icone': 'circuloX', 'color': (.4, 0, 0),
                                          'size': 2},
                     'baseCntrlSetup': {'nameTempl': 'R_bk_footBase', 'icone': 'quadradoY', 'color': (.4, 0, 0), 'size': 3},
                     'toeCntrlSetup': {'nameTempl': 'R_bk_footToe', 'icone': 'circuloX', 'color': (.4, 0, 0), 'size': 1.0},
                     'toeJntSetup': {'nameTempl': 'R_bk_footToe', 'icone': 'Bone', 'size': 1.0},
                     'ankleCntrlSetup': {'nameTempl': 'R_bk_footAnkle', 'icone': 'cubo', 'color': (.4, 0, 0), 'size': 1},
                     'centerGuideSetup': {'nameTempl': 'R_bk_footCenter', 'icone': 'grp', 'color': (1, 1, 0), 'size': 0.5},
                     'flipAxis': False,
                     'inCntrlSetup': {'nameTempl': 'R_bk_footIn', 'icone': 'bola', 'color': (.4, 0, 0), 'size': 0.4},
                     'tipGuideSetup': {'nameTempl': 'R_bk_footTip', 'icone': 'bola', 'color': (0, 1, 1), 'size': 0.5},
                     'guideDict': {'ball': [(-1.0, 0.5, 0.0), (0.0, -0.0, 0.0),[1, 1, 1]],
                                   'center': [(0.0, 0.0, 0.0), (0.0, 0.0, 0.0), [1, 1, 1]],
                                   'tip': [(3.0, 0.0, 0.0), (0.0, -0.0, 0.0),[1, 1, 1]],
                                   'moveall': [(1.82, 0.0, 0.0), (0.0, -90.0, 0.0), [1, 1, 1]],
                                   'in': [(-1.0, 0.0, -1.0), (0.0, -0.0, 0.0),[1, 1, 1]],
                                   'ankle': [(0.0, 1.0, 0.0), (0.0, -0.0, 0.0),[1, 1, 1]],
                                   'heel': [(-1.0, 0.0, 0.0), (0.0, -0.0, 0.0),[1, 1, 1]],
                                   'out': [(-1.0, 0.0, 1.0), (0.0, -0.0, 0.0),[1, 1, 1]]}}

        neckDict = {
                    'moveAllGuideSetup': {'nameTempl': 'neckMoveall','icone': 'circuloX',},

                    'name': 'neck',

                    'guideDict': {'start': [(0.0, 0.0, 0.0), (0.0, -0.0, 0.0), (1.0, 1.0, 1.0)],
                                  'moveall': [(0.0, 13, 11), (30, -0.0, 0.0), (1.0, 1.0, 1.0)],
                                  'end': [(0.0, 2.0, 0.0), (0.0, -0.0, 0.0), (1.0, 1.0, 1.0)]
                                  },
                    'endGuideSetup': {'nameTempl': 'head','icone': 'circuloZ', 'color': (0, 1, 0), 'size': 3},
                    'moveAllCntrlSetup': {'nameTempl': 'neckMoveall', 'icone': 'circuloX', 'color': (0, 1, 0),
                                          'size': 1},
                    'midGuideSetup': {'nameTempl': 'midNeck','icone': 'circuloX', 'color': (1, 1, 0.15), 'size': 1},
                    'startCntrlSetup': {'nameTempl': 'Neck', 'icone': 'circuloY', 'color': (1, 1, 0.15), 'size': 3},
                    'endCntrlSetup': {'nameTempl': 'Head', 'icone': 'circuloZ', 'color': (1, 1, 0.15), 'size': 2},
                    'flipAxis': False,
                    'startGuideSetup': {'nameTempl': 'neck','icone': 'circuloY', 'color': (1, 1, 0.15), 'size': 1},
                    'axis': 'X'}

        spineDict = {
                     'spineFkCntrlSetup': {'nameTempl': 'spineWaistFk', 'icone': 'cubo', 'color': (1, 1, 0.15),
                                           'size': 4}, 'name': 'spine',
                     'startFkCntrlSetup': {'nameTempl': 'spineHipFk', 'icone': 'cubo',
                                           'color': (1, 1, 0.15), 'size': 3.0},
                     'endFkCntrlSetup': {'nameTempl': 'spineChestFk', 'icone': 'cubo',
                                         'color': (1, 1, 0.15), 'size': 4},
                     'midFkCntrlSetup': {'nameTempl': 'spineAbdomenFk', 'icone': 'cubo',
                                         'color': (1, 1, 0.15),'size': 4},
                     'midFkOffsetCntrlSetup': {'nameTempl': 'spineAbdomenFkOff', 'icone': 'circuloY',
                                               'color': (0, 1, 1), 'size': 2.5},

                     'moveallGuideSetup': {'nameTempl': 'spineMoveall', 'icone': 'quadradoZ', 'color': (1, 0, 0), 'size': 6},
                     'startGuideSetup': {'nameTempl': 'spineHip', 'icone': 'circuloZ', 'color': (0, 1, 0), 'size': 5},
                     'midGuideSetup': {'nameTempl': 'spineAbdomen','icone': 'circuloZ', 'color': (0, 1, 0), 'size': 5},
                     'endGuideSetup': {'nameTempl': 'spineChest', 'icone': 'circuloZ', 'color': (0, 1, 0), 'size': 5},
                     'endTipGuideSetup': {'nameTempl': 'spineChestTip','icone': 'null', 'color': (0, 1, 0), 'size': 1},
                     'startTipGuideSetup': {'nameTempl': 'spineHipTip','icone': 'null', 'color': (0, 1, 0), 'size': 1},
                     'startJntSetup': {'nameTempl': 'spineHip', 'icone': 'Bone', 'size': 2}, 'axis': 'X',
                     'endJntSetup': {'nameTempl': 'spineChest', 'icone': 'Bone', 'size': 2},

                     'guideDict': {'start': [(0.0, 0.0, 0.0), (0.0, 0.0, 0.0), (1.0, 1.0, 1.0)],
                                   'moveall': [(0.0, 11.0, 0.0), (0.0, 0.0, 0.0), (1.0, 1.0, 1.0)],
                                   'end': [(0.0, 0.0, 8.0), (0.0, 0.0, 0.0), (1.0, 1.0, 1.0)],
                                   'endTip': [(0.0, 0, 2.0), (0.0, 0.0, 0.0), (1.0, 1.0, 1.0)],
                                   'startTip': [(0.0, 0, -3.0), (0.0, 0.0, 0.0), (1.0, 1.0, 1.0)],
                                   'mid': [(0.0, 0.0, 0.0), (0.0, 0.0, 0.0), (1.0, 1.0, 1.0)]
                                  },

                     'flipAxis': False,
                     'hipCntrlSetup': {'nameTempl': 'spineCOG', 'icone': 'cogZ', 'color': (1, 0, 0), 'size': 5.5},
                     'moveallSetup': {'nameTempl': 'spineMoveAll', 'icone': 'grp', 'color': (1, 1, 0), 'size': 1.8},

                     'startIkCntrlSetup': {'nameTempl': 'spineHipIk', 'icone': 'circuloPontaZ',
                                          'color': (1, 1, 0.15), 'size': 4},
                     'midIkCntrlSetup': {'nameTempl': 'spineAbdomenIk', 'icone': 'circuloPontaZ', 'color': (1, 1, 0.15),
                                        'size': 4},
                     'endIkCntrlSetup': {'nameTempl': 'spineChestIk', 'icone': 'circuloPontaZ', 'color': (1, 1, 0.15),
                                         'size': 4}}

        lclavDict = {
                     'name': 'L_clavicle',
                     'moveAllCntrlSetup': {'nameTempl': 'L_clavicleMoveall', 'icone': 'circuloX',
                                           'color': (1, 1, 0), 'size': 2.5},
                     'guideDict': {
                                    'moveall': [(1.82, 11.0, 9.73), (0.0, -0.0, -90), (1.0, 1.0, 1.0)],
                                    'guide2': [(1, 0, 0), (0.0, -0.0, 0.0), (1.0, 1.0, 1.0)],
                                    'guide1': [(0.0, 0.0, 0.0), (0.0, -0.0, 0.0), (1.0, 1.0, 1.0)]
                                },
                     'fkCntrlSetup': {'nameTempl': 'L_clavicleChainFk', 'icone': 'circuloX', 'color': (0.01, 0.05, 0.2 ),
                                      'size': 0.8}, 'flipAxis': False,
                     'jntSetup': {'nameTempl': 'L_clavicleChain', 'icone': 'Bone', 'size': 0.8},
                     'guideSetup': {'nameTempl': 'L_clavicleChain','icone': 'circuloX',
                                    'color': (0.010, 0.050, 0.2), 'size': 0.8}, 'axis': 'X'}

        rclavDict = {
                     'name': 'R_clavicle',
                     'moveAllCntrlSetup': {'nameTempl': 'R_clavicleMoveall', 'icone': 'circuloX',
                                           'color': (1, 1, 0),'size': 2.5},
                     'guideDict': {
                                    'moveall': [(1.82, 11.0, 9.73), (0.0, -0.0,  -90), (1.0, 1.0, 1.0)],
                                    'guide2': [(1, 0, 0), (0.0, -0.0, 0.0), (1.0, 1.0, 1.0)],
                                    'guide1': [(0.0, 0.0, 0.0), (0.0, -0.0, 0.0), (1.0, 1.0, 1.0)]
                                    },

                     'fkCntrlSetup': {'nameTempl': 'R_clavicleChainFk', 'icone': 'circuloX', 'color': (.4, 0, 0),
                                      'size': 0.8}, 'flipAxis': False,
                     'jntSetup': {'nameTempl': 'R_clavicleChain', 'icone': 'Bone', 'size': 0.8},
                     'guideSetup': {'nameTempl': 'R_clavicleChain','icone': 'circuloX', 'color': (.4, 0, 0), 'size': 0.8},
                     'axis': 'X'
                    }

        llegShoulderDict = {'name': 'L_legShoulder',
                            'moveAllCntrlSetup': {'nameTempl': 'L_legShoulderMoveAll', 'icone': 'circuloX',
                                                  'color': (1, 1, 0), 'size': 1.8},
                            'guideDict': {
                                            'moveall': [(1.82, 11.0, 0.0), (0.0, 0.0, -90), (1.0, 1.0, 1.0)],
                                            'guide2': [(1.0, 0.0, 0.0), (0.0, -0.0, 0.0), (1.0, 1.0, 1.0)],
                                            'guide1': [(0.0, 0.0, 0.0), (0.0, -0.0, 0.0), (1.0, 1.0, 1.0)]
                                        },

                            'fkCntrlSetup': {'nameTempl': 'L_legShoulderChainFk', 'icone': 'circuloX',
                                             'color': (0.01, 0.05, 0.2 ), 'size': 2.5}, 'flipAxis': False,
                            'jntSetup': {'nameTempl': 'L_legShoulderChain', 'icone': 'Bone', 'size': 0.8},
                            'guideSetup': {'nameTempl': 'L_legShoulderChain', 'icone': 'circuloX', 'color': (0, 1, 0), 'size': 0.8},
                            'axis': 'X'}

        rlegShoulderDict = {'name': 'R_legShoulder',
                            'moveAllCntrlSetup': {'nameTempl': 'R_legShoulderMoveAll', 'icone': 'circuloX',
                                                  'color': (1, 1, 0), 'size': 1.8},
                            'guideDict': {
                                            'moveall': [(1.82, 11.0, 0.0), (0.0, 0.0, -90), (1.0, 1.0, 1.0)],
                                            'guide2': [(1.0, 0.0, 0.0), (0.0, -0.0, 0.0), (1.0, 1.0, 1.0)],
                                            'guide1': [(0.0, 0.0, 0.0), (0.0, -0.0, 0.0), (1.0, 1.0, 1.0)]},

                            'fkCntrlSetup': {'nameTempl': 'R_legShoulderChainFk', 'icone': 'circuloX',
                                             'color': (.4, 0, 0), 'size': 2.5}, 'flipAxis': False,
                            'jntSetup': {'nameTempl': 'R_legShoulderChain', 'icone': 'Bone', 'size': 0.8},
                            'guideSetup': {'nameTempl': 'R_legShoulderChain','icone': 'circuloX', 'color': (0, 1, 0), 'size': 0.8},
                            'axis': 'X'}

        self.lfrLeg.__dict__.update(**larmDict)
        self.rfrLeg.__dict__.update(**rarmDict)

        self.lfrFoot.__dict__.update(**lhandDict)
        self.rfrFoot.__dict__.update(**rhandDict)

        self.lbkFoot.__dict__.update(**lfootDict)
        self.rbkFoot.__dict__.update(**rfootDict)

        self.lclav.__dict__.update(**lclavDict)
        self.rclav.__dict__.update(**rclavDict)

        if self.tail:
            self.tail.__dict__.update(**tailDict)

        self.lbkLeg.__dict__.update(**llegDict)
        self.rbkLeg.__dict__.update(**rlegDict)

        self.llegShoulder.__dict__.update(**llegShoulderDict)
        self.rlegShoulder.__dict__.update(**rlegShoulderDict)

        self.spine.__dict__.update(**spineDict)
        self.neck.__dict__.update(**neckDict)

    def saveSkin(self):
        dirName = os.path.expanduser('~/maya/autoRig3')
        if not os.path.exists(dirName):
            os.mkdir(dirName)
        path = os.path.join(dirName, self.name + '.skin')

        self.getSkinJntsFromScene()
        self.getSkinnedModels()
        skinTools.saveSkinning(path, meshes=self.modelList)

    def loadSkin(self):
        dirName = os.path.expanduser('~/maya/autoRig3')
        path = os.path.join(dirName, self.name + '.skin')

        if not os.path.exists(path):
            logger.error ('file not found!!')
            return
        skinTools.loadSkinning(path)

    def doGuides(self, **kwargs):
        self.__dict__.update(**kwargs)


        self.lfrLeg.doGuide()
        self.rfrLeg.doGuide()
        self.rfrLeg.mirrorConnectGuide(self.lfrLeg)

        self.lfrFoot.doGuide()
        self.rfrFoot.doGuide()
        self.rfrFoot.mirrorConnectGuide(self.lfrFoot)

        self.lbkFoot.doGuide()
        self.rbkFoot.doGuide()
        self.rbkFoot.mirrorConnectGuide(self.lbkFoot)

        self.lclav.doGuide()
        self.rclav.doGuide()
        self.rclav.mirrorConnectGuide(self.lclav)

        self.lbkLeg.doGuide()
        self.rbkLeg.doGuide()
        self.rbkLeg.mirrorConnectGuide(self.lbkLeg)

        self.llegShoulder.doGuide()
        self.rlegShoulder.doGuide()
        self.rlegShoulder.mirrorConnectGuide(self.llegShoulder)

        self.spine.doGuide()
        self.neck.doGuide()

        self.master.doGuide()

        pm.parent(self.lfrLeg.guideMoveall, self.rfrLeg.mirrorGuide, self.lfrFoot.guideMoveall,
                  self.rfrFoot.mirrorGuide, self.lbkFoot.guideMoveall, self.rbkFoot.mirrorGuide,
                  self.lclav.guideMoveall, self.rclav.mirrorGuide, self.lbkLeg.guideMoveall, self.rbkLeg.mirrorGuide,
                  self.llegShoulder.guideMoveall, self.rlegShoulder.mirrorGuide, self.spine.guideMoveall,
                  self.neck.guideMoveall, self.master.guideMoveall)

        if self.tail:
            self.tail.doGuide()
            pm.parent(self.tail.guideMoveall, self.master.guideMoveall)

        pm.parentConstraint(self.lfrLeg.lastGuide, self.lfrFoot.guideMoveall, mo=True)
        pm.scaleConstraint(self.lfrLeg.lastGuide, self.lfrFoot.guideMoveall, mo=True)
        pm.parentConstraint(self.lbkLeg.lastGuide, self.lbkFoot.guideMoveall, mo=True)
        pm.scaleConstraint(self.lbkLeg.lastGuide, self.lbkFoot.guideMoveall, mo=True)

        pm.addAttr(self.master.guideMoveall, ln='quadrupedDict', dt='string')
        self.master.guideMoveall.quadrupedDict.set(json.dumps(self.exportDict()))

    def exportDict(self):
        expDict = {}
        for key in self.toExport:
                expDict[key] = self.__dict__[key]
        return expDict

    def storeDictOnControl(self):
        self.lfrLeg.getDict()
        self.master.moveall3.larmDict.set(json.dumps(self.lfrLeg.exportDict()))
        self.rfrLeg.getDict()
        self.master.moveall3.rarmDict.set(json.dumps(self.rfrLeg.exportDict()))

        self.lbkLeg.getDict()
        self.master.moveall3.llegDict.set(json.dumps(self.lbkLeg.exportDict()))
        self.rbkLeg.getDict()
        self.master.moveall3.rlegDict.set(json.dumps(self.rbkLeg.exportDict()))

        self.lfrFoot.getDict()
        self.master.moveall3.lhandDict.set(json.dumps(self.lfrFoot.exportDict()))
        self.rfrFoot.getDict()
        self.master.moveall3.rhandDict.set(json.dumps(self.rfrFoot.exportDict()))

        self.lbkFoot.getDict()
        self.master.moveall3.lfootDict.set(json.dumps(self.lbkFoot.exportDict()))
        self.rbkFoot.getDict()
        self.master.moveall3.rfootDict.set(json.dumps(self.rbkFoot.exportDict()))

        self.neck.getDict()
        self.master.moveall3.neckDict.set(json.dumps(self.neck.exportDict()))
        self.spine.getDict()
        self.master.moveall3.spineDict.set(json.dumps(self.spine.exportDict()))

        self.lclav.getDict()
        self.master.moveall3.lclavDict.set(json.dumps(self.lclav.exportDict()))
        self.rclav.getDict()
        self.master.moveall3.rclavDict.set(json.dumps(self.rclav.exportDict()))

        if self.tail:
            self.tail.getDict()
            self.master.moveall3.tailDict.set(json.dumps(self.tail.exportDict()))

        self.llegShoulder.getDict()
        self.master.moveall3.llegShoulderDict.set(json.dumps(self.llegShoulder.exportDict()))
        self.rlegShoulder.getDict()
        self.master.moveall3.rlegShoulderDict.set(json.dumps(self.rlegShoulder.exportDict()))

        jnts = [x.name() for x in self.skinJoints]
        self.master.moveall3.skinJoints.set(json.dumps(jnts))

    def doRig(self):
        self.rfrFoot.doRig()
        self.lfrFoot.doRig()
        self.lfrLeg.doRig()
        self.rfrLeg.doRig()
        self.lbkFoot.doRig()
        self.rbkFoot.doRig()
        self.lbkLeg.doRig()
        self.rbkLeg.doRig()
        self.llegShoulder.doRig()
        self.rlegShoulder.doRig()
        self.master.doRig()
        self.neck.doRig()
        self.spine.ribbonJntNum = self.spineRibbonJnts
        self.spine.doRig()
        self.lclav.doRig()
        self.rclav.doRig()

        self.skinJoints = self.rfrFoot.skinJoints + self.lfrFoot.skinJoints + \
                          self.rbkFoot.skinJoints + self.lbkFoot.skinJoints + self.llegShoulder.skinJoints + \
                          self.rlegShoulder.skinJoints + self.neck.skinJoints + self.spine.skinJoints + \
                          self.lclav.skinJoints + self.rclav.skinJoints

        if self.tail:
            self.tail.doRig()
            self.skinJoints += self.tail.skinJoints

        if self.armRibbonJnts > 0:
            ribbonSkinJnts = self.doArmRibbons(numJnts=self.armRibbonJnts * 2,
                                               offsetStart=self.armRibbonFirstOffset*0.1,
                                               offsetEnd=self.armRibbonLastOffset*0.1)
            self.skinJoints += ribbonSkinJnts
        else:
            self.skinJoints += self.lfrFoot.skinJoints + self.rfrFoot.skinJoints

        if self.legRibbonJnts > 0:
            ribbonSkinJnts = self.doLegRibbons(numJnts=self.legRibbonJnts * 2,
                                               offsetStart=self.legRibbonFirstOffset*0.1,
                                               offsetEnd=self.legRibbonLastOffset*0.1)
            self.skinJoints += ribbonSkinJnts
        else:
            self.skinJoints += self.lbkLeg.skinJoints + self.rbkLeg.skinJoints

        if self.moduleConnection:
            self.parentModules()
        else:
            self.constraintModules()

        self.doHipAttrs()
        self.doFootAttrs()
        self.doSpaceSwitches()

        self.moveallAttrs()

        self.storeDictOnControl()

    def getDict(self):
        logger.debug('pegando guides da cena')

        self.lfrLeg.getDict()
        self.rfrLeg.getDict()
        self.lfrFoot.getDict()
        self.rfrFoot.getDict()
        self.lbkFoot.getDict()
        self.rbkFoot.getDict()
        self.lbkLeg.getDict()
        self.rbkLeg.getDict()
        self.llegShoulder.getDict()
        self.rlegShoulder.getDict()
        self.neck.getDict()
        self.spine.getDict()
        self.lclav.getDict()
        self.rclav.getDict()
        self.master.getDict()
        if self.tail:
            self.tail.getDict()

        try:
            jsonDict = self.master.guideMoveall.quadrupedDict.get()
            dictRestored = json.loads(jsonDict)

            self.__dict__.update(**dictRestored)
        except:
            pass

    def doArmRibbons(self, numJnts=10, offsetStart=0.1, offsetEnd=0.1):
        self.lfrRibbon = ribbonBezier.RibbonBezier(name='L_fr_legBezier', size=self.lfrLeg.jointLength, offsetStart=offsetStart,
                                                   offsetEnd=offsetEnd, numJnts=numJnts)
        self.lfrRibbon.doRig()
        self.lfrRibbon.connectToLimb(self.lfrLeg)
        self.rfrRibbon = ribbonBezier.RibbonBezier(name='R_fr_legBezier', size=self.lfrLeg.jointLength, offsetStart=offsetStart,
                                                   offsetEnd=offsetEnd, numJnts=numJnts)
        self.rfrRibbon.doRig()
        self.rfrRibbon.connectToLimb(self.rfrLeg)

        startJntName = self.lfrLeg.startJnt.replace('_jnt', '_jxt')
        self.lfrLeg.startJnt.rename(startJntName)
        midJntName = self.lfrLeg.midJnt.replace('_jnt', '_jxt')
        self.lfrLeg.midJnt.rename(midJntName)
        endJntName = self.lfrLeg.endJnt.replace('_jnt', '_jxt')
        self.lfrLeg.endJnt.rename(endJntName)

        startJntName = self.rfrLeg.startJnt.replace('_jnt', '_jxt')
        self.rfrLeg.startJnt.rename(startJntName)
        midJntName = self.rfrLeg.midJnt.replace('_jnt', '_jxt')
        self.rfrLeg.midJnt.rename(midJntName)
        endJntName = self.rfrLeg.endJnt.replace('_jnt', '_jxt')
        self.rfrLeg.endJnt.rename(endJntName)

        return self.rfrRibbon.skinJoints + self.lfrRibbon.skinJoints

    def doLegRibbons(self, numJnts=10, offsetStart=0.08, offsetEnd=0.1):
        self.lbkRibbon = ribbonBezier.RibbonBezier(name='L_bk_legBezier', size=self.lbkLeg.jointLength, offsetStart=offsetStart,
                                                   offsetEnd=offsetEnd, numJnts=numJnts)
        self.lbkRibbon.doRig()
        self.lbkRibbon.connectToLimb(self.lbkLeg)
        self.rbkRibbon = ribbonBezier.RibbonBezier(name='R_bk_legBezier', size=self.lbkLeg.jointLength, offsetStart=offsetStart,
                                                   offsetEnd=offsetEnd, numJnts=numJnts)
        self.rbkRibbon.doRig()
        self.rbkRibbon.connectToLimb(self.rbkLeg)

        startJntName = self.lbkLeg.startJnt.replace('_jnt', '_jxt')
        self.lbkLeg.startJnt.rename(startJntName)
        midJntName = self.lbkLeg.midJnt.replace('_jnt', '_jxt')
        self.lbkLeg.midJnt.rename(midJntName)
        endJntName = self.lbkLeg.endJnt.replace('_jnt', '_jxt')
        self.lbkLeg.endJnt.rename(endJntName)

        startJntName = self.rbkLeg.startJnt.replace('_jnt', '_jxt')
        self.rbkLeg.startJnt.rename(startJntName)
        midJntName = self.rbkLeg.midJnt.replace('_jnt', '_jxt')
        self.rbkLeg.midJnt.rename(midJntName)
        endJntName = self.rbkLeg.endJnt.replace('_jnt', '_jxt')
        self.rbkLeg.endJnt.rename(endJntName)

        return self.rbkRibbon.skinJoints + self.lbkRibbon.skinJoints

    def constraintModules(self):
        pm.parentConstraint(self.spine.endTipJnt, self.lclav.moveall, mo=True)
        pm.parentConstraint(self.spine.endTipJnt, self.rclav.moveall, mo=True)
        pm.parentConstraint(self.spine.endTipJnt, self.neck.moveall, mo=True)
        pm.parentConstraint(self.rclav.jntList[-1], self.rfrLeg.moveall, mo=True)
        pm.parentConstraint(self.lclav.jntList[-1], self.lfrLeg.moveall, mo=True)
        pm.parentConstraint(self.lfrLeg.lastJnt, self.lfrFoot.limbConnectionCntrl.getParent())
        pm.parentConstraint(self.rfrLeg.lastJnt, self.rfrFoot.limbConnectionCntrl.getParent())
        pm.parentConstraint(self.spine.startTipJnt, self.llegShoulder.moveall, mo=True)
        pm.parentConstraint(self.spine.startTipJnt, self.rlegShoulder.moveall, mo=True)
        pm.parentConstraint(self.rlegShoulder.jntList[-1], self.rbkLeg.moveall, mo=True)
        pm.parentConstraint(self.llegShoulder.jntList[-1], self.lbkLeg.moveall, mo=True)
        pm.parentConstraint(self.lbkFoot.ballCntrl, self.lbkLeg.ikCntrl, mo=True)  # checar...
        pm.parentConstraint(self.rbkFoot.ballCntrl, self.rbkLeg.ikCntrl, mo=True)
        if self.tail:
            pm.parentConstraint(self.spine.endTipJnt, self.tail.moveall, mo=False)
        pm.parentConstraint(self.lbkLeg.lastJnt, self.lbkFoot.limbConnectionCntrl.getParent())
        pm.parentConstraint(self.rbkLeg.lastJnt, self.rbkFoot.limbConnectionCntrl.getParent())

    def parentModules(self):
        pm.parent(self.neck.moveall, self.spine.endTipJnt)
        pm.parent(self.lclav.moveall, self.spine.endTipJnt)
        pm.parent(self.rclav.moveall, self.spine.endTipJnt)

        #if self.tail:
        #    pm.parent(self.tail.moveall,  self.spine.startTipJnt, r=True)

        pm.parent(self.llegShoulder.moveall, self.spine.startTipJnt)
        pm.parent(self.rlegShoulder.moveall, self.spine.startTipJnt)
        
        pm.parent(self.lfrLeg.ikCntrl.getParent(), self.lfrFoot.ballCntrl)
        pm.parent(self.rfrLeg.ikCntrl.getParent(), self.rfrFoot.ballCntrl)
        pm.parentConstraint(self.lfrLeg.startCntrl, self.lfrFoot.ankleFkCntrl, mo=True)
        pm.parentConstraint(self.rfrLeg.startCntrl, self.rfrFoot.ankleFkCntrl, mo=True)
        pm.parent(self.rfrLeg.moveall, self.rclav.jntList[-1])
        pm.parent(self.lfrLeg.moveall, self.lclav.jntList[-1])
        pm.parent(self.lfrFoot.limbConnectionCntrl.getParent(), self.lfrLeg.lastJnt)
        pm.parent(self.rfrFoot.limbConnectionCntrl.getParent(), self.rfrLeg.lastJnt)
        
        pm.parent(self.lbkLeg.ikCntrl.getParent(), self.lbkFoot.ballCntrl)
        pm.parent(self.rbkLeg.ikCntrl.getParent(), self.rbkFoot.ballCntrl)
        pm.parentConstraint(self.lbkLeg.startCntrl, self.lbkFoot.ankleFkCntrl, mo=True)
        pm.parentConstraint(self.rbkLeg.startCntrl, self.rbkFoot.ankleFkCntrl, mo=True)
        pm.parent(self.rbkLeg.moveall, self.rlegShoulder.jntList[-1])
        pm.parent(self.lbkLeg.moveall, self.llegShoulder.jntList[-1])
        pm.parent(self.lbkFoot.limbConnectionCntrl.getParent(), self.lbkLeg.lastJnt)
        pm.parent(self.rbkFoot.limbConnectionCntrl.getParent(), self.rbkLeg.lastJnt)

    def doHipAttrs(self):
        self.spine.cogCntrl.addAttr('L_arm_FkIk', at='float', dv=1, max=1, min=0, k=1)
        self.spine.cogCntrl.addAttr('R_arm_FkIk', at='float', dv=1, max=1, min=0, k=1)
        self.spine.cogCntrl.addAttr('L_leg_FkIk', at='float', dv=1, max=1, min=0, k=1)
        self.spine.cogCntrl.addAttr('R_leg_FkIk', at='float', dv=1, max=1, min=0, k=1)
        self.spine.cogCntrl.addAttr('Spine_FkIk', at='float', dv=1, max=1, min=0, k=1)

        self.spine.cogCntrl.addAttr('L_arm_poleVec', at='float', dv=0, max=1, min=0, k=1)
        self.spine.cogCntrl.addAttr('R_arm_poleVec', at='float', dv=0, max=1, min=0, k=1)
        self.spine.cogCntrl.addAttr('L_leg_poleVec', at='float', dv=0, max=1, min=0, k=1)
        self.spine.cogCntrl.addAttr('R_leg_poleVec', at='float', dv=0, max=1, min=0, k=1)

        self.spine.cogCntrl.Spine_FkIk >> self.spine.moveall.ikfk
        self.spine.cogCntrl.R_leg_FkIk >> self.rbkLeg.moveall.ikfk
        self.spine.cogCntrl.L_leg_FkIk >> self.lbkLeg.moveall.ikfk

        self.spine.cogCntrl.R_leg_FkIk >> self.rbkFoot.moveall.ikfk
        self.spine.cogCntrl.L_leg_FkIk >> self.lbkFoot.moveall.ikfk

        self.spine.cogCntrl.R_arm_FkIk >> self.rfrLeg.moveall.ikfk
        self.spine.cogCntrl.L_arm_FkIk >> self.lfrLeg.moveall.ikfk

        self.spine.cogCntrl.R_arm_FkIk >> self.rfrFoot.moveall.ikfk
        self.spine.cogCntrl.L_arm_FkIk >> self.lfrFoot.moveall.ikfk

        self.spine.cogCntrl.R_arm_poleVec >> self.rfrLeg.moveall.poleVec
        self.spine.cogCntrl.L_arm_poleVec >> self.lfrLeg.moveall.poleVec
        self.spine.cogCntrl.R_leg_poleVec >> self.rbkLeg.moveall.poleVec
        self.spine.cogCntrl.L_leg_poleVec >> self.lbkLeg.moveall.poleVec

    def doFootAttrs(self):
        self.lfrFoot.baseCntrl.addAttr('pin', at='float', min=0, max=1, dv=0, k=1)
        self.lfrFoot.baseCntrl.addAttr('bias', at='float', min=-0.9, max=0.9, k=1)
        self.lfrFoot.baseCntrl.addAttr('autoStretch', at='float', min=0, max=1, dv=1, k=1)
        self.lfrFoot.baseCntrl.addAttr('manualStretch', at='float', dv=1, k=1)
        self.lfrFoot.baseCntrl.addAttr('twist', at='float', dv=0, k=1)
        self.lfrFoot.baseCntrl.pin >> self.lfrLeg.ikCntrl.pin
        self.lfrFoot.baseCntrl.bias >> self.lfrLeg.ikCntrl.bias
        self.lfrFoot.baseCntrl.autoStretch >> self.lfrLeg.ikCntrl.autoStretch
        self.lfrFoot.baseCntrl.manualStretch >> self.lfrLeg.ikCntrl.manualStretch
        self.lfrFoot.baseCntrl.twist >> self.lfrLeg.ikCntrl.twist
        self.lfrLeg.ikCntrl.visibility.set(0)

        self.rfrFoot.baseCntrl.addAttr('pin', at='float', min=0, max=1, dv=0, k=1)
        self.rfrFoot.baseCntrl.addAttr('bias', at='float', min=-0.9, max=0.9, k=1)
        self.rfrFoot.baseCntrl.addAttr('autoStretch', at='float', min=0, max=1, dv=1, k=1)
        self.rfrFoot.baseCntrl.addAttr('manualStretch', at='float', dv=1, k=1)
        self.rfrFoot.baseCntrl.addAttr('twist', at='float', dv=0, k=1)
        self.rfrFoot.baseCntrl.pin >> self.rfrLeg.ikCntrl.pin
        self.rfrFoot.baseCntrl.bias >> self.rfrLeg.ikCntrl.bias
        self.rfrFoot.baseCntrl.autoStretch >> self.rfrLeg.ikCntrl.autoStretch
        self.rfrFoot.baseCntrl.manualStretch >> self.rfrLeg.ikCntrl.manualStretch
        self.rfrFoot.baseCntrl.twist >> self.rfrLeg.ikCntrl.twist
        self.rfrLeg.ikCntrl.visibility.set(0)
        
        
        self.lbkFoot.baseCntrl.addAttr('pin', at='float', min=0, max=1, dv=0, k=1)
        self.lbkFoot.baseCntrl.addAttr('bias', at='float', min=-0.9, max=0.9, k=1)
        self.lbkFoot.baseCntrl.addAttr('autoStretch', at='float', min=0, max=1, dv=1, k=1)
        self.lbkFoot.baseCntrl.addAttr('manualStretch', at='float', dv=1, k=1)
        self.lbkFoot.baseCntrl.addAttr('twist', at='float', dv=0, k=1)
        self.lbkFoot.baseCntrl.pin >> self.lbkLeg.ikCntrl.pin
        self.lbkFoot.baseCntrl.bias >> self.lbkLeg.ikCntrl.bias
        self.lbkFoot.baseCntrl.autoStretch >> self.lbkLeg.ikCntrl.autoStretch
        self.lbkFoot.baseCntrl.manualStretch >> self.lbkLeg.ikCntrl.manualStretch
        self.lbkFoot.baseCntrl.twist >> self.lbkLeg.ikCntrl.twist

        self.rbkFoot.baseCntrl.addAttr('pin', at='float', min=0, max=1, dv=0, k=1)
        self.rbkFoot.baseCntrl.addAttr('bias', at='float', min=-0.9, max=0.9, k=1)
        self.rbkFoot.baseCntrl.addAttr('autoStretch', at='float', min=0, max=1, dv=1, k=1)
        self.rbkFoot.baseCntrl.addAttr('manualStretch', at='float', dv=1, k=1)
        self.rbkFoot.baseCntrl.addAttr('twist', at='float', dv=0, k=1)
        self.rbkFoot.baseCntrl.pin >> self.rbkLeg.ikCntrl.pin
        self.rbkFoot.baseCntrl.bias >> self.rbkLeg.ikCntrl.bias
        self.rbkFoot.baseCntrl.autoStretch >> self.rbkLeg.ikCntrl.autoStretch
        self.rbkFoot.baseCntrl.manualStretch >> self.rbkLeg.ikCntrl.manualStretch
        self.rbkFoot.baseCntrl.twist >> self.rbkLeg.ikCntrl.twist

    def doSpaceSwitches(self):
        if pm.objExists('spaces'):
            pm.delete('spaces')

        spaceSwitchTools.createSpc(None, 'global')
        spaceSwitchTools.createSpc(self.lfrLeg.lastJnt, 'lhand')
        spaceSwitchTools.createSpc(self.rfrLeg.lastJnt, 'rhand')
        spaceSwitchTools.createSpc(self.spine.cogCntrl, 'hip')
        spaceSwitchTools.createSpc(self.spine.endJnt, 'chest')
        spaceSwitchTools.createSpc(self.spine.startJnt, 'cog')
        spaceSwitchTools.createSpc(self.lbkLeg.lastJnt, 'lfoot')
        spaceSwitchTools.createSpc(self.rbkLeg.lastJnt, 'rfoot')
        spaceSwitchTools.createSpc(self.lclav.jntList[-1], 'lclav')
        spaceSwitchTools.createSpc(self.rclav.jntList[-1], 'rclav')
        spaceSwitchTools.createSpc(self.neck.startJnt, 'neck')
        spaceSwitchTools.createSpc(self.neck.endJnt, 'head')

        spaceSwitchTools.addSpc(target=self.lfrLeg.poleVec, spaceList=['hip', 'global', 'chest', 'cog', 'lclav'],
                            switcher=self.lfrLeg.poleVec.getParent(), type='parent')

        spaceSwitchTools.addSpc(target=self.rfrLeg.poleVec, spaceList=['hip', 'global', 'chest', 'cog', 'rclav'],
                            switcher=self.rfrLeg.poleVec.getParent(), type='parent')

        spaceSwitchTools.addSpc(target=self.lbkLeg.poleVec, spaceList=['hip', 'global', 'chest', 'cog'],
                            switcher=self.lbkLeg.poleVec.getParent(), type='parent')

        spaceSwitchTools.addSpc(target=self.rbkLeg.poleVec, spaceList=['hip', 'global', 'chest', 'cog'],
                            switcher=self.rbkLeg.poleVec.getParent(), type='parent')

        spaceSwitchTools.addSpc(target=self.spine.endIkCntrl, spaceList=['hip', 'global', 'cog'],
                            switcher=self.spine.endIkCntrl.getParent(), type='parent')

        spaceSwitchTools.addSpc(target=self.neck.endCntrl, spaceList=['global', 'hip', 'chest', 'cog', 'neck'],
                            switcher=self.neck.endCntrl.getParent(), type='orient', posSpc=self.neck.startJnt)

        if self.tail:
            spaceSwitchTools.addSpc(target=self.tail.cntrlList[0], spaceList=['global', 'hip', 'cog'],
                                switcher=self.tail.cntrlList[0].getParent(), type='orient', posSpc=self.spine.startTipJnt)

    def getSkinJntsFromScene(self):
        try:
            print self.master.moveall3
            print self.master.name+'_moveall3_ctrl'
            if self.master.moveall3:
                moveall3 = self.master.moveall3
            else:
                moveall3 = pm.PyNode(self.master.name + '_moveall3_ctrl')
        except:
            logger.error('Nao conseguiu achar moveall3')
            return

        skinJntsJson = moveall3.getAttr('skinJoints')
        skinJns = json.loads(skinJntsJson)
        self.skinJoints = skinJns
        return skinJns

    def getSkinnedModels(self):
        modelList = []
        for jnt in self.skinJoints:
            skinClsList = list(set(pm.listConnections(jnt, type='skinCluster')))
            for skinCls in skinClsList:
                msh = list(set(pm.listConnections(skinCls, d=True, s=False, sh=True, type='surfaceShape')))
                if msh:
                    modelList.append(msh[0])

        self.modelList = list(set(modelList))
        return self.modelList

    def moveallAttrs(self):
        pm.addAttr(self.master.moveall3, ln='larmDict', dt='string')
        pm.addAttr(self.master.moveall3, ln='rarmDict', dt='string')
        pm.addAttr(self.master.moveall3, ln='llegDict', dt='string')
        pm.addAttr(self.master.moveall3, ln='rlegDict', dt='string')
        pm.addAttr(self.master.moveall3, ln='lhandDict', dt='string')
        pm.addAttr(self.master.moveall3, ln='rhandDict', dt='string')
        pm.addAttr(self.master.moveall3, ln='lfootDict', dt='string')
        pm.addAttr(self.master.moveall3, ln='rfootDict', dt='string')
        pm.addAttr(self.master.moveall3, ln='neckDict', dt='string')
        pm.addAttr(self.master.moveall3, ln='spineDict', dt='string')
        pm.addAttr(self.master.moveall3, ln='lclavDict', dt='string')
        pm.addAttr(self.master.moveall3, ln='rclavDict', dt='string')
        pm.addAttr(self.master.moveall3, ln='llegShoulderDict', dt='string')
        pm.addAttr(self.master.moveall3, ln='rlegShoulderDict', dt='string')
        pm.addAttr(self.master.moveall3, ln='tailDict', dt='string')
        pm.addAttr(self.master.moveall3, ln='skinJoints', dt='string')
