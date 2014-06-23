import KamiLevels
import copy, logging
import functools

################### class definition #####################
class CKami:
    def __init__(self,PuzzleLevelName):
        
        self.__zones=None
        self.__patterns=None
        self.zonecount=0
        self.patcount=0
        self.solution=[]
        
        self.__lattice=None 
        self.lattice=KamiLevels.levels[PuzzleLevelName][0]
        self.__maxdepth=KamiLevels.levels[PuzzleLevelName][1]
        
        self.TryNo=0  #for DFS, number of DFSolve funciton calls
        
        #DFSolve used variables only
        self.InLevelOneNo=0 #for DFS, number of a real or thorough try, that from the initial lattice down deep to the death or success end.
        self.InLevelOneTotal=0        
        self.CheckedLattices=[]     #Lattices checked before.
        self.CheckedLatticeSols=[]  #solution leads to CheckedLattice
        self.CheckedLatticesExp=[]  #lattices with no zonecount decease
        self.CheckedLatticeSolsExp=[]
        self.LatticeMetNo=0
        self.UsefulLatticeMetNo=0
        self.onetimestep=None
        self.chooselog=[[0,0] for i in range(self.__maxdepth)]

    @property
    def lattice(self):
        return self.__lattice
    
    @lattice.setter
    def lattice(self,value):
        #init lattice with string
        if(isinstance(value,str)): 
            value=[list(i) for i in value.split()]

        #init lattice with list
        if(isinstance(value,list)):
            self.__ValidLatticeCheck(value)
            self.__lattice=value
            self.__rowcount=len(value)     #total rows count
            self.__colcount=len(value[0])  #total columns count
            self.__recal()
        
        else:
            raise NameError('lattice assignment error')
    
    def __ValidLatticeCheck(self,inputlist):
        if(isinstance(inputlist,list)): 
            for i in range(1,len(inputlist)):
                if(len(inputlist[i])!=len(inputlist[0])):
                    raise NameError('input lattice irregular')
    
    def PaintPts(self,pts,pat):
        #paint points in 'pts' list to the color 'pat'
        for point in pts:
            self.__lattice[point[0]][point[1]]=pat
        self.__recal()
        
    def __getZonesFromLattice(self,lattice):
        #given a lattice, return its scattered zones according to color connectivity
        #zone format：[[color1, [[px1,py1],[px2,py2]...]],...]
        
        flags = [[0 for col in range(self.__colcount)] for row in range(self.__rowcount)]
        zones=[]
        
        for i in range(self.__rowcount):
            for j in range(self.__colcount):
                if(flags[i][j]==0): #a new zone found
                    stack=[[i,j]]
                    color=lattice[i][j]
                    newset=[]            
                    while(len(stack)>0):
                        curi,curj=stack.pop()                
                        if(flags[curi][curj]==0):
                            flags[curi][curj]=1
                            newset.append([curi,curj])
                            for di, dj in [[-1,0],[1,0],[0,-1],[0,1]]:  #up, down, left, right
                                if(-1<curi+di<self.__rowcount and -1<curj+dj<self.__colcount and
                                   flags[curi+di][curj+dj]==0 and lattice[curi+di][curj+dj]==color):
                                    stack.append([curi+di,curj+dj])
                    #newset.sort(key=functools.cmp_to_key(ListCompFunc))
                    zones.append([color,newset])
        #zones.sort(key=lambda x:len(x[1]),reverse=True)
        return zones
    
    def __getPatsFromZones(self,zones):
        return list(set([x[0] for x in zones]))
        
    
    def __recal(self):
        #update associated properties in a lattice status
        self.__zones = self.__getZonesFromLattice(self.__lattice)
        self.__patterns=self.__getPatsFromZones(self.__zones)        
        self.zonecount=len(self.__zones)
        self.patcount=len(self.__patterns)
    
    #Depth First Search
    def DFSolve(self,depth=0,PauseAfterEachStep=False):
        #display some basic info of current DFSolve call
        if(depth==1):  #this DFSolve call comes from depth 0, the beginning lattice
            self.InLevelOneNo+=1
            logging.info("=========#{0} {1} real tries. UsefulMet/TotalMet: {2}/{3}=========".format(
                self.TryNo, self.InLevelOneNo, self.UsefulLatticeMetNo,self.LatticeMetNo))            
            if(self.InLevelOneNo==1):
                self.onetimestep=time.process_time()
                remaintimeinfo=''
            else:
                remaintimeinfo=', estimated waiting time: {:.1f}s'.format(self.onetimestep*(self.InLevelOneTotal+1-self.InLevelOneNo))
                if(self.InLevelOneNo==2):
                    self.onetimestep=time.process_time()-self.onetimestep
                    logging.info('one real try\'s time: %.1fs', self.onetimestep)

            logging.info("in level 1: %d/%d, progress=%.1f%%%s",self.InLevelOneNo, self.InLevelOneTotal,
                         (self.InLevelOneNo-1)*100/self.InLevelOneTotal, remaintimeinfo)
        self.PrintCurrentStatus()
        
        if(self.zonecount==1):
            logging.info("***********************\npuzzle solved:")
            logging.info(ArrayStr(self.solution))
            logging.info("***********************")
            raise NameError('Done')
        
        if(PauseAfterEachStep):
            cmd=input("press any key to continue...")        

        if(depth+self.patcount>self.__maxdepth+1): 
            #one move can only decrease one pat
            logging.debug("this try has no future, %d moves available, %d colors to wipe",
                          self.__maxdepth-depth, self.patcount-1)
            return
        else:
            GoodMovesCache=[]
            logging.debug("checking good moves...")
            for cur_pat,pts in self.__zones:
                for pat in self.__patterns:
                    if(pat!=cur_pat):
                        oldzonecount=self.zonecount
                        self.PaintPts(pts, pat)
                        
                        #whether this move should be added to the GoodMovesCache for consideration
                        bAddtoGoodMovesCache=False
                        if self.zonecount>=oldzonecount:
                            #an bad move: no zonecount decrease
                            self.CheckedLatticesExp.append(copy.deepcopy(self.__lattice))
                            #newsol=copy.deepcopy(self.solution)
                            #newsol.append("Point{0}: {1} -> {2}".format(pts[0],cur_pat,pat))
                            #self.CheckedLatticeSolsExp.append(newsol)
                        elif self.__lattice in self.CheckedLattices:
                            self.LatticeMetNo+=1                            
                            alreadyLatticeIndex=self.CheckedLattices.index(self.__lattice)
                            oldsol=self.CheckedLatticeSols[alreadyLatticeIndex]
                            logging.debug("an bad move: #%d has met before at %d/%d...",
                                self.LatticeMetNo,alreadyLatticeIndex,len(self.CheckedLattices))
                            if(depth+1<len(oldsol)):  #len(newsol)=depth+1
                                logging.debug(oldsol)
                                logging.debug('now as:')
                                newsol=copy.deepcopy(self.solution)
                                newsol.append("Point{0}: {1} -> {2}".format(pts[0],cur_pat,pat))
                                logging.debug(newsol)
                                self.UsefulLatticeMetNo+=1
                                logging.debug('but it has less moves(%d->%d), so it should be reconsidered. and solution log is updated to the lesser move',len(oldsol),depth+1)
                                self.CheckedLatticeSols[alreadyLatticeIndex]=newsol
                                bAddtoGoodMovesCache=True
                            else:
                                logging.debug('and it has no less moves, so just dumpt it.')
                        elif self.__lattice in self.CheckedLatticesExp:
                            #if the lattice has been checked as on zonecount decrease, then it has no need to reconsider.
                            #i guess it's true. so this section can be commented out for performance improvement
                            #if(depth+1<len(self.CheckedLatticeSolsExp[self.CheckedLatticesExp.index(self.__lattice)])):
                                #logging.warn(self.CheckedLatticeSolsExp[self.CheckedLatticesExp.index(self.__lattice)])
                                #logging.warn(self.solution,"Point{0}: {1} -> {2}".format(pts[0],cur_pat,pat))
                            pass
                        else:
                            bAddtoGoodMovesCache=True
                        
                        if(bAddtoGoodMovesCache):
                            for tmpcol,tmppats in self.__zones:
                                if(pts[0] in tmppats):
                                    patlist=[z[0] for z in self.__zones]
                                    #NofSingleZonePattern=[patlist.count(tmppat) for tmppat in self.__patterns].count(1)  
                                    #patern of single zone, its increase means a pattern with scaterred zones has joined
                                    #GoodMovesCache.append([self.zonecount,len(pts)-len(tmppats),pts,cur_pat,pat])
                                    GoodMovesCache.append([self.zonecount,-len(tmppats),pts,cur_pat,pat])
                                    break
                        self.PaintPts(pts, cur_pat)
            GoodMovesCount=len(GoodMovesCache)            
            logging.debug('%d good moves added at level %d.', GoodMovesCount, depth+1)            
            GoodMovesCache.sort(key=functools.cmp_to_key(ListCompFunc)) #start with best move that downsize the zonecount most
            
            
            chooseid=0
            if(bPrefTestMode):self.chooselog[depth][1]=[[x[0],x[1],x[2][0],x[3],x[4]] for x in GoodMovesCache]
            
            if(depth==0):
                self.InLevelOneTotal=GoodMovesCount
            for dump1,dump2,pts,cur_pat,pat in GoodMovesCache:
                if(bPrefTestMode):self.chooselog[depth][0]=chooseid
                self.TryNo+=1
                step="Point{0}: {1} -> {2}".format(pts[0],cur_pat,pat)
                logging.debug("trying %d/%d at level %d: %s",chooseid+1, GoodMovesCount, depth+1, step)
                self.PaintPts(pts, pat)                    
                self.solution.append(step)
                self.CheckedLattices.append(copy.deepcopy(self.__lattice))
                self.CheckedLatticeSols.append(copy.deepcopy(self.solution))
                self.DFSolve(depth+1,PauseAfterEachStep)
                logging.debug("backforce popping..")
                chooseid+=1
                self.solution.pop()
                self.PaintPts(pts, cur_pat)
            
            if(depth==0):
                logging.info('no solution was found. There must be sth wrong.')
                
    def DFSolveTypical(self, PauseAfterEachStep=False):
        #Typical Depth First Search
        logging.debug("=========#{0}=========".format(self.TryNo))
        self.PrintCurrentStatus()
        
        if(self.zonecount==1):
            logging.info("***********************\npuzzle solved:")
            logging.info(ArrayStr(self.solution))
            logging.info("***********************")
            raise NameError('Done')
        
        if(len(self.solution)+self.patcount>self.__maxdepth+1):
            return
        else:
            for cur_pat,pts in self.__zones:
                for pat in self.__patterns:
                    if(pat!=cur_pat):
                        step="Point{0}: {1} -> {2}".format(pts[0],cur_pat,pat)
                        logging.debug("trying %s...",step)
                        
                        oldzonecount=self.zonecount
                        self.PaintPts(pts, pat)

                        self.TryNo+=1
                        if self.zonecount>=oldzonecount:
                            logging.debug("an bad move: no zonecount decrease...")
                        else:
                            self.solution.append(step)
                            self.DFSolveTypical(PauseAfterEachStep)
                            self.solution.pop()
                        
                        logging.debug("backforce popping..")
                        self.PaintPts(pts, cur_pat)
         
    def __win(self,la):
        # win status quick checker
        for row in la:
            for item in row:
                if(item!=la[0][0]):
                    return False
        return True
    
    def BFSolve(self,PauseAfterEachStep=False):
        #Breadth First Search
        QueueStatus=[self.__lattice]
        QueueSolution=[[]]
        CheckedStatus=[]
        Skelten=[[len(x[1]) for x in self.__zones]]
        oldsollen=0
        while(len(QueueStatus)>0):
            #number of checked case: len(CheckedStatus) == self.TryNo
            logging.info("=========#{0}=========".format(self.TryNo))
            logging.info("{0} checked, {1} to be checked".format(len(CheckedStatus), len(QueueStatus))) 
            CheckedStatus.append(QueueStatus.pop(0))
            self.lattice=CheckedStatus[-1]
            sol=QueueSolution.pop(0)
            logging.info('zones: %d',self.zonecount)
            
            if(PauseAfterEachStep):
                cmd=input("press any key to continue...")
            if(len(sol)>oldsollen):
                oldsollen=len(sol)
                logging.info("now comes to cases of %d steps solution",oldsollen)

            self.PrintCurrentStatus()

            self.TryNo=self.TryNo+1
            cache=[] #tune tech
            for cur_pat,pts in self.__zones:
                for pat in self.__patterns:
                    if(pat!=cur_pat):
                        newstatus=copy.deepcopy(self.__lattice)
                        for point in pts:
                            newstatus[point[0]][point[1]]=pat
                        if(self.__win(newstatus)):
                            sol.append("Point{0}: {1} -> {2}".format(pts[0],cur_pat,pat))
                            logging.info("**********************************\npuzzle solved in %d steps:",len(sol))
                            logging.info(ArrayStr(sol))
                            logging.info("**********************************")
                            raise NameError('Done')
                        if( newstatus not in QueueStatus and newstatus not in CheckedStatus):
                            newzonelen=len(self.__getZonesFromLattice(newstatus));
                            if newzonelen>=self.zonecount:
                                CheckedStatus.append(newstatus)
                            else:
                                newsol=copy.deepcopy(sol)
                                newsol.append("Point{0}: {1} -> {2}".format(pts[0],cur_pat,pat))
                                cache.append([newzonelen,newstatus,newsol])
                                QueueStatus.append(newstatus)
                                QueueSolution.append(newsol)
            cache.sort(key=lambda x:x[0]) #move with less zones is considered first
            for ns in cache:
                QueueStatus.append(ns[1])
                QueueSolution.append(ns[2])

    
    def PrintCurrentStatus(self):
        if(len(self.solution)==0):
            logging.debug("=========initial status=========")
        else:
            logging.debug("solution: After %d steps:",len(self.solution))
            logging.debug(ArrayStr(self.solution))
            logging.debug('')
            
        logging.debug("lattice:")
        logging.debug(ArrayStr(self.__lattice))
        
        MaxItemOnEachRow=5
        zoneid=0
        logging.debug("\nConnectivity: %d zones \n#zoneid(zone pattern * zone cells count): points list",self.zonecount)
        for pat, row in self.__zones:
            logging.debug("#{0}({1}*{2}): ".format(zoneid,pat,len(row))+RowStr(row,',',MaxItemOnEachRow))
            zoneid+=1
        
        logging.debug("\n%d patterns: %s",self.patcount,self.__patterns)


################### function definition #####################
def ListCompFunc(item1,item2):
    #compare list according list item[0], item[1]...
    
    #whether ascending(False,defaut value) or descending(True)
    CompReverse=[False,False]
    
    ret=0
    for i in range(len(CompReverse)):
        if(item1[i]<item2[i]):
            ret=-1
            break
        elif(item1[i]==item2[i]):
            pass
        else:
            ret=1
            break
    if ret==0:
        return 0
    else:
        if CompReverse[i]:
            return -1*ret
        else:
            return ret

def CharList(s): # get a string from char list
    if(isinstance(s,str)):
        return ''.join(s)
    else:
        return str(s)

def RowStr(row,delimeter,MaxItemOnEachRow):
    if(MaxItemOnEachRow=="all"):
        MaxItemOnEachRow=len(row)
    s=delimeter.join(map(CharList,row[:MaxItemOnEachRow]))
    
    if(len(row)>MaxItemOnEachRow):
        s+='...'
    return s

def ArrayStr(arr,ShowLineNumber=False, delimeter='',MaxItemOnEachRow="all"):
    count=0
    infos=[]
    for row in arr:
        s=''
        count=count+1
        if(ShowLineNumber):
            s+="#{0}({1}): ".format(count,len(row))
        s+=RowStr(row,delimeter,MaxItemOnEachRow)
        infos.append(s)
    return '\n'.join(infos)


################### main #####################
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO,format='%(message)s')
    bPrefTestMode = False  #test preferences strategy of candidate moves or not. chooselog is involved.
    
    levelname='A1'
    il=CKami(levelname)
    
    import time
    StartingTime=time.process_time()
    try:
        il.DFSolve()
        #il.BFSolve()
    except NameError:
        if(bPrefTestMode):
            logging.debug(il.chooselog)
            logging.info([x[0] for x in il.chooselog])
        EndingTime=time.process_time()
        logging.info("total time: {:.2f}s, {:d} tries, {:d} real tries".format(
            EndingTime-StartingTime,il.TryNo, il.InLevelOneNo))