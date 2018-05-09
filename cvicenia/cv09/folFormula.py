import copy

class Term():
    def __init__(self):
        pass
    def subtfs(self):
        pass
    def name(self):
        pass
    def toString(self):
        pass
    def equals(self,other):
        pass
    def variables(self):
        pass
    def constants(self):
        pass
    def functions(self):
        pass
    def eval(self,m,t):
        pass
    def substitute(self,var,t):
        pass

class Variable(Term):
    def __init__(self, name):
        self.meno = name
        
    def subts(self):
        return []
    
    def name(self):
        return self.meno
    
    def toString(self):
        if type(self.meno)== str:
            return self.meno 
        return self.meno.toString()
    
    def equals(self, other):
        if type(self) != type(other)or self.toString() != other.toString():
            return False
        return True
    
    def variables(self):
        return set([self.meno])
    
    def constants(self):
        return set()
    
    def functions(self):
        return set()
    
    def eval(self, m, e):
        return e[self.meno]
    
    def substitute(self, var, term):
        if var == self.meno:
            self.substitued = term
            self.meno = term
            return self.meno
        return self

class Constant(Term):
    def __init__(self, name):
        self.meno = name
        
    def subts(self):
        return list()
    
    def name(self):
        return self.meno
    
    def toString(self):
        return self.meno
    
    def equals(self, other):
        if type(self) != type(other) or self.toString() != other.toString():
            return False
        return True
    
    def variables(self):
        return set()
    
    def constants(self):
        return set([self.meno])
    
    def functions(self):
        return set()
    
    def eval(self, m, e):
        return m.iC[self.meno]
    
    def substitute(self, var, term):   
        new = copy.deepcopy(self)
        if (self.equals(var)):
            new.meno = term
        return new

class Function(Term):
    def __init__(self, name, array = []):
        self.meno = name
        self.array = array
        
    def subts(self):
        return self.array
    
    def name(self):
        return self.meno
    
    def toString(self):
        ret = self.meno + '(';
        for a in self.array:
            ret += a.toString() + ','
        return ret[:-1] + ')'
    
    def equals(self, other):
        if type(self) != type(other) or self.toString() != other.toString():
            return False
        return True
    
    def variables(self):
        m = set()
        for a in self.array:
            m = m.union(a.variables())
        return m

    def constants(self):
        m =  set()
        for a in self.array:
            m = m.union(a.constants())
        return m

    def functions(self):
        m = set()
        m.add(self.meno)
        for a in self.array:
            m = m.union(a.functions())
        return m
    

    def eval(self, m, e):
        for a in self.array:
            mn = a.eval(m, e)
        return m.iF["bff"](mn)

    def substitute(self, var, term):
        [a.substitute(var, term) for a in self.array]
        return self

class Formula():
    def __init__(self):
        pass
    def subfs(self):
        pass
    def toString(self):
        pass
    def equals(self, other):
        pass
    def variables(self):
        pass
    def constants(self):
        pass
    def functions(self):
        pass
    def predicates(self):
        pass
    def isSatisfied(self, m, e):
        pass
    def freeVariables(self):
        pass
    def substituste(self):
        pass

class Predicate(Formula):
    def __init__(self, name, array):
        self.meno = name
        self.array = array

    def name(self):
        return self.meno

    def subfs(self):
        return []

    def subts(self):
        return self.array

    def toString(self):
        ret = self.meno +'(';
        for a in self.array:
            ret += a.toString() + ','
        return ret[:-1] +')'
    
    def equals(self, other):
        if type(self) != type(other) or self.toString() != other.toString():
            return False
        return True

    def variables(self):
        m = set()
        for a in self.array:
            m = m.union(a.variables())
        return m

    def constants(self):
        m = set()
        for a in self.array:
            m = m.union(a.constants())
        return m

    def functions(self):
        m = set()
        for a in self.array:
            m = m.union(a.functions())
        return m

    def predicates(self):
        return set([self.meno])

    def isSatisfied(self, m, e):
        p = []
        p2 =[m.iP[self.meno]]
        vysl = True
        for i in self.array:
            if isinstance(i,Constant):
                if [m.iC[i.name()]] in p:
                    vysl = False
                    return vysl
                
            if isinstance(i,Variable):
                if [e[i.name()]] in p:
                    vysl = False
                return vysl
        return vysl

    def freeVariables(self):
        m = set()
        for a in self.array:
            m = m.union(a.variables())
        return m

    def substitute(self, var, term):
        if  Predicate == type(term):
            return new
        new = copy.deepcopy(self)
        for i in range(len(new.array)):
            if (new.array[i].equals(term)):
                new.array[i] = new.array[i].substitute(var,term)
        return new

class Negation(Formula):
    def __init__(self, originalFormula):
        self.originalFormula = originalFormula

    def originalFormula(self):
        return self.originalFormula

    def subfs(self):
        return self.originalFormula.subfs()

    def toString(self):
        return '-' + self.originalFormula.toString()

    def equals(self, other):
        if type(self) != type(other) or self.toString() != other.toString():
            return False
        return True

    def variables(self):
        return self.originalFormula.variables()

    def constants(self):
        return self.originalFormula.constants()

    def functions(self):
        return self.originalFormula.functions()

    def predicates(self):
        return self.originalFormula.predicates()

    def isSatisfied(self, m, e):
        return not self.originalFormula.isSatisfied(m, e)

    def freeVariables(self):
        return self.originalFormula.freeVariables()

    def substitute(self, var, t):
        self.originalFormula.substitute(var, t)
        return self

class Disjunction(Formula):
    def __init__(self, array):
       self.array = array

    def subfs(self):
        return self.array

    def toString(self):
        return "(" + "|".join([i.toString() for i in self.array]) + ")"

    def equals(self, other):
        if type(self) != type(other) or self.toString() != other.toString():
            return False
        return True

    def variables(self):
        m = set()
        for a in self.array:
            m = m.union(a.variables())
        return m

    def constants(self):
        m = set()
        for a in self.array:
            m = m.union(a.constants())
        return m

    def functions(self):
        m = set()
        for a in self.array:
            m = m.union(a.functions())
        return m

    def predicates(self):
        m = set()
        for a in self.array:
            m = m.union(a.predicates())
        return m

    def isSatisfied(self, m, e):
        for a in self.array:
            if a.isSatisfied(m, e) is True:
                return True
        return False

    def freeVariables(self):
        m = set()
        for a in self.array:
            m = m.union(a.freeVariables())
        return m

    def substitute(self, var, term):
        return [a.substitute(var, t) for a in self.array]
    

class Conjunction(Formula):
    def __init__(self, array):
       self.array = array

    def subfs(self):
        return self.array

    def toString(self):
        return "("+ "&".join([i.toString() for i in self.array]) + ")"

    def equals(self, other):
        if type(self) != type(other) or self.toString() != other.toString():
            return False
        return True

    def variables(self):
        m = set()
        for a in self.array:
            m = m.union(a.variables())
        return m

    def constants(self):
        m = set()
        for a in self.array:
            m = m.union(a.constants())
        return m

    def functions(self):
        m = set()
        for a in self.array:
            m = m.union(a.functions())
        return m

    def predicates(self):
        m = set()
        for a in self.array:
            m = m.union(a.predicates())
        return m

    def isSatisfied(self, m, e):
        for var in self.array:
            if var.isSatisfied(m,e) == False:
                return False
        return True

    def freeVariables(self):
        m = set()
        for a in self.array:
            m = m.union(a.freeVariables())
        return m

    def substitute(self, var, term):
        
        return [a.substitute(var, t) for a in self.array]
    
class BinaryFormula(Formula):
    def __init__(self, leftSide, rightSide):
        self.leftSide = leftSide
        self.rightSide = rightSide

    def leftSide(self):
        return self.leftSide

    def rightSide(self):
        return self.rightSide

class Implication(BinaryFormula):
    def equals(self, other):
        if type(self) != type(other) or self.toString() != other.toString():
            return False
        return True
    
    def toString(self):
        return "(" + self.leftSide.toString() + "->" + self.rightSide.toString() + ")"

    def subfs(self):
        return [self.leftSide,self.rightSide]

    def variables(self):
        return self.leftSide.variables().union(self.rightSide.variables())

    def constants(self):
        return self.leftSide.constants().union(self.rightSide.constants())

    def functions(self):
        return self.leftSide.functions().union(self.rightSide.functions())

    def predicates(self):
        return self.leftSide.predicates().union(self.rightSide.predicates())

    def isSatisfied(self,m,e):
        if self.leftSide.isSatisfied(m,e) and not self.rightSide.isSatisfied(m,e):
                return False
        return True

    def freeVariables(self):
        return self.leftSide.freeVariables().union(self.rightSide.freeVariables())

    def substitute(self,var,term):
        self.leftSide.substitute(var, term)
        self.rightSide.substitute(var, term)
        return self
    
class Equivalence(BinaryFormula):
    def toString(self):
        return "(" + self.leftSide.toString() + "<->" + self.rightSide.toString() + ")"

    def equals(self, other):
        if type(self) != type(other) or self.toString() != other.toString():
            return False
        return True

    def subfs(self):
        return [self.leftSide, self.rightSide]

    def variables(self):
        return self.leftSide.variables().union(self.rightSide.variables())

    def constants(self):
        return self.leftSide.constants().union(self.rightSide.constants())

    def functions(self):
        return self.leftSide.functions().union(self.rightSide.functions())

    def predicates(self):
        return self.leftSide.predicates().union(self.rightSide.predicates())

    def isSatisfied(self,m,e):
        if self.leftSide.isSatisfied(m,e) and self.rightSide.isSatisfied(m,e):
             return True
        if not self.leftSide.isSatisfied(m,e) and not self.rightSide.isSatisfied(m,e):
            return True
        return False

    def freeVariables(self):
        return self.leftSide.freeVariables().union(self.rightSide.freeVariables())

    def substitute(self,var,term):
        self.leftSide.substitute(var, term)
        self.rightSide.substitute(var, term)
        return self

class QuantidiedFormula(Formula):
    def __init__(self, qvar, originalFormula):
        self.originalFormula = originalFormula
        self.qvar = qvar

    def originalFormula(self):
        return self.originalFormula

    def qvar(self):
        return self.qvar

class ForAll(QuantidiedFormula):
    def toString(self):
        return self.qvar + self.originalFormula.toString()

    def equals(self, other):
        if type(self) != type(other) or self.toString() != other.toString():
            return False
        return True

    def freeVariables(self):
        return self.originalFormula.freeVariables() - set(self.qvar)

    def substitute(self, var, term):
        self.originalFormula.substitute(var, term)
        return self

class Exists(QuantidiedFormula):
    def toString(self):
        return self.qvar + self.originalFormula.toString()

    def equals(self, other):
        if type(self) != type(other) or self.toString() != other.toString():
            return False
        return True

    def freeVariables(self):
        return self.originalFormula.freeVariables() - set(self.qvar)

    def substitute(self, var, t):
        self.originalFormula.substitute(var, t)
        return self
