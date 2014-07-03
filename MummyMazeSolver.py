import copy, logging, math,time
#all x-y cordinates use the row-column numbers, starting from 1

#DIRECTIONS
RIGHT,DOWN,LEFT,UP,STAY=1,2,3,4,5

ExplorerMoves=[RIGHT,DOWN,LEFT,UP,STAY]
MoveStrs=['RIGHT','DOWN','LEFT','UP','STAY']

def Move2Str(m):
    return MoveStrs[ExplorerMoves.index(m)]

class CMummyMaze(object):
    def __init__(self,row,col):
        self.mazesize=[row,col]
        self.MovableItems={
            'explorer':None,
            'mummies':[],
            'redmummies':[],
            'scorpions':[],
            'redscorpions':[],
            'XDirections':[] #Forbidden Directions
        }
        
        self.traps=[]
        self.gate=None
        self.key=None
        self.exit=None
        
        self.Checked=[]
        self.CheckedSol=[]
        self.solution=[]
        self.SingleSolMode=False
        self.TryNo=0
        self.TotalSolutions=[]
        
    def CanMoveInDirection(self,x,y,d,CheckWalls=True):
    #whether move in direction d at (x,y) is blocked by boundries, or walls(when CheckWalls is True).
        newx,newy=x,y
        if((not CheckWalls) or ([x,y,d] not in self.MovableItems['XDirections'])):
            if(d==RIGHT):   newy+=1
            elif(d==DOWN):  newx+=1
            elif(d==LEFT):  newy-=1
            elif(d==UP):    newx-=1
            elif(d==STAY):  pass
            if(1<=newx<=self.mazesize[0] and 1<=newy<=self.mazesize[1]):
                return [True,[newx,newy]]
            else:
                return [False,[newx,newy]]
        else:
            return [False,[newx,newy]]
        
    #find the reverse direction of d
    def ReverseDir(self,d):
        a=[RIGHT,DOWN,LEFT,UP]
        r=[LEFT,UP,RIGHT,DOWN]
        return r[a.index(d)]
    

    def DelDumplicates(self,lofl):
        ret=[]
        for l in lofl:
            if l not in ret:
                ret.append(l)
        return [ret,len(ret)<len(lofl)]
    #[list(b) for b in set([tuple(a) for a in lofl])]   using set for this purpose will change the list item order
    
    def Setup(self,barlist,itemstr):
        self.__SetXDFromWalls(barlist)
        self.__SetMovableItems(itemstr)
                
    def __SetXDFromWalls(self,barlist):
        for bar in barlist:
            x,y=bar[:2]
            for d in bar[2:]:
                self.MovableItems['XDirections'].append([x,y,d])
                ret,pos=self.CanMoveInDirection(x, y, d,False)
                if(ret):
                    self.MovableItems['XDirections'].append([pos[0],pos[1],self.ReverseDir(d)])
        self.MovableItems['XDirections'],dump=self.DelDumplicates(self.MovableItems['XDirections'])
        
    def __SetMovableItems(self,itemstr):
        abbrs=['x','g','k','t','e','rm','m','rs','s']
        fullnames=['exit','gate','key','traps','explorer','redmummies','mummies','redscorpions','scorpions']
        items=itemstr.split('/')
        for item in items:
            if(len(item)>=4):
                item=item.replace(' ','').lower()
                mark=[]
                for c in item:
                    if(c.isalpha()):
                        mark.append(c)
                    else:
                        break
                mark=''.join(mark)
                if(mark in abbrs):
                    spos=len(mark)
                    fn=fullnames[abbrs.index(mark)]
                    one=[int(i) for i in item[spos:].split(',')]
                    multis=[[int(i) for i in x.split(',')] for x in item[spos:].split(';')]
                    if(mark=='e'):
                        self.MovableItems['explorer']=one
                    elif(mark=='x'):
                        self.exit=one
                    elif(mark=='t'):
                        self.traps=multis
                    elif(mark=='g'):
                        self.gate=one
                        self.gate.append(DOWN)
                    elif(mark=='k'):
                        self.key=one
                    elif(fn in self.MovableItems):
                        self.MovableItems[fullnames[abbrs.index(mark)]]=multis
                    #else:(eval('self.'+fn))=one
                else:
                    raise Exception('there\'s sth wrong in the item str')
                
    def NewPosAfterOneStep(self,t,curpos):
        #a animal of type t at current position(curpos) tries to move towards the explorer
        #the newpos returned
        epos=self.MovableItems['explorer']
        newpos=curpos
        H=[1,LEFT,RIGHT]
        V=[0,UP,DOWN]
        
        if(t=='mummies' or t=='scorpions'):
            decisions=[H,V]
        elif(t=='redmummies' or t=='redscorpions'):
            decisions=[V,H]
        
        bCanMov=False
        for i,d1,d2 in decisions:
            if(curpos[i]!=epos[i]):
                if(curpos[i]>epos[i]): mdir=d1
                else: mdir=d2
                bCanMov,newpos=self.CanMoveInDirection(curpos[0],curpos[1],mdir)
                if(bCanMov):
                    break

        if(bCanMov): #the animal can move to a new position
            self.LoseCheck(newpos)
            if(newpos==self.key): #it steps on the key 
                self.ToggleGate()
        return newpos
    
    def LoseCheck(self,pos):
        if(self.MovableItems['explorer']==pos):
            raise Exception('lose')
        
    def EatCheck(self):
        foodchains=['redmummies','mummies','redscorpions','scorpions']
        for t in foodchains:
            self.MovableItems[t],dump=self.DelDumplicates(self.MovableItems[t])
            if(dump):
                logging.debug("%s eat %s", t,t)
        
        for i in range(len(foodchains)-1):
            hunter=foodchains[i]
            preys=foodchains[i+1:]
            for pos in self.MovableItems[hunter]:
                for prey in preys:
                    if(pos in self.MovableItems[prey]):
                        logging.debug("%s eat %s", hunter ,prey)
                        self.MovableItems[prey].remove(pos)
        
    def ToggleGate(self):
        if(self.gate in self.MovableItems['XDirections']):
            logging.debug('now gate opens')
            self.MovableItems['XDirections'].remove(self.gate)
            x,y,d=self.gate
            ret,pos=self.CanMoveInDirection(x, y, d,False)
            if(ret):
                self.MovableItems['XDirections'].remove([pos[0],pos[1],self.ReverseDir(d)])            
        else:
            logging.debug('now gate closes')
            self.MovableItems['XDirections'].append(self.gate)
            x,y,d=self.gate
            ret,pos=self.CanMoveInDirection(x, y, d,False)
            if(ret):
                self.MovableItems['XDirections'].append([pos[0],pos[1],self.ReverseDir(d)])

    def UpdateLattice(self,d,epos): 
        #explorer move in direction d, and the new postition is epos
        
        #explorer move
        self.MovableItems['explorer']=epos
        if(d!=STAY and epos==self.key):
            self.ToggleGate()
        
        #scorpions and redscorpions move first
        #or todo: nearest to the explorer move first. i'm not sure
        foodchains=['redmummies','mummies','redscorpions','scorpions']
        foodchains.reverse()
        
        for t in foodchains[:2]:
            if(len(self.MovableItems[t])>0):
                self.MovableItems[t]=[self.NewPosAfterOneStep(t,s) for s in self.MovableItems[t]]
        self.EatCheck()


        #mummies's 1st move
        for t in foodchains[2:]:
            if(len(self.MovableItems[t])>0):
                self.MovableItems[t]=[self.NewPosAfterOneStep(t,s) for s in self.MovableItems[t]]
        self.EatCheck()
        

        #mummies's 2nd move
        for t in foodchains[2:]:
            if(len(self.MovableItems[t])>0):
                self.MovableItems[t]=[self.NewPosAfterOneStep(t,s) for s in self.MovableItems[t]]
        self.EatCheck()
        
    def PrintCurrentStatus(self):
        if(len(self.solution)==0):
            logging.debug("=========initial status=========")
            logging.debug('%d Forbidden Moves:', len(self.MovableItems['XDirections']))
            for x,y,d in self.MovableItems['XDirections']:
                logging.debug('%d, %d, %s', x, y, Move2Str(d))
        else:
            logging.debug("=========#{0}=========".format(self.TryNo))
            logging.debug(SolStr(self.solution))
            logging.debug('')
        
        #always print explorer info first. dict can not assure that.
        logging.debug('explorer: %s',self.MovableItems['explorer'])
        for k,v in self.MovableItems.items():
            if(k!='explorer' and k!='XDirections' and len(v)):
                if(isinstance(v[0],list)):
                    logging.debug('%s: %s',k,','.join([str(i) for i in v]))
                else:
                    logging.debug('%s: %s',k,v)
        logging.debug('')
        
    def DFSolve(self,depth=0):
        self.TryNo+=1
        self.PrintCurrentStatus()
        
        if(self.MovableItems in self.Checked):
            alreadyindex=self.Checked.index(self.MovableItems)
            if(len(self.solution)>=self.CheckedSol[alreadyindex]):
                logging.debug('u have been here before')
                return
            else:
                self.CheckedSol[alreadyindex]=len(self.solution) #UPDATE info
        else:
            self.Checked.append(copy.deepcopy(self.MovableItems))
            self.CheckedSol.append(len(self.solution))
        
        saved=copy.deepcopy(self.MovableItems)
        curpos=self.MovableItems['explorer']
        PrefMoves=[]
        for d in ExplorerMoves:
            ret,epos=self.CanMoveInDirection(curpos[0],curpos[1],d)
            if(ret and epos not in self.traps):
                PrefMoves.append([math.fabs(epos[0]-self.exit[0])+math.fabs(epos[1]-self.exit[1]),d,epos])
        PrefMoves.sort(key=lambda x: x[0])
        
        for dump,d,epos in PrefMoves:
            try:
                self.UpdateLattice(d,epos)
                if([epos[0],epos[1]] == self.exit):
                    l=self.solution[:]
                    l.append(d)
                    self.TotalSolutions.append(l)
                    if(self.SingleSolMode):
                        raise Exception('Done')
                    else:                        
                        self.MovableItems=copy.deepcopy(saved)
                        continue
            except Exception as e:
                if(e.args[0]=='lose'):
                    self.MovableItems=copy.deepcopy(saved)  #very trival mistake: deepcopy needed
                    continue
                else:
                    raise
            
            self.solution.append(d)
            logging.debug('trying %s at level %d...', Move2Str(d),depth)
            self.DFSolve(depth+1)
            logging.debug('backforce popping...')
            self.solution.pop()
            self.MovableItems=copy.deepcopy(saved)  #very trival mistake: deepcopy needed
        
        if(depth==0 and self.SingleSolMode):
            logging.info("hmm..., no solution found.")

def SolStr(sol):
    s=[]
    for i in sol:
        s.append(Move2Str(i))
    return "Solution: After {:d} steps:\n".format(len(sol))+(', '.join(s))

def InitFromTaM(TaMStr):  #Theseus and the Minotaur
    TaMlist=[i.strip() for i in TaMStr.split('\n') if i!='']
    lattice=TaMlist[1:10]
    walls=[]
    for i in range(9):
        if(lattice[i][0]=='6'):
            break
        for j in range(14):
            cell=lattice[i][j]
            if(cell=='6'):
                break
            elif(cell!='0'):
                if(cell=='1'):
                    walls.append([i+1,j+1,LEFT])
                elif(cell=='2'):
                    walls.append([i+1,j+1,UP])
                elif(cell=='3'):
                    walls.append([i+1,j+1,UP,LEFT])
    if(i==8):i=9
    if(j==13):j=14
    mm.mazesize=[i,j]
    items='m{0},{1}/e{2},{3}/x{4},{5}'.format(int(TaMlist[15])+1,int(TaMlist[14])+1,int(TaMlist[12])+1,int(TaMlist[11])+1,
                                              int(TaMlist[18])+1,int(TaMlist[17])+1)
    mm.Setup(walls,items)
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO,format='%(message)s')
    
    #init
    #the 14th puzzle in Pharaoh's Tomb, has the solution with most moves
    mm=CMummyMaze(10,10)
    #walls=[[1,5,DOWN],[1,6,DOWN],[1,7,DOWN],[1,8,DOWN],[1,9,LEFT],[1,10,LEFT],[\
2,2,DOWN],[2,7,DOWN],[3,1,DOWN],[3,2,DOWN],[3,6,LEFT],[3,10,LEFT],[4,\
2,DOWN],[4,4,DOWN,LEFT],[4,5,DOWN],[4,8,DOWN],[4,9,DOWN,LEFT],[4,10,\
DOWN,LEFT],[5,1,DOWN],[5,4,DOWN],[5,5,DOWN],[5,8,DOWN],[5,9,DOWN],[6,\
2,DOWN],[6,4,DOWN],[6,8,LEFT],[6,9,LEFT],[7,1,DOWN],[7,3,DOWN,LEFT],[\
7,8,DOWN,LEFT],[7,10,LEFT],[8,2,LEFT],[8,5,DOWN,LEFT],[8,7,LEFT],[8,\
10,LEFT],[9,5,LEFT],[9,6,DOWN],[9,8,DOWN],[9,9,DOWN,LEFT],[10,6,LEFT],\
[10,9,LEFT]]
    #items='x4,10/e7,1/t2,1/rs5,4/rm8,6'   #gate always faces down, see also class's __SetMovableItems func
    #mm.Setup(walls,items)
    
    #level 87 of game: Theseus and the Minotaur
    #0-empty 1-wall at left, 2-wall at top, 3-wall at both left and top
    #6-border
    #Theseus/Minotaur/Goal coordinates orignating from the upper-left corner (0,0)
    TaMStr='''
Theseus and the Minotaur Level
00100000001000
01021320121331
02300020021100
01022130210111
01111121111100
00000110111133
02221001001001
23113201202021
00002200122200
Theseus
12
5
Minotaur
6
3
Goal
13
5
End
85
'''
    InitFromTaM(TaMStr)
    
    #True: find a solution 
    #False: find the best solution with least moves
    mm.SingleSolMode=False
    
    StartingTime=time.process_time()

    try:
        mm.DFSolve()
    except:
        pass

    EndingTime=time.process_time()
    logging.info("total time: {:.2f}s, {:d} tries".format(EndingTime-StartingTime,mm.TryNo))
    l=[len(sol) for sol in mm.TotalSolutions]
    l.sort()
    logging.info("total %d solutions found:%s",len(mm.TotalSolutions),l)
    minv=float('Infinity')
    mins=[]
    for sol in mm.TotalSolutions:
        logging.debug(SolStr(sol))
        if(len(sol)<minv):
            minv=len(sol)
            mins=sol
    logging.info("Best solution is:")
    logging.info(SolStr(mins))