# This is a puzzle solver for Magic Griddlers of big fish games

import itertools,pickle,logging,os.path

#setup which symbol to use for display the lattice
OCCUPIED='■'
UNOCCUPIED='×'

################### class definition #####################
class CMagicGriddlerSolver:
    DATAFILENAME='data.pickle'
    OCCUPIED='1'
    UNOCCUPIED='0'
    UNKNOWN='?'
    
    def __init__(self,patrow,patcol):
        logging.basicConfig(level=logging.INFO, format='%(message)s')  #%(asctime)s - %(levelname)s - 
        logging.info("initializing...")
        
        rownum=len(patrow)
        colnum=len(patcol)
        self.rownum=rownum
        self.colnum=colnum
        for i in range(rownum):
            if isinstance(patrow[i],int):
                patrow[i]= list(map(int,list(str(patrow[i]))))
        for i in range(colnum):
            if isinstance(patcol[i],int):
                patcol[i]= list(map(int,list(str(patcol[i]))))
        self.lattice=[]
        for i in range(rownum):
            self.lattice.append([CMagicGriddlerSolver.UNKNOWN for j in range(colnum)])
        
        self.__patsetrels={}
        self.loaddata()
        logging.info("done.\nsize: {0} * {1}, rowtotal:{2},  coltotal:{3}\ntotal complexity:{4:.1e}\n".format
                     (rownum,colnum, 2**colnum, 2**rownum,2**(rownum*colnum)))

        self.__rowComplexity=[]
        self.__colComplexity=[]
        self.rowsets=[]
        self.colsets=[]
        
        logging.debug("Calculating row patterns...")
        for i in range(rownum):
            self.rowsets.append(self.__patsetrels[colnum][tuple(patrow[i])])
        logging.debug(ArrayStr(self.rowsets,True,',',5))
        self.__rowComplexity.append(printarrStat(self.rowsets))
        
        logging.debug("Calculating column patterns...")
        for i in range(colnum):
            self.colsets.append(self.__patsetrels[rownum][tuple(patcol[i])])
        logging.debug(ArrayStr(self.colsets,True,',',5))
        self.__colComplexity.append(printarrStat(self.colsets))


    def savedata(self):
        totalsets={}
        totalpats={}
        patsetrels={}
        for i in range(5,21,5):
            totalsets[i]=list(itertools.product([CMagicGriddlerSolver.OCCUPIED,CMagicGriddlerSolver.UNOCCUPIED],repeat=i))
            totalpats[i]=[CMagicGriddlerSolver.getLinePattern(''.join(line)) for line in totalsets[i]]
            patsetrels[i]={}
            for Apat,Aset in zip(totalpats[i],totalsets[i]):
                if Apat in patsetrels[i]:
                    patsetrels[i][Apat].append(Aset)
                else:
                    patsetrels[i][Apat]=[Aset]

        with open(CMagicGriddlerSolver.DATAFILENAME, 'wb') as f:
            pickle.dump(patsetrels, f, pickle.HIGHEST_PROTOCOL)
        self.__patsetrels=patsetrels
        
    def loaddata(self):
        if not os.path.exists(CMagicGriddlerSolver.DATAFILENAME):
            self.savedata()
        else:
            with open(CMagicGriddlerSolver.DATAFILENAME, 'rb') as f:
                self.__patsetrels = pickle.load(f)
    
    def getLinePattern(line):
        tmp=line.split(CMagicGriddlerSolver.UNOCCUPIED)
        if list(set(tmp))==['']:
            return 0
        return tuple([len(x) for x in tmp if x!=''])  #tuple
    
    def ScanPat(self):
        for i in range(self.rownum):
            for j in range(self.colnum):
                if(self.lattice[i][j]==CMagicGriddlerSolver.UNKNOWN):
                    #find whether there is a pat in position i,j
                    row=self.rowsets[i]
                    col=self.colsets[j]
                    
                    tmp=list(zip(*row))[j]
                    logging.debug("Column {0} Filtering using pattern found in Row {1}...".format(j+1,i+1))
                    if(len(set(tmp))==1): #a pattern found                
                        logging.debug("\tFound a pattern: [{0},{1}]={2}".format(i+1,j+1,tmp[0]))
                        self.lattice[i][j]=tmp[0]
                        colselect=[]
                        for ci in col:
                            if ci[i]==tmp[0]:
                                colselect.append(ci)
                        if(len(colselect)<len(col)):
                            logging.debug('\tcolumn {0} downsized from {1} to {2}'.format(j+1,len(col),len(colselect)))                        
                            logging.debug(ArrayStr(col))
                            logging.debug('\t==>')
                            logging.debug(ArrayStr(colselect))
                            logging.debug('')
                            logging.debug(ArrayStr(self.lattice))
                            self.colsets[j]=colselect
                        else:
                            logging.debug('\talready follow the pattern. no changes.\n')                        
                    else:
                        logging.debug('\tno pattern was found. Now changes into row filtering...')
                                           
                        if(self.lattice[i][j]==CMagicGriddlerSolver.UNKNOWN): 
                            row=self.rowsets[i]
                            col=self.colsets[j]                
                            tmp=list(zip(*col))[i]
                            logging.debug("Row {0} Filtering using pattern found in Column {1}...".format(i+1,j+1))
                            if(len(set(tmp))==1): #a pattern found                  
                                logging.debug("\tFound a pattern: [{0},{1}]={2}".format(i+1,j+1,tmp[0]))
                                self.lattice[i][j]=tmp[0]                    
                                rowselect=[]
                                for ri in row:
                                    if ri[j]==tmp[0]:
                                        rowselect.append(ri)
                                if(len(rowselect)<len(row)):
                                    logging.debug('\trow {0} downsized from {1} to {2}'.format(i+1,len(row),len(rowselect)))
                                    logging.debug(ArrayStr(row))
                                    logging.debug('\t==>')
                                    logging.debug(ArrayStr(rowselect))
                                    logging.debug('')
                                    logging.debug(ArrayStr(self.lattice))
                                    self.rowsets[i]=rowselect
                                else:
                                    logging.debug('\talready follow the pattern. no changes.\n')
                            else:
                                logging.debug('\tpatten not found either.')
                else:
                    logging.debug("lattice[{0},{1}] has been confirmed.".format(i+1,j+1))      
        
        self.__rowComplexity.append(printarrStat(self.rowsets))
        self.__colComplexity.append(printarrStat(self.colsets))
    def Solve(self):
        flag=True
        scanNO=0
        while (flag):
            self.ScanPat()            
            scanNO+=1
            
            flag=False
            for i in self.lattice:
                if CMagicGriddlerSolver.UNKNOWN in i:
                    flag=True
                    break;
            if flag:    
                pass
            else:
                logging.info('bingo!')
                print("After",scanNO,"ScanPat, we got:")
                logging.info(ArrayStr(self.lattice).replace(CMagicGriddlerSolver.OCCUPIED,OCCUPIED).replace(CMagicGriddlerSolver.UNOCCUPIED,UNOCCUPIED))

        logging.debug(','.join(map(str,self.__rowComplexity)))
        logging.debug(','.join(map(str,self.__colComplexity)))

################### function definition #####################
from functools import reduce
import operator
def product(factors):
    return reduce(operator.mul, factors, 1)

def CharList(s): # get a string from char list
    return ''.join(s)

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
        
def printarrStat(arr):
    s=[len(row) for row in arr]
    a=product(s)
    logging.debug("Complexity: "+"*".join([str(x) for x in s if x>1])+"={0:.3g}\n".format(a))
    return a


################### main #####################
if __name__ == '__main__': 
    #patrow=[1,131,313,474,[2,12,2],23342,14151,1781,24151,12331,262,293,343,421,66]
    #patcol=[4,33,312,3121,73,64,712,2322,13141,75,1314,2331,92,612,611,74,3121,312,33,3]
    patrow=[22,11,5,11,22]
    patcol=[111,5,1,111,5]
    
    mgs=CMagicGriddlerSolver(patrow, patcol)
    mgs.Solve()
