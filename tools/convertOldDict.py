import pymel.core as pm
import pprint as pp
import json

sel = pm.ls(sl=True)
for x in sel:
    jsonString = x.getAttr('handDict')
    hDict = json.loads(jsonString)

    if 'Pink' in hDict['fingers']:
        print 'tem pink'
        hDict['fingers']['Pinky'] = hDict['fingers']['Pink']
        del hDict['fingers']['Pink']

    jsonString = json.dumps(hDict)
    x.handDict.set(jsonString)
