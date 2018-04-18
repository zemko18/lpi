import os
import sys
sys.path[0:0] = [os.path.join(sys.path[0], '../examples/sat')]
import sat


Agatha = 0
Butler = 1
Charles = 2
People = [Agatha, Butler, Charles]
P = len(People)
Names = ['Agatha', 'Butler', 'Charles ']


def killed(p1, p2):
    return 0 * P * P + p2 * P + p1 + 1

def hates(p1, p2):
    return 1 * P * P + p1 * P + p2 + 1

def richer(p1, p2):
    return 2 * P * P + p1 * P + p2 + 1

class WhoKilledAgatha():        
    
    def ries(self):
        
        subor = sat.DimacsWriter('./vstup.txt')
        
        ##Someone in Dreadsbury Mansion killed Aunt Agatha. 
        for x in People:
            subor.writeLiteral(killed(x, Agatha))
        subor.finishClause()
        
        ##A killer always hates, and is no richer than his victim.
        for x in People:
            for y in People:
                subor.writeClause([-killed(x, y), hates(x, y)])
                subor.writeClause([-killed(x, y), -richer(x, y)])
        
        ##Charles hates no one whom Agatha hates.
        for x in People:
            subor.writeClause([-hates(Agatha, x), -hates(Charles, x)])

        ##Agatha hates everybody except the butler.
        subor.writeClause([hates(Agatha, Agatha)])
        subor.writeClause([-hates(Agatha, Butler)])
        subor.writeClause([hates(Agatha, Charles)])
        
        ##The butler hates everyone not richer than Aunt Agatha.
        for x in People:
            subor.writeClause([richer(x, Agatha), hates(Butler, x)])
            
        ##The butler hates everyone whom Agatha hates.
        for x in People:
            subor.writeClause([-hates(Agatha, x), hates(Butler, x)])

        ##No one hates everyone.
        for x in People:
            subor.writeClause([-hates(x, Agatha), -hates(x, Butler), -hates(x, Charles)])


            
        ok, riesenie = sat.SatSolver().solve('vstup.txt', 'vystup.txt')
        if not ok:
            print('Chyba')
            return
                        
        for lit in riesenie: # lit = literaly
            for v in People: # v = vrahovia
                if lit == killed(v, Agatha):          
                    with open('vstup.txt', 'a') as subor:                      
                        subor.write("{} 0\n".format(-killed(v, Agatha))) #doplnenie o negaciu dokazovaneho tvrdenia

                    ok2, riesenie2 = sat.SatSolver().solve('vstup.txt', 'vystup.txt')
                    if not ok2:
                        print('Vrahom je {} '.format(Names[v]))


vrah = WhoKilledAgatha()
vrah.ries()                      
