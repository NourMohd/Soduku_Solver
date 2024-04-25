class GridVariable():
    def __init__(self,i,j,updatecallback,val=None) -> None:
        self.i = i
        self.j = j
        self.notifyBoard = updatecallback
        if val:
            self.domain = set([val])
            
        else:
            self.domain = set([1,2,3,4,5,6,7,8,9])
        self.val = val
    def __hash__(self) -> int:
        return hash((self.i,self.j))
    def __repr__(self) -> str:
         return str((self.i,self.j))
    def set_val(self,val):
        self.val = val
        self.domain = set([val])
        self.notifyBoard(self)
    def update_domain(self,val):
         self.domain.remove(val)
         if(len(self.domain)==0):
              self.notifyBoard(self)
class Board():
    def __init__(self,notifyUI) -> None:
        self.vars = [[GridVariable(i,j,self.handle_notification) for j in range(9)] for i in range(9)]
        self.arcs = dict()
        self.notifyUI = notifyUI
        self.incon = set()
        self.init_arcs()
    def init_arcs(self) -> None:
        for i in range(9):
            for j in range(9):
                x = self.vars[i][j]
                self.arcs[x] = self.get_arcs(x)
    def get_arcs(self,var) -> set:
                arcs = set()
                i = var.i
                j = var.j
                bigGrid_i = (i//3)*3
                bigGrid_j = (j//3)*3 
                for k in range(9):
                    arcs.add(self.vars[i][k])
                    arcs.add(self.vars[k][j])
                for k in range(3):
                     for l in range(3):
                          arcs.add(self.vars[bigGrid_i+k][bigGrid_j+l])
                arcs.remove(var)
                return arcs
    def handle_notification(self,var):
        if(len(var.domain)==0):
              self.incon.add((var.i,var.j))
              self.notifyUI(self.incon)
        else:
             incons = self.get_incons(var).get(var.val,set())
             if(len(incons)>0):
                  incon = [var]
                  incon.extend(list(incons))
                  self.incon.update(map(lambda x: (x.i,x.j),incon))
                  self.notifyUI(self.incon)
        
    def update_board(self):
         for row in self.vars:
              for var in row:
                incons = self.get_incons(var)
                for key in incons:
                   print(key)
                   var.update_domain(key)
    def get_incons(self,var):
        incons = dict()
        arcs = self.arcs[var]
        for arc in arcs:
            if len(arc.domain)>1:
                continue
            for val in var.domain:
                if(next(iter(arc.domain))==val):
                    incon = incons.get(val,set())
                    incon.add(arc)
                    incons[val] = incon
                    break
        return incons
    def __getitem__(self,items):
         if(type(items) == tuple):
              return self.vars[items[0]][items[1]]
         if(type(items) == int):
              return self.vars[items]
         return
