import pymel.core as pm

## code by zansyabana@gmail.com
def oneLiner(nName, method='s'):
    # get selection method
    if nName.find('/s') != -1:
        method = 's'
        nName = nName.replace('/s', '')
    elif nName.find('/h') != -1:
        method = 'h'
        nName = nName.replace('/h', '')
    elif nName.find('/a') != -1:
        if nName.find('>') != -1:
            method = 'a'
            print method
        nName = nName.replace('/a', '')

    if method == 's':
        slt = pm.selected()
    elif method == 'h':
        sltH = []
        slt = pm.selected()
        for i in slt:
            sltH.append(i)
            for child in reversed(i.listRelatives(ad=True, type='transform')):
                sltH.append(child)
        print sltH
        slt = sltH
    elif method == 'a':
        slt = pm.ls()

    # find numbering replacement
    def numReplace(numName, idx, start=1):
        global padding
        if numName.find('//') != -1:
            start = int(numName[numName.find('//') + 2:len(numName)])
            numName = numName.replace(numName[numName.find('//'):len(numName)], '')
            print start
        number = idx + start
        if numName.find('#') != -1:
            padding = numName.count('#')
            hastag = "{0:#>{1}}".format("#", padding)  # get how many '#' is in the new name
            num = "{0:0>{1}d}".format(number, padding)  # get number
            numName = numName.replace(hastag, num)
        return numName

    for i in slt:  # for every object in selection list
        # check if there is '>' that represents the replacement method
        if nName.find('>') != -1:
            wordSplit = nName.split('>')
            oldWord = wordSplit[0]
            newWord = wordSplit[1]
            try:
                pm.rename(i,i.replace(oldWord,newWord))
            except:
                print "{} is not renamed".format(i)

        # check if the first character is '-' or '+', remove character method
        elif nName[0] == '-':
            charToRemove = int(nName[1:len(nName)])
            try:
                pm.rename(i, i[0:-charToRemove])
            except:
                print "{} is not renamed".format(i)

        elif nName[0] == '+':
            charToRemove = int(nName[1:len(nName)])
            pm.rename(i, i[charToRemove:len(str(i))])

        else:
            newName = numReplace(nName, slt.index(i))
            # get current Name if '!' mentioned
            print i
            if newName.find('!') != -1:
                newName = newName.replace('!', str(i))
                print newName
            try:
                pm.rename(i, newName)
            except:
                print "{} is not renamed".format(i)

class oneLinerWindow(object):

    windowName = "OneLiner"

    def show(self):

        if pm.window(self.windowName, q=True, exists=True):
            pm.deleteUI(self.windowName)
            pm.windowPref(self.windowName, remove=True)
        pm.window(self.windowName, s=True, w=300, h=100, rtf=False)

        self.buildUI()

        pm.showWindow()

    def buildUI(self):
        toolTip = 'Character replacement symbols:' \
                  '\n! = old name' \
                  '\n# = numbering based on selection, add more # for more digits' \
                  '\n\nFind and replace method:' \
                  '\n"oldName">"newName" (without quotes)' \
                  '\n\nRemove first or last character(s):' \
                  '\n-(amount of characters to remove) = removes specific amounts of characters from last character'\
                  '\n+(amount of characters to remove) = removes specific amounts of characters from first character' \
                  '\n\nAdd these symbols at the end to change the options:' \
                  '\n//(number) = define the start number of numbering from #' \
                  '\n/s = selected only (this is default, you dont have to type this)' \
                  '\n/h = add items from all hierarchy descendants of selected items' \
                  '\n/a = all objects in scene'

        column = pm.columnLayout(cal='center', adj=True)
        pm.separator(h=15, style='none')
        self.rnmInput = pm.textField(ec=self.runFunc, aie=True, w=200, ann=toolTip)
        pm.separator(h=10, style='none')
        pm.text(label='Hover mouse to text field for tool tips')
        pm.text(label='zansyabana@gmail.com')
        pm.separator(h=10, style='none')

    def runFunc(self,*args):
        self.rnmQ = pm.textField(self.rnmInput, text=True,q=True)
        oneLiner(self.rnmQ)