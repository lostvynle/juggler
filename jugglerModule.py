import sys,re
""" Sorts jugglers into circuit teams based on compatibility score and set of juggler preferences.

    See problems statement for full description of problem.
    Since there are only 10 prefs per juggler it is likely that not all jugglers will get to have 
    one of their top ten choices (ie if all chose the same ten then clearly only 60 jugglers 
    would get any of their choices).
    The only requirement is that they cannot be moved to a higher choice (of those given) and 
    be better than anyone on that team.
    To make the sorting easier I fill in the choice list with all the unused choices as lower 
    preferences.  
    I then take jugglers one at a time and try to place them in their first available choice.
    If this displaces a previous team member with a lower score, I then move that one to his next 
    available choice and so on.  When there are finally no displaced jugglers, I move to the next
    unplaced juggler in the original list.

    Finally I get the sum of the six team members from C1970
    and check that in fact no jugglers can be moved up to a better location.

    This can be run as a python script.
"""

class Circuit(object):
    """ Container for methods and parameters for each trick circuit.
    
        The team property is a list of jugglers(by object) assigned to this circuits team.
        Circuits initialized with skill emphasis given by paramsCHEP for circuit number (C), 
        hand-eye coordination (H), endurance (E) and pizzazz (P).
    """
    def __init__(self,paramsCHEP):
        self.index = paramsCHEP[0]
        self.skills = [int(skill) for skill in paramsCHEP[1:]]
        self.team = []
        self.maxTeamSize = 0
        self.teamsize = 0
    
    def getMatchValue(self,juggler):
        """
        returns match value for this juggler-circuit pairing
        """
        return sum([ skill[0]*skill[1] for skill in zip(self.skills,juggler.skills)])
        
    def addJuggler(self,juggler):
        juggler.matchValue = self.getMatchValue(juggler)
        self.team.append(juggler)
        self.teamsize+=1
        
    def removeJuggler(self,juggler):
        self.team.remove(juggler)
        self.teamsize+=-1
        
    @property
    def showTeam(self):
        a=[(repr(J),J.matchValue,J.prefIndex) for J in self.team]
        return a
        
    @property
    def overFull(self):
        return max(0,self.teamsize-self.maxTeamSize)
         
    @property
    def currentMinMatch(self):
        return min([x.matchValue for x in self.team])
        
    def insertJuggler(self,juggler):
        """ We check if juggler makes this team, changing its match value and prefIndex.
        
            If team is not full we add juggler there but if team is full we must 
            remove the worst juggler to be relocated.
        """
        self.addJuggler(juggler)
        if self.overFull:  # team full : find worst juggler to remove
            sortedJugglers = sorted(self.team, key=lambda x:x.matchValue)
            worstMatch = sortedJugglers[0]
            if worstMatch.matchValue == juggler.matchValue:
                worstMatch = juggler # don't kick out placed juggler if equal
            self.removeJuggler(worstMatch)
        else:  # juggler successfully added
            worstMatch = 0
        return worstMatch
        
    @property        
    def code(self):
        """ returns email code for this circuit/team"""
        
        return sum([int(j.index) for j in self.team])
        
class Juggler(object):
    """ Container for methods and parameters for each juggler.
    
        Jugglers initialized skills given by paramsJHEPC for juggler number (J), 
        hand-eye coordination (H), endurance (E) and pizzazz (P); as well as 
        circuit preferences in order (Cs).
        matchValue tracks the Match value for the current circuit pairing given by the 'prefIndex'
        position in the circuitPrefs list.
    """
    
    def __init__(self,paramsJHEPCs):
        self.index = paramsJHEPCs[0]
        self.skills = [int(skill) for skill in paramsJHEPCs[1:4]]
        self.inputPrefs=paramsJHEPCs[4:]
        self.circuitPrefs=[]
        self.prefIndex=-1
        self.matchValue = -1
        self.places = []
        #self.orphan = False
        #self.circuitIndex=-1
    
    def fillPrefs(self,Ncircuits):
        """ Fill preference list for each juggler.
        
            Creates a complete pref list by filling in with remainder of the
            circuit numbers after the given pref list.
            All added preferences will have equally low value.
        """
        
        cIndices=range(Ncircuits)
        for i in self.inputPrefs:
            cIndices.remove(i)
        self.circuitPrefs = self.inputPrefs + cIndices
    
    @property
    def circuitIndex(self):
        return self.circuitPrefs[self.prefIndex]
    
    @property
    def numberOfPrefs(self):
        return len(self.circuitPrefs)
    
    def __repr__(self):
        """ repr is just fluff or verbose output if desired. """
        
        return 'juggler%s'%self.index

def failureTest(juggler,jugglerList,circuitDict):
    """ Check that the solution verification method works.
    
        Place each juggler in first available circuit
        Run instead of shuffleJuggler to test the check function.
    """
    
    for c in circuitDict.values():
        if (c.teamsize-c.maxTeamSize)<0:
            c.addJuggler(juggler)
            juggler.prefIndex=9
            juggler.circuitPrefs = juggler.inputPrefs
            break
        
def shuffleJuggler(juggler,jugglerList,circuitDict):
    """ Places current juggler in first valid choice and recursively shuffles 
        all the other jugglers down the list as necessary.
    """    
    
    NumberOfCircuits=len(circuitDict)
    juggler.fillPrefs(NumberOfCircuits)
    worstMatch = juggler
    while worstMatch:
        worstMatch.prefIndex+=1  
        newCircuit = circuitDict[worstMatch.circuitIndex]
        worstMatch = newCircuit.insertJuggler(worstMatch)  # return 0 = false if successfully added

        #juggler.prefIndex+=1  
        #newCircuit = circuitDict[juggler.circuitIndex]
        #worstMatch = newCircuit.insertJuggler(juggler)  # return 0 = false if successfully added

def readFile(inputFile):
    """ Read data file assuming prescribed format. 
     
        Reads circuit definition lines and juggler definition lines, make circuit and juggler
        objects respectively for each line which are put in circuitDict and jugglerList respectively.
        Also calculates and stores maxTeamSize and numTeams in all circuit classes for their use.
    """
    REGEX=r'\d+'
    p=re.compile(REGEX)
    circuitDict={}
    jugglerList=[]
    datafile=open(inputFile,'r')
    for line in datafile:
        if line.startswith('C'):
            CHEP = [int(s) for s in p.findall(line)]
            try:
                newCircuit = Circuit(CHEP)
                circuitDict[newCircuit.index] = newCircuit
            except:
                print 'Error in input format'
                datafile.close()
                return 0
                
        if line.startswith('J'):
            JHEPCs = [int(s) for s in p.findall(line)] 
            try:
                jugglerList.append(Juggler(JHEPCs))
            except:
                print 'Error in input format'
                datafile.close()
                return 0
                
    maxTeamSize=len(jugglerList)/len(circuitDict)
    for c in circuitDict.values():
        c.maxTeamSize = maxTeamSize
    datafile.close()
    print 'Read %d circuits and %d jugglers'%(len(circuitDict),len(jugglerList))
    return circuitDict,jugglerList,maxTeamSize
    
def writeFile(filename,circuitDict,verbose=False):
    """ Writes output file in prescribed format:
        - one line per circuit.
        - list of full circuit team with preferences and match scores for each juggler on team
    """
    outFile = open(filename,'w')
    outputByJuggler=[]
    for circuit in sorted(circuitDict.values(),key=lambda x:x.index, reverse=True):
        newline = 'C%s '%circuit.index
        jugglersStatList = []
        for juggler in circuit.team:
            jugglerMatchList=[' C%s:%d'%(c.index,c.getMatchValue(juggler)) for c in [circuitDict[i] for i in juggler.circuitPrefs[:10]]]
            s=''.join(['J%s'%juggler.index]+jugglerMatchList)
            jugglersStatList.append(s)
            outputByJuggler.append(' '.join(['Circuit %s: '%circuit.index,s]))
        jugglerInfo = ','.join(jugglersStatList)
        newline = ''.join([newline, jugglerInfo, '\n'])
        outFile.write(newline)
    outFile.close()
    print '\nWrote results to "%s"'%filename
    return '\n'.join(outputByJuggler)
    
def checkResults(jugglerList,circuitDict):
    """ Check that result meets solution criteria.
    
        The only requirement is that 
        'NO JUGGLER CAN SWITCH TO A HIGHER PREFERENCE AND BE BETTER MATCHED'
        So this checks each juggler against his initial preference list and makes sure
        that for all higher circuit preferences than where he is assigned that he is not
        better than any of the jugglers there.
    """
    preferenc_check_failures = []
    
    for juggler in jugglerList[:]:
        ### first get all prefs higher than current
        ### by selecting the slice from the jugglers preference list
        ### from the highest(index=0) to the current pref (index=prefIndex)
        higherPrefs = juggler.circuitPrefs[:juggler.prefIndex]
        match=juggler.matchValue  # save original match value so we can change back each time
        juggler.places=[]
        for choice in higherPrefs: # check higher prefs, highest to lowest 
            # Temporarily add juggler to this choice and check that j cannot be better fit 
            # at this circuit than other team members.
            # Then return circuit as it was.
            circuit=circuitDict[choice] 
            juggler.matchValue = circuit.getMatchValue(juggler)
            team = circuit.team
            team.append(juggler)
            sortedJugglers = sorted(team, key=lambda x:x.matchValue)
            place = sortedJugglers.index(juggler)
            if juggler.matchValue > sortedJugglers[0].matchValue : #juggler not lowest : means failure.
                juggler.places.append(circuit.index)
                
            team.remove(juggler)  # put circuit back the way it was.
        juggler.matchValue=match # put juggler back the way it was
        
        score = len(juggler.places)
        if score > 0:
            preferenc_check_failures.append((juggler.index,score))
    return preferenc_check_failures
    
    
if __name__ == "__main__":
    
    ######### Required Calls #####################
    inputFile = 'jugglefest.txt';Nprefs=10
    outputFile = 'outputFile.txt'
    
    circuitDict,jugglerList,maxTeamSize = readFile(inputFile)
    for juggler in jugglerList:
        print '#############   placing %s   ############'%repr(juggler)
        shuffleJuggler(juggler,jugglerList,circuitDict)
        #failureTest(juggler,jugglerList,circuitDict)
    outputByJuggler = writeFile(outputFile,circuitDict)
    
    ######### Check assignments #####################
    preferenc_check_failures=checkResults(jugglerList,circuitDict)
    print 'number of failures = ', len(preferenc_check_failures)
    
    ######### Output email code #####################
    
    codeCircuit = 1970 #circuit to check for email address
    
    if int(codeCircuit)+1:
        circuit = circuitDict[codeCircuit]
        print 'secret code for %d is %d'%(codeCircuit,circuit.code)
        print 'code circuit %d team is\n'%circuit.index,circuit.showTeam
    
