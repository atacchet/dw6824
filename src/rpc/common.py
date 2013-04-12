from ui.stroke import Stroke
from rpc.priority import Priority
from rpc.vt import VT
from threading import Lock
import copy

class PeerState:
    """Stores all data concerning a peer's state

    Contains:
        - list of other peers
        - dOPT structures
        - drawn objects (strokes)

    Is shared between UI and Network threads
    
    """
    # NOTE: lock around access to the structure?
    def __init__(self, peer_id):
        self.id      = peer_id
        self.peers   = []
        self.queue   = []
        self.log     = []
        self.vt      = [0 for x in range(3)]
        self.strokes = []

        self.window = None

        self.lock = Lock()

    def executeOperations(self):
        #NOTE: should be locking

        print '\033[32m--execute\033[0m'

        print '\tcurrent vt:',self.vt

        to_del = []
        lq = copy.deepcopy(self.queue)
        for i, rq in lq:
            print '\tunqueue vt:', rq.vt
            cmp = VT.cmp(rq.vt,self.vt)
            print '\tcmp is:', cmp
            if  cmp ==0 or cmp == -1:
                #print rq.vt,'<=',self.vt
                to_del.append(i)
                if cmp==-1:
                    #print rq.vt,'<',self.vt
                    mr = self.mostRecent(rq.vt)
                    print '\tmr', mr
                    print 'rq-op', rq.op
                    while mr and rq.op.type != OpType.NoOp:
                        if rq.vt[mr.sender] <= mr.vt[mr.sender]:
                            rq.op = self.transform(rq,mr)
                        mr = self.mostRecent(rq.vt)

                self.performOperation(rq.op)
                self.log.append(rq)
                self.vt[rq.sender] += 1
                print '\tupdated vt', self.vt

        to_del.sort()
        to_del.reverse()

        print '\tdel', to_del

        for i in to_del:
           del self.queue[i] 
           
        print '\033[31m--done\033[0m\n'


    def mostRecent(self,vt):
        for i in range(len(self.log)-1,-1,-1):
            if VT.cmp(self.log[i].vt,vt) <= 0:
                return self.log[i]

        return None

    def performOperation(self,op):
        if op.type == OpType.ADD:
            print 'added', op.stroke
            self.strokes.insert(op.pos,op.stroke);
        if op.type == OpType.DEL:
            print 'deleted', op.pos
            print self.strokes
            del self.strokes[op.pos]
            print self.strokes
        self.window.scribbleArea.draw()
        pass

    def transform(self,ri,rj):
        oi = ri.op
        oj = rj.op
        PosI = oi.pos
        PosJ = oj.pos

        pi = ri.priority
        pj = rj.priority


        if oi.type == OpType.ADD and oj.type == OpType.ADD:
            if PosI < PosJ:
                pass
            elif PosI > PosJ:
                oi.pos += 1
            else:
                if oi.stroke.id== oj.stroke.id:
                    op.type = OpType.NoOp
                else:
                    if pi > pj:
                        oi.pos += 1
                    else:
                        pass


        if oi.type == OpType.ADD and oj.type == OpType.DEL:
            if PosI < PosJ:
                pass
            else:
                oi.pos -= 1
                
            

        if oi.type == OpType.DEL and oj.type == OpType.ADD:
            if PosI < PosJ:
                pass
            else:
                oi.pos += 1

        if oi.type == OpType.DEL and oj.type == OpType.DEL:
            if PosI < PosJ:
                pass
            elif PosI > PosJ:
                oi.pos -= 1
            else:
                oi.type = OpType.NoOp

        print '\033[32m--transformed\033[0m',ri,'\n'

        
class Request:
    def __init__(self,sender=-1,vt=None,op=None,priority=0,request_id=0):
        if isinstance(op,dict):
            self.op = Operation(**op)
        else:
            self.op = op 

        if isinstance(priority,dict):
            self.priority = Priority(**priority)
        else:
            self.priority = priority

        self.sender = sender
        self.vt = vt
        self.request_id = request_id

    def __str__(self):
        return "< sd:{4} | vt:{3} | op:{2} | p:{1} | rid:{0} >".format(
                self.request_id[0:5],self.priority,self.op,self.vt,self.sender)

class Operation:
    def __init__(self,type=None,stroke_id=None,stroke=None,pos=-1,opos=-1):
        if isinstance(stroke,dict):
            self.stroke = Stroke(**stroke)
        else:
            self.stroke = stroke

        self.type = type
        self.stroke_id = stroke_id
        self.pos = pos
        if opos == -1:
            self.opos = pos
        else: # unmarshalling
            self.opos = opos

    def __str__(self):
        return "{{ {0} {1} at {2}({3})}}".format(
                self.type,self.stroke_id[0:5],self.pos,self.opos)

class OpType:
    ADD = 'ADD'
    DEL = 'DEL'
    NoOp = 'NoOp'
